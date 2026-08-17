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
