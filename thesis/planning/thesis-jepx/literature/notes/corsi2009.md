# Corsi (2009) J. Financial Econometrics — HAR-RV

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Heterogeneous Autoregressive Model of Realized Volatility (HAR-RV)


### HAR-RV Model Specification and Heterogeneous Market Hypothesis

The Heterogeneous Autoregressive model of Realized Volatility (HAR-RV) is an additive cascade model of volatility components, where each component is defined over different time periods. It is inspired by the Heterogeneous Market Hypothesis, which posits that financial markets are composed of participants with varying trading frequencies and time horizons  (Corsi, 2009) .
- Heterogeneous Market Hypothesis: This hypothesis recognizes that different types of market participants (e.g., short-term traders, medium-term investors, long-term agents) perceive, react to, and cause different volatility components  (Corsi, 2009). Short-term traders (daily or higher frequency) are influenced by long-term volatility, which determines expected future trends and risk, causing them to revise trading behavior and generate short-term volatility. Conversely, long-term traders are not significantly affected by short-term volatility . This hierarchical structure leads to a volatility cascade from low to high frequencies .
- Model Specification: The HAR-RV model considers volatilities realized over different interval sizes. It is an AR-type model that, despite its simplicity and not formally being a long-memory model, can reproduce volatility persistence and other stylized facts of financial data  (Corsi, 2009) . The model for daily realized volatility, denoted as RVt+1d(d)RV_{t+1d}^{(d)}RVt+1d(d)​, is specified as:
RVt+1d(d)=c+β(d)RVt(d)+β(w)RVt(w)+β(m)RVt(m)+wt+1d(d)RV_{t+1d}^{(d)} = c + \beta^{(d)} RV_{t}^{(d)} + \beta^{(w)} RV_{t}^{(w)} + \beta^{(m)} RV_{t}^{(m)} + w_{t+1d}^{(d)}RVt+1d(d)​=c+β(d)RVt(d)​+β(w)RVt(w)​+β(m)RVt(m)​+wt+1d(d)​  (Corsi, 2009)
Where:
- RVt(d)RV_{t}^{(d)}RVt(d)​ is the daily realized volatility.
- RVt(w)RV_{t}^{(w)}RVt(w)​ is the weekly realized volatility, calculated as the average of the past five daily realized volatilities  (Corsi, 2009).
- RVt(m)RV_{t}^{(m)}RVt(m)​ is the monthly realized volatility, representing the average of the past 22 daily realized volatilities.
- ccc, β(d)\beta^{(d)}β(d), β(w)\beta^{(w)}β(w), and β(m)\beta^{(m)}β(m) are coefficients.
- wt+1d(d)w_{t+1d}^{(d)}wt+1d(d)​ is the disturbance term  (Corsi, 2009).

### Construction of Realized Volatility from Intraday Data and Sampling Issues

Realized volatility is constructed from intraday data by summing squared returns over a specific time interval  (Corsi, 2009).
- Construction: For a time interval of one day, realized volatility (RVt(d)RV_t^{(d)}RVt(d)​) is defined as the sum of intraday squared returns  (Corsi, 2009):
RVt(d)=∑j=0M−1rt−j⋅Δ2RV_t^{(d)} = \sum_{j=0}^{M-1} r_{t-j\cdot\Delta}^2RVt(d)​=∑j=0M−1​rt−j⋅Δ2​  (Corsi, 2009)
where rt−j⋅Δr_{t-j\cdot\Delta}rt−j⋅Δ​ represents continuously compounded Δ\DeltaΔ-frequency returns sampled at time interval Δ\DeltaΔ, and MMM is the number of intraday periods within the day  (Corsi, 2009). This method approximates the integrated variance, which is the integral of instantaneous variance over the day .
- Sampling Issues: The paper mentions that the definition of aggregated volatility, as used in the HAR model, cannot be exactly interpreted as the realized volatility over the specific time interval due to Jensen's inequality. However, this difference is considered immaterial for empirical applications, as this definition simplifies the interpretation of the HAR model  (Corsi, 2009). The daily realized volatility is then aggregated at weekly and monthly scales by averaging the daily quantities to have comparable measures over different horizons  .

### OLS Estimation and Forecast Performance Comparison

- OLS Estimation Justification: The HAR-RV model can be estimated using Ordinary Least Squares (OLS) because all terms in the model (past realized volatilities at daily, weekly, and monthly horizons) can be considered observed variables  (Corsi, 2009). Standard OLS regression estimators are consistent and normally distributed. To account for potential serial correlation in the data, the Newey–West covariance correction is employed .
- Forecast Performance Comparison: The HAR(3)-RV model demonstrates strong forecasting performance, often outperforming short-memory models and being comparable to more complex long-memory models  (Corsi, 2009).
- Against Short-Memory Models: The HAR(3) model consistently outperforms short-memory models like AR(1) and AR(3) across one-day, one-week, and two-week horizons  (Corsi, 2009) . The superior performance becomes particularly evident at weekly and biweekly horizons, where short-memory models' forecasts converge too quickly to their unconditional mean due to their limited memory .
- Against Long-Memory Models: The HAR(3) model's performance is comparable to the more complicated and tedious-to-estimate ARFIMA (fractionally integrated) model  (Corsi, 2009) . While ARFIMA forecasts are not truly out-of-sample due to the fractional difference coefficient d being estimated on the whole sample, the HAR-RV model achieves similar results with significantly fewer parameters and greater simplicity  .
In essence, the HAR-RV model provides a parsimonious and tractable way to capture the long-memory characteristics of volatility, offering competitive forecasting accuracy compared to more complex models, particularly over longer horizons.
