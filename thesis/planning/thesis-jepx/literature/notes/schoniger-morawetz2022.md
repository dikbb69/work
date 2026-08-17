# Schöniger & Morawetz (2022) Energy Economics — U字型の実証

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## U-shaped Relationship Between Intermittent Renewables and Price Variance

The study investigates the non-monotonic, U-shaped relationship between the share of variable renewable electricity production and electricity spot price variance, along with the roles of interconnection and flexible generation.

### Regression Specification and Testing of the U-shaped Relationship

The U-shaped relationship between intermittent renewable capacity and price variance is specified and tested by modeling the shape of the supply function using a linear and a squared term of the daily mean residual load. This allows for a U-shaped relationship between residual load and price variance to be captured  (Schöniger & Morawetz, 2022). The model used to analyze the impact of wind and solar generation on price variance is the "Wind & Solar Model" . Its specification is:
Var(Price)it=α+Witβ′+Kitγ′+θt+pt+Ciδ′+UitVar(Price)_{it} = \alpha + W_{it} \beta' + K_{it} \gamma' + \theta_t + p_t + C_i \delta' + U_{it}Var(Price)it​=α+Wit​β′+Kit​γ′+θt​+pt​+Ci​δ′+Uit​  (Schöniger & Morawetz, 2022)
Where:
- Var(Price)itVar(Price)_{it}Var(Price)it​ is the daily price variance for country iii at day ttt.
- WitW_{it}Wit​ is an N×12N \times 12N×12 matrix containing variables such as load, load squared, wind, wind squared, solar, solar squared, variance of load, variance of intermittent renewable electricity (IRE), covariance between IRE and load, and interaction terms like 'Load * wind', 'Load * Solar', and 'Wind * Solar'  (Schöniger & Morawetz, 2022).
- β′\beta'β′ represents the respective coefficients  (Schöniger & Morawetz, 2022).
- KitK_{it}Kit​ is a matrix for control variables (e.g., natural gas price)  (Schöniger & Morawetz, 2022).
- θt\theta_tθt​ and ptp_tpt​ are matrices for day-fixed and month-fixed effects, respectively  (Schöniger & Morawetz, 2022).
- Ciδ′C_i \delta'Ci​δ′ accounts for time-constant variables  (Schöniger & Morawetz, 2022).
- UitU_{it}Uit​ is the error term  (Schöniger & Morawetz, 2022).
This model is based on an earlier specification, the Basic Model, which uses Residual Load and Residual Load² to capture the U-shaped relationship  (Schöniger & Morawetz, 2022) . The model is tested using Ordinary Least Squares (OLS) regression with heteroskedasticity and autocorrelation robust standard errors .

### Countries Confirming U-shape and Minimum Variance Range

The U-shaped relationship, where price variance is higher for low and high average residual loads, is confirmed for the majority of countries analyzed  (Schöniger & Morawetz, 2022) . Specifically, the hypothesis of a convex quadratic influence of the residual load on price variance is supported for Austria/Germany, Denmark, Great Britain (GB), Greece, Italy, Romania, and Sweden .
For these countries, the minimum price variance is found to be between 10% and 40% of the intermittent renewable electricity (IRE) share  (Schöniger & Morawetz, 2022). This implies that in the early stages of IRE deployment, price variance tends to decrease, reaching a minimum in this range, and then increases with higher shares .

### Effect of Exports/Imports and Flexible Generation

Exports/imports (interconnection) and flexible generation significantly affect price variance, often having a greater impact than the variability of renewable output itself  (Schöniger & Morawetz, 2022).
- Interconnection: The study finds that "the better a country is interconnected to its neighboring markets, the lower the effect of IRE infeed on the price variance"  (Schöniger & Morawetz, 2022). This is considered more important than the level and variance of IRE generation itself .
- Flexible Generation: Similarly, the higher the capabilities of flexible power plants (e.g., oil and gas plants, hydro storage), the less distinct the impact of IRE infeed on price variance  (Schöniger & Morawetz, 2022). The authors state that "the availability of flexible power plants and export/import capacities are more important factors for a country's ability to balance IRE infeed than the extent and the variance of the IRE production itself" .

### Policy Conclusion on Flexibility Investment Timing

The authors conclude that policies are needed to secure investments in flexibility options during the period of low price variance, when market-based solutions might fail. They state:
"The findings call for policies to secure investments in flexibility options, such as grid expansion, storage facilities, flexible power plants, and DSM, in the period of low price variance when market-based solutions might fail and eventually lead to situations where grid stability is at risk."  (Schöniger & Morawetz, 2022)
This indicates that early investment in flexibility is crucial, even when current renewable penetration levels might be reducing price variance, to prepare for future increases in variance as renewable shares grow further  (Schöniger & Morawetz, 2022).
