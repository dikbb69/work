# Wozabal, Graf & Hirschmann (2016) OR Spectrum 38 — U字型の理論モデル

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Theoretical Model of Intermittent Renewables and Price Variance

This section explains the theoretical model generating a non-monotonic relationship between intermittent renewable capacity and price variance, the penetration levels at which variance changes, the empirical methodology, and the underlying assumptions.

### Theoretical Model and Merit Order Convexity

The theoretical model predicts a non-monotonic (U-shaped) relationship between intermittent renewable capacity and price variance. This relationship is primarily driven by two factors: the curvature of the supply function (merit order) and the distribution of the random intermittent electricity sources (IES) supply  (Wozabal et al., 2015).
- Inverse S-shaped Supply Function: The model incorporates an "inverse S-shaped" supply curve, which better fits the merit order curve on the German spot market than a purely convex function  (Wozabal et al., 2015). This shape arises because inflexible, slow base-load producers may accept producing at a loss rather than switching off, leading to very low or even negative prices during times of low demand and high intermittent infeed .
- Impact of Residual Demand Shift: When IES infeed increases, it effectively shifts the residual demand (total demand minus IES infeed) to the left  (Wozabal et al., 2015).
- If this shift moves the residual demand into a flatter part of the supply curve, and the shape of the residual demand distribution remains unchanged, the variance of prices decreases  (Wozabal et al., 2015).
- However, if the increased IES share also broadens the distribution of residual demand, the variance could increase, even if the residual demand is pushed into a flat area  (Wozabal et al., 2015).
- When the demand is shifted into the concave part of an inverse S-shaped supply function, the variance tends to increase due to the steeper slope in that region  (Wozabal et al., 2015). This results in a U-shaped dependence of variance on the residual demand, being high for very high and very low demand, and smaller in the middle section .

### Penetration Levels and Variance Changes

The model predicts that the overall effect of IES infeed depends on the produced amount, leading to a non-monotonic relationship between IES capacity and price variance  (Wozabal et al., 2015).
- Variance Decrease (Small to Moderate Quantities): "small to moderate quantities of IES tend to decrease the price variance"  (Wozabal et al., 2015). This initial decrease occurs because the IES infeed shifts the residual demand into a flatter part of the supply curve, reducing price fluctuations .
- Variance Increase (Large Quantities): "large quantities have the opposite effect"  (Wozabal et al., 2015), meaning they tend to increase price variance. This happens when the residual demand is pushed into the steeper, concave part of the inverse S-shaped supply function, or if the IES infeed significantly broadens the distribution of residual demand  . Empirically, the paper notes that in the early years of their analysis, IES infeed had a variance-dampening effect, but in later years with increased capacity, IES increased variance on many days .

### Data and Estimation Approach

For the empirical part, the study uses data from Germany covering the period from 2007 to 2013  (Wozabal et al., 2015).
- Data Sources: Hourly day-ahead spot prices for Germany/Austria are obtained from EPEX  (Wozabal et al., 2015). Hourly day-ahead wind and photovoltaic (PV) forecasts for Germany/Austria are provided by Transmission System Operators (TSOs) . Hourly load data for Germany/Austria comes from ENTSO-E . Other variables include daily temperature, oil prices, and daylight minutes .
- Dependent Variable: The dependent variable is daily price variance, calculated from 24 hourly observations per day  (Wozabal et al., 2015). The variance is chosen over other measures due to its theoretical properties, despite its sensitivity to outliers .
- Estimation Approach: Ordinary Least Squares (OLS) regression models are used to explain daily spot price variance  (Wozabal et al., 2015). The models incorporate residual demand, demand, and IES infeed (wind and PV) as explanatory variables, along with other control factors  . The regressions use heteroskedasticity and autocorrelation robust standard errors due to the rejection of i.i.d. residuals .

### Assumptions About Demand and Supply Curves

The theoretical model's results are driven by specific assumptions about demand and supply curves:
- Inelastic Demand: The model assumes an inelastic, random aggregate demand for electricity (Q)  (Wozabal et al., 2015).
- Competitive Market and Supply Curve: It assumes a competitive market with a convex market supply curve (S), which equals the aggregate industry cost function  (Wozabal et al., 2015). The market price is obtained by intersecting the inelastic demand with the supply curve, implying no player exercises market power .
- IES Infeed as Residual Demand Reduction: Intermittent production (I) is modeled by subtracting it from the demand, resulting in "residual demand" (Q – I) that conventional plants must cover  (Wozabal et al., 2015). This assumes IES production is always fed-in regardless of price, as intermittent sources typically have near-zero marginal costs and are often subsidized with feed-in tariffs .
What would break these assumptions?
- Flexible IES Response: If IES providers had incentives to switch off production when prices fall below zero, their infeed would depend on market prices, complicating the model's assumption of price-independent IES supply  (Wozabal et al., 2015).
- Market Power: If players could exercise market power, the market price would not solely be determined by the intersection of inelastic demand and the competitive supply curve  (Wozabal et al., 2015).
- Elastic Demand: If demand were elastic, the price response to changes in supply would differ, altering the impact on variance. The model assumes inelastic demand, which is typical for electricity in the short term.
In essence, the theoretical framework highlights that the interplay between the shape of the supply curve and the characteristics of intermittent renewable generation determines the complex, non-linear effect on price variance. The empirical analysis in Germany supports these theoretical predictions, demonstrating the U-shaped relationship in practice.
