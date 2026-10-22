#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""乖離の勘定表: LTDA 落札蓄電池のエリア照合（第1〜3回）と、北海道の接続済み・契約申込の属性別の kW 勘定

第9章 9.2 の末尾に置く「乖離の勘定表」と、3.4・5.5・9.2(b)・9.5.5 の「北海道の LTDA 落札蓄電池」の数値を作る。

手法:
  (A) LTDA 落札電源のエリア照合（第1〜3回共通。notes/28 §1.6 の方法を第1・2回にも適用）。
      OCCTO の約定結果の別紙（落札電源一覧。応札事業者名・案件名・電源種・落札容量[kW]）の全電源（蓄電池以外と
      LNG 専焼火力を含む）を転記し、別紙の地名（都道府県・市町村・発電所名）でエリアが決まる電源を固定する。
      地名のない電源を9エリアに総当たりで割り当て、各エリアの合計が本文 p.15 のエリア別落札容量
      （0.1万kW に丸めた公表値。誤差 ±0.05万kW＝±500kW）に一致する割当をすべて列挙する。
      頑健性として、(i) 地名の読みに疑いの余地がある蓄電池（第1回の旧 CSV の誤りを含む10件）も自由にした列挙、
      (ii) 旧 CSV の割当（森町睦実２＝北海道）での各エリア合計、(iii) 第3回で地名の推定に疑いのある3件
      （HC25 中国第一・HC25 東北第二・イーレックス新潟）を自由にした8通り、を行う。
      第3回の別解（しろくま33＋水素専焼のホクエナジー第一が北海道に入る割当。県市名の蓄電池を2件以上
      地名と異なるエリアへ動かす場合にだけ現れる。notes/28 §1.6）は、その割当で p.15 と一致することを検算する。
  (B) data/processed/ltda_battery_projects.csv の訂正（既存ファイルの訂正は許可済み。根拠は notes/33）。
      pref（都道府県）を地名どおりに直し、エリアの推定（area_est）、根拠（area_basis）、確度（area_conf）、
      照合で残る候補（area_candidates）、継続時間の区分（duration_class）の列を加える。
  (C) 北海道の LTDA 落札蓄電池の合計（主の割当と別解）、6時間級の kWh を4時間に換算した値、
      外生の契約型容量 K_exo（接続済み約20万kW＋LTDA 北海道分）。
  (D) 乖離の勘定表。行は案件（LTDA 北海道分・SII 交付決定の北海道分・既知の運開案件）、列は kW・kWh・
      duration・運開（予定）時期・収入形態。集計は「接続済み（2026年5月末、約20万kW）」と「契約申込（約234万kW）」
      の合計254万kW を、LTDA／補助（SII 交付決定）／併設／マーチャント／不明 に分ける。各属性に表9.7 の APV
      （39 の apv_decomposition.csv の「収入の基準＝実績整合」の行が主。r_A^M=9%（9.5.3 の主、39 の図と同じ）が主で 8% を参考に、
      旧基準（旧0.81PF・旧裾補正）を参考列に置く。LTDA は r_C=5%）を対応させ、「市場外収入で APV が正の kW」
      「APV が負のまま参入した kW」「属性不明の kW」に分け、不明の kW が建設されるとした場合に計測外の成分が
      埋める必要のある額（円）を残差として示す。9.2(e) の3つの解釈が説明しうる kW も対応させる。
      SII の交付決定一覧には kW がないので、補助額÷(補助率×実勢資本費) で kWh を推定し、
      duration 2〜4時間で kW の幅にする（推定であることを明記）。
出典（すべて一次資料、またはリポジトリ内の資料）:
  OCCTO 長期脱炭素電源オークション約定結果 本文・別紙（応札年度2023・2024・2025。data/raw/ltda/）。
  SII「令和6年度／令和7年度 再生可能エネルギー導入拡大・系統用蓄電池等電力貯蔵システム導入支援事業費補助金
  交付決定について」（2024年12月23日、2025年12月25日。https://sii.or.jp/chikudenchi06/uploads/R6kess_d_koufukettei.pdf、
  https://sii.or.jp/chikudenchi07/uploads/R7kess_koufukettei.pdf。2026年10月21日閲覧。北海道の行だけを転記）。
  接続済み約20万kW・契約申込約234万kW（2026年5月末）は原稿 1.1.3・9.1 の値（北海道電力ネットワークの公表値とされるが、
  一次資料はリポジトリになく未照合）。Helios（5万kW/10.4万kWh、マーチャント）は原稿 3.7・8.7（ESS News 2025、
  HD Renewable Energy 2025）。北豊富（24万kW/72万kWh、風力送電網の併設）と DAX 札幌・ENEOS 室蘭は notes/14（二次資料由来）。
出力: data/processed/ltda_battery_projects.csv（訂正）、ltda_area_reconciliation.csv、ltda_hokkaido_summary.csv、
      gap_ledger_projects.csv、gap_ledger_summary.csv、gap_ledger_apv_basis.csv（D1 の収益基準の APV と APV=0 の割引率）、
      figures/hokkaido/gap_ledger.png
限界: 別紙にエリアの列はなく、第2回の地名のない案件と第3回の北海道の蓄電池はエリア別落札容量との整合による推定
      （公表値ではない）。LTDA の落札容量は契約容量（期待容量＝設備容量×調整係数以下）で、設備容量はこれより大きい。
      LTDA 落札案件が北海道電力ネットワークの「契約申込」に含まれるかは公表資料で確認できない（含まれると仮定）。
      SII 案件の kW・運開時期は一覧にない。接続済み約20万kW の内訳は公表されておらず、大半が「不明」に残る。
      APV は K=0（参入に有利な側）。マーチャント4h・補助（4h）・LTDA の APV は 39 の apv_decomposition.csv の値で、
      収入の基準は実績整合が主（pi_k_curve_v3.csv の π_実績整合。モデル直値と旧基準＝旧0.81PF・旧裾補正を参考に併記）。
      r_A^M は 9% が主、8% が参考。IRR・割引率3%/6% の APV と2h（Helios 型、実績価格の上の戦略c を2時間で直接計算）は
      39 と同じ式を本スクリプトで直接計算し、4h では 39 の値と一致することを確かめる。
      θ=1.567 の2h の収益は4h の粗収益の比で換算した近似。
      残差（円）は、kW では全量が建設される場合の上限だが、1kW あたりの不足は K=0 の値（全量が建設されれば π(K) の低下で
      大きくなる）なので、総額は規模の目安であり上限ではない（2026-10-21 の検証で訂正）。勘定の kW は LTDA が落札容量
      （契約容量）、ほかは設備の kW で、LTDA を設備容量に換算した上限側の行を参考に置く（同）。
2026-10-21 の修正（39 の apv_decomposition.csv の更新に合わせる）: 39 のケース名の変更（旧「θ=1（モデル…」→
      「θ=1（FY2023〜25）・旧0.81PF」、旧「θ=1 ×1.25」→「θ=1（FY2023〜25）・旧裾補正」、旧「FY2026上期水準 ×1.25」→
      「FY2026上期水準 θ=1.567・旧裾補正」）と列「収入の基準」の追加に対応し、各属性の APV を実績整合の行（主）に替えた。
      LTDA は収入の基準で1行に絞る（実績整合が主、旧裾補正を参考）。r_A^M の主を 8% から 9% に替え（9.5.3）、8% を参考列に残す。
      勘定表に APV の数値列（主・参考）と、3分類（市場外収入で APV が正／負のまま参入／不明）の集計行を加えた。
"""
import itertools
import os
from collections import Counter

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

AREAS = ["北海道", "東北", "東京", "中部", "北陸", "関西", "中国", "四国", "九州"]
TOL = 500  # kW（p.15 は0.1万kW 単位の公表値。±0.05万kW）

# ============================================================================================
# (A) 別紙の転記（全電源）と本文 p.15 のエリア別落札容量
#     各要素: (key, no, 区分, 落札容量kW, 地名で決まるエリア or None, 地名の根拠)
#     区分: "B"=蓄電池, "O"=蓄電池以外の脱炭素電源, "L"=LNG 専焼火力
# ============================================================================================
R1 = [  # 応札年度2023（2024-04-26 公表）。本文 p.15: 北海道120.7 東北78.4 東京60.5 中部178.8 北陸4.0 関西324.6 中国187.7 四国0.0 九州21.8
    ("米原湖東", 1, "B", 96208, "関西", "滋賀県米原市"), ("静岡菊川", 2, "B", 22077, "中部", "静岡県菊川市"),
    ("苫東厚真", 3, "O", 132200, "北海道", "北海道電力 苫東厚真"), ("奥多々良木3", 4, "O", 254308, "関西", "兵庫県"),
    ("奥多々良木4", 5, "O", 254308, "関西", "兵庫県"), ("島根3", 6, "O", 1315707, "中国", "島根県"),
    ("青森野木山口", 7, "B", 27158, "東北", "青森県青森市"), ("岡山美作", 8, "B", 22719, "中国", "岡山県美作市"),
    ("宮の沢", 9, "B", 28060, "北海道", "北海道札幌市西区"), ("留辺蘂", 10, "B", 25250, "北海道", "北見市留辺蘂町"),
    ("神戸1", 11, "O", 131433, "関西", "兵庫県神戸市"), ("神戸2", 12, "O", 132000, "関西", "兵庫県神戸市"),
    ("高根第一", 13, "O", 68321, "中部", "岐阜県高山市"), ("苫小牧", 14, "B", 70213, "北海道", "北海道苫小牧市"),
    ("白老", 15, "B", 39027, "北海道", "北海道白老町"), ("森町睦実2", 16, "B", 56351, "中部", "静岡県周智郡森町睦実"),
    ("苫東バイオ", 17, "O", 100000, "北海道", "北海道苫小牧市"), ("石狩湾新港バイオ", 18, "O", 99258, "北海道", "北海道石狩湾新港"),
    ("伊賀川西", 19, "B", 22531, "中部", "三重県伊賀市"), ("恵庭西島松", 20, "B", 23217, "北海道", "北海道恵庭市"),
    ("小矢部石名田", 21, "B", 39983, "北陸", "富山県小矢部市"), ("熊本弓削", 22, "B", 29615, "九州", "熊本県熊本市"),
    ("田川伊加利", 23, "B", 22189, "九州", "福岡県田川市"), ("白老北吉原", 24, "B", 23393, "北海道", "北海道白老郡白老町"),
    ("白老石山", 25, "B", 39004, "北海道", "北海道白老郡白老町"), ("福知山荒河", 26, "B", 36918, "関西", "京都府福知山市"),
    ("松阪上川", 27, "B", 28568, "中部", "三重県松阪市"), ("美唄", 28, "B", 39004, "北海道", "北海道美唄市"),
    ("由利本荘乙助渕", 29, "B", 37597, "東北", "秋田県由利本荘市"), ("臼杵", 30, "B", 37019, "九州", "大分県臼杵市"),
    ("直方", 31, "B", 37019, "九州", "福岡県直方市"), ("三池改修", 32, "O", 55300, "九州", "福岡県大牟田市"),
    ("三重多気", 33, "B", 36222, "中部", "三重県多気町"), ("FUKO-B1", 34, "B", 36814, None, "地名なし"),
    ("西郷1", 35, "B", 16535, "東北", "福島県西郷村"), ("西郷2", 36, "B", 16527, "東北", "福島県西郷村"),
    ("今別", 37, "B", 32677, "東北", "青森県今別町"), ("石川2", 38, "B", 37997, "東北", "福島県石川町"),
    ("新美祢2", 39, "B", 74669, "中国", "山口県美祢市"), ("長沼", 40, "B", 37515, "北海道", "北海道夕張郡長沼町"),
    ("碧南4", 41, "O", 187334, "中部", "愛知県碧南市"), ("碧南5", 42, "O", 187315, "中部", "愛知県碧南市"),
    ("LNG石狩湾新港", "L1", "L", 551217, "北海道", "北海道"), ("LNG東新潟6", "L2", "L", 615849, "東北", "新潟県"),
    ("LNG南港1", "L3", "L", 591812, "関西", "大阪府"), ("LNG南港2", "L4", "L", 591812, "関西", "大阪府"),
    ("LNG南港3", "L5", "L", 591812, "関西", "大阪府"), ("LNG柳井", "L6", "L", 463535, "中国", "山口県"),
    ("LNG千葉袖ケ浦", "L7", "L", 604831, "東京", "千葉県"), ("LNG姫路", "L8", "L", 565780, "関西", "兵庫県"),
    ("LNG知多7", "L9", "L", 589836, "中部", "愛知県"), ("LNG知多8", "L10", "L", 589836, "中部", "愛知県"),
]
T1 = dict(北海道=120.7, 東北=78.4, 東京=60.5, 中部=178.8, 北陸=4.0, 関西=324.6, 中国=187.7, 四国=0.0, 九州=21.8)

R2 = [  # 応札年度2024（2025-04-28 公表）。本文 p.15: 166.3 56.4 248.1 10.2 9.6 36.1 28.7 69.2 9.9
    ("東海第二", 1, "O", 1056000, "東京", "茨城県"), ("泊3", 2, "O", 902107, "北海道", "北海道電力 泊"),
    ("奥吉野1", 3, "O", 180323, "関西", "奈良県"), ("奥吉野2", 4, "O", 180323, "関西", "奈良県"),
    ("西条1", 5, "O", 94600, "四国", "愛媛県"), ("諸塚", 6, "O", 51800, "九州", "宮崎県"),
    ("Shizen-601", 7, "B", 47226, None, "地名なし"), ("柏崎刈羽6", 8, "O", 1195000, "東京", "東京電力 柏崎刈羽（東京エリアの電源）"),
    ("BatteryNo22", 9, "B", 129797, None, "地名なし"), ("BatteryNo31", 10, "B", 37827, None, "地名なし"),
    ("BatteryNo32", 11, "B", 30129, None, "地名なし"), ("BS浪江", 12, "B", 49905, "東北", "福島県浪江町"),
    ("EshiBEES1", 13, "B", 119266, None, "地名なし"), ("津山杉宮", 14, "B", 88654, "中国", "岡山県津山市"),
    ("Risu-101", 15, "B", 78922, None, "地名なし"), ("Risu-203", 16, "B", 40705, None, "地名なし"),
    ("Risu-301", 17, "B", 77545, None, "地名なし"), ("Risu-502", 18, "B", 39832, None, "地名なし"),
    ("青葉1", 19, "B", 29195, None, "地名なし"), ("青葉2", 20, "B", 25953, None, "地名なし"),
    ("青葉5", 21, "B", 25953, None, "地名なし"), ("青葉6", 22, "B", 25784, None, "地名なし"),
    ("室蘭", 23, "B", 46270, "北海道", "北海道室蘭市"), ("石巻", 24, "B", 25953, "東北", "宮城県石巻市"),
    ("SRE北海道G", 25, "B", 46270, "北海道", "案件名に「北海道」"), ("SRE山形県B", 26, "B", 29195, "東北", "案件名に「山形県」"),
    ("SRE秋田県F", 27, "B", 38930, "東北", "案件名に「秋田県」"), ("しろくま03", 28, "B", 36554, None, "地名なし"),
    ("しろくま04", 29, "B", 46591, None, "地名なし"), ("福島富岡2", 30, "B", 40582, "東北", "福島県富岡町"),
    ("青森十和田", 31, "B", 40566, "東北", "青森県十和田市"), ("青森階上", 32, "B", 40501, "東北", "青森県階上町"),
    ("青森八戸", 33, "B", 92548, "東北", "青森県八戸市"), ("北海道北見", 34, "B", 39383, "北海道", "北海道北見市"),
    ("LNG石狩湾新港3", "L1", "L", 551217, "北海道", "北海道"), ("LNG坂出5", "L2", "L", 561263, "四国", "香川県"),
    ("LNG市原", "L3", "L", 100550, "東京", "千葉県市原市"), ("LNG東邦瓦斯", "L4", "L", 101614, "中部", "東邦瓦斯（中部エリアの事業者）"),
]
T2 = dict(北海道=166.3, 東北=56.4, 東京=248.1, 中部=10.2, 北陸=9.6, 関西=36.1, 中国=28.7, 四国=69.2, 九州=9.9)

R3 = [  # 応札年度2025（2026-05-13 公表）。本文 p.15: 101.6 196.6 182.2 4.7 75.9 13.1 27.2 7.5 121.1
    ("大間", 1, "O", 1381275, "東北", "青森県大間町"), ("イーレックス新潟", 2, "O", 100926, "東北", "新潟県（推定）"),
    ("泊1", 3, "O", 557848, "北海道", "北海道電力 泊"), ("京極3", 4, "O", 185889, "北海道", "北海道電力 京極"),
    ("苫東厚真4", 5, "O", 132200, "北海道", "北海道電力 苫東厚真"), ("益田市", 6, "B", 75633, "中国", "島根県益田市"),
    ("新富町", 7, "B", 36722, "九州", "宮崎県新富町"), ("神戸1改修", 8, "O", 131433, "関西", "兵庫県神戸市"),
    ("HC25中国第一", 9, "B", 46927, "中国", "案件名に「中国」（推定）"), ("HC25東北第二", 10, "B", 43543, "東北", "案件名に「東北」（推定）"),
    ("三池水素", 11, "O", 146400, "九州", "福岡県大牟田市"), ("NRE中川第二", 12, "B", 46828, None, "地名なし"),
    ("Kingdom-3", 13, "B", 95582, None, "地名なし"), ("Kingdom-6", 14, "B", 45931, None, "地名なし"),
    ("Kingdom-1", 15, "B", 32778, None, "地名なし"), ("蓄電所3号", 16, "B", 36722, None, "地名なし"),
    ("Battery116号", 17, "B", 141527, None, "地名なし"), ("Battery23号", 18, "B", 140098, None, "地名なし"),
    ("ホクエナジー第一", 19, "O", 106654, None, "地名なし"), ("HD1号", 20, "B", 45192, None, "地名なし"),
    ("しろくま33", 21, "B", 33737, None, "地名なし"), ("しろくま36", 22, "B", 30128, None, "地名なし"),
    ("ZEUS-A", 23, "B", 75165, None, "地名なし"), ("ZEUS-B", 24, "B", 74163, None, "地名なし"),
    ("CS青森八戸2", 25, "B", 90734, "東北", "青森県八戸市"), ("鹿児島薩摩川内", 26, "B", 45705, "九州", "鹿児島県薩摩川内市"),
    ("宮城石巻2", 27, "B", 114012, "東北", "宮城県石巻市"), ("塩原2", 28, "O", 267550, "東京", "栃木県（塩原）"),
    ("LNG富山新港2", "L1", "L", 583750, "北陸", "富山県"), ("LNG新小倉6", "L2", "L", 900000, "九州", "福岡県北九州市"),
    ("LNG袖ケ浦新1", "L3", "L", 777058, "東京", "千葉県"), ("LNG袖ケ浦新2", "L4", "L", 777058, "東京", "千葉県"),
]
T3 = dict(北海道=101.6, 東北=196.6, 東京=182.2, 中部=4.7, 北陸=75.9, 関西=13.1, 中国=27.2, 四国=7.5, 九州=121.1)
TOTALS_P15 = {1: 976.6, 2: 634.5, 3: 729.9}   # 本文 p.15 の全国の落札容量（万kW）
BATT_P14 = {1: 1092076, 2: 1370036, 3: 1251127}  # 別紙の蓄電池合計（本文 p.14 の 109.2・137.0・125.1万kW と一致）


def enumerate_assignments(projects, target, free_keys):
    """free_keys の電源を9エリアに総当たりで割り当て、各エリアの合計が target（万kW）と ±TOL kW で一致する割当を列挙する。"""
    base = {a: 0 for a in AREAS}
    for key, _, _, kw, area, _ in projects:
        if key not in free_keys:
            base[area] += kw
    need = {a: target[a] * 1e4 - base[a] for a in AREAS}
    if any(need[a] < -TOL for a in AREAS):
        return []
    items = sorted([(kw, key) for key, _, _, kw, _, _ in projects if key in free_keys], reverse=True)
    sols, cur, asg = [], {a: 0.0 for a in AREAS}, {}
    suffix = np.cumsum([kw for kw, _ in items][::-1])[::-1].tolist() + [0]

    def rec(j):
        if j == len(items):
            if all(abs(cur[a] - need[a]) <= TOL for a in AREAS):
                sols.append(dict(asg))
            return
        # 残りで埋めきれない不足があれば打ち切り
        if sum(max(0.0, need[a] - cur[a] - TOL) for a in AREAS) > suffix[j] + 1e-9:
            return
        kw, key = items[j]
        for a in AREAS:
            if cur[a] + kw > need[a] + TOL:
                continue
            cur[a] += kw; asg[key] = a
            rec(j + 1)
            cur[a] -= kw; del asg[key]
    rec(0)
    return sols


def area_sums(projects, assign):
    s = {a: 0 for a in AREAS}
    for key, _, _, kw, area, _ in projects:
        s[assign.get(key, area)] += kw
    return s


def check_sums(projects, assign, target):
    s = area_sums(projects, assign)
    return {a: (round(s[a] / 1e4, 2), target[a], abs(s[a] - target[a] * 1e4) <= TOL) for a in AREAS}


recon_rows = []
print("=== (A) LTDA 落札電源のエリア照合（本文 p.15 のエリア別落札容量、±0.05万kW）===")
for rnd, proj, tgt in ((1, R1, T1), (2, R2, T2), (3, R3, T3)):
    tot = sum(p[3] for p in proj)
    batt = sum(p[3] for p in proj if p[2] == "B")
    print(f"第{rnd}回: 別紙の全電源 {tot / 1e4:.1f}万kW（p.15 {TOTALS_P15[rnd]}）、蓄電池 {batt:,}kW（p.14 {BATT_P14[rnd]:,}）、"
          f"p.15 の9エリア合計 {sum(tgt.values()):.1f}")
    assert abs(tot / 1e4 - TOTALS_P15[rnd]) < 0.06 and batt == BATT_P14[rnd]
    recon_rows.append(dict(回=rnd, 検査="別紙の合計と本文の公表値", 自由にした電源="—", 解の数=np.nan,
                           北海道の蓄電池kW_最小=np.nan, 北海道の蓄電池kW_最大=np.nan,
                           備考=f"全電源 {tot:,}kW（p.15 {TOTALS_P15[rnd]}万kW）、蓄電池 {batt:,}kW（p.14 と一致）"))


def hk_batt(proj, sol):
    return sum(kw for key, _, typ, kw, area, _ in proj if typ == "B" and sol.get(key, area) == "北海道")


def run_case(rnd, proj, tgt, free, label):
    sols = enumerate_assignments(proj, tgt, set(free))
    hk = [hk_batt(proj, s) for s in sols]
    cnt = Counter(tuple(sorted(k for k, v in s.items() if v == "北海道")) for s in sols)
    note = "; ".join(f"{'+'.join(k) if k else '（地名のない電源は北海道に入らない）'}: {c}解" for k, c in cnt.most_common())
    print(f"  第{rnd}回 [{label}] 自由 {len(free)}件 → 解 {len(sols)}通り、北海道の蓄電池 "
          f"{min(hk) if hk else float('nan'):,}〜{max(hk) if hk else float('nan'):,}kW。北海道に入る自由な電源: {note}")
    recon_rows.append(dict(回=rnd, 検査=label, 自由にした電源="、".join(free), 解の数=len(sols),
                           北海道の蓄電池kW_最小=min(hk) if hk else np.nan, 北海道の蓄電池kW_最大=max(hk) if hk else np.nan,
                           備考=note))
    return sols


# 第1回: 主（地名で固定、地名のない FUKO-B1 だけ自由）と、地名の読みを疑う10件を自由にした頑健性
free1_main = [p[0] for p in R1 if p[4] is None]
s1_main = run_case(1, R1, T1, free1_main, "主: 地名で固定し地名のない電源だけ自由")
free1_rob = ["静岡菊川", "留辺蘂", "森町睦実2", "伊賀川西", "松阪上川", "美唄", "由利本荘乙助渕", "三重多気", "FUKO-B1", "長沼"]
s1_rob = run_case(1, R1, T1, free1_rob, "頑健性: 旧 CSV で誤り・不明だった蓄電池を含む10件を自由")
# 旧 CSV の割当（森町睦実２＝北海道、FUKO-B1 は九州に置く）で各エリアの合計を検算
old = {"森町睦実2": "北海道", "FUKO-B1": "九州"}
chk = check_sums(R1, old, T1)
print("  第1回 旧 CSV の割当（森町睦実２＝北海道）: " + "、".join(f"{a} {v[0]}（p.15 {v[1]}）" for a, v in chk.items() if not v[2]))
recon_rows.append(dict(回=1, 検査="旧 CSV の割当（森町睦実２＝北海道）", 自由にした電源="—", 解の数=0,
                       北海道の蓄電池kW_最小=hk_batt(R1, old), 北海道の蓄電池kW_最大=hk_batt(R1, old),
                       備考="p.15 と不一致: " + "、".join(f"{a} {v[0]}万kW（公表 {v[1]}）" for a, v in chk.items() if not v[2])))

# 第2回: 地名のない15件を自由（主）
free2 = [p[0] for p in R2 if p[4] is None]
s2 = run_case(2, R2, T2, free2, "主: 地名で固定し地名のない電源だけ自由")

# 第3回: 地名のない13件を自由（主）と、推定の3件も自由にした8通り
free3 = [p[0] for p in R3 if p[4] is None]
s3 = run_case(3, R3, T3, free3, "主: 地名で固定し地名のない電源だけ自由")
uncertain3 = ["HC25中国第一", "HC25東北第二", "イーレックス新潟"]
hk_relax = set()
for r in range(1, 4):
    for comb in itertools.combinations(uncertain3, r):
        ss = enumerate_assignments(R3, T3, set(free3) | set(comb))
        for s in ss:
            hk_relax.add(tuple(sorted(k for k, v in s.items() if v == "北海道" and k not in uncertain3)))
print(f"  第3回 [頑健性: 推定の3件も自由にした7通り] 北海道に入る地名のない電源の組: {sorted(hk_relax)}")
recon_rows.append(dict(回=3, 検査="頑健性: 推定の3件（HC25×2・イーレックス新潟）も自由にした7通り", 自由にした電源="、".join(uncertain3),
                       解の数=np.nan, 北海道の蓄電池kW_最小=140098, 北海道の蓄電池kW_最大=140098,
                       備考="北海道に入る地名のない電源の組: " + " / ".join("+".join(k) for k in sorted(hk_relax))))
# 第3回の別解（notes/28 §1.6）の検算: 北海道＝しろくま33＋ホクエナジー第一。県市名の蓄電池を2件以上動かす割当の一例として、
# 地名の蓄電池5件（益田市・新富町・CS青森八戸2・鹿児島薩摩川内・宮城石巻2）と推定3件も自由にし、北海道を
# 「しろくま33＋ホクエナジー第一」に固定して残りを列挙する。
placed5 = ["益田市", "新富町", "CS青森八戸2", "鹿児島薩摩川内", "宮城石巻2"]
R3_alt = [(k, n, t, kw, ("北海道" if k in ("しろくま33", "ホクエナジー第一") else a), b) for k, n, t, kw, a, b in R3]
free_alt = [k for k in free3 + uncertain3 + placed5 if k not in ("しろくま33", "ホクエナジー第一")]
tgt_alt = dict(T3)
s3_alt = enumerate_assignments(R3_alt, tgt_alt, set(free_alt))
moved = Counter()
for s in s3_alt:
    m = sum(1 for k in placed5 if s[k] != dict((p[0], p[4]) for p in R3)[k])
    moved[m] += 1
print(f"  第3回 別解（北海道＝しろくま33＋ホクエナジー第一）: 整合する割当 {len(s3_alt)}通り、"
      f"地名の蓄電池を動かす件数の分布 {dict(sorted(moved.items()))}（0件で成り立つ割当はない）")
recon_rows.append(dict(回=3, 検査="別解の検算: 北海道＝しろくま33＋ホクエナジー第一（水素）", 自由にした電源="地名のない11件＋推定3件＋県市名の蓄電池5件",
                       解の数=len(s3_alt), 北海道の蓄電池kW_最小=33737, 北海道の蓄電池kW_最大=33737,
                       備考=f"県市名の蓄電池を地名と異なるエリアへ動かす件数の分布 {dict(sorted(moved.items()))}"))
pd.DataFrame(recon_rows).to_csv(os.path.join(PROC, "ltda_area_reconciliation.csv"), index=False)
print("saved ltda_area_reconciliation.csv")

# ============================================================================================
# (B) ltda_battery_projects.csv の訂正（pref の誤り・会社名と案件名の分割・エリア推定の列を追加）
# ============================================================================================
csv_path = os.path.join(PROC, "ltda_battery_projects.csv")
L = pd.read_csv(csv_path)
base_cols = ["round", "no", "company", "project", "type", "kw", "pref"]
L = L[base_cols].copy()
# 会社名に案件名が混ざっている行（第2回 Risu、第3回 Kingdom）を分割
for i, r in L.iterrows():
    if isinstance(r["company"], str) and (pd.isna(r["project"]) or r["project"] == ""):
        for pre in ("Risu Energy Development Holdings株式会社 ", "Stonepeak Kingdom Holdings 合同会社 "):
            if r["company"].startswith(pre):
                L.at[i, "company"] = pre.strip()
                L.at[i, "project"] = r["company"][len(pre):]
PREF_FIX = {(1, 16): "静岡県", (1, 27): "三重県", (1, 28): "北海道", (1, 29): "秋田県", (1, 40): "北海道",
            (2, 12): "福島県", (2, 14): "岡山県", (2, 24): "宮城県"}
fixed_log = []
for (rd, no), pref in PREF_FIX.items():
    m = (L["round"] == rd) & (L["no"] == no)
    assert m.sum() == 1
    old_pref = L.loc[m, "pref"].iloc[0]
    if old_pref != pref:
        fixed_log.append((rd, no, L.loc[m, "project"].iloc[0], old_pref, pref))
    L.loc[m, "pref"] = pref

ROUNDS = {1: (R1, s1_main), 2: (R2, s2), 3: (R3, s3)}
NAME_BASIS = {"SRE北海道G", "SRE山形県B", "SRE秋田県F", "HC25中国第一", "HC25東北第二"}
est = {}
for rd, (proj, sols) in ROUNDS.items():
    for key, no, typ, kw, area, basis in proj:
        if typ != "B":
            continue
        if area is not None:
            conf = "名称（案件名のエリア・県名）" if key in NAME_BASIS else "確定（別紙の地名）"
            if key in ("HC25中国第一", "HC25東北第二"):
                conf = "名称（案件名のエリア名。p.15 照合と整合）"
            est[(rd, no)] = (area, basis, conf, area)
        else:
            c = Counter(s[key] for s in sols)
            cands = "／".join(f"{a}（{n}/{len(sols)}解）" for a, n in c.most_common())
            top = c.most_common(1)[0][0]
            conf = "高（p.15 照合の全解で一意）" if len(c) == 1 else "参考（p.15 照合で複数の候補）"
            if rd == 3 and key == "Battery23号":
                conf += "。別解（県市名の蓄電池を2件以上動かす割当）では しろくま33 が北海道"
            est[(rd, no)] = (top, "本文 p.15 のエリア別落札容量との照合（推定）", conf, cands)
L["area_est"] = [est[(r, n)][0] for r, n in zip(L["round"], L["no"])]
L["area_basis"] = [est[(r, n)][1] for r, n in zip(L["round"], L["no"])]
L["area_conf"] = [est[(r, n)][2] for r, n in zip(L["round"], L["no"])]
L["area_candidates"] = [est[(r, n)][3] for r, n in zip(L["round"], L["no"])]


def dur_class(rd, typ):
    if rd == 1:
        return "区分なし（第1回。別紙に継続時間の記載なし）"
    if rd == 2:
        return "6時間以上" if "6時間以上" in typ else "3時間以上6時間未満"
    return "6時間以上（第3回の要件）"


L["duration_class"] = [dur_class(r, t) for r, t in zip(L["round"], L["type"])]
assert L["kw"].sum() == sum(BATT_P14.values())
L.to_csv(csv_path, index=False)
print("\n=== (B) ltda_battery_projects.csv を訂正 ===")
for rd, no, pj, o, n in fixed_log:
    print(f"  第{rd}回 no.{no} {pj}: pref {o} → {n}")
if not fixed_log:
    print("  pref は既に訂正済み（再実行。訂正した8行と根拠は notes/33 §2。訂正前の版は git の HEAD）")
print("  第2回 Risu×4・第3回 Kingdom×3: 会社名に入っていた案件名を project 列へ移した")
print("  列を追加: area_est, area_basis, area_conf, area_candidates, duration_class")

# ============================================================================================
# (C) 北海道の LTDA 落札蓄電池と K_exo
# ============================================================================================
hk = L[L["area_est"] == "北海道"].copy()
r2_alt_hk = 37827 + 39832  # 第2回の別の割当（BatteryNo31＋Risu-502）
by_round = hk.groupby("round")["kw"].agg(["sum", "size"])
hk_main = int(by_round["sum"].sum())
r1, r2, r3 = (int(by_round.loc[i, "sum"]) for i in (1, 2, 3))
r2_named = int(hk[(hk["round"] == 2) & (hk["area_conf"].str.startswith(("確定", "名称")))]["kw"].sum())
r2_hi = r2_named + max(77545, r2_alt_hk)
r3_alt = 33737
six = int(hk[hk["duration_class"].str.startswith("6時間以上")]["kw"].sum())
K_CONN = 20.0  # 万kW（接続済み、2026年5月末。原稿 1.1.3・9.1）
KAPPA_4H, KAPPA_6H = 0.836, 0.932   # 北海道・2029年度向けの調整係数（原稿 9.2(a)(b) の値）
installed = sum(kw / (KAPPA_6H if d.startswith("6時間以上") else KAPPA_4H) for kw, d in zip(hk["kw"], hk["duration_class"]))
summ = [
    dict(項目="第1回（応札年度2023）", kW=r1, 件数=int(by_round.loc[1, "size"]), 根拠="別紙の地名（9件すべて）。p.15 と整合（唯一解）"),
    dict(項目="第2回（応札年度2024）", kW=r2, 件数=int(by_round.loc[2, "size"]),
         根拠=f"地名のある3件 {r2_named:,}kW＋地名のない案件（Risu-301 77,545kW、別の割当では BatteryNo31＋Risu-502 {r2_alt_hk:,}kW）。p.15 照合の12解"),
    dict(項目="第3回（応札年度2025）", kW=r3, 件数=int(by_round.loc[3, "size"]),
         根拠="Battery23号（p.15 照合の推定）。別解ではしろくま33（33,737kW）"),
    dict(項目="計（主）", kW=hk_main, 件数=int(by_round["size"].sum()), 根拠="第3回の別解では計 " + f"{r1 + r2 + r3_alt:,}kW"),
    dict(項目="計（第3回の別解）", kW=r1 + r2 + r3_alt, 件数=np.nan, 根拠="第3回＝しろくま33"),
    dict(項目="うち6時間級", kW=six, 件数=np.nan, 根拠="室蘭・SRE北海道G（第2回、6時間以上）、Battery23号（第3回）"),
    dict(項目="4時間換算（6時間級の kWh を4時間で割る）", kW=round(hk_main + six * 0.5), 件数=np.nan, 根拠="CFaR の K を4時間換算で置く場合"),
    dict(項目="設備容量への換算（上限側、落札容量＝期待容量と仮定）", kW=round(installed), 件数=np.nan,
         根拠=f"6時間級は ÷{KAPPA_6H}、その他は ÷{KAPPA_4H}（北海道・2029年度向けの調整係数で代用）"),
    dict(項目="旧原稿の値（少なくとも57.7万kW）", kW=577000, 件数=np.nan,
         根拠="第1・2回 436,438kW（森町睦実２の56,351kW を誤って含み、美唄・長沼と第2回の地名のない約7.76万kW を落とす）＋第3回140,098kW"),
]
for d in summ:
    d["万kW"] = round(d["kW"] / 1e4, 2)
K_rows = [
    dict(項目="K_exo（主）＝接続済み20万＋LTDA 北海道（主）", kW=K_CONN * 1e4 + hk_main),
    dict(項目="K_exo（第3回の別解）", kW=K_CONN * 1e4 + r1 + r2 + r3_alt),
    dict(項目="K_exo（4時間換算）", kW=K_CONN * 1e4 + hk_main + six * 0.5),
    dict(項目="K_exo（設備容量への換算、上限側）", kW=K_CONN * 1e4 + installed),
]
for d in K_rows:
    d["万kW"] = round(d["kW"] / 1e4, 1); d["件数"] = np.nan
    d["根拠"] = ("接続済み（2026年5月末）と LTDA は供給力の提供時期が重ならない（LTDA の供給力提供は実需給2027年度以降。第1回本文 p.17）。"
                 "ただし LTDA 案件の物理的な連系が先行して接続済み20万kW に含まれているかは一次資料で確認できない（含まれていれば K_exo はその分過大）")
S = pd.DataFrame(summ + K_rows)[["項目", "kW", "万kW", "件数", "根拠"]]
S.to_csv(os.path.join(PROC, "ltda_hokkaido_summary.csv"), index=False)
print("\n=== (C) 北海道の LTDA 落札蓄電池 ===")
print(S[["項目", "万kW"]].to_string(index=False))

# ============================================================================================
# (D) 乖離の勘定表
# ============================================================================================
# SII 交付決定一覧（北海道の行。都道府県順の表の転記。kW・kWh の記載はない）
SII = [
    ("R6", 1, "石油資源開発株式会社", 1862934438), ("R6", 2, "テラスエナジー株式会社", 820233710),
    ("R6", 3, "東京センチュリー株式会社・JFEエンジニアリング株式会社", 1558110000),
    ("R6", 4, "四電エンジニアリング株式会社ほか8社（東日本旅客鉄道・株式会社脱炭素化支援機構ほか）", 1046732850),
    ("R6", 5, "東京瓦斯株式会社・岡谷鋼機株式会社", 2257148025), ("R6", 6, "ミツウロコグリーンエネルギー株式会社", 162322823),
    ("R6", 7, "ミツウロコグリーンエネルギー株式会社", 162330738), ("R6", 8, "株式会社ユーラスエナジーホールディングス", 3346205000),
    ("R6", 9, "NTTアノードエナジー株式会社", 1947501895),
    ("R7", 1, "株式会社重建", 171300665), ("R7", 2, "株式会社東釧路蓄電所", 3824696500),
    ("R7", 3, "ミツウロコグリーンエネルギー株式会社", 908546500),
]
CAPEX = 68000.0  # 円/kWh（系統用蓄電システムの実勢、2024年度。補助事業の実績に基づく系列。3.7）


def sii_size(amount):
    """補助額から kWh・kW の幅を推定。補助率は 1,000〜10,000kW で1/3（上限10億円）、10,000kW 以上で1/2（上限40億円）。
    duration 2・3・4時間のうち、補助率の区分と規模が整合する組合せだけを残す。"""
    combos = []
    for rate, lo, hi, cap in ((1 / 3, 1000, 10000, 1e9), (0.5, 10000, np.inf, 4e9)):
        if amount > cap + 1:
            continue
        kwh = amount / rate / CAPEX
        for dur in (2, 3, 4):
            kw = kwh / dur
            if lo <= kw < hi:
                combos.append((rate, dur, kwh, kw))
    return combos


proj_rows = []
for _, r in hk.iterrows():
    proj_rows.append(dict(区分="LTDA（契約型）", 案件=f"第{r['round']}回 no.{r['no']} {r['project']}", 事業者=r["company"],
                          kW_下限=r["kw"], kW_上限=r["kw"], kWh="不明", duration=r["duration_class"],
                          運開予定=f"供給力提供は実需給2027年度以降（第{r['round']}回）", 段階="契約申込（と仮定）",
                          収入形態="LTDA（固定収入、他市場収益の約9割を還付）", エリアの確度=r["area_conf"],
                          出典=f"OCCTO LTDA 約定結果 別紙（応札年度{2022 + int(r['round'])}）・本文 p.15"))
sii_lo = sii_hi = sii_kwh_lo = sii_kwh_hi = 0.0
for yr, no, name, amt in SII:
    cb = sii_size(amt)
    kws = [c[3] for c in cb]; kwhs = [c[2] for c in cb]
    rates = sorted({"1/3" if c[0] < 0.4 else "1/2" for c in cb})
    durs = sorted({c[1] for c in cb})
    sii_lo += min(kws); sii_hi += max(kws); sii_kwh_lo += min(kwhs); sii_kwh_hi += max(kwhs)
    proj_rows.append(dict(区分="補助（SII 交付決定）", 案件=f"{'令和6' if yr == 'R6' else '令和7'}年度 No.{no}", 事業者=name,
                          kW_下限=round(min(kws)), kW_上限=round(max(kws)),
                          kWh=f"{min(kwhs):,.0f}〜{max(kwhs):,.0f}（推定）", duration=f"{'・'.join(map(str, durs))}時間（推定）",
                          運開予定="不明（交付決定 " + ("2024年12月" if yr == "R6" else "2025年12月") + "）", 段階="不明（接続済みか契約申込）",
                          収入形態=f"補助（補助率 {'または'.join(rates)}、補助額 {amt / 1e8:.2f}億円）＋市場収入",
                          エリアの確度="確定（交付決定一覧の実施場所＝北海道）",
                          出典="SII 交付決定について（" + ("2024-12-23" if yr == "R6" else "2025-12-25") + "）"))
sii_amt = sum(a for *_, a in SII)
proj_rows += [
    dict(区分="マーチャント", 案件="Helios（札幌市）", 事業者="HD Renewable Energy", kW_下限=50000, kW_上限=50000, kWh="104,000",
         duration="約2時間", 運開予定="2025年12月（運開済み）", 段階="接続済み", 収入形態="マーチャント（長期の買取契約なし。需給調整市場・容量市場に参加予定）",
         エリアの確度="確定", 出典="原稿 3.7・8.7（ESS News 2025; HD Renewable Energy 2025）。SII の交付決定一覧（2024・2025年度）に同社の名前はない"),
    dict(区分="不明（運開済みとされる）", 案件="DAX 札幌", 事業者="不明", kW_下限=50000, kW_上限=50000, kWh="100,000", duration="約2時間",
         運開予定="2025年11月", 段階="接続済み（二次資料）", 収入形態="不明", エリアの確度="確定", 出典="notes/14（二次資料由来、一次資料で未確認）"),
    dict(区分="不明", 案件="ENEOS 室蘭", 事業者="ENEOS", kW_下限=50000, kW_上限=50000, kWh="88,000", duration="約1.8時間",
         運開予定="不明", 段階="不明", 収入形態="不明", エリアの確度="確定", 出典="notes/14（二次資料由来、一次資料で未確認）"),
    dict(区分="併設（系統用の統計の対象外）", 案件="北豊富（風力送電網）", 事業者="北海道北部風力送電", kW_下限=240000, kW_上限=240000,
         kWh="720,000", duration="3時間", 運開予定="2023年3月（運開済み）", 段階="接続済み（ただし系統用20万kW には含めない）",
         収入形態="風力送電網の設備（併設）", エリアの確度="確定", 出典="原稿 3.7、notes/14、HANDOFF（2026-10-05 の方針: 接続済み20万kW は系統用、北豊富は併設）"),
]
P = pd.DataFrame(proj_rows)
P.to_csv(os.path.join(PROC, "gap_ledger_projects.csv"), index=False)

# APV（表9.7、39 の出力 apv_decomposition.csv）。収入の基準は実績整合が主、旧基準（旧0.81PF・旧裾補正）とモデル直値は参考。
# r_A^M は 9% が主（9.5.3。39 の図と同じ）、8% が参考。LTDA は r_C=5%。
A = pd.read_csv(os.path.join(PROC, "apv_decomposition.csv"))
RM_MAIN, RM_REF = 0.09, 0.08
RMS = (RM_MAIN, RM_REF)


def apv(panel, case_prefix, comp, rM=RM_MAIN, rC=None, suffix="", basis=None):
    m = (A["パネル"] == panel) & A["ケース"].str.startswith(case_prefix) & A["ケース"].str.endswith(suffix) & (A["成分"] == comp) & np.isclose(A["r_A^M"], rM)
    if rC is not None:
        m &= np.isclose(A["r_C"], rC)
    if basis is not None:
        m &= A["収入の基準"] == basis
    v = A.loc[m, "現在価値(円/kW)"]
    assert len(v) == 1, (panel, basis, case_prefix, comp, rM, len(v))
    return float(v.iloc[0])


c29 = "・容量1.25万（2029年度向け）"
# 4h マーチャントのケース（39 の「収入の基準」, ケース名の先頭）。旧ラベルとの対応: 旧「θ=1（モデル…」＝旧0.81PF、
# 旧「θ=1 ×1.25」＝旧裾補正、旧「FY2026上期水準 ×1.25」＝FY2026旧裾補正。
CASE_M = {"実績整合": ("実績整合", "θ=1（FY2023〜25）・実績整合"),
          "FY2026水準": ("実績整合", "FY2026上期水準 θ=1.567・実績整合"),
          "モデル直値": ("モデル直値", "θ=1（FY2023〜25）・モデル直値"),
          "旧0.81PF": ("旧0.81PF", "θ=1（FY2023〜25）・旧0.81PF"),
          "旧裾補正": ("旧裾補正", "θ=1（FY2023〜25）・旧裾補正"),
          "FY2026旧裾補正": ("旧裾補正", "FY2026上期水準 θ=1.567・旧裾補正")}
apv_m = {r: {k: apv("4h マーチャント", pre, "APV: 基礎＋容量", r, suffix=c29, basis=b) for k, (b, pre) in CASE_M.items()} for r in RMS}
apv_s = {r: {k: apv("4h マーチャント", pre, "APV: 基礎＋容量＋補助1/2", r, suffix=c29, basis=b) for k, (b, pre) in CASE_M.items()}
         for r in RMS}
# LTDA 6h は収入の基準で1行に絞る（実績整合が主、旧裾補正が参考）
CASE_L = {"積み上げ5%": "積み上げ（事業報酬率5%）・契約容量＝期待容量κ=0.932",
          "上限7.2万・期待容量": "上限7.2万（応札年度2026・北海道71,768）・契約容量＝期待容量κ=0.932",
          "上限7.7万・設備容量": "上限7.7万（第3回・北海道77,033）・契約容量＝設備容量"}
apv_ltda = {(b, r): {lab: apv("6h LTDA", pre, "LTDA 電源の APV", r, rC=0.05, basis=b) for lab, pre in CASE_L.items()}
            for b in ("実績整合", "旧裾補正") for r in RMS}
print("\n=== 39 の APV（apv_decomposition.csv、円/kW）===")
for r in RMS:
    print(f"  r_A^M {r:.0%}: 4h 容量1.25万 " + "、".join(f"{k} {v:,.0f}" for k, v in apv_m[r].items()))
    print(f"           4h 容量1.25万＋1/2補助 " + "、".join(f"{k} {v:,.0f}" for k, v in apv_s[r].items()))
    for b in ("実績整合", "旧裾補正"):
        print(f"           LTDA 6h（{b}、r_C 5%） " + "、".join(f"{k} {v:,.0f}" for k, v in apv_ltda[(b, r)].items()))


def annuity(r, n=20):
    return (1 - (1 + r) ** -n) / r if abs(r) > 1e-12 else float(n)


# ---- D1 の収益基準での APV（39 の表9.7 と同じ式を直接計算。4h は 39 の値と一致することを確かめ、IRR・3%/6% と2h に使う）
#   APV ＝ −d×資本費×(1−補助率) ＋ (π − 固定費 ＋ κP)×年金現価(r, 20年)
#   π: 充電従量負担を控除した K=0 のスポット収益。固定費: 運維0.5万＋廃止300（4h）・150（2h）＋託送等固定0.69万。
#   κP: 容量収入（2029年度向け北海道 14,972×調整係数0.836＝12,517円/kW-年、4h のみ。2h は0）。
#   4h の π は T1 の pi_k_curve_v3.csv（仕様A 26・現状・完全予見の増分貪欲・刻み1万kW、K=0）: 実績整合（主）・モデル直値・旧0.81×π_PF、
#   と θ=1.567（FY2026 4〜6月の水準）の実績整合。2h の π は実績価格の上の戦略c を2時間で直接計算した値（実績整合）。
V0 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
V0 = V0[(V0["価格モデル"] == "仕様A（26、水準係数付き）") & (V0["シナリオ"] == "現状") & (V0["フリート配分"] == "完全予見の増分貪欲（主）")
        & (V0["刻み(万kW)"].astype(str) == "1.0") & (V0["K(万kW)"] == 0)].set_index("θ")
FIX4, FIX2 = 5000 + 300 + 6900, 5000 + 150 + 6900
KP = 0.836 * 14972
PI4 = {"実績整合 θ=1（主）": float(V0.loc[1.0, "π_実績整合"]), "実績整合 θ=1.567（FY2026 4〜6月の水準）": float(V0.loc[1.567, "π_実績整合"]),
       "モデル直値 θ=1": float(V0.loc[1.0, "π_モデル直値"]), "旧0.81×π_PF θ=1（旧基準、旧表9.7）": float(V0.loc[1.0, "π_旧0.81PF"])}


def apv4(pi, sub=0.0, r=RM_MAIN, kp=KP):
    return -4 * CAPEX * (1 - sub) + (pi - FIX4 + kp) * annuity(r)


def apv2(pi, r=RM_MAIN):
    return -2 * CAPEX + (pi - FIX2) * annuity(r)


# 39 の apv_decomposition.csv（4h・容量1.25万）の再現: 実績整合 θ=1・θ=1.567、モデル直値、旧0.81PF を r_A^M 9%・8% で
for k49, k39 in (("実績整合 θ=1（主）", "実績整合"), ("実績整合 θ=1.567（FY2026 4〜6月の水準）", "FY2026水準"),
                 ("モデル直値 θ=1", "モデル直値"), ("旧0.81×π_PF θ=1（旧基準、旧表9.7）", "旧0.81PF")):
    for r in RMS:
        assert abs(apv4(PI4[k49], r=r) - apv_m[r][k39]) < 50, (k49, r, apv4(PI4[k49], r=r), apv_m[r][k39])
        assert abs(apv4(PI4[k49], sub=0.5, r=r) - apv_s[r][k39]) < 50, (k49, r)
print("  本スクリプトの直接計算（4h）は 39 の値と一致（±50円/kW）")


def strategy_c_actual(hours):
    """実績価格の上の戦略c（直近29日・同じ曜日区分の時刻別平均価格のランク、5日以上、同値は均等配分。41 と同じ定義）の
    FY2023〜25 平均（円/kW-年、充電従量負担の控除前）"""
    hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
    hp = hp[(hp["ts"] >= "2022-02-01") & (hp["ts"] < "2026-04-01")].copy()
    hp["day"] = hp["ts"].dt.normalize(); hp["h"] = hp["ts"].dt.hour
    M = hp.pivot(index="day", columns="h", values="p_hokkaido")
    M = M[M.count(axis=1) == 24]
    dd = M.index; PA = M.to_numpy(float); wk = np.asarray(dd.dayofweek >= 5)
    n = len(dd); Wm = np.zeros((n, n)); has = np.zeros(n, bool)
    for i in range(n):
        hh = [j for j in range(max(0, i - 29), i) if wk[j] == wk[i]]
        if len(hh) >= 5:
            Wm[i, hh] = 1.0 / len(hh); has[i] = True
    Cm = Wm @ PA

    def tw(sig, k):
        srt = np.sort(sig, 1); thr_ = srt[:, k - 1:k]; w = (sig < thr_).astype(float); tied = sig == thr_
        return w + tied * ((k - w.sum(1, keepdims=True)) / tied.sum(1, keepdims=True))
    cday = 0.85 * (tw(-Cm, hours) * PA).sum(1) - (tw(Cm, hours) * PA).sum(1)
    fyv = np.asarray(dd.year - (dd.month < 4).astype(int))
    m = (fyv >= 2023) & (fyv <= 2025) & has
    return float(pd.Series(cday[m]).groupby(fyv[m]).sum().mean())


C4_ACT, C2_ACT = strategy_c_actual(4), strategy_c_actual(2)
assert abs(C4_ACT - 1752 - PI4["実績整合 θ=1（主）"]) < 1.0
TH157 = (PI4["実績整合 θ=1.567（FY2026 4〜6月の水準）"] + 1752) / C4_ACT   # 4h の粗収益の比（θ=1.567 ÷ θ=1）を2h にも当てる（近似）
PI2 = {"実績整合 θ=1（主）": C2_ACT - 876, "実績整合 θ=1.567（FY2026 4〜6月の水準、4h の比で換算）": C2_ACT * TH157 - 876,
       "旧0.81×π_PF θ=1": 0.81 * 4721 - 876, "旧0.81×π_PF θ=1.22（恒久成分）": 0.81 * 1.22 * 4721 - 876}
print(f"\n実績価格の上の戦略c（FY2023〜25 平均、充電従量負担の控除前）: 4h {C4_ACT:,.1f}・2h {C2_ACT:,.1f} 円/kW-年")


def irr_of(inv, annual):
    """−inv ＋ annual×年金現価(r) ＝ 0 の r（20年）。年額の合計が投資額に届かなければ NaN（IRR は負）。"""
    if annual * 20 <= inv:
        return np.nan
    lo, hi = 1e-9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if annual * annuity(mid) > inv:
            lo = mid
        else:
            hi = mid
    return lo


basis_rows = []
SUBS = (("補助なし（マーチャント）", 0.0), ("補助1/3", 1 / 3), ("補助1/2（上限40億・5万kW 規模で実効29%）", 80000 / 272000), ("補助1/2（上限なし）", 0.5))
for lab, pi in PI4.items():
    for slab, sub in SUBS:
        ann = pi - FIX4 + KP
        basis_rows.append(dict(仕様="4h・容量1.25万（2029年度向け）", 補助=slab, 収益基準=lab, π_spot=round(pi), 年額_π_固定費控除_κP込み=round(ann),
                               投資額_補助後=round(4 * CAPEX * (1 - sub)), APV_9pct=round(apv4(pi, sub, 0.09)), APV_8pct=round(apv4(pi, sub, 0.08)),
                               APV_6pct=round(apv4(pi, sub, 0.06)), APV_3pct=round(apv4(pi, sub, 0.03)),
                               必要な割引率_IRR=irr_of(4 * CAPEX * (1 - sub), ann)))
for lab, pi in PI2.items():
    ann = pi - FIX2
    basis_rows.append(dict(仕様="2h・容量0（Helios 型）", 補助="補助なし（マーチャント）", 収益基準=lab, π_spot=round(pi), 年額_π_固定費控除_κP込み=round(ann),
                           投資額_補助後=round(2 * CAPEX), APV_9pct=round(apv2(pi, 0.09)), APV_8pct=round(apv2(pi, 0.08)),
                           APV_6pct=round(apv2(pi, 0.06)), APV_3pct=round(apv2(pi, 0.03)), 必要な割引率_IRR=irr_of(2 * CAPEX, ann)))
basis_rows.append(dict(仕様="2h・容量0（Helios 型）", 補助="補助なし（マーチャント）", 収益基準="事業者の見込み（年最大20億円＝約4万円/kW）が粗利の場合",
                       π_spot=40000, 年額_π_固定費控除_κP込み=40000 - FIX2, 投資額_補助後=round(2 * CAPEX), APV_9pct=round(apv2(40000, 0.09)),
                       APV_8pct=round(apv2(40000, 0.08)), APV_6pct=round(apv2(40000, 0.06)), APV_3pct=round(apv2(40000, 0.03)),
                       必要な割引率_IRR=irr_of(2 * CAPEX, 40000 - FIX2)))
BASIS = pd.DataFrame(basis_rows)
BASIS["必要な割引率_IRR"] = BASIS["必要な割引率_IRR"].apply(lambda x: "負（年額の20年合計が投資額に届かない）" if pd.isna(x) else f"{x * 100:.1f}%")
BASIS.to_csv(os.path.join(PROC, "gap_ledger_apv_basis.csv"), index=False)
print("\n=== D1 の収益基準での APV（円/kW。r_A^M 9% が主、8% が参考）と、APV=0 になる割引率（事業 IRR、20年）===")
print(BASIS[["仕様", "補助", "収益基準", "π_spot", "APV_9pct", "APV_8pct", "APV_6pct", "必要な割引率_IRR"]].to_string(index=False))


def bas(spec, sub, lab, col="APV_9pct"):
    r = BASIS[(BASIS["仕様"].str.startswith(spec)) & (BASIS["補助"] == sub) & (BASIS["収益基準"] == lab)]
    assert len(r) == 1, (spec, sub, lab)
    return r.iloc[0][col]


# 4h のマーチャント・補助の APV は上の apv_m・apv_s（39 の値）を使う。ここでは IRR と2h（Helios 型）を取る。
L1, L157, LM, LO = list(PI4)
irr_s = {k: bas("4h", "補助1/2（上限なし）", v, "必要な割引率_IRR") for k, v in (("実績整合", L1), ("FY2026水準", L157))}
irr_s3 = bas("4h", "補助1/3", L157, "必要な割引率_IRR")
H1, H157, HO, HO122 = list(PI2)
RCOL = {0.09: "APV_9pct", 0.08: "APV_8pct"}
apv_h = {r: {"実績整合": bas("2h", "補助なし（マーチャント）", H1, RCOL[r]), "FY2026水準": bas("2h", "補助なし（マーチャント）", H157, RCOL[r]),
             "旧": bas("2h", "補助なし（マーチャント）", HO, RCOL[r])} for r in RMS}
irr_h = [bas("2h", "補助なし（マーチャント）", h, "必要な割引率_IRR") for h in (H1, H157)]
assert all(x.startswith("負") for x in irr_h), irr_h   # Helios 型は θ=1・θ=1.567 とも IRR が負
apv_h_pub = {r: apv2(40000, r) for r in RMS}

TOTAL_CONN, TOTAL_APP = 20.0e4, 234.0e4
ltda_lo, ltda_hi = r1 + r2 + r3_alt, hk_main
helios = 50000
unk_lo = TOTAL_CONN + TOTAL_APP - ltda_hi - sii_hi - helios
unk_hi = TOTAL_CONN + TOTAL_APP - ltda_lo - sii_lo - helios
fmt = lambda x: f"{x / 1e4:+.1f}万"
M9, M8 = RM_MAIN, RM_REF
LM9, LM8 = apv_ltda[("実績整合", M9)], apv_ltda[("実績整合", M8)]     # LTDA（実績整合、主）
LO9, LO8 = apv_ltda[("旧裾補正", M9)], apv_ltda[("旧裾補正", M8)]     # LTDA（旧裾補正、参考）
# 数値列: 主＝実績整合・r_A^M 9%、参考＝実績整合・8%、旧基準・9%／8%（4h・2h は旧0.81PF、LTDA は旧裾補正）
C_MAIN, C_REF8 = "APV主_円per_kW（実績整合・r_A^M 9%）", "APV参考_円per_kW（実績整合・r_A^M 8%）"
C_OLD9, C_OLD8 = "APV参考_円per_kW（旧基準・r_A^M 9%）", "APV参考_円per_kW（旧基準・r_A^M 8%）"


def num(rep, main9, ref8, old9=np.nan, old8=np.nan, old_lab="—"):
    return {"APV の代表ケース": rep, C_MAIN: round(main9) if pd.notna(main9) else np.nan,
            C_REF8: round(ref8) if pd.notna(ref8) else np.nan, C_OLD9: round(old9) if pd.notna(old9) else np.nan,
            C_OLD8: round(old8) if pd.notna(old8) else np.nan, "旧基準の内容": old_lab}


ledger = [
    dict(属性="LTDA（北海道の落札蓄電池）", 段階="契約申込（供給力提供は FY2027 以降、と仮定）", kW_下限=ltda_lo, kW_上限=ltda_hi,
         APV_円per_kW=(f"{fmt(LM9['積み上げ5%'])}〜{fmt(LM9['上限7.7万・設備容量'])}（6h、実績整合、r_A^M 9%・r_C 5%。上限7.2万・期待容量で "
                       f"{fmt(LM9['上限7.2万・期待容量'])}）。r_A^M 8% では {fmt(LM8['積み上げ5%'])}〜{fmt(LM8['上限7.7万・設備容量'])}"
                       f"（上限7.2万・期待容量で {fmt(LM8['上限7.2万・期待容量'])}）。旧裾補正（参考）は上限7.2万・期待容量で "
                       f"{fmt(LO9['上限7.2万・期待容量'])}（9%）・{fmt(LO8['上限7.2万・期待容量'])}（8%）。39 の apv_decomposition.csv。"
                       "他市場収益の約9割を還付するので収入の基準の影響は小さい"),
         **num("6h・上限7.2万・期待容量κ=0.932・r_C 5%", LM9["上限7.2万・期待容量"], LM8["上限7.2万・期待容量"],
               LO9["上限7.2万・期待容量"], LO8["上限7.2万・期待容量"], "旧裾補正（6h、39）"),
         分類="市場外収入で APV が正", 説明しうる92e="—（(b) で説明）",
         出典="OCCTO 別紙・本文 p.15（本スクリプト (A)）。APV は 39 の apv_decomposition.csv（収入の基準＝実績整合）"),
    dict(属性="補助（SII 交付決定、北海道12件）", 段階="不明（接続済みか契約申込）", kW_下限=round(sii_lo), kW_上限=round(sii_hi),
         APV_円per_kW=(f"{fmt(apv_s[M9]['実績整合'])}（実績整合 θ=1）／{fmt(apv_s[M9]['FY2026水準'])}（実績整合 θ=1.567）／"
                       f"{fmt(apv_s[M9]['モデル直値'])}（モデル直値）。4h・1/2補助（上限なし）・容量1.25万、r_A^M 9%。"
                       f"r_A^M 8% では {fmt(apv_s[M8]['実績整合'])}／{fmt(apv_s[M8]['FY2026水準'])}／{fmt(apv_s[M8]['モデル直値'])}。"
                       f"旧基準（参考、9%・8%）は旧0.81PF {fmt(apv_s[M9]['旧0.81PF'])}・{fmt(apv_s[M8]['旧0.81PF'])}、"
                       f"旧裾補正 θ=1 {fmt(apv_s[M9]['旧裾補正'])}・{fmt(apv_s[M8]['旧裾補正'])}、"
                       f"旧裾補正 θ=1.567 {fmt(apv_s[M9]['FY2026旧裾補正'])}・{fmt(apv_s[M8]['FY2026旧裾補正'])}"),
         **num("4h・1/2補助（上限なし）・容量1.25万・θ=1", apv_s[M9]["実績整合"], apv_s[M8]["実績整合"],
               apv_s[M9]["旧0.81PF"], apv_s[M8]["旧0.81PF"], "旧0.81PF（4h、39）"),
         分類=(f"APV が負のまま参入（r_A^M=9%。8% でも負）。APV=0 の割引率は1/2補助で {irr_s['実績整合']}（θ=1）・{irr_s['FY2026水準']}（θ=1.567）、"
               f"1/3補助・θ=1.567 で {irr_s3}"),
         説明しうる92e="第三（価格水準の見通し）と、契約型並みの割引率",
         出典=f"SII 交付決定一覧（補助額計 {sii_amt / 1e8:.1f}億円）。kWh は補助額÷(補助率×6.8万円/kWh)、kW は2〜4時間の幅（推定）。APV は 39"),
    dict(属性="マーチャント（確認できた案件: Helios）", 段階="接続済み", kW_下限=helios, kW_上限=helios,
         APV_円per_kW=(f"{fmt(apv_h[M9]['実績整合'])}（2h・容量0・補助なし、実績の戦略c）／{fmt(apv_h[M9]['FY2026水準'])}（θ=1.567）、r_A^M 9%。"
                       f"r_A^M 8% では {fmt(apv_h[M8]['実績整合'])}／{fmt(apv_h[M8]['FY2026水準'])}。旧基準（0.81×π_PF、参考）"
                       f"{fmt(apv_h[M9]['旧'])}（9%）・{fmt(apv_h[M8]['旧'])}（8%）。"
                       f"事業者の見込み（約4万円/kW-年）が粗利なら {fmt(apv_h_pub[M9])}（9%）・{fmt(apv_h_pub[M8])}（8%）"),
         **num("2h・容量0・補助なし・θ=1（本スクリプトで直接計算）", apv_h[M9]["実績整合"], apv_h[M8]["実績整合"],
               apv_h[M9]["旧"], apv_h[M8]["旧"], "旧0.81×π_PF（2h、本スクリプト）"),
         分類="計測した成分（スポット＋容量）では APV が負（どの割引率でも IRR は負）", 説明しうる92e="第二（需給調整市場の移行期レントと短い duration）",
         出典="原稿 3.7・8.7。APV は gap_ledger_apv_basis.csv（39 と同じ式）"),
    dict(属性="併設", 段階="系統用の接続済み・契約申込には含まれない（定義）", kW_下限=0, kW_上限=0,
         APV_円per_kW="50_colocation_v3.py（併設の参入条件。現行の資本費6.8万円/kWh ではローカル価値を加えても負）",
         **num("—", np.nan, np.nan),
         分類="対象外（北豊富24万kW は系統用20万kW の外）", 説明しうる92e="—（併設のローカル価値は系統用の申込を説明できない）",
         出典="原稿 3.7、HANDOFF の定義"),
    dict(属性="不明（残差）", 段階="接続済み約15万kW（Helios 以外）＋契約申込の残り", kW_下限=round(unk_lo), kW_上限=round(unk_hi),
         APV_円per_kW=(f"マーチャント4h（補助なし・容量1.25万）として {fmt(apv_m[M9]['実績整合'])}（実績整合 θ=1）／"
                       f"{fmt(apv_m[M9]['FY2026水準'])}（実績整合 θ=1.567）／{fmt(apv_m[M9]['モデル直値'])}（モデル直値）、r_A^M 9%。"
                       f"r_A^M 8% では {fmt(apv_m[M8]['実績整合'])}／{fmt(apv_m[M8]['FY2026水準'])}／{fmt(apv_m[M8]['モデル直値'])}。"
                       f"旧基準（参考、9%・8%）は旧0.81PF {fmt(apv_m[M9]['旧0.81PF'])}・{fmt(apv_m[M8]['旧0.81PF'])}、"
                       f"旧裾補正 θ=1 {fmt(apv_m[M9]['旧裾補正'])}・{fmt(apv_m[M8]['旧裾補正'])}"),
         **num("4h・補助なし・容量1.25万・θ=1", apv_m[M9]["実績整合"], apv_m[M8]["実績整合"],
               apv_m[M9]["旧0.81PF"], apv_m[M8]["旧0.81PF"], "旧0.81PF（4h、39）"),
         分類="属性不明", 説明しうる92e="第一（接続枠の待機オプション: 契約申込の段階の kW）、第二（接続済みの kW）、第三",
         出典="合計254万kW（原稿 1.1.3・9.1。一次資料は未照合）から上の属性を引いた残り。APV は 39"),
]
G = pd.DataFrame(ledger)
G["万kW_下限"] = (G["kW_下限"] / 1e4).round(1); G["万kW_上限"] = (G["kW_上限"] / 1e4).round(1)
G["シェア_下限%"] = (G["kW_下限"] / (TOTAL_CONN + TOTAL_APP) * 100).round(1)
G["シェア_上限%"] = (G["kW_上限"] / (TOTAL_CONN + TOTAL_APP) * 100).round(1)
# 残差を円で: 不明の kW が建設されるとした場合に、計測外の成分（需給調整市場・見通し・オプション価値など）が埋める必要のある現在価値
res_rows = []
for lab in ("実績整合", "FY2026水準", "モデル直値"):
    need, need8 = -apv_m[M9][lab], -apv_m[M8][lab]
    a9, a8 = annuity(M9), annuity(M8)
    res_rows.append(dict(属性=f"残差（円）: 不明の kW × マーチャント4h の不足（{lab}、r_A^M 9%）", 段階="—",
                         kW_下限=round(unk_lo), kW_上限=round(unk_hi),
                         APV_円per_kW=(f"{need:,.0f}円/kW（年額 {need / a9:,.0f}円/kW-年）。r_A^M 8% では {need8:,.0f}円/kW"
                                       f"（年額 {need8 / a8:,.0f}円/kW-年）"),
                         **num(f"4h・補助なし・容量1.25万（{lab}）", apv_m[M9][lab], apv_m[M8][lab]),
                         分類=(f"現在価値 {need * unk_lo / 1e8:,.0f}〜{need * unk_hi / 1e8:,.0f}億円、年額 {need / a9 * unk_lo / 1e8:,.0f}〜"
                               f"{need / a9 * unk_hi / 1e8:,.0f}億円/年（r_A^M 8% では現在価値 {need8 * unk_lo / 1e8:,.0f}〜{need8 * unk_hi / 1e8:,.0f}億円、"
                               f"年額 {need8 / a8 * unk_lo / 1e8:,.0f}〜{need8 / a8 * unk_hi / 1e8:,.0f}億円/年）"),
                         説明しうる92e=("kW は全量が建設される場合の上限（契約申込の大半は建設されない: 9.2(e) 第一）。一方、1kW あたりの不足は K=0（参入に最も有利）の値で、"
                                      "全量が建設されれば π(K) と容量価格の低下で大きくなる（実績整合の π は K=100万kW で −1,202円/kW-年）。総額は規模の目安で、上限でも下限でもない"),
                         出典="39 の apv_decomposition.csv（収入の基準＝" + ("モデル直値" if lab == "モデル直値" else "実績整合") + "）"))
# 参考（検証で追加）: LTDA の落札容量は契約容量（期待容量以下）で、接続の統計（設備の kW）より小さい。設備容量に換算した上限側の勘定。
inst = lambda d: d["kw"] / (KAPPA_6H if d["duration_class"].startswith("6時間以上") else KAPPA_4H)
ltda_inst_hi = float(hk.apply(inst, axis=1).sum())
ltda_inst_lo = float(hk[~((hk["round"] == 3))].apply(inst, axis=1).sum() + r3_alt / KAPPA_6H)
res_rows2 = [dict(属性="参考: LTDA を設備容量に換算（上限側、落札容量＝期待容量と仮定）", 段階="同上", kW_下限=round(ltda_inst_lo), kW_上限=round(ltda_inst_hi),
                  APV_円per_kW="—", 分類=(f"このとき不明は {(TOTAL_CONN + TOTAL_APP - ltda_inst_hi - sii_hi - helios) / 1e4:.1f}〜"
                                         f"{(TOTAL_CONN + TOTAL_APP - ltda_inst_lo - sii_lo - helios) / 1e4:.1f}万kW"),
                  説明しうる92e="—", 出典=f"6時間級は ÷{KAPPA_6H}、その他は ÷{KAPPA_4H}（北海道・2029年度向けの調整係数で代用）",
                  万kW_下限=round(ltda_inst_lo / 1e4, 1), 万kW_上限=round(ltda_inst_hi / 1e4, 1),
                  **{"シェア_下限%": round(ltda_inst_lo / (TOTAL_CONN + TOTAL_APP) * 100, 1),
                     "シェア_上限%": round(ltda_inst_hi / (TOTAL_CONN + TOTAL_APP) * 100, 1)})]
# 集計: 3分類（市場外収入で APV が正／負のまま参入／不明）と、段階別（接続済み・契約申込）の内訳。
# 下限と上限は対で読む（LTDA・SII が上限のとき不明が下限）。SII の段階は不明なので、段階別では「不明（SII を含みうる）」に入る。
app_rest_lo, app_rest_hi = TOTAL_APP - ltda_hi, TOTAL_APP - ltda_lo
agg = [
    dict(属性="集計（分類別）: 市場外収入で APV が正（LTDA）", 段階="契約申込（と仮定）", kW_下限=ltda_lo, kW_上限=ltda_hi,
         分類="市場外収入で APV が正", APV_円per_kW=f"{fmt(LM9['上限7.2万・期待容量'])}（上限7.2万・期待容量、r_A^M 9%）"),
    dict(属性="集計（分類別）: APV が負のまま参入（SII＋Helios）", 段階="接続済み（Helios）＋不明（SII）", kW_下限=round(sii_lo + helios),
         kW_上限=round(sii_hi + helios), 分類="APV が負のまま参入（r_A^M 9%・8% とも）",
         APV_円per_kW=f"SII {fmt(apv_s[M9]['実績整合'])}・Helios {fmt(apv_h[M9]['実績整合'])}（実績整合 θ=1、r_A^M 9%）"),
    dict(属性="集計（分類別）: 属性不明", 段階="接続済み＋契約申込の残り", kW_下限=round(unk_lo), kW_上限=round(unk_hi), 分類="属性不明",
         APV_円per_kW=f"マーチャント4h として {fmt(apv_m[M9]['実績整合'])}（実績整合 θ=1、r_A^M 9%）"),
    dict(属性="集計（段階別）: 接続済み（2026年5月末）", 段階="接続済み", kW_下限=TOTAL_CONN, kW_上限=TOTAL_CONN,
         分類=f"Helios {helios / 1e4:.1f}万kW（APV 負）＋不明 {(TOTAL_CONN - helios) / 1e4:.1f}万kW（SII の一部を含みうる）", APV_円per_kW="—"),
    dict(属性="集計（段階別）: 契約申込（2026年5月末）", 段階="契約申込", kW_下限=TOTAL_APP, kW_上限=TOTAL_APP,
         分類=(f"LTDA {ltda_lo / 1e4:.1f}〜{ltda_hi / 1e4:.1f}万kW（APV 正）＋不明 {app_rest_lo / 1e4:.1f}〜{app_rest_hi / 1e4:.1f}万kW"
               "（SII の一部を含みうる）"), APV_円per_kW="—"),
]
for d in agg:
    d.update(説明しうる92e="—", 出典="上の各行の集計", **{"APV の代表ケース": "—", "旧基準の内容": "—"},
             万kW_下限=round(d["kW_下限"] / 1e4, 1), 万kW_上限=round(d["kW_上限"] / 1e4, 1),
             **{"シェア_下限%": round(d["kW_下限"] / (TOTAL_CONN + TOTAL_APP) * 100, 1),
                "シェア_上限%": round(d["kW_上限"] / (TOTAL_CONN + TOTAL_APP) * 100, 1)})
# 下限・上限の対の整合: LTDA 上限＋SII 上限＋Helios＋不明 下限＝254万kW（逆も同じ）
assert abs(ltda_hi + sii_hi + helios + unk_lo - (TOTAL_CONN + TOTAL_APP)) < 1 and abs(ltda_lo + sii_lo + helios + unk_hi - (TOTAL_CONN + TOTAL_APP)) < 1
G = pd.concat([G, pd.DataFrame(res_rows), pd.DataFrame(res_rows2), pd.DataFrame(agg)], ignore_index=True)
G["万kW_下限"] = (G["kW_下限"] / 1e4).round(1); G["万kW_上限"] = (G["kW_上限"] / 1e4).round(1)   # 残差の行にも入れる
G["シェア_下限%"] = (G["kW_下限"] / (TOTAL_CONN + TOTAL_APP) * 100).round(1)
G["シェア_上限%"] = (G["kW_上限"] / (TOTAL_CONN + TOTAL_APP) * 100).round(1)
G.to_csv(os.path.join(PROC, "gap_ledger_summary.csv"), index=False)
print("\n=== (D) 乖離の勘定表（接続済み20万＋契約申込234万＝254万kW）===")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140)
print(G[["属性", "万kW_下限", "万kW_上限", "シェア_下限%", "シェア_上限%", "分類"]].to_string(index=False))
for _, r in G.iterrows():
    print(f"  [{r['属性']}] APV: {r['APV_円per_kW']}")
print(f"  SII 北海道12件: 補助額 {sii_amt / 1e8:.1f}億円（令和6年度 {sum(a for y, *_, a in SII if y == 'R6') / 1e8:.1f}・令和7年度 {sum(a for y, *_, a in SII if y == 'R7') / 1e8:.1f}）、"
      f"推定 kWh {sii_kwh_lo / 1e4:.1f}〜{sii_kwh_hi / 1e4:.1f}万kWh、kW {sii_lo / 1e4:.1f}〜{sii_hi / 1e4:.1f}万kW")
print(f"  SII の交付先と LTDA 北海道の落札事業者の名称の重なり: "
      f"{sorted(set(n for *_, n, _ in SII) & set(hk['company'])) or 'なし（SPC の親会社は未照合）'}")

# 図: 段階別（接続済み・契約申込）の属性の内訳（範囲は中央値）と属性別の APV（実績整合 θ=1 〜 θ=1.567、r_A^M 9%。LTDA は積み上げ〜上限7.7万・設備容量）
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、2つのパネルを縦に並べ、文字は8.5pt 以上にする。
# APV の割引率（r_A^M=9%）と実績整合ケースは図の注に書く
fig = plt.figure(figsize=(6.1, 5.6), layout="constrained")
sf_a, sf_b = fig.subfigures(2, 1, height_ratios=[1.0, 1.0], hspace=0.03)
ax = [sf_a.subplots(), sf_b.subplots()]
mid = lambda a, b: (a + b) / 2 / 1e4
COL = {"LTDA": "#2a6f97", "SII": "#8ab17d", "Helios": "#e9c46a", "不明": "#c9c9c9"}
rows_fig = [("接続済み 20万kW", [("Helios", helios / 1e4), ("不明", 20 - helios / 1e4)]),
            ("契約申込 234万kW", [("LTDA", mid(ltda_lo, ltda_hi)), ("不明", 234 - mid(ltda_lo, ltda_hi))]),
            ("うち SII（時点不明・推定）", [("SII", mid(sii_lo, sii_hi))])]
for i, (lab, segs) in enumerate(rows_fig):
    left = 0.0
    for key, w in segs:
        ax[0].barh(i, w, left=left, color=COL[key], edgecolor="white", height=0.6)
        if w < 12:
            ax[0].text(left + w / 2, i + 0.34, f"{w:.0f}", ha="center", va="top", fontsize=8.5)   # y 軸は反転（棒の下に置く）
        else:
            ax[0].text(left + w / 2, i, f"{w:.0f}", ha="center", va="center", fontsize=8.5)
        left += w
ax[0].set_yticks(range(3)); ax[0].set_yticklabels([r[0] for r in rows_fig], fontsize=8.5); ax[0].invert_yaxis()
ax[0].set_ylim(2.55, -0.45)
ax[0].set_xlim(0, 240)
ax[0].set_xlabel(f"万kW（LTDA は{ltda_lo / 1e4:.1f}〜{ltda_hi / 1e4:.1f}、SII は{sii_lo / 1e4:.1f}〜{sii_hi / 1e4:.1f} の中央値）", fontsize=9)
from matplotlib.patches import Patch
sf_a.legend(handles=[Patch(color=COL[k], label=l) for k, l in (("LTDA", "LTDA（APV>0）"), ("SII", "SII の補助（APV<0）"),
                                                              ("Helios", "マーチャント Helios（APV<0）"), ("不明", "不明（SII を含みうる）"))],
            fontsize=8.5, loc="outside lower center", ncol=2, frameon=False, columnspacing=1.5)
ax[0].set_title("(a) 乖離の勘定（北海道、系統用蓄電池、2026年5月末）", loc="left", fontsize=9.5)
labs = ["LTDA 6時間\n（積み上げ〜上限）", "SII の1/2補助 4時間\n（θ=1〜1.567）", "Helios 型 2時間\n（スポットのみ）", "マーチャント 4時間\n（不明の参照）"]
lo_hi = [(LM9["積み上げ5%"], LM9["上限7.7万・設備容量"]), (apv_s[M9]["実績整合"], apv_s[M9]["FY2026水準"]),
         (apv_h[M9]["実績整合"], apv_h[M9]["FY2026水準"]), (apv_m[M9]["実績整合"], apv_m[M9]["FY2026水準"])]
for i, (a, b) in enumerate(lo_hi):
    ax[1].plot([a / 1e4, b / 1e4], [i, i], lw=6, color=[COL["LTDA"], COL["SII"], COL["Helios"], COL["不明"]][i], solid_capstyle="butt")
ax[1].axvline(0, color="#333", lw=0.8)
ax[1].set_yticks(range(4)); ax[1].set_yticklabels(labs, fontsize=8.5); ax[1].invert_yaxis()
ax[1].set_xlabel("APV（万円/kW）", fontsize=9); ax[1].set_title("(b) 属性別の APV", loc="left", fontsize=9.5)
for a_ in ax:
    a_.tick_params(labelsize=8.5)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIG, "gap_ledger.png"), dpi=300)
print("saved ltda_battery_projects.csv（訂正）, ltda_hokkaido_summary.csv, gap_ledger_projects.csv, gap_ledger_summary.csv, gap_ledger_apv_basis.csv, figures/hokkaido/gap_ledger.png")
