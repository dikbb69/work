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
