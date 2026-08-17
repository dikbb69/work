# Fanone, Gamba & Prokopczuk (2013) Energy Economics 35 — 負値価格モデルと0.01円床への読み替え

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Modeling Negative Day-Ahead Electricity Prices


### Stochastic Process and Distribution for Negative Day-Ahead Prices

Negative day-ahead electricity prices are modeled using an arithmetic Lévy-based fractional autoregressive (FAR) model. This model is designed to capture the unique characteristics of electricity prices, including seasonality, mean reversion, long memory, excess kurtosis, and crucially, both positive and negative price spikes  (Fanone et al., 2011)  . The model is expressed in a discrete-time setting for risk management applications .
- Model Structure: The hourly electricity spot price, E(t), is described as the sum of two parts: a deterministic component, s(t), and an adjusted spot price, S(t)  (Fanone et al., 2011). The adjusted spot price S(t) follows a first-order fractional autoregressive (FAR(1)) process .
The model equation is:
S(t) = µs(t-1) + (1−L)⁻ᵈ(ΔL(t) + ΔJ(t)) 
Where:
- L is the lag operator  (Fanone et al., 2011).
- d is the fractional integration parameter, describing multiscale autocorrelation, with 0 < d < 0.5  (Fanone et al., 2011).
- ΔL(t) = L(t) - L(t-1) and ΔJ(t) = J(t) - J(t-1) are discrete-time increments of two independent Lévy processes  (Fanone et al., 2011).
- Lévy Components: The Lévy process L(t) describes fluctuations around the long-term price level s(t), and its marginal distributions are modeled using Generalized Hyperbolic (GH) distributions, which are flexible enough to capture skewness and heavy tails  (Fanone et al., 2011) . The GH density is given by a specific formula involving Bessel functions . The second Lévy process, J(t), captures positive and negative price spikes and is modeled as the sum of two homogeneous compound Poisson (CP) processes, J⁺(t) and J⁻(t)  .
- J(t) = J⁺(t) + J⁻(t)  (Fanone et al., 2011)
- J⁺(t) and J⁻(t) are sequences of independent and identically distributed random variables, with cumulative jump sizes defined by Poisson processes with intensities φ⁺ and φ⁻ respectively  (Fanone et al., 2011). The jump sizes (Ψ) are modeled using Generalized Pareto Distribution (GPD) variables .

### Model Estimation and Key Parameter Estimates

The model is estimated through a multi-step calibration procedure to market data  (Fanone et al., 2011).
- De-meaning the data: The time series is made mean-stationary  (Fanone et al., 2011).
- Identifying positive and negative extreme price spikes: The Peak Over Threshold (POT) method is used, fitting a Generalized Pareto Distribution (GPD) to exceedances over a threshold  (Fanone et al., 2011) .
- Key GPD parameters for the right tail (positive spikes): threshold u+ = 54.21 €/MWh, shape parameter ξ = 0.4154, and scale parameter ψ = 18.1907  (Fanone et al., 2011).
- Key GPD parameters for the left tail (negative spikes): threshold u- = -37.99 €/MWh, shape parameter ξ = 0.4312, and scale parameter ψ = 8.5517  (Fanone et al., 2011).
- De-seasonalizing the data: A non-parametric approach using a simple clustering mean week method is employed to identify and filter out the hourly seasonal component  (Fanone et al., 2011) .
- Estimation of mean reversion and long memory parameters: The fractional autoregressive (FAR(1)) process is fitted to the de-spiked and de-seasonalized data. This step estimates the d parameter for long memory and μ for mean reversion  (Fanone et al., 2011).
- Key FAR parameter estimates: d = 0.4690 and μ = 0.0899  (Fanone et al., 2011).
- Estimation of GH parameters: The residuals, which are non-Gaussian and exhibit fat tails, are modeled using Generalized Hyperbolic (GH) distributions. Specifically, the Normal Inverse Gaussian (NIG) distribution is found to be a better fit than the Hyperbolic (HYP) distribution  (Fanone et al., 2011) .
- Key NIG parameters: λ = -0.5, α = 0.1815, β = 0.0059, δ = 2.7549  (Fanone et al., 2011).

### Application to a Market with a Price Floor at 0.01 Yen/kWh

For a market with a price floor at 0.01 yen/kWh instead of negative prices, the core elements of this modeling approach that would transfer include the handling of seasonality, mean reversion, long memory, and positive spikes. The primary change would be in how negative prices are treated, shifting from modeling them as actual values to treating the price floor as a censoring or truncation point.
- Elements that transfer: The methodology for de-meaning, de-seasonalizing, and estimating the FAR component for general price dynamics (mean reversion, long memory) would largely remain applicable. The modeling of positive spikes using GPD would also transfer directly, as these are still relevant for capturing upward extreme price movements  (Fanone et al., 2011)  . The use of Lévy processes to capture jump dynamics (positive spikes) would still be valid .
- What would need to change: The explicit modeling of negative price spikes and the GH distribution for the L(t) component would need adjustment. Instead of allowing prices to go negative and modeling their distribution, the model would need to incorporate the price floor as a hard boundary.
- Censoring/Truncation: The most significant change would be to treat any simulated price path that falls below 0.01 yen/kWh as being censored or truncated at that floor. This means the J⁻(t) component, which specifically models negative spikes, would need to be reinterpreted or modified. Instead of generating actual negative price values, it would contribute to the probability of hitting or staying at the price floor. The model might need to incorporate a mechanism that reflects the accumulation of
