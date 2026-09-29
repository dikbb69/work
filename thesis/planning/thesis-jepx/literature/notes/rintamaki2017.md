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

## 原典精読（2026-09-29）
- 書誌: Rintamäki, T., Siddiqui, A.S., Salo, A. (2017). Does renewable energy generation decrease the volatility of electricity prices? An analysis of Denmark and Germany. *Energy Economics* 62, 270–282. DOI 10.1016/j.eneco.2016.12.019
- 出所: Google Drive 参考研究_20260728/SetA/Rintamaki2017_RenewableVolatilityDenmarkGermany.pdf を全文読取。上記 SciSpace ログの $V_d$, $V_w$ の定義は原典と一致。

### 1. 問いと貢献（著者の主張する新規性）
- 問い: VRE（風力・太陽光）は日前価格の**日次**ボラティリティと**週次**ボラティリティを下げるのか上げるのか。デンマーク（DK1, DK2）とドイツで結果が異なるのはなぜか。
- 貢献: (1) 日次ボラティリティ（日内の時間別価格の分散）と週次ボラティリティ（週内の日平均価格の分散）を**分けて**推定。(2) ピーク／オフピークのブロック価格モデルで機構（どの時間帯の価格が下がるか）を特定。(3) 柔軟性（北欧水力への連系）と風力の日内パターンの違いで DK と DE の対照を説明。

### 2. データ・市場・期間
- DK1/DK2: Nord Pool Spot 時間別日前価格、2010年1月1日〜2014年12月31日。DE: EPEX、2012年1月1日〜2014年12月31日（国際潮流の公開データ制約）。
- 説明変数: 風力・太陽光発電（日平均、ピーク時平均、浸透率、日次標準偏差）、負荷、国際連系潮流（DK1–NO2, DK1–SE3, DK2–SE4 等）、ガス価格。

### 3. 手法（被説明変数、変動性の定義、推定式の要点）
- **日次ボラティリティ** $V_d=\ln\left(\frac{1}{24}\sum_{h=1}^{24}(p_h-\bar p_d)^2\right)$ ＝**日内**の時間別価格の分散（対数）。**週次** $V_w=\ln\left(\frac{1}{7}\sum_{d=1}^{7}(\bar p_d-\bar p_w)^2\right)$ ＝日平均価格の週内分散。
- モデル: SARMA(p,q)(P,Q)[s]＋外生変数（分布ラグ）、対数変換で係数は弾力性。
- ブロックモデル: ピーク時平均価格・オフピーク価格を被説明変数として風力の時間帯別効果を推定（Table 5–7）。

### 4. 主要結果（数値を必ず。表番号を付す）
- Table 2–3（DK 日次）: 風力 $wind_d$ 係数 **DK1 −0.0892、DK2 −0.0696**（1%有意）→ 風力1%増で日次ボラティリティ −0.06〜−0.09%。
- Table 4（DE 日次）: 風力 **+0.03%**（model 1）、太陽光（一階差分）**−0.04%**（model 2）、風力＋太陽光の合算 $vre_d$ は非有意（相殺）。
- Table 5–7（ブロック価格）: DK ではピーク時風力1%増でピーク価格 −0.07%（DK1）、−0.06%（DK2）とオフピークとほぼ同率 → 日内プロファイルの**平坦化**。DE では風力はオフピークに強く効き、太陽光1%増でピーク価格 −0.05%。風力浸透率倍増の価格効果は約 −6%（Jónsson et al. 2010 の −10% と整合）。
- Table 8–10（週次）: DK1 週平均風力1%増で週次ボラティリティ **+0.18%**；日平均風力の週内標準偏差（間欠性）1%増で **DK1 +0.37%、DK2 +0.18%**；DE 週平均風力の一階差分1%増で **+0.11%**。週平均太陽光は週次ボラティリティに非有意。
- 機構（Fig. 3, 結論）: DK は風力がピーク時にも出力ピークを持ち、北欧水力への大きな連系容量で柔軟性が高い。DE は風力がオフピークに最大で、連系が系統規模に比べ小さい。

### 5. 著者が挙げる限界・今後の課題
- 単一係数で VRE 効果を表し、市場状況依存・時間変化を捉えない（全期間一括推定）。
- 時系列モデルは価格形成過程を正確に捉えない可能性。
- 今後: GARCH（DK）、非パラメトリック（DE）、実供給曲線データ、他地域（スペイン・アイルランド・カリフォルニア）、イントラデイ市場。

### 6. 本研究との関係
- 引用予定箇所: 第2章2.1（**時間スケール別**の変動性の先行研究として中核）、第3章（帯域分解の動機づけ）、第4章（北海道の結果との対比）。
- 何を言うために引用するか: (i) 「風力は日次（日内）ボラティリティを**下げることも上げることもある**が、週次ボラティリティは**一貫して上げる**」＝本研究の「風力の変動性は 1–7 日帯域に現れ、日内帯域には現れない」の先行的証拠。(ii) 日内への効果の符号は風力の日内出力パターンと柔軟性資源で決まる（DK 平坦化 vs DE 急峻化）。北海道は空間分散した風力と単一エリア価格で DK 型に近いことを示す必要がある。(iii) 太陽光は DE で日次ボラティリティを下げる（ピーク切り下げ）が、これは低浸透期の効果で、高浸透期のダックカーブ（本研究）とは局面が異なる。
- 支持する点: 週次帯域での風力効果、日内帯域での風力効果の小ささ・符号の不定性。
- 対立する点: 太陽光が日内分散を下げるという DE 結果（低浸透期）。本研究は九州・北海道の高浸透期でスプレッド拡大を示す＝U 字の右側。
- 手法の源流: $V_d$（日内分散）は本研究の TB4h スプレッドと同じ対象を測る代替指標。本研究は分散ではなく上位4h−下位4h の差を使い、蓄電池の裁定価値に直結させる。
- 新規性チェック: Rintamäki らは日次・週次の2スケールだが、本研究は日内／1–7日／7日超の3帯域に分解し、さらに蓄電池の参入均衡につなげる点で拡張。

### 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "We find that in Denmark wind power decreases the daily volatility of prices by flattening the hourly price profile, but in Germany it increases the volatility because it has a stronger impact on off-peak prices." (Abstract, p.270)
2. "By contrast, the weekly volatility of prices increases in both areas due to the intermittency of VRE." (Abstract, p.270)
3. "Increasing the daily German wind power, $wind_d$, by 1% increases the daily volatility of German prices by 0.03% as indicated by model 1 in Table 4. The result is in line with Ketterer (2014) whose estimate from a rolling regression ranges from 0% to approximately 0.05%." (Sec. 4)
4. "the standard deviation of daily average wind power outputs, i.e., the intermittency of daily wind power increases the weekly price volatility by 0.37% and 0.18% both in DK1 and DK2" (Sec. 4, Tables 8–9)
5. "Because the flexibility to respond to high peak and low off-peak prices is crucial for demand-response applications and may compensate for the losses of conventional generators caused by lower average prices, there is a need to understand how the penetration of VRE affects volatility." (Abstract, p.270)
