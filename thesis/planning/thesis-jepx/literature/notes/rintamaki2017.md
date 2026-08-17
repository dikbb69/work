# Rintamäki, Siddiqui & Salo (2017) Energy Economics 62 — RV構築と時間スケール分解

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Volatility of Electricity Prices and Renewable Energy Integration

This section details the calculation of daily and weekly realized volatility, the model used to relate wind/solar to volatility, the differing impacts of wind in Denmark and Germany, solar results for Germany, and market features influencing the effect of renewables on volatility.

### Daily and Weekly Realized Volatility Formulas

The paper defines daily and weekly realized volatility from hourly electricity prices using the following formulas:
- Daily Volatility (VdV_dVd​): This is the logarithm of the standard deviation calculated from hourly prices (php_hph​) and the average daily price (pdp_dpd​).
Vd=ln⁡(124∑h=124(ph−pd)2)V_d = \ln\left(\frac{1}{24} \sum_{h=1}^{24} (p_h - p_d)^2\right)Vd​=ln(241​∑h=124​(ph​−pd​)2)  (Rintamäki et al., 2017)
- Weekly Volatility (VwV_wVw​): This is computed from daily average prices (pdp_dpd​) and the weekly average price (pwp_wpw​).
Vw=ln⁡(17∑d=17(pd−pw)2)V_w = \ln\left(\frac{1}{7} \sum_{d=1}^{7} (p_d - p_w)^2\right)Vw​=ln(71​∑d=17​(pd​−pw​)2)  (Rintamäki et al., 2017)

### Model for Relating Wind/Solar to Volatility

To estimate the effect of exogenous variables like wind and solar power on electricity price volatility, the study employs a seasonally adjusted autoregressive moving average (SARMA) model with exogenous variables (SARMAX or distributed lag model)  (Rintamäki et al., 2017). The general specification for the daily volatility model, which includes exogenous variables (xtx_txt​), is:
Vd=C0+∑i=1lαiVd−i+∑i=1mβiϵd−i+∑j=1Pαj,sVd−j⋅s+∑j=1Qβj,sϵd−j⋅s+ϵd+γxtV_d = C_0 + \sum_{i=1}^{l} \alpha_i V_{d-i} + \sum_{i=1}^{m} \beta_i \epsilon_{d-i} + \sum_{j=1}^{P} \alpha_{j,s} V_{d-j\cdot s} + \sum_{j=1}^{Q} \beta_{j,s} \epsilon_{d-j\cdot s} + \epsilon_d + \gamma x_tVd​=C0​+∑i=1l​αi​Vd−i​+∑i=1m​βi​ϵd−i​+∑j=1P​αj,s​Vd−j⋅s​+∑j=1Q​βj,s​ϵd−j⋅s​+ϵd​+γxt​  (Rintamäki et al., 2017)
Specifically, for the daily volatility analysis, the model used is a SARMA(2,1)(2,1)[7] model, which includes AR(1) and AR(2) terms for short-term price volatility, and SAR(1) and SAR(2) terms for weekly seasonality. Exogenous variables are added to the right-hand side of this model  (Rintamäki et al., 2017).

### Differing Impact of Wind in Denmark and Germany

Wind power decreases daily volatility in Denmark but increases it in Germany. The authors propose the following mechanisms:
- Denmark: Wind power output is roughly evenly distributed throughout the day, and Denmark has high transmission capacity to Nordic countries with large hydropower reservoirs. This allows both peak and off-peak hour prices to decrease nearly equally due to wind power generation, leading to a reduction in daily price volatility  (Rintamäki et al., 2017). The paper states: "wind power output decreases daily price volatility in Denmark because wind speeds are roughly evenly distributed throughout the day."
- Germany: Wind power output is greater during off-peak hours, and Germany has smaller cross-border transmission lines relative to its average electricity demand, with limited access to flexible hydro generation. This leads to prices diverging, with the price-decreasing impact of wind power amplified during off-peak hours, increasing price volatility  (Rintamäki et al., 2017). The paper notes: "In Germany, however, there is an increase in price volatility because of greater wind power output during off-peak hours."

### Solar Results for Germany by Time Scale

For Germany, solar power generally has a volatility-reducing effect:
- Daily Volatility: An increase of 1% in the first difference of daily solar power production (Δsolard\Delta solar_dΔsolard​) decreases the daily volatility of German prices by 0.04%  (Rintamäki et al., 2017). This indicates that a higher absolute level of solar power leads to lower daily price volatility . Solar power's price-decreasing impact is stable during peak hours, making it likely that solar power decreases price volatility .
- Weekly Volatility: The impact of the first difference in weekly average solar power (Δsolarw\Delta solar_wΔsolarw​) and its penetration (Δsolar_penw\Delta solar\_pen_wΔsolar_penw​) is inconclusive, as the coefficients are statistically insignificant. However, the effect is likely negative  (Rintamäki et al., 2017). The paper also states that "the average weekly solar power is not found to contribute to the weekly price volatility, which can be explained by the peak-price-decreasing impact of solar power in Germany."

### Market Features Determining the Sign of the Effect

The authors highlight several market features that determine whether renewable energy generation increases or decreases price volatility:
- Access to flexible generation capacity: "access to flexible generation capacity"  (Rintamäki et al., 2017) is crucial. This includes "large hydropower reservoirs"  . Denmark's access to these reservoirs contributes to its reduction in daily price volatility .
- Transmission capacity and interconnection: "adequate transmission capacity"  (Rintamäki et al., 2017) and "integration of adjacent markets"  are vital. Germany's "cross-border transmission lines are smaller relative to its average electricity demand" , which contributes to increased volatility.
- Market size and demand patterns: The "size of its power system"  (Rintamäki et al., 2017) and "wind power generation patterns"  also play a role. For instance, the differing impacts in Denmark and Germany are partly due to "the patterns of wind and solar power production as well as cross-border exchanges."
In conclusion, the study provides a detailed econometric analysis of how wind and solar power affect electricity price volatility. It highlights the importance of market design, including flexible generation, transmission capacity, and market integration, in mitigating the volatility challenges posed by intermittent renewable energy sources. The GARCH model framework effectively quantifies these complex relationships, showing that while renewables generally reduce price levels, their impact on volatility is nuanced and depends heavily on specific market characteristics.
