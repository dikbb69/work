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

## 原典精読（2026-09-29）
- 書誌: Ketterer, J.C. (2014). The impact of wind power generation on the electricity price in Germany. *Energy Economics* 44, 270–280. DOI 10.1016/j.eneco.2014.04.003
- 出所: Google Drive 参考研究_20260728/SetA/Ketterer2014_WindPriceGermany.pdf を全文読取。上記 SciSpace ログの数値（Table 3 の −0.098 / 0.002 / −1.489 / 0.020、規制ダミー −0.008）は原典と一致することを確認。

### 1. 問いと貢献（著者の主張する新規性）
- 問い: 風力発電（日前予測値）はドイツ日前価格の**水準**と**ボラティリティ**にどう影響し、その関係は時間とともに（特に 2010 年の AusglMechV 施行で）どう変わったか。
- 著者の貢献（第1節）: 「few papers have explicitly modelled the impact of wind power on the volatility of the electricity price or elaborated on the development of this relationship over time」→ (1) 風力を GARCH の平均式と分散式の**両方**に入れ統合推定、(2) ローリング回帰と規制ダミーで関係の時間変化を追跡。

### 2. データ・市場・期間
- 価格: EEX Phelix Day Base（24 時間平均の日次）、2006年1月1日〜2012年1月31日。外れ値（3σ 超）を曜日別 3σ 値に置換、曜日・月ダミーで季節除去（Table 2）、対数化。
- 風力: 4 TSO の日前**予測**（MWh/日、平均 111 GWh/日、負荷 1,332 GWh/日、平均シェア約 8%）。負荷予測は実績＋N(0, 平均負荷の2%) の擬似予測（Jónsson et al. 2010 方式）。
- 追加: 規制ダミー（2010/1 以降＝1）、EMCC 北向き連系容量（Table 4 仕様 E）。

### 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 被説明変数: 除季節・対数化した日次価格。AR(7)-GARCH(1,1)。
- 変動性の定義: **条件付き分散 $h_t$**（日次平均価格の日間ボラティリティ）。日内形状は Phelix Day Base の平均化で消えている。
- 仕様: (A) ベンチマーク、(B) log(wind), log(load) を平均・分散両式に、(C) wind/load シェア、(D) (C)＋規制ダミー（分散式のみ）、(E) ＋連系容量。

### 4. 主要結果（数値を必ず。表番号を付す）
- Table 3 (B): 平均式 log(wind) **−0.098**（p<0.0001；風力1%増で価格0.1%低下）、log(load) 0.081；分散式 log(wind) **+0.002**（p=0.047）、log(load) −0.021（高需要時に分散低下、著者は「反直観的」と注記）。
- Table 3 (C): wind/load 平均 −1.489（1%ポイントで価格 −1.46%）、分散 +0.020（p=0.063）。
- Table 3 (D): 規制ダミー（分散式）**−0.008**（p<0.0001）、wind/load 分散 +0.045。GARCH α 0.16〜0.25、β 0.31〜0.73。
- Fig. 6（3年ローリング、仕様 C）: **分散式の風力係数はほぼ一定**（0〜約0.05%と Rintamäki et al. 2017 が要約）、**平均式の風力係数（メリットオーダー効果）は縮小**。2011年4月以降（原発停止）さらに縮小。要因として太陽光がピーク価格を下げ日平均を押し下げること、輸出による平滑化を挙げる。
- Table 4 (E): EMCC 連系容量は非有意、規制・風力の結論は不変。

### 5. 著者が挙げる限界・今後の課題
- 太陽光との相互作用を**時間別価格**で分析することは「left for further research」（第5.1節）。
- 負荷予測は擬似生成（脚注18–19）。
- 政策提言はゲートクローズ後倒し・15分商品・市場プレミアムなど定性的。

### 6. 本研究との関係
- 引用予定箇所: 第2章2.1（風力→水準低下・分散増の代表的実証）、第3章（変動性定義の比較表）、第4章（結果の対比）。
- 何を言うために引用するか: 「風力は分散を増やす」の代表例だが、その分散は**日次平均価格の日間条件付き分散**であり、係数は 0.002（対数風力）と極小。ローリングでも安定的に小さい。本研究の帯域分解で風力の寄与が 1–7日帯域に現れ日内帯域に現れないという結果と整合する（Ketterer の $h_t$ は日内を含まない）。
- 支持する点: 分散効果が小さく安定／メリットオーダー効果が時間とともに縮小（本研究の π(K) 急速カニバリゼーションと同じ「効果の逓減」の観察）。
- 対立する点: 見出し上の「風力は変動性を上げる」。時間スケールを明示すれば対立しない。
- 手法の源流: GARCH-X。本研究は分位点回帰＋帯域分解で置き換える。
- 新規性チェック: Ketterer 自身が「時間別価格による太陽光との相互作用分析」を今後の課題としており、本研究の TB4h／帯域分解はまさにその空白。

### 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "The results show that variable wind power reduces the price level but increases its volatility." (Abstract, p.270)
2. "When the wind electricity feed-in (MWh per day) increases by 1%, the price decreases 0.1%." (Table 3 note / Sec. 5.1)
3. "The negative and significant coefficient for the dummy variable indicates a reduction of the conditional variance after the regulatory change." (Sec. 5.2)
4. "The rolling regressions illustrate, on the one hand, that the wind coefficient from the variance equation remains fairly constant. On the other hand, the coefficient for the wind share in the mean equation ... [declines over time]" (Sec. 5.1, Fig. 6)
5. "Investigating this interaction in an analysis with hourly prices would be interesting but is left for further research." (Sec. 5.1)
