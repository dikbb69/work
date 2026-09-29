# Sioshansi et al. (2009) Energy Economics 31 — 価格テイカーLP裁定の原型

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Analysis of Price-Taking Storage Arbitrage and Welfare Impacts

This study examines the welfare impacts of electricity storage, focusing on the incentives of different ownership structures and the effects on price spreads. It models storage operation and analyzes how large-scale storage can influence market dynamics.

### Optimization Problem for Price-Taking Storage Arbitrageur

The optimization problem for a price-taking storage arbitrageur involves maximizing the arbitrage value, which is the difference between the revenue from discharging and the cost of charging, subject to technical constraints. The paper models this within a two-period electricity market framework.
- Objective Function: The arbitrageur aims to maximize the net profit from buying energy when prices are low and selling it when prices are high. This is represented by the total net profit of the owner(s) of the storage devices, given by the equation: Π_arb (δ) = δp(l₂ – δ) – φδp(l₁ + φδ) which simplifies to δ[c₀ (1–φ) + c₁ (l₂ – φl₁)] – δ²c₁ (1 + φ²)  (Sioshansi, 2010). Here, δ represents the amount of energy discharged, p(l) is the price-load relationship, l₁ and l₂ are loads in off-peak and on-peak periods, respectively, and φ = 1/η where η is the roundtrip efficiency  .
- Constraints: The storage device operates within specific technical limits:
- Discharge Capacity: The storage device has a discharge capacity of δ MW  (Sioshansi, 2010).
- Charging Capacity: Its total charging capacity is δ/η MW, allowing one hour of charging at full capacity to provide enough energy for one hour of full-capacity discharge  (Sioshansi, 2010).
- Energy Balance: If x MWh of energy is put into storage, at most ηx MWh can be taken out, reflecting energy losses  (Sioshansi, 2010).
- Operational Limits: The amount of energy discharged, δ, must be between 0 and the maximum storage capacity δ (0 ≤ δ ≤ δ)  (Sioshansi, 2010).
- Notation: The key notations include:
- p(l): Electricity price as a function of generating load l  (Sioshansi, 2010).
- c₀ + c₁l: Linear relationship for electricity prices  (Sioshansi, 2010).
- η: Roundtrip efficiency of the storage device (0 < η < 1)  (Sioshansi, 2010).
- x: MWh of energy put into storage  (Sioshansi, 2010).
- δ: Discharge capacity of the storage device in MW, and also the amount of energy discharged in MWh  (Sioshansi, 2010) .
- δ/η: Total charging capacity in MW  (Sioshansi, 2010).
- l₁: Load in the off-peak period (period 1)  (Sioshansi, 2010).
- l₂: Load in the on-peak period (period 2)  (Sioshansi, 2010).
- φ: Defined as 1/η  (Sioshansi, 2010).

### Change in Arbitrage Value with Storage Duration

The provided text does not explicitly detail how arbitrage value changes with storage duration (hours of capacity) using specific numerical values. However, it mentions that the price-smoothing effect of large-scale storage can reduce the arbitrage value. Specifically, the analysis in Sioshansi et al. (2009) shows that the price-smoothing effect of large-scale storage can reduce the arbitrage value of 1 GW of storage by more than 20%, compared to the arbitrage value for a price-taker  (Sioshansi, 2010). This indicates that as storage capacity increases, the per-unit arbitrage value can decrease due to market response.

### Effect of Large-Scale Storage on Price Spread (Self-Cannibalization)

Large-scale electricity storage affects the price spread through a mechanism often referred to as "self-cannibalization." This occurs because the very act of arbitrage by large storage units tends to smooth out the price differences they exploit.
- Mechanism: Larger utility-scale storage can smooth the load pattern by lowering on-peak and increasing off-peak generating loads. This action results in a similar smoothing of on- and off-peak price patterns, which in turn reduces arbitrage opportunities for the storage device itself  (Sioshansi, 2010).
- Impact on Arbitrage Value: While this load smoothing reduces the arbitrage value for the storage operator, it generates significant external welfare effects by reducing energy prices for consumers and increasing profits for electricity generators  (Sioshansi, 2010). The paper notes that this price-smoothing effect can reduce the arbitrage value of 1 GW of storage by over 20% .

### Assumed Round-Trip Efficiency and Other Technical Parameters

The model assumes a roundtrip efficiency and other technical parameters for the storage device:
- Roundtrip Efficiency (η): The storage device has a roundtrip efficiency, η, which captures energy losses during the storage cycle. It is assumed that 0 < η < 1  (Sioshansi, 2010).
- Discharge Capacity (δ): The storage device has a discharge capacity of δ MW  (Sioshansi, 2010).
- Charging Capacity (δ/η): The total charging capacity is δ/η MW, designed to allow one hour of full-capacity charging to provide enough energy for one hour of full-capacity discharge  (Sioshansi, 2010).
- Price-Load Relationship: Electricity prices are assumed to respond to generating loads based on a linear relationship: p(l) = c₀ + c₁l, where c₀ ≥ 0 and c₁ > 0  (Sioshansi, 2010).
- Price-Inelastic Loads: Consumer loads (l₁ and l₂) are assumed to be price-inelastic because consumers face a time-invariant retail rate of electricity  (Sioshansi, 2010).
In essence, the study highlights that while storage can reduce price volatility and offer welfare gains, the arbitrage value for storage operators can diminish as storage capacity increases due to its own price-smoothing effect. The model simplifies market operations to analyze these fundamental economic incentives and their implications for different ownership structures.

## 原典精読（2026-09-29）
- 書誌: Ramteen Sioshansi, Paul Denholm, Thomas Jenkin, Jurgen Weiss (2009). Estimating the value of electricity storage in PJM: Arbitrage and some welfare effects. *Energy Economics* 31(2), 269–277. DOI 10.1016/j.eneco.2008.10.005（JEL D60, D62, Q41, Q42）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読）。上記 SciSpace ログは Sioshansi (2010) の内容と混在しているので、以下を正とする。

### 1. 問いと貢献
- 4つの分析（§1）: (1) 蓄電の効率・エネルギー容量（時間数）と裁定価値の関係、(2) 完全予見の理論的ディスパッチ vs 不確実性下の「実際の」価値捕捉、(3) 送電制約・ガス価格・燃料構成による地域・時間的な価値変動、(4) 大規模蓄電がオンピーク価格を下げオフピークを上げて裁定価値を減らす一方、消費者・発電事業者に厚生効果を生むこと（＋価格ショックからの消費者保護）。
- Jenkin & Weiss (2005) の拡張。価格テイカー LP 裁定分析（Graves et al. 1999 等）を、価格影響を持つ大規模装置の凸二次計画に拡張した点が新規。

### 2. データ・市場・期間
- PJM（2007年ピーク 139 GW、5,100万人）、2002–2007 年の負荷加重平均限界価格（時間値）。2006年は47母線の価格も使用。ガス価格は EIA（NJ/MD/PA 平均）。
- 蓄電: 往復効率 80%（Bath County 揚水 80.3%）を基本、感応度 50–90%。充放電出力は同一。2週間ごとに15日の計画期間で最適化（週末効果と繰越価値を取り込む）。GAMS/CPLEX（LP）、大規模ケースは GAMS/MINOS（QP）。

### 3. モデル・手法
- 価格テイカー: 2週間ブロックの LP（Appendix A）。
- **バックキャスト**（§3）: 直前2週間の価格で最適化したディスパッチを当該2週間に適用し実価格で評価（「no-foresight」の下限）。
- **大規模装置**（§5.1）: 月ごとに価格–発電負荷の線形関係 p = a + b·l を制約付き最小二乗（非減少制約）で推定し、1 GW 装置が自らの充放電で価格を動かすことを織り込んだ凸QP。「Theoretically, entry by storage devices should occur until all profitable opportunities to buy inexpensive energy off-peak and sell expensive energy on-peak are arbitraged away.」（§5、自由参入の言及）
- 厚生（§5.2, Fig.16）: 充放電1サイクルで ΔCS = C+D+E−A、ΔPS = A+B−C−D、合計 B+E > 0。発電は競争的（価格＝限界費用）と仮定。

### 4. 主要結果（数値）
- **Fig.2**: 12h 装置の年間裁定価値は 2002年 約$60/kW-yr → 2005年 $110/kW-yr 超（2006年 $77/kW-yr、2007年 $99/kW-yr）。
- **Fig.3–4（時間数）**: **最初の4時間で捕捉可能価値の50%超**、8h で約85%、20h で約95%。限界価値は約8hまでほぼ線形に低下し、それ以降は僅少（「knee at about 8 h」）。
- **Fig.5（効率）**: 20h 装置で効率 70%→80% により裁定価値 $60→$80/kW-yr（+30%超）。90% の価値を捕捉するには 9–10h で十分。
- **Fig.6（バックキャスト）**: 12h 装置で6年すべて**完全予見価値の約85%以上**を捕捉。理由: 日内・週内の価格パターンが予測可能。簡単な予測を加えれば大幅改善が見込まれる（下限）。
- **Fig.8, 11（ガス価格・燃料構成）**: ガス価格 2002→2007 で100%超上昇、裁定価値は30–60%上昇。2006→2007 はガス価格横ばいでもオンピークでガスが限界電源になる時間が増え価値上昇。オフピークは石炭が価格設定（原子力は33%シェアでも価格設定しない、脚注14）。
- **Fig.12（母線別）**: 2006年平均 $77/kW-yr に対し母線最大 $105/kW-yr（+$30/kW-yr、Bedington 母線）。2007年は $99 vs $137。
- **Fig.15（1 GW の価格影響）**: 価格テイカー比で直近3年は約10%減、初期の年（2002年、ピーク負荷 63.8 GW）は 20%超減。PJM 拡大（2007年ピーク 139.4 GW）で相対規模が縮小したため。
- **Table 1–3（1 GW、効率80%、$M/年）**: 4h: 2002年 裁定26.8／ΔCS +16.8／ΔPS −14.3、2007年 47.3／+22.7／−20.2。8h: 37.0／+21.5／−17.3、64.9／+27.3／−23.4。16h: 42.1／+26.3／−21.7、73.7／+34.6／−30.3。外部厚生効果は裁定価値と同程度の規模、ΔCS > |ΔPS| で純厚生増。
- **Table 4（Katrina 前後、1 GW 8h、1日）**: 裁定 $345k→$590k（+70%超）、ΔCS $188k→$320k（約+70%）。価格–負荷関係の傾きが急になると蓄電の価格平準化効果が大きくなる。
- 容量支払いは「potential adder」として推定せず（脚注23: Felder & Newell 2007 の CONE $58/kW-yr を参照）、アンシラリーとの共最適化も対象外。

### 5. 著者が挙げる限界
- 線形価格–負荷関係は「illustrative」（1か月以内なら良好なフィット）。
- 「static」評価: 送電増強は地域差を縮小、混雑地域の負荷成長は裁定機会を増やす。
- 「any analysis of energy storage that considers only one or a few attributes (such as energy arbitrage) and neglects the interplay among various sources of value is likely to significantly underestimate the value and social benefits of energy storage.」
- 所有構造の問題（merchant は外部便益を捕捉できず投資誘因が低い；送電事業者・規制事業者の方が誘因が良い可能性）は Sioshansi (2010) で展開。

### 6. 本研究との関係（追記）
- **第2章2.2／第6章（バックテスト）**: 「最初の4hで価値の50%超」「限界価値の膝は8h」は、本研究が4h 蓄電池を基準にする根拠。「バックキャストで完全予見の85%以上」は本研究の capture ratio 81–83% の直接の比較対象（PJM の RT 時間値と JEPX の DA 30分値の違いを注記）。
- **第7章（π(K)）**: 「1 GW で価格テイカー比 10–20%超の減価、市場規模に反比例」を、北海道（需要 3–5 GW、PJM の約1/30）に当てはめると 1 GW の相対規模は PJM 2002年の約20倍 → 本研究の「≈1 GW で spot rent 枯渇」と整合。Table 1–3 の裁定価値／ΔCS の比は、本研究の政策ウェッジ（消費者余剰増を根拠とする容量市場・LTDA）の規模感の参照。
- **第8章**: 「Theoretically, entry by storage devices should occur until all profitable opportunities ... are arbitraged away」は自由参入ゼロレントの最初期の言及として引用。容量支払いを「adder」として扱う姿勢は本研究の κ·P_cap の扱いと同型。
- 新規性チェック: 既に行われていること＝価格テイカー裁定価値、効率・時間数感応度、バックキャスト捕捉率、線形価格影響下の大規模装置の減価と厚生効果。本研究が新たに行うこと＝これを風力主導ゾーンで K の関数（フリート）として推計し、自由参入均衡と政策ウェッジへ接続。

### 7. 引用に使える原文
1. §2 (p.271): "most of the arbitrage value in storage comes from intra-day arbitrage, with more than 50% of the total capturable value derived from the first 4 h of storage. ... 8 h of storage captures about 85% of the potential value, while 20 h of storage captures about 95% of potential value."
2. §3 (p.272): "In each of the six years evaluated, the backcasting approach captured about 85% or more of the potential arbitrage value. This approach is successful because the hourly operation and value of energy storage is strongly based on historical price and load patterns over a variety of different time-frames, which are to a large extent predictable."
3. §5 (p.274): "Theoretically, entry by storage devices should occur until all profitable opportunities to buy inexpensive energy off-peak and sell expensive energy on-peak are arbitraged away."
4. §5.1 (p.275): "Our analysis shows that the value of storage would have been diminished relative to a price taker—by approximately 10% during the past three years, but more than 20% for some earlier years. ... Because the off- and on-peak price difference did not change in proportion to the size of the load, a 1-GW device would have a much larger price-shifting effect in 2002 than in 2007."
5. §6 (p.276): "Because these external welfare benefits will not necessarily be captured by a private-sector investor who relies on arbitrage, such an investor may have a reduced incentive to invest in energy storage due to the diminished value of arbitrage."
