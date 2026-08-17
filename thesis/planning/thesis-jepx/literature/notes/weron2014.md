# Weron (2014) IJF 30 — モデル5類型

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Electricity Price Modeling Approaches and Volatility Analysis

This review categorizes various electricity price forecasting (EPF) models, highlighting their suitability for different applications, particularly in volatility analysis and spike modeling.

### Five Model Classes for Electricity Price Modeling

The paper outlines five main model classes for electricity price forecasting, each with distinct characteristics and applications:
- Multi-agent Models:
- These models simulate the operation of a system with heterogeneous agents (e.g., generating units, companies) interacting to determine price through supply and demand matching  (Weron, 2014).
- Representative Model: Nash-Cournot framework, which treats electricity as a homogeneous good and determines market equilibrium through suppliers' capacity setting decisions  (Weron, 2014).
- Fundamental Models:
- These models describe price dynamics by modeling the impacts of important physical and economic factors on electricity prices  (Weron, 2014).
- Representative Model: Parameter-rich fundamental models, which are often proprietary and focus on factors like hydro inflow, snow, and temperature to explain spot price formation  (Weron, 2014). Kanamura and Ōhashi (2007) proposed a parsimonious structural model using a hockey-stick shaped supply curve .
- Reduced-form Models:
- Finance-inspired quantitative or stochastic models primarily aim to replicate the main characteristics of daily electricity prices, such as marginal distributions and price dynamics, rather than providing accurate hourly forecasts  (Weron, 2014).
- Representative Model: Jump-diffusion models, which incorporate sudden, abrupt changes (jumps) in price dynamics  (Weron, 2014).
- Statistical Models:
- These approaches forecast prices using mathematical combinations of previous prices and/or historical or current values of exogenous factors like consumption and production figures or weather variables  (Weron, 2014).
- Representative Model: AR-type time series models, which express the current price as a linear function of its past values and previous noise  (Weron, 2014).
- Computational Intelligence (AI) Models:
- These models combine elements of learning, evolution, and fuzziness to create adaptive approaches for complex dynamic systems  (Weron, 2014).
- Representative Model: Artificial Neural Networks (ANNs), which can be classified by architecture and learning algorithm and are used for forecasting  (Weron, 2014).

### Model Classes Recommended for Volatility Analysis

For volatility analysis rather than point forecasting, the following model classes are recommended:
- Reduced-form Models: These models are generally not expected to forecast hourly prices accurately but are effective in recovering the main characteristics of electricity spot prices, making them suitable for derivatives pricing and risk analysis  (Weron, 2014). They have been reported to perform reasonably well for volatility or price spike forecasts .
- Fundamental Models: While their primary intention is not always accurate hourly price forecasts, they are used to model the stochastic price dynamics for risk management and derivatives valuation  (Weron, 2014).

### Regime-Switching and Jump-Diffusion Models for Spike Modeling

- Jump-Diffusion Models:
- Mechanism: These models incorporate sudden, large price changes (jumps) in addition to continuous price movements. They are characterized by a mean-reverting process that forces the price back to a normal level after a jump  (Weron, 2014).
- Strengths: They can generate electricity price spikes and fit observed data better than some other models by incorporating the sudden increase in the supply curve slope  (Weron, 2014). They are also used to model the optimal operation policy for pumped-storage hydropower generators .
- Estimation Pitfalls: The empirical data suggests that a homogeneous Poisson process (HPP) might not be the best choice for the jump component, as price spikes are seasonal and typically occur in higher-price seasons  (Weron, 2014). The scarcity of jumps on a daily scale can make it difficult to identify an adequate periodic function . Calibration results can be highly questionable if based on a small number of spike occurrences . A high rate of mean reversion, necessary to force the price back to normal after a jump, can lead to an overestimated value for prices outside the spike regime .
- Regime-Switching Models (MRS):
- Mechanism: These models represent the observed stochastic behavior of a deseasonalized and detrended spot price process by using multiple distinct states or regimes, with transitions between these states governed by a Markov chain  (Weron, 2014). They allow for temporary dependence within regimes and mean reversion .
- Strengths: MRS models allow for consecutive spikes in a natural way, and the return of prices to the 'normal' regime after a spike is straightforward due to temporal changes in model dynamics  (Weron, 2014). They are more versatile than hidden Markov models as they allow for temporary dependence within regimes and mean reversion, a characteristic feature of electricity spot prices .
- Estimation Pitfalls: One major weakness of jump-diffusion models is their inability to exhibit consecutive spikes at the frequency found in market data, a problem that MRS models address  (Weron, 2014). However, MRS models have been reported to perform poorly in forecasting in general .
In summary, while reduced-form and fundamental models are better suited for volatility analysis, jump-diffusion and regime-switching models offer specific mechanisms for capturing price spikes. However, both face challenges related to data characteristics and estimation accuracy, particularly when dealing with the complex, spiky nature of electricity prices.
