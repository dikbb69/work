# Lamp & Samano (2022) Energy Economics 107 — 蓄電池→スプレッド圧縮のイベントスタディ設計

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Empirical Design and Findings on Battery Storage in Electricity Markets

This study investigates the impact of large-scale battery storage on short-term electricity market outcomes and price spreads, particularly focusing on the California market. It employs an empirical design to analyze charging and discharging patterns and compares actual battery operations with an optimal arbitrage model.

### Empirical Design for Identifying Effects on Price Spreads

The authors use a "difference" framework to estimate the effect of battery capacity additions on equilibrium price spreads and peak prices  (Lampa & Samano, 2022).
- Regression Model: The study uses a regression model to analyze the impact of new battery capacity on price spreads. The general form of the regression is given by:
log(y_t) = β_0 + Σ β_j × capacity_{t-j} + α'X_t + γ_τ + ε_t  (Lampa & Samano, 2022)
- y_t: This represents either the maximum or mean daily Real-Time Market (RTM) price spread, or the maximum daily RTM price  (Lampa & Samano, 2022).
- capacity_{t-j}: This is the treatment variable, representing the new battery capacity added. The index j ranges from -4 to 12, indicating weeks relative to the battery installation  (Lampa & Samano, 2022).
- X_t: This includes control variables such as renewable output, large-hydro output, and load  (Lampa & Samano, 2022).
- γ_τ: This term accounts for month and week-of-year fixed effects  (Lampa & Samano, 2022).
- Treatment Variable: The treatment variable is the capacity_{t-j}, which signifies the new battery capacity added to the system  (Lampa & Samano, 2022). The analysis considers the impact of this capacity over a period of weeks relative to its installation.
- Control Group/Exogeneity: The authors assume that the exact timing of battery entry is exogenous to current wholesale prices  (Lampa & Samano, 2022). To support this, they examine coefficients in the four weeks leading to the entry event, finding them not statistically different from zero, which is consistent with the exogeneity hypothesis .

### Estimated Spread Compression and Horizon

The study finds a negative and statistically significant effect of new storage capacity on price spreads and maximum prices in the Real-Time Market (RTM)  (Lampa & Samano, 2022).
- Magnitude of Compression: For a 1 MWh of new capacity, the price spread changes by 100 × β_j percentage points  (Lampa & Samano, 2022). While specific percentage figures for β_j are not directly quoted in the provided text for this section, the results indicate a reduction in price spreads.
- Horizon of Impact: The significant effect is observed in the weeks following the addition of new storage capacity  (Lampa & Samano, 2022). This effect then fades away after five weeks, though mean point estimates remain negative .

### Gap Between Actual Battery Operation and Optimal Arbitrage

The authors identify a significant gap between how batteries actually operate and what an "optimal" arbitrage strategy would dictate.
- Optimal Definition: "Optimal" arbitrage is defined by a model where a price-taking storage facility maximizes its arbitrage value, subject to technological constraints, assuming perfect foresight of wholesale prices  (Lampa & Samano, 2022) . This model serves as a best-case scenario for comparison .
- Discrepancies: The empirical data shows significantly less responsiveness to prices compared to the output from the optimal model  (Lampa & Samano, 2022). Specifically, actual battery discharge is much smaller during evening peak hours than what the optimal model suggests . While the optimal model predicts large arbitrage opportunities in the evening when prices are highest, the observed output shows much lower responses . The actual battery fleet only responds positively to marginal price increases during early morning and a small increase in the afternoon for DAM prices, and at specific hours for RTM prices, indicating less flexible employment than an optimal arbitrageur .

### Data Granularity

- Primary Data Sources: The study utilizes publicly available data from the California Independent System Operator (CAISO) and OASIS  (Lampa & Samano, 2022).
- Frequency: Data on load, batteries, and renewable output are available at 5-minute intervals, while Real-Time Market (RTM) and Day-Ahead Market (DAM) price data are retrieved hourly  (Lampa & Samano, 2022).
- Minimum Data Needed for Replication: To replicate this in another market, the minimum data needed would include: hourly wholesale prices (both day-ahead and real-time if available), battery output (charging and discharging patterns), load data, and information on installed storage capacity over time  (Lampa & Samano, 2022) . The study's sample period for primary analysis is from June 6, 2018, to March 1, 2020, to ensure consistent data reporting and avoid COVID-19 pandemic effects . For studying equilibrium impacts of new capacity, hourly data on DAM and RTM wholesale market prices from 2013 to 2017 are used .

### Threats to Identification

The authors discuss several threats to identification, particularly when comparing the optimal model to empirical findings:
- Perfect Foresight Assumption: The optimization model assumes perfect foresight of market prices, which is not realistic in practice  (Lampa & Samano, 2022).
- Aggregate Data: The study only observes aggregate battery responses, not individual plant output, making it difficult to distinguish if batteries are used for purposes other than arbitrage (e.g., frequency control, ramping/spinning reserves)  (Lampa & Samano, 2022).
- Simplified Model: The optimal storage model is stylized and simpler than real-world operations, not accounting for complex dynamic charge and discharge decisions or large differences in battery power and capacity sizes  (Lampa & Samano, 2022).
- Price-Taking Assumption: While individual batteries are small and assumed to be price-takers, the possibility of some battery facilities exercising market power or strategically responding to opponents' storage behavior exists  (Lampa & Samano, 2022).
- Endogeneity of Battery Siting/Entry: While the authors assume the timing of battery entry is exogenous for their price spread analysis, they acknowledge that a linear regression of wholesale prices on battery output could suffer from endogeneity if individual storage units are large enough to impact market equilibrium  (Lampa & Samano, 2022). However, they address this by using a "difference" framework and confirming that coefficients for weeks leading up to entry are not statistically significant .
- Concurrent Policy Changes: The paper does not explicitly detail concurrent policy changes as a threat to identification in the provided snippets, but it does acknowledge that the market context, including policies, affects battery deployment and profitability, suggesting these external factors could influence outcomes beyond the scope of their direct model  (Lampa & Samano, 2022).
In summary, the study provides empirical insights into how large-scale battery storage interacts with electricity markets in California. While it reveals that batteries do respond to price signals, their actual operation falls short of an idealized optimal arbitrage strategy, indicating complexities and non-arbitrage roles. The analysis also suggests that increased battery capacity can compress price spreads, though profitability under current market conditions appears limited.

## 原典精読（2026-09-29）
- 書誌: Stefan Lamp and Mario Samano (2022). Large-scale battery storage, short-term market outcomes, and arbitrage. *Energy Economics* 107, 105786. DOI 10.1016/j.eneco.2021.105786（JEL Q41, Q42, Q48, Q55）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読）。上記 SciSpace ログの要約は概ね正確だが、数値は以下を正とする。

### 1. 問いと貢献
- 3つの問い（§1）: (i) 蓄電池は負荷が高いときに多く放電するか、(ii) 最適裁定モデルと整合的に安値で充電し高値で売るか、(iii) 新規蓄電容量の参入は卸価格に影響するか。
- 貢献: 「文献で広く仮定される蓄電池の裁定行動に対する**最初の実証的証拠**」（§6）。CAISO のフリート集計出力を、2019年時点の中央値規模の蓄電池（7.2 MWh）の価格テイカー最適解と比較し、価格スプレッドへの参入効果をイベントスタディ型の回帰で推定。

### 2. データ・市場・期間
- CAISO/OASIS: 負荷・蓄電池出力・再エネは5分値、DAM/RTM 価格は時間値。行動分析は 2018-06-06〜2020-03-01（COVID 前）、スプレッド分析は 2013-01〜2017-05（DOE-GESD の商用運転日で参入日を特定）。VRE シェア約23%。最大の蓄電池は約30 MW。往復効率 66% を価値計算に仮定（Sioshansi et al. 2009 は 0.8）。

### 3. モデル・手法
- 最適裁定: 完全予見・価格テイカーの LP（状態 S_t = S_{t−1} + ηE^c − E^d、出力上限 P_max、容量上限）。7.2 MWh の代表的蓄電池。
- 分位点別の放電応答（Fig.2–4, 6）: 負荷・価格・再エネ出力の分位点ごとの正規化放電量。
- 限界価格応答（式(2), Fig.8）: 時間帯別の価格係数 β_h（月・曜日・時間固定効果で制御）。
- スプレッド回帰（§5.1）: log y_t = β₀ + Σ_{j=−4..12} β_j·capacity_{t−j} + α′X_t + γ_τ + ε_t、週次集計、y は日次 RTM の最大・平均スプレッドまたは最大価格、X は再エネ・大規模水力・負荷、γ は月・年内週固定効果、標準誤差は月クラスタ。参入時期の外生性は事前4週の係数がゼロで確認。

### 4. 主要結果（数値）
- 放電は高負荷・高価格と関連。日内パターンは朝（3–6時）と夕方ピーク（17–19時）に一致。最適モデルは DAM で 3–4時・17–19時に容量制約で価格応答ゼロ、RTM では全時間で正。最大応答は 9時で価格 +1 $/MWh あたり平均絶対出力の約3%（DAM）／4%（RTM）。
- 観測フリートは DAM で 5–6時と 17時のみ、RTM で 12・15・16時のみ有意な正の価格応答 → 「batteries are less flexibly employed than would be foreseen by an optimal arbitrageur」。昼間は周波数制御等の別用途と解釈。
- **Fig.9（スプレッド圧縮）**: 新規容量参入後の数週間、RTM の最大・平均スプレッドと最大価格に負で有意（90%）な効果、**5週間後に有意性が消える**（点推定は負のまま）。係数は 1 MWh あたり 100×β_j パーセントポイント（本文に数値表なし、図のみ）。
- **Table 1（私的価値、$ per MWh of energy capacity per year、RTM 価格・効率66%）**: 予測時間別出力: 最適化 11,246、データ −9,032。実際の時間別出力: 最適化 34,798、データ −6,192。代表プラント 7.2 MWh・9年・5%割引の生涯利益: 0.656／−0.527／2.031／−0.361 $M。DAM 価格を使うと最適化列は 2.506 $M（8倍超）だが観測出力列は −2.077 $M。→ 「regardless of what the true objective function the fleet may have, even the annual revenue is negative at current prices」。
- 結論: 「without additional policies or other sources of revenue, e.g. from ancillary services, profit maximizing firms would not enter this market」。新規容量はスプレッドを縮小するので中長期の投資魅力をさらに下げる。

### 5. 著者が挙げる限界
- 集計フリートのみ観測、個別プラントのパネルなし。様式化モデルは動学的考慮（劣化、複数市場）を捨象。完全予見。価格テイカー仮定は個別には妥当だが市場支配力の可能性。今後: **容量市場への蓄電池のコミットが卸価格への影響を左右する**（PJM、英国、スペインの例）。

### 6. 本研究との関係（追記）
- 第2章2.2／第7章: 「参入後5週間でスプレッド圧縮効果が消える」は短期の均衡効果の実証であり、本研究の π(K)（フリート規模での恒常的なスプレッド縮小）とは時間軸が異なることを明記。本研究の K→スプレッドのマッピングはシミュレーション（Butters/Zhao 型）で、Lamp & Samano は事後計量。両者の整合（短期の有意効果が薄れるのは、蓄電が他用途に転用されるか、火力の応答か）を議論。
- 第6章（バックテスト）: 観測フリートが最適裁定の一部しか捕捉していない（負の年間収入）事実は、本研究の capture ratio（実行可能戦略で81–83%）が「最適運用」を前提にした上限であり、実際の運用者はさらに下回りうる、という留保の根拠。
- 第8章8.3〜8.4: 「追加政策やアンシラリー収入なしに利潤最大化企業は参入しない」「容量市場へのコミットとの相互作用は今後の課題」は、本研究の二層参入（容量市場を含む政策ウェッジ）の必要性を直接支持。
- 新規性チェック: 既に行われていること＝CAISO の実蓄電池行動と価格スプレッドへの短期効果の計量。本研究が新たに行うこと＝北海道でフリート容量 K に対する π(K) の推計と、容量市場・LTDA・BTM を含む自由参入均衡の定量化（Lamp & Samano が「今後の課題」とした容量市場との相互作用を扱う）。

### 7. 引用に使える原文
1. Abstract: "we provide evidence that battery deployment in the years 2013 through 2017 lowered average intra-day wholesale price spreads and that current market conditions limit the profitability of batteries in this market."
2. §5.1 (p.13): "Fig. 9 shows that for our three different price statistics there is a negative and statistically significant effect (at the 90% level) in the weeks following the addition of new storage capacity in the system. The significance of this effect fades away after five weeks, yet the mean point estimates remain negative."
3. §5.2 (p.14): "Our calculations highlight that under current conditions it is not profitable for battery owners to operate in this market. While the model predicts positive (and sizeable) lifetime profits, these are not met in the empirical data, indicating that without additional policies or other sources of revenue, e.g. from ancillary services, profit maximizing firms would not enter this market."
4. §5.2 (p.14): "the entry of new battery capacity could reduce future profit opportunities in the medium and long-run, making investment less attractive."
5. §6 (p.15): "In the future, the effect of the storage output on wholesale equilibrium prices will also be related to how much storage gets committed to the capacity market needs, provided it exists."
