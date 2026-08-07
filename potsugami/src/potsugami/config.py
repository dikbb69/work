"""設定値・定数。

スコアの重みなど「発案者の体感に合わせて回すつまみ」はすべてここに集める。
CLI からは --param key=value で個別に上書きできる。
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields

USER_AGENT = "potsugami/0.1 (potsu-shrine finder; personal research tool)"

# 発案者の拠点 (東京都江東区役所付近)。直線距離列の基準点。
HOME_LAT = 35.6731
HOME_LON = 139.8173

# Overpass API エンドポイント (上から順に試す)
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# 地理院タイル
GSI_TILE_BASE = "https://cyberjapandata.gsi.go.jp/xyz"
# ベクトルタイル (建物ポリゴン)。source 名 → (URL テンプレート, ズーム, 建物レイヤ名候補)
#   optimal: 最適化ベクトルタイル (現行提供。建物レイヤは BldA)
#   experimental: ベクトルタイル提供実験 (旧。提供終了がアナウンスされており、
#                 optimal で建物が取れない場合の代替として残す)
GSI_BVMAP_SOURCES: dict[str, tuple[str, int, tuple[str, ...]]] = {
    "optimal": (
        GSI_TILE_BASE + "/optimal_bvmap-v1/{z}/{x}/{y}.pbf",
        16,
        ("blda", "building", "建築物"),
    ),
    "experimental": (
        GSI_TILE_BASE + "/experimental_bvmap/{z}/{x}/{y}.pbf",
        16,
        ("building", "建築物"),
    ),
}
GSI_BVMAP_DEFAULT_SOURCE = "optimal"
# 無壁舎 (温室・車庫・上屋など) の ftCode (基盤地図情報の種別コード)。
# 除外はしない (ビニールハウス地帯が「無人」判定になるため)。
# ScoreParams.roofless_weight で低重み算入する。
GSI_ROOFLESS_FTCODES = {"3103", "3104"}

# 標高タイル (上から順にフォールバック)。(タイルID, ズーム)
# dem5a/b/c は 5m メッシュ (整備範囲が地域で異なる)、dem_png は 10m メッシュ全国。
# dem_png の高さ精度は ±5m 級なので、これで測った小さな標高差は信用しない
# (レポートに低精度フラグを出す)。
GSI_DEM_SOURCES = (
    ("dem5a_png", 15),
    ("dem5b_png", 15),
    ("dem5c_png", 15),
    ("dem_png", 14),
)
DEM_LOW_PRECISION_KINDS = {"dem_png"}


@dataclass
class ScoreParams:
    """孤立度スコア v0.1 (距離減衰カーネル和) のパラメータ。

      P     = Σ_i a_i · exp(-d_i / tau_m)
      S_iso = 100 · exp(-P / p_scale)
        d_i : 神社から建物 (ポリゴン外周) までの距離。self_exclusion_m 以内は境内扱いで除外
        a_i : min(面積 / area_norm_m2, area_cap)。面積不明 (OSM 代表点) は 1.0。
              無壁舎 (温室・車庫) は× roofless_weight で算入

    リング計数の旧方式は「田んぼの中の集落鎮守 (近接建物ゼロが自動成立) が
    山中のポツ神を逆転する」「境界 ±2m でスコアが跳ぶ」という構造問題があり、
    設計レビューを受けてカーネル和に置き換えた。
    検算 (a_i=1): 集落 30 戸 (300m 中心) → S≈7、小屋 1 棟 80m のみ → S≈77、無建物 → 100。
    """
    # 境内自己除外: この距離以内の建物は社殿・社務所とみなして無視する
    # (数は n_adjacent 列に残し、屋敷神の偽陽性チェックに使う)
    self_exclusion_m: float = 40.0
    # 建物探索半径。tau=180m なら 1000m 超の建物の寄与は無視できる
    search_radius_m: float = 1000.0
    tau_m: float = 180.0
    p_scale: float = 2.5
    area_norm_m2: float = 80.0
    area_cap: float = 5.0
    roofless_weight: float = 0.3
    # 表示用リング境界 (スコアには使わない。CSV の n_inner / n_outer 列)
    inner_r_m: float = 150.0
    outer_r_m: float = 500.0

    def override(self, kv: dict[str, float]) -> "ScoreParams":
        valid = {f.name for f in fields(self)}
        bad = set(kv) - valid
        if bad:
            raise ValueError(f"unknown score params: {sorted(bad)}; valid: {sorted(valid)}")
        d = {f.name: getattr(self, f.name) for f in fields(self)}
        d.update(kv)
        return ScoreParams(**d)


@dataclass
class NuisanceParams:
    """迷惑土地利用 (メガソーラー・工場・採石場・ゴルフ場) と幹線道路の減点係数。

    「建物がない」≠「静かで人がいない」の穴を塞ぐ。距離はいずれも
    施設ジオメトリ (頂点列) までの最短距離。
    """
    near_m: float = 150.0
    far_m: float = 400.0
    near_mult: float = 0.5
    far_mult: float = 0.7
    road_dist_m: float = 100.0     # 幹線道路 (国道・主要地方道クラス) がこの距離内
    road_mult: float = 0.7


@dataclass
class StepsParams:
    """石段フィルタのパラメータ。"""
    # 神社からこの距離以内の highway=steps を参道候補としてマッチ
    match_radius_m: float = 120.0
    # 段数レンジ推定: 段数 ≈ 標高差 / 蹴上げ。踊り場込みの実効値として広めに取る。
    riser_min_m: float = 0.18   # 段数の上限側 (細かい段)
    riser_max_m: float = 0.30   # 段数の下限側 (踊り場が多い)


# 都道府県名 → ISO3166-2 コード (Overpass の area 検索に使う)
PREF_ISO: dict[str, str] = {
    "北海道": "JP-01", "青森県": "JP-02", "岩手県": "JP-03", "宮城県": "JP-04",
    "秋田県": "JP-05", "山形県": "JP-06", "福島県": "JP-07", "茨城県": "JP-08",
    "栃木県": "JP-09", "群馬県": "JP-10", "埼玉県": "JP-11", "千葉県": "JP-12",
    "東京都": "JP-13", "神奈川県": "JP-14", "新潟県": "JP-15", "富山県": "JP-16",
    "石川県": "JP-17", "福井県": "JP-18", "山梨県": "JP-19", "長野県": "JP-20",
    "岐阜県": "JP-21", "静岡県": "JP-22", "愛知県": "JP-23", "三重県": "JP-24",
    "滋賀県": "JP-25", "京都府": "JP-26", "大阪府": "JP-27", "兵庫県": "JP-28",
    "奈良県": "JP-29", "和歌山県": "JP-30", "鳥取県": "JP-31", "島根県": "JP-32",
    "岡山県": "JP-33", "広島県": "JP-34", "山口県": "JP-35", "徳島県": "JP-36",
    "香川県": "JP-37", "愛媛県": "JP-38", "高知県": "JP-39", "福岡県": "JP-40",
    "佐賀県": "JP-41", "長崎県": "JP-42", "熊本県": "JP-43", "大分県": "JP-44",
    "宮崎県": "JP-45", "鹿児島県": "JP-46", "沖縄県": "JP-47",
}


def pref_iso(pref: str) -> str:
    """都道府県名 (または ISO コードそのもの) → ISO3166-2 コード。"""
    if pref in PREF_ISO:
        return PREF_ISO[pref]
    if pref.upper().startswith("JP-") and pref.upper() in PREF_ISO.values():
        return pref.upper()
    raise ValueError(
        f"unknown prefecture: {pref!r} (例: 千葉県, または JP-12)"
    )
