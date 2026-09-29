# Sakaguchi & Fujii (2021) Frontiers in Sustainability — 日本のMOE（北海道含む）

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Merit-Order Effects of Wind and Solar PV in Japan

This study investigates the Merit-Order Effect (MOE) of wind and solar photovoltaics (PV) on wholesale electricity prices in Japan, analyzing regional variations, temporal changes, and impacts across different price ranges.

### Estimated Merit-Order Effects (MOE) by Region and Technology

The study quantifies the MOE as the reduction in electricity price for each 1 GWh of additional variable renewable energy (VRE) generation per hour  (Sakaguchi & Fujii, 2021). The results from the Ordinary Least Squares (OLS) regression analysis, broken down by region and year, show significant variations:
- Hokkaido: This region consistently shows the largest MOE for both wind and PV. For wind, the MOE in Hokkaido was -4.825 yen/kWh (all years average), with specific annual values of -4.269 yen/kWh in 2016, -3.109 yen/kWh in 2017, -3.598 yen/kWh in 2018, and -7.019 yen/kWh in 2019  (Sakaguchi & Fujii, 2021). For PV, Hokkaido's MOE averaged -1.846 yen/kWh (all years), with annual values of -1.810 yen/kWh in 2016, -1.231 yen/kWh in 2017, -2.338 yen/kWh in 2018, and -1.710 yen/kWh in 2019 . These values are notably higher than in other areas .
- Other Regions: The MOEs for wind were generally lower in other regions, with West and Kyushu not showing significant MOEs in 2016 and 2017  (Sakaguchi & Fujii, 2021). However, PV MOEs were significant across all areas and years .

### Changes in Effects Between FY2016 and FY2019

The MOE of wind and PV exhibited distinct trends between fiscal years 2016 and 2019:
- Wind MOE: The MOE of wind generally increased each year during this period  (Sakaguchi & Fujii, 2021). For example, in Hokkaido, it deepened from -4.269 yen/kWh in 2016 to -7.019 yen/kWh in 2019 . This suggests that wind power's price-reducing impact became stronger over time.
- PV MOE: In contrast, the MOE of PV generally decreased from 2016 to 2019  (Sakaguchi & Fujii, 2021). This decline is attributed to the corresponding increase in PV energy generation, as the impact of a single unit of PV generation diminishes with higher overall PV installations .

### Quantile Regression Results on Price Spikes

The quantile regression analysis provides insights into how wind and PV affect different price ranges, particularly high-price quantiles (spikes) and low-price quantiles:
- PV and Price Spikes: PV had a price-reducing effect on high price ranges (spikes) in 2016 and 2017  (Sakaguchi & Fujii, 2021) . Specifically, the MOEs of the 95th quantile for PV decreased from 2016 to 2019, demonstrating its effect on price spikes . However, this effect weakened over time as trade volumes increased . The study also notes sharp drops between the 90th and 95th quantiles in 2016 and 2017 for PV .
- Wind and Price Spikes: The MOEs of wind were not significant in most quantiles in the national analysis  (Sakaguchi & Fujii, 2021), meaning wind generally did not significantly reduce price spikes . However, in Hokkaido, the MOE of wind became larger for the highest quantiles, indicating that wind power can reduce price spikes in that specific region .
- General Trend: For PV, the lower the price range, the larger the MOE, indicating a stronger price-reducing effect at lower prices  (Sakaguchi & Fujii, 2021).

### Data Construction and Sources

The study utilizes publicly available data from the Japan Electric Power Exchange (JEPX) and other sources:
- JEPX Price Data: The independent variable is the JEPX day-ahead spot price. For national analysis, this is the hourly weighted average of JEPX day-ahead spot prices by trade volume. For area analysis, a simple average of 30-minute price periods is used as JEPX only discloses trade volume at the national level  (Sakaguchi & Fujii, 2021) . The system price data covers April 1, 2016, to March 31, 2020 .
- Renewable Output Data: Variables for wind and PV electricity generation are included  (Sakaguchi & Fujii, 2021). These are hourly wind and solar PV electricity generation data . The amount of electricity generation is calculated as the sum of generation from nine areas per hour, reported by respective transmission system operators .
- Control Variables: The models include several control variables: Demand, lagged prices (24 hours prior, 7 days prior, and average of previous day), price volatility (standard deviation of spot prices for the same hour over the past five days), fossil fuel price, and dummy variables for Summer, Winter, Daytime, Holiday, Gross bidding, and Implicit auction  (Sakaguchi & Fujii, 2021) .

### Limitations and Mention of Batteries/Storage

The authors acknowledge several limitations in their study:
- Oligopoly Market: The Japanese electricity market is still an oligopoly, with former general electric utilities monopolizing area markets before liberalization, which could influence JEPX spot prices due to imperfect competition  (Sakaguchi & Fujii, 2021).
- External Factors: The variables used in the study did not fully explain observed price changes, suggesting other factors determine electricity prices  (Sakaguchi & Fujii, 2021).
- Trade Volume and MOE: The price spike reduction effect of PV weakened as the JEPX transaction volume increased, particularly during 2016 and 2017 when trade volume was relatively small  (Sakaguchi & Fujii, 2021).
- Specific MOE Trends: The study was unable to infer the reason for the dramatically larger MOE of wind during daytime hours compared to night-time hours  (Sakaguchi & Fujii, 2021).
- Area Analysis Limitations: The area analysis did not account for the effect of electricity passing through interconnection lines, which can lead to inaccuracies because actual consumption may not equal local generation  (Sakaguchi & Fujii, 2021).
The provided document does not mention batteries or storage in the context of their empirical design, findings, or limitations. The focus is exclusively on the Merit-Order Effect of variable renewable energy sources (wind and solar PV) on wholesale electricity prices.

## 原典精読（2026-09-29）
- 書誌: Frontiers in Sustainability, 2:770045 (12 pp.), doi:10.3389/frsus.2021.770045（受理 2021-11-08、公開 2021-11-30、九州大学）
- 出所: Google Drive 参考研究_20260728/SetC（原文精読 2026-09-29）。上の SciSpace ログの数値は原典と照合済み（Table 3 の北海道値は一致）。

### 1. 問いと貢献（著者の主張する新規性）
- 三つの研究目的（§Background 末尾）: (1) MOE の年次変化（JEPX 取引量拡大に伴う変化）、(2) 価格レンジ別の MOE（分位点回帰で VRE がスパイクを抑えるか）、(3) 四地域（北海道・東・西・九州）別の差。「the first study to the authors' knowledge to investigate the MOE of VRE in Japan considering price ranges」（§Comparison With Previous Research）。
- Maekawa et al. (2018) への批判: 気象代理変数を使い、JEPX 取引比率 10% 未満の時期の分析。本論文は実発電量（各一般送配電事業者公表）を使用。
- 結論: 風力の MOE は PV より数倍大きく年々増加、PV は減少。「wind power has more potential to reduce electricity prices than PV」。

### 2. データ・市場・期間（Table 1）
- 全国分析: システムプライス、2016-04-01〜2020-03-31（FY2016–19）、30分値を約定量で加重平均して時間別に変換、35,064 観測。発電量は9エリアの合計（時間別 GWh）。
- 地域分析: エリア価格（JEPX は約定量を全国分しか開示しないため 30分値2つの単純平均）、2016-04-08〜2020-03-31。四地域は価格相関（Table A1: 北海道–東北 0.801、北海道–東京 0.791、北海道–中部 0.556、北海道–九州 0.521；中部〜中国は 0.997–1.000）で区分。東＝東北・東京、西＝中部・北陸・関西・中国・四国。
- 変数: Demand（時間別総発電量 GWh）、Wind・PV（GWh）、Price_{t−24}、Price_{t−168}、前日24時間平均、Volatility（同時刻・直近5日の SD、Paraschiv et al. 2014 に倣う）、原油 CIF 月次（千円/kL）、Summer（7–9月）、Winter（12–2月）、Daytime（8–22時）、Holiday、Gross bidding（2017-04-01〜）、Implicit auction（2018-10-01〜）。
- 制度記述: 2019 年に市場分断が起きなかったコマは 5% のみ。グロスビディング 2017-04、間接オークション 2018-10。2019 年に JEPX 経由が発電量の 30–40%。

### 3. 手法
- 式(1) OLS: Price_t = α + β1 Wind_t + β2 PV_t + β3 Demand_t + β4 Price_{t−24} + β5 Price_{t−168} + β6 AverageLag_t + β7 Volatility_t + β8 Oil_t + β9 Summer + β10 Winter + β11 Daytime + β12 Holiday + β13 Policy + γ_t。
- 式(2) 分位点回帰: q ∈ {5, 10, 25, …, 95%}（本文は "5, 10, 25..., and 95%" と省略表記）。
- 単位: 係数は「1 GWh/h の VRE 追加当たりの円/kWh 低下」。ADF で定常、DW で正の自己相関 → ラグ項で対処。
- 変動性は Volatility（過去5日の同時刻 SD）を制御変数として入れるのみで、被説明変数としては扱わない。

### 4. 主要結果（数値）
- Table 2（全国 OLS、Model 5）: Wind −0.345***、PV −0.085***、Demand 0.092***、Gross Bidding +1.547***、Implicit Auction −1.111***、R² 0.758。年別（Model 5）: Wind 2016 −0.061（n.s.）、2017 −0.194***、2018 −0.325***、2019 −0.322***；PV 2016 −0.106***、2017 −0.087***、2018 −0.085***、2019 −0.077***。Adj R² は 0.807 → 0.706 と低下（「他要因が強まった」）。
- Figure 4（全国分位点）: 風力は多くの分位で非有意だが有意な分位が年々増加。PV は全分位で有意、95% 分位の効果は 2016 → 2019 で縮小、2016・17 年は 90 → 95% 分位で急落（スパイク抑制は初期のみ）。Figure 5: 2018・19 年の風力 MOE は夜間は不変、日中は「dramatically larger」（理由は不明と明記）。
- Table 3（地域 OLS、円/kWh per GWh/h）:
  | | All | 2016 | 2017 | 2018 | 2019 |
  |---|---|---|---|---|---|
  | Wind 北海道 | −4.825*** | −4.269*** | −3.109*** | −3.598*** | −7.019*** |
  | Wind 東 | −0.760*** | −0.529*** | −0.324*** | −0.699*** | −0.677*** |
  | Wind 西 | −0.337*** | −0.00623 | 0.0549 | −0.586*** | −0.672*** |
  | Wind 九州 | 0.270* | 2.022*** | 1.558*** | −1.707*** | −0.651** |
  | PV 北海道 | −1.846*** | −1.810*** | −1.231*** | −2.338*** | −1.710*** |
  | PV 東 | −0.212*** | −0.296*** | −0.139*** | −0.220*** | −0.225*** |
  | PV 西 | −0.211*** | −0.238*** | −0.260*** | −0.187*** | −0.201*** |
  | PV 九州 | −0.498*** | −0.414*** | −0.537*** | −0.433*** | −0.589*** |
- 北海道の分位点結果（Figure 6）は**グラフのみで係数表はない**。本文の記述: 「The MOE of wind became larger for the highest quantiles only in Hokkaido which means wind power can reduce price spikes」「Since Hokkaido has the largest share of electricity generation from wind in the four areas, the MOE for wind power was significant in all quantiles analyzed」。九州の最低分位で PV の MOE が急増するのは 0.01 円/kWh の下限と出力抑制のため。→ 本研究で「τ=0.9 の北海道風力 MOE = −11.2 円/kWh/GW（FY2016–19）」と書く際は「本研究による再推定値」であり、原典は図のみであることを明記する必要がある。
- Table 4（2019 年）: 北海道 平均 10.7 円/kWh、15 円超の比率 9.7%、風力シェア 3.7%、PV 6.5%；東 9.1／2.9%／1.1%／6.5%；西 7.2／0.9%／0.5%／7.3%；九州 6.8／0.9%／0.8%／12.4%。
- Table 5（国際比較、1 GWh 当たり）: 本研究 日本 FY2016–19 風力 2.77 €/MWh、PV 0.68 €/MWh；ドイツ Cludius et al. 0.94–2.27／0.84–1.14；Keeley et al. 0.88／0.93。日本だけ風力 ≫ PV。

### 5. 著者が挙げる限界・今後の課題
- 地域分析は連系線を通じた電力の出入りを考慮しない（発電地と消費地の不一致による誤差）。
- 日中の風力 MOE 拡大の理由は不明（今後の課題）。
- 寡占構造（旧一電）の影響、説明変数が価格変動を十分説明しない（Adj R² 低下）。
- 2020-12〜2021-01 の高騰期は外生要因が多く同列に扱えないため除外、今後の課題。

### 6. 本研究との関係（精読後の更新）
- 引用予定箇所: 第2章2.3（手法の直接の源流：式(2) の分位点回帰と制御変数群をそのまま北海道 FY2016–19 で再現し、FY2023–25 に延長）、第3章（グロスビディング +1.547、間接オークション −1.111 の制度ダミー効果；2019 年の分断率 95%）、第4章（北海道 OLS −4.825 → −7.019 の増加トレンドと、本研究の連系線拡張後の減衰 −4〜−7 の対比）。
- 支持する点: 北海道の風力 MOE が高分位で大きい（右裾に効く）＝本研究の τ=0.9 の推定と方向一致。風力 ≫ PV という日本固有の順序。
- 対立点／注意: (a) 原典の分位点係数は図のみで、数値は本研究の再推定に依存する。(b) 原典は「連系線を考慮しない」と明記しており、本研究の「連系線拡張で MOE が減衰」はこの限界を埋める拡張。(c) 原典の Volatility は制御変数で、日内スプレッド（TB4h）は扱わない。(d) 原典は 30分→1時間に集約、本研究は 30 分値のまま扱える。
- 新規性チェック: 既に行っていること＝FY2016–19 の全国・四地域の OLS/分位点 MOE。本研究が新たに行うこと＝北海道単独で FY2023–25 まで延長し、時間変化（連系線・LNG 期）を分位点別に追い、日内スプレッド（TB4h）を被説明変数に加え、蓄電池の自由参入均衡に接続する。

### 7. 引用に使える原文
1. "Overall, the key finding of our study is that wind power has more potential to reduce electricity prices than PV."（Abstract, p.1）
2. "The MOE of wind became larger for the highest quantiles only in Hokkaido which means wind power can reduce price spikes."（Area Analysis (Quantile Regression), p.6）
3. "Since Hokkaido has the largest share of electricity generation from wind in the four areas, the MOE for wind power was significant in all quantiles analyzed."（Discussion Area Analysis, p.7）
4. "It should be noted that the area analysis did not take into account the effect of electricity passing through interconnection lines, which are used to trade electricity with other areas."（Discussion Area Analysis, p.6）
5. "we compared how much the price of electricity was reduced for each 1 GWh of additional VRE (wind and PV) generation per hour."（Comparison With Previous Research, p.8）
6. "Although we use weighted average prices in our national analysis, a simple average of each pair of 30-min price periods is employed in our area analysis because the JEPX discloses trade volume only at the national level."（Data, Area Analysis, p.4）
