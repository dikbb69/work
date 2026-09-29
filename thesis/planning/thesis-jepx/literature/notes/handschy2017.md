# Handschy, M. A., Rose, S., & Apt, J. (2017) Is it always windy somewhere? Occurrence of low-wind-power events over large areas
- 書誌: *Renewable Energy* 101, 1124–1130. DOI 10.1016/j.renene.2016.10.004（非OA、© 2016 Elsevier）。受付 2015-12-20／改訂 2016-08-12／受理 2016-10-03。所属: Enduring Energy LLC・CU Boulder CIRES（Handschy）、Carnegie Mellon EPP（Rose, Apt）・Tepper（Apt）
- 出所: Drive 上の PDF（1-s2.0-S0960148116308680-main.pdf, fileId 19y_D8TvoW_nHQ0KTjMX4b963V_wlXRyj）を 2026-09-29 精読。Table 1・式(2)(3)・Fig. 4 キャプションの式は PDF のページ画像で照合済み（**Drive のテキスト抽出では Table 1 の負号 13 個と式(2)の負号が落ちていた**）。Fig. 4 の h/年 は PDF のベクター描画から読み取った近似値（9 サイト・5% 閾値の値が本文の 36 h/年と一致することで較正を確認）。Supplementary data は未参照
- 筆頭著者 Handschy は E11（st-martin2015.md）の第 3 著者。E11 の相関距離が「独立サイト数」を与え、本論文がその数で低出力時間がどう減るかを与える関係

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 地理的に離れた（弱相関の）風力を束ねると、低出力（設備容量比 1%・5%・15% 未満）の時間は集約サイト数 N とともにどれだけ減るか。「どこかは常に風が吹いているか」。ELCC（実効負荷担当容量＝風力の供給力価値）や予備力の評価に効く下側の裾確率が動機（§1）。
- 貢献: 大偏差理論（Large Deviations Theory, LDT）で集約出力の下側の裾を、単一サイトの出力ヒストグラムのみから調整パラメータなしで推定。中心部は正規分布（CLT）と接ぎ、独立 N サイトの発電時間曲線（duration curve）全体を近似。裾は N に指数的（e^{−QN}）、標準偏差・変動係数は 1/√N（Bienaymé）という差を定量化（Carlin & Haslett 1982 の観察「分散の効果は零出力・定格出力の確率の方が変動係数より顕著」を裏付け）。
- 位置づけ: 先行研究（Justus & Mikhail 1978、Carlin & Haslett 1982、Hasche 2010 など）は Weibull・ベータ等の分布形を仮定。本論文は風力（風速×パワーカーブの畳み込み）の分布形を仮定しない。ただし「統計的に独立なサイト」が前提で、独立サイト数が地理的分散の良い代理指標かは未検証と自認（§5）。

## 2. データ・設定
- 対象: 米国本土の 9 地点の高塔（tall-tower）風速観測（Fig. 1, Table 1）。選定基準は 4 点: 高塔（一般気象官署より高い）で公開データがある／平均風速が近い／データ期間が重なる／シミュレーション出力の相関が低い（=互いに遠い）。
- 期間・品質: 1 時間平均風速、2007-01〜2012-12（5.26×10⁴ h）。品質管理で各地点 9〜38% を除外し、9 地点が同時に揃うのは 1.46×10⁴ h（約 1.7 年分）。各地点で平均風速が 6 m/s に最も近い高さ（23〜122 m）を採用。地点の平均風速は 4.6〜6.3 m/s と、商業風力の典型より低い。
- 出力変換: Vestas V110-2.0 MW のパワーカーブ（カットイン 3 m/s、11 m/s で定格=1、カットアウト 25 m/s）。出力は設備容量比。N サイト集約は各地点の時別出力の単純平均（等容量。欠測のある時刻は除外）。
- 「代表サイト」: 9 地点の出力をプールしたヒストグラム（約 4.2×10⁵ サンプル、72 ビン）。平均 μ=CF=0.31、標準偏差 σ=0.34、零出力割合 δ0=0.23（≈2,000 h/年）、定格出力割合 δ1=0.06（≈520 h/年）。

| 地点 | 高さ h (m) | 平均風速 (m/s) | CF | δ0 | δ1 |
|---|---|---|---|---|---|
| Argonne | 60 | 5.4 | 0.27 | 0.11 | 0.02 |
| Brookhaven | 88 | 5.8 | 0.32 | 0.13 | 0.03 |
| Hanford | 122 | 5.0 | 0.27 | 0.36 | 0.08 |
| Kennedy | 90 | 6.0 | 0.35 | 0.12 | 0.03 |
| LLNL | 23 | 6.0 | 0.37 | 0.27 | 0.12 |
| Los Alamos | 92 | 4.6 | 0.23 | 0.38 | 0.04 |
| NWTC | 80 | 4.8 | 0.22 | 0.37 | 0.06 |
| SGP | 25 | 6.1 | 0.36 | 0.15 | 0.08 |
| WLEF | 122 | 6.3 | 0.41 | 0.13 | 0.03 |
| 代表サイト | | | 0.31 | 0.23 | 0.06 |
- 地点間相関（Table 1、時別出力の Pearson 相関、36 ペア。原 PDF で負号を確認）: 平均 0.030、中央値 0.026、範囲 −0.077〜0.240、負が 13 ペア、0.1 超は 3 ペア（SGP–Los Alamos 0.240、WLEF–Argonne 0.220、SGP–Argonne 0.170）。
- 商業風力の典型に近い比較用サイト（Sweetwater, TX, 平均風速 7.9 m/s。Supplementary）: δ0=6.3%。

## 3. 手法
- 集約出力 P̄_N を、代表サイト分布 X の N 個の独立同分布（i.i.d.）コピーの平均とみなす（実データは独立でも同分布でもないが近似として採用）。
- 裾（p0 が平均から遠いとき）: 式(2)（Rozovsky 2003 の精密化）
  Pr(P̄_N < p0) = [−1 / (ϑ·σ(ϑ)·√(2πN))] · e^{−Q(p0)·N} · (1+o(1))
  Q(p0) = sup_θ [p0·θ − λ(θ)]（レート関数。累積母関数 λ(θ)=ln⟨e^{θX}⟩ のルジャンドル変換）、ϑ は上限を与える θ、σ(ϑ)=[λ''(ϑ)]^{1/2}。累積母関数はヒストグラムから式(3): λ(θ)=ln[δ0 + δ1·e^θ + Σ_{k=1..70} y_k·e^{((2k−1)/140)θ}]。
- Q(0) = −ln δ0（N サイトすべてが同時にゼロ出力＝δ0^N）。正規分布のレート関数は Q=½(p0−μ)²/σ²。有界な風力の裾は正規分布より薄いので、正規近似は低出力確率を過大評価する（Fig. 3）。
- 中心部（p0 が平均寄り）: CLT による正規近似 Pr(P̄_N<p0) ≈ Φ[(p0−μ)/(σ/√N)]、時間 = 8760·Φ[(p0−μ)/σ_N]。**原文（本文・Fig. 4/6 キャプション）は Φ[(μ−p0)/(σ/√N)] と書かれ、下側確率としては符号が逆**。本ノートの検算では (p0−μ) の向きが Fig. 4（p0=15%・N=9 で 692 h/年 ↔ 実測 721）・Fig. 6（N=6, p0=0.1 で 571 h/年）と整合し、原文の符号だと 8,000 h 前後になる。数式を引用する際は要注意。N=6 では p0≈0.1 で LDT と正規が交差（Fig. 6）、交差軌跡は Fig. 7。Fig. 4 では p0=1%・5% に LDT、p0=15% に正規近似を用いる。
- Introduction で紹介された標準偏差の式（Justus & Mikhail 1978）: σ_N = σ_1 [(1+ρ(N−1))/N]^{1/2}（ρ=サイト間平均相関）。

## 4. 主要結果
- 対象・閾値・持続時間の要点: 米国本土の 9 地点（互いに数百〜数千 km）、閾値は設備容量比 1%・5%・15%、集約は N=1〜9。**持続時間（連続する低出力の長さ）の分布は論文に無い**（時間あたりの超過頻度のみ。§5）。
- 見出し（Abstract）: 設備容量の 5% 未満の時間は、中央値の単一サイトで 2,140 h/年 → 9 サイト集約で 36 h/年（約 1/60。年の 24.4% → 0.41%）。標準偏差は 1/3。低出力時間は N に指数的に減る。
- 分散: 9 サイト集約の分散 0.0154 は単一サイト平均分散 0.118 の 1/7.6 → 独立 8 サイト相当（Table 1 の平均相関 0.03 を等相関式に入れると 1/7.2）。
- **Fig. 4（N サイト集約で設備容量比 p0 未満になる時間、h/年）**: 箱=N サイトの全組合せの四分位範囲（PDF 描画からの読取り）、N=9 は唯一の組合せ（円）。低風速サイト（平均風速 4.6〜6.3 m/s）での値。

| N | p0=15% | p0=5% | p0=1% |
|---|---|---|---|
| 1 | 3,320–5,260 | 1,809–4,160（中央値 2,140） | 1,083–3,182 |
| 2 | 2,450–3,440 | 863–1,538 | 248–577 |
| 3 | 1,901–2,554 | 473–845 | 92–211 |
| 4 | 1,480–2,020 | 270–471 | 31–66 |
| 5 | 1,248–1,606 | 163–260 | 11–25 |
| 6 | 1,026–1,313 | 101–160 | 3.0–8.5 |
| 7 | 899–1,077 | 62–101 | 0.8–3.7 |
| 8 | 783–891 | 44–57 | 0.3–2.1 |
| 9 | 721（年の 8.2%） | 36（年の 0.41%） | 0（観測なし） |
- 平均（0.31）に近い 15% 閾値は 9 サイトでも約 720 h/年（年の 8%）残る。単一サイトの四分位 3,320–5,260 h が 9 サイトで 721 h と、減り方は緩い（正規近似のレート Q=½(0.16/0.34)²≈0.11 と、LDT の Q(0.05)=0.49・Q(0.01)=0.97 より小さい）。1% 閾値の 9 サイト値は同時 1.46×10⁴ h の中で 0 h（稀事象の推定には標本が短い）。
- LDT の式（Fig. 4 キャプション）: p0=5%: (1.69/√(2πN))·e^{−0.49N}、p0=1%: (1.67/√(2πN))·e^{−0.97N}（時間割合。×8760 で h/年）。レート関数は Q(0.05)=0.49、Q(0.01)=0.97、Q(0)=−ln 0.23=1.47。独立サイトを 1 つ増やすごとに 5% 未満の時間は約 1/1.6（e^0.49）、1% 未満は約 1/2.6（e^0.97）、零出力は約 1/4.4（e^1.47）に減る（√N 因子は別）。式の計算値（h/年）:

| N | p0=5% | p0=1% |
|---|---|---|
| 1 | 3,618 | 2,212 |
| 3 | 784 | 184 |
| 6 | 127 | 7.1 |
| 9 | 24 | 0.3 |
  （実測: N=9 で 5% は 36 h、1% は 0 h。N=1 の式は漸近式の適用外）
- 規模感（結論）: 1% 未満の確率を 20 分の 1 にするには 3 → 6 サイトで足りる（式では 26 分の 1）が、標準偏差を同じ 20 分の 1 にするには独立サイト数を 400 倍（3 → 1,200）にする必要があり「ほぼ不可能」。
- 平均風速の高いサイト（Sweetwater, TX, 7.9 m/s。Fig. 4 の×印、Fig. 3 破線）: 単一サイトで 15%/5%/1% 未満が約 1,880/970/550 h/年（図から読取り。1% 未満は δ0=6.3% ≈ 553 h と一致）、Q(0)≈2.76（=−ln 0.063）。低風速の 9 地点より低出力時間が大幅に少なく、集約の効き（Q）も大きい。
- 年変動: 年ごとの出力分布の違いがレート関数に与える影響は小さい（著者が Supplementary Fig. S4 で示す。本ノートでは未確認）。
- 先行研究の数値（Introduction からの再掲。二次引用）: Molly（旧西独 25 気象官署）: 零出力時間が単一サイト 1,500–7,200 h/年 → 国内 800 km 内の 18 サイト集約で 5 h/年未満。Archer & Jacobson 2003（米中西部、午後の風速<3 m/s）: 単一 7.6% → 3 サイト（120×160 km）2.6% → 8 サイト（550×700 km）0%。同 2007: 設備容量の 5% 未満が単一 21% → 7 サイト 10% → 19 サイト 1.6%。Holttinen 2005（北欧実績）: デンマーク単独では 2000–2002 年に 1% 未満が約 5% の時間あったが、北欧全体では一度も無かった。Fisher et al. 2013（MISO 域 108 サイト）: 時間の 90% で確保できる出力は冬 7%・夏 3%（設備容量比）。

## 5. 著者が挙げる限界・今後の課題
- **個々の低出力イベントの持続時間は計算していない**: 「ten 1-h periods と one 10-h period を区別しない」（§5）。時間あたりの超過頻度のみ。
- 独立サイトの仮定: 良風況地域にクラスタ化して相関が高い配置や、より近接した配置には未対応。米国本土で独立 9 を超えるサイトが得られるかは不明。追加研究が必要。
- 負荷との相関を無視 → ELCC は未推定。
- 相関の低いサイトを優先して低風速サイトを選んだため、低出力時間は商業サイトより多い（Sweetwater との比較）。
- （本ノートの確認）実データではなく風速からのシミュレーション、1 時間平均（サブ時間変動なし）、単純平均（容量配分・抑制・後流なし）。9 地点同時の有効データは 1.46×10⁴ h のみ。

## 6. 本研究との関係
- 引用予定箇所: 第6章（帯域分解の議論で「集約効果は独立サイト数で決まる」「裾と分散で効き方が違う」）、第10章（含意・限界: 独立サイトが得られない規模への外挿）。E11 と組で使う。
- 支持できる主張（条件付き）:
  1. 標準偏差は 1/√N でしか減らない（9 サイトで 1/3）。集約後も設備容量の 15% 未満が年約 720 h（約 8%）残る（低風速サイト設定・独立 9 サイトでも）。
  2. 効果の大きさは相関＝独立サイト数で決まる。Justus–Mikhail の式より、平均相関 ρ の下で分散比の上限は 1/ρ（ρ=0.1 → 10 倍、0.3 → 3.3 倍。本ノートの整理）。本論文の 9 サイトは平均相関 0.03 と極端に低い best case。
  3. 独立サイト数は E11 の相関距離で見積もれる（N≈A/(2ξ)²）。最遅の変動で ξmax=89〜447 km（E11）→ 北海道規模（A≈8×10⁴ km²、概数）では N_eff≈0.1〜2.5（本ノートの整理）。LDT の e^{−QN} は N≈1 では効かない。「フリートに集約しても遅い変動・低出力は消えない」（第6章・第10章）は、E11（N_eff）と本論文（N_eff から裾・分散への効き方）を合成した論理として立てる。
- 注意（誤引用の防止）:
  - 本論文は「数日〜週の帯域に変動が分布する」ことの直接の根拠にならない。帯域分解・スペクトル分析は無く、持続時間も著者が対象外と明記。
  - 見出しの結論は逆向きに読まれ得る: 米国本土規模（数千 km）で独立 6〜9 サイトなら低出力は年数十時間まで激減する（5% 未満: 2,140→36 h）。「集約しても消えない」の裏付けに単独で使わず、「N が小さい・相関が高い場合は効かない」という理論的条件（レート関数と 1/√N の差、独立サイト数）として使う。
  - 北海道（数百 km 規模）へは外挿できない（著者も近接配置と独立 9 超のサイトは対象外と明記）。
  - シミュレーション（風速→V110 出力、単純平均）であり、実際の風力の出力・抑制・容量配分は含まない。
  - 持続時間・多日イベントの実証は別文献が必要。候補: Ohlendorf & Schill (2020, *Environ. Res. Lett.* 15) のドイツの低風力イベントの頻度・持続時間分析（記憶ベース。書誌・DOI は未検証。使う前に検証すること）。
- 新規性チェック: 集約による裾確率の指数減少（LDT）は本論文で既出。本研究は帯域別の分散シェア（λ）と、蓄電池価値・均衡容量への接続が新規、という位置づけ。

## 7. 引用に使える原文
- "The number of low-power hours per year declines exponentially with the number of sites being aggregated. Hours with power levels below 5% of total capacity, for example, drop by a factor of about 60, from 2140 h/y for the median single site to 36 h/y for the generation aggregated from all nine sites; the standard deviation drops by a factor of 3."（Abstract）
- "Combining this theory for tail behavior with the normal distribution for behavior near the mean allows us to estimate, without the use of any adjustable parameters, the entire generation duration curve as a function of the number of essentially independent sites in the array."（Abstract）
- "Our results demonstrate that aggregating wind plants can decrease the occurrence frequency of low-power events more dramatically than it decreases the magnitude of typical of variations around the mean."（§5。"typical of variations" は原文のまま）
- "it is important to note the important caveat that our results do not calculate the time duration of individual low-wind-power events, i.e. they do not distinguish between ten 1-h periods and one 10-h period of low power."（§5）
- "However, relating the predictions of our model to the variability of real wind power plants depends critically on the extent to which the number of statistically independent sites is a good proxy for geographic diversity."（§5）
- "The data we analyze inform speculation neither about the performance of arrays of more-closely spaced wind plants nor about achieving more than nine effectively independent sites within the contiguous U.S."（§5）
- "Cutting the standard deviation by a similar factor would require increasing the number of independent sites from 3 by a factor of 400, to 1200—almost certainly not possible."（§5）
- "We are not aware of other data sets with these characteristics; for example, the data used by Rose and Apt [22] come from a region of smaller geographical extent with consequently higher correlation."（§2.1）
