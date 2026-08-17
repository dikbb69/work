# Ketterer (2014) Energy Economics 44 — GARCH-X仕様の詳細

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Wind Power Impact on German Electricity Prices and GARCH Model Details

This response details the GARCH model specification used to analyze the impact of wind power generation on German electricity prices, how wind generation is measured, the estimated coefficients, the effect of the 2010 market design change, and the data cleaning steps applied.

### GARCH Model Specification

The paper utilizes an ARX-GARCHX model to investigate the influence of intermittent renewable electricity generation on the electricity price level and volatility in Germany. The model's mean and variance equations, incorporating wind generation (Wt−jW_{t-j}Wt−j​), are specified as follows:
- Mean Equation:Yt=μ+∑i=1lϕiϵt−i+∑j=1mθjWt−j+ϵtY_t = \mu + \sum_{i=1}^{l} \phi_i \epsilon_{t-i} + \sum_{j=1}^{m} \theta_j W_{t-j} + \epsilon_tYt​=μ+∑i=1l​ϕi​ϵt−i​+∑j=1m​θj​Wt−j​+ϵt​  (Ketterer, 2014)
- Variance Equation:ht=ω+∑i=1pαiϵt−i2+∑j=1qβjht−j+∑k=1sγkWt−kh_t = \omega + \sum_{i=1}^{p} \alpha_i \epsilon_{t-i}^2 + \sum_{j=1}^{q} \beta_j h_{t-j} + \sum_{k=1}^{s} \gamma_k W_{t-k}ht​=ω+∑i=1p​αi​ϵt−i2​+∑j=1q​βj​ht−j​+∑k=1s​γk​Wt−k​  (Ketterer, 2014)
In these equations, YtY_tYt​ represents the logarithmic electricity price, hth_tht​ is its conditional variance, ϵt=htZt\epsilon_t = \sqrt{h_t}Z_tϵt​=ht​​Zt​ with Zt∼NID(0,1)Z_t \sim NID(0,1)Zt​∼NID(0,1), and ω\omegaω is the long-run variance. For the model to be stationary, αi+βj<1\alpha_i + \beta_j < 1αi​+βj​<1 and αi,βj>0\alpha_i, \beta_j > 0αi​,βj​>0 are required  (Ketterer, 2014) .

### Measurement of Wind Generation

Wind generation is measured using daily levels of German wind power generation, estimated in megawatt hours (MWh) per day  (Ketterer, 2014). To align with the day-ahead horizon of the dependent variable (electricity price), the study uses predictions for daily wind power generation . These short-term forecasts are provided by the four German transmission system operators (TSOs) and are considered accurate, reflecting the information available to day-ahead market participants . The TSOs sell the predicted amount of renewable electricity on the day-ahead market, typically as price-independent bids to ensure they are sold .

### Estimated Coefficients on Wind

The paper presents results from various GARCH(1,1) model specifications. For the specification (B) where logarithms of wind and load are included:
- Mean Equation (Log(wind)): The coefficient for log(wind) is -0.098, which is highly significant (p-value <0.0001)  (Ketterer, 2014). This indicates that when the wind electricity feed-in (MWh per day) increases by 1%, the price decreases by 0.1% .
- Variance Equation (Log(wind)): The coefficient for log(wind) is 0.002, with a significance level of (0.0470)  (Ketterer, 2014). This positive and significant coefficient indicates that fluctuating wind feed-in increases the volatility of the electricity price .
In specification (C), where the wind variable reflects the share of wind relative to the total electricity load, the coefficient for this wind penetration measure in the mean equation is -1.489 (p-value <0.0001), and in the variance equation, it is 0.020 (p-value 0.0631)  (Ketterer, 2014).

### Impact of the 2010 Market Design Change on Volatility

The study finds that the 2010 market design change, which amended the rules for marketing renewable electricity in Germany, had a significant impact on price volatility. Specifically, the paper states:
'The negative and significant coefficient for the dummy variable indicates a reduction of the conditional variance after the regulatory change.'  (Ketterer, 2014)
This means that the volatility of the German electricity price decreased after the regulatory change  (Ketterer, 2014). The new regulation aimed to reduce forecasting uncertainty and interventions in spot markets, which led to a substantial reduction in balancing costs .

### Data Cleaning Steps

The following data cleaning steps were applied to the electricity price series:
- Outlier Detection and Replacement: Values exceeding three times the standard deviation of the original price series were detected  (Ketterer, 2014). These outliers were then replaced with the value of three times the standard deviation for the respective weekday . This process was repeated once, but no additional outliers were found .
- Seasonality Removal: After smoothing outliers, the seasonal cycle was removed from the time series  (Ketterer, 2014). Weekly and yearly seasonalities were addressed by using constant step functions, which consist of dummies for each seasonal cycle . The coefficients for weekday dummies indicate that the price remains high at the beginning of the week, declines from Friday onward, and reaches its minimum on Sundays .
- Logarithmic Transformation: Finally, the logarithmic electricity price was calculated and used in the subsequent analysis  (Ketterer, 2014).
In summary, the GARCH model effectively captures the dual impact of wind power on German electricity prices, reducing the price level but increasing its volatility. The 2010 regulatory changes successfully reduced price volatility, highlighting the importance of market design in integrating renewable energy. Data cleaning involved outlier replacement and comprehensive seasonality removal to ensure robust analysis.
