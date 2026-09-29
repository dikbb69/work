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

## 原典精読（2026-09-29）
- 書誌: Wozabal, D., Graf, C., Hirschmann, D. (2016). The effect of intermittent renewables on the electricity price variance. *OR Spectrum* 38, 687–709. DOI 10.1007/s00291-015-0395-x（published online 7 March 2015）
- 出所: Google Drive 参考研究_20260728/SetA/Wozabal2016_IntermittentRenewablesPriceVariance.pdf を全文読取。

### 1. 問いと貢献（著者の主張する新規性）
- 問い: 「再エネは価格分散を増やす」という支配的見解は正しいか。
- 貢献: (1) 静学的市場モデルで、価格分散を左右する2要因＝**供給曲線の傾き（形状）**と**IES 投入量の分散**を特定。(2) 凸（逆 S 字）供給曲線の下で、少量〜中程度の IES は分散を**下げ**、大量では**上げる**（U 字）と予測。(3) ドイツ 2007–2013 のデータで検証し、PV と風力の限界効果を分けて推定。

### 2. データ・市場・期間
- 市場: EPEX ドイツ／オーストリア日前、2007〜2013 年、時間別。
- 被説明変数: **日次価格分散**（1日24時間値から1つの分散）。半日は「意味がない」、週以上は情報を失うとして日次を選択（3.2節）。
- 説明変数: 日平均残余需要とその2乗、残余需要の日内分散、需要・IES（風力・PV の TSO 日前**予測**、PV は 2010 年以降、2010 年は Tennet 予測から外挿）、気温、3か月ラグ石油価格（燃料価格代理）。
- 推定: OLS、HAC 標準誤差（Andrews 1991）。

### 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 理論（第2節）: 一次近似で $\mathrm{Var}(S(X))\approx S'(E[X])^2\,\mathrm{Var}(X)$。IES 投入 $I$ は残余需要 $Y=X-I$ を左（平坦部）にシフト（分散↓）させる一方 $\mathrm{Var}(Y)$ を増やす（分散↑）。逆 S 字（左端が凹）なら残余需要が凹部に押し込まれると分散↑ → 残余需要平均に対して U 字。
- 実証: model 1（残余需要とその2乗・分散）、model 2（需要と IES を分離、$X^2=(Q-I)^2$ と $\mathrm{Var}(X)=\mathrm{Var}(Q)-2\mathrm{Cov}(Q,I)+\mathrm{Var}(I)$ の各項）、model 3（IES を風力と PV に分離。PV の平均と分散は相関 0.95 のため平均のみ）。

### 4. 主要結果（数値を必ず。表番号を付す）
- Table 3 (1): 残余需要 **−40.06**（p<0.001）、残余需要² **+0.43**（p<0.001）→ 凸2次（U 字）。残余需要の分散は強い正。
- Table 3 (2): 需要 −15.59（n.s.）、需要² 0.23（p=0.007）、再エネ 18.64（p=0.096）、再エネ×需要 **−0.69**（p=0.002）、再エネ分散 1.88（p<0.001）。
- Table 3 (3): 風力 29.74（p=0.011）、風力² 0.50（p=0.007）、**PV −53.71**（p=0.023）、PV² 9.93（p<0.001）、風力×需要 −0.74、PV×需要 −1.13、PV×風力 2.52、再エネ分散 2.75。
- 限界効果（観測点で評価、平均需要 61.6 GW）: **PV 1 GWh あたり −83、風力 −7**（PV は風力の約12倍の分散低減）。風力の係数は正だが需要との負の交差項で全体としては分散低減。
- 転換点（第4節）: model 2 から分散最小は需要 42.8 GWh・再エネ 5.7 GWh；平均需要 61.6 GWh に固定すると再エネ **12 GWh** で最小 → 初期は分散低減、後期の高投入日には分散増。
- その他: 気温（夏に分散大：PV 大＋低需要で凹部へ）、石油価格は正。

### 5. 著者が挙げる限界・今後の課題
- 静学モデル（時間間の結合＝動学的ディスパッチを無視）。戦略的相互作用なし。
- PV 予測は 2010 年のみ外挿。PV の分散と平均が分離不能。
- 今後: ディスパッチモデルによる入札動学、戦略的行動、政策手段（要求型柔軟性・容量市場・貯蔵補助）の効率比較。

### 6. 本研究との関係
- 引用予定箇所: 第2章2.1（U 字仮説の理論的源流）、第2章2.2（変動性を日内分散で測る先例）、第5章（市場ベースの柔軟性投資が「低分散期」に不足する＝政策ウェッジの論拠）。
- 何を言うために引用するか: (i) 価格分散＝（供給曲線の傾き）²×（残余需要の分散）という分解は、本研究の「太陽光は形状（傾きの位置）を、風力は分散（水準）を動かす」という整理の理論的裏付け。(ii) 被説明変数が**日内分散**なので本研究の TB4h と同じ対象。ドイツ 2007–2013 では PV が日内分散を強く下げた（昼ピーク切り下げ）が、PV² が正（9.93）で凸 → 高浸透ではダックカーブで分散増に転じる。九州・北海道は U 字の右側。(iii) 「市場ベースの柔軟性投資は時機に間に合わない可能性があり補助・容量市場が必要」＝本研究の政策ウェッジの先行的主張。
- 支持する点: 風力の日内分散効果は小さい（−7/GWh、需要との交差項で相殺）。太陽光は日内形状に強く効く（符号は浸透率に依存）。
- 対立する点: 「PV は分散を下げる」（低浸透期のドイツ）。本研究では拡大。U 字の左右で整理。
- 手法の源流: 日次分散の OLS。本研究は分位点回帰・TB4h・帯域分解。
- 新規性チェック: Wozabal らは貯蔵を「政策で支えるべき柔軟性」と外生的に扱う。本研究は蓄電池の**参入均衡**を内生化し、カニバリゼーション π(K) で「市場が柔軟性投資を十分に生まない」ことを定量化する。

### 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "while small to moderate quantities of IES tend to decrease the price variance, large quantities have the opposite effect." (Abstract, p.687)
2. "Hence, the variance of the prices is approximated by the squared slope of S market supply curve evaluated at the mean of the residual demand times the variance of the residual demand." (Sec. 2)
3. "The average marginal effects of PV and wind infeed (per GWh) on the price variance evaluated at the observations yield an average reduction of 83 for PV compared to 7 in the case of wind." (Sec. 3.4)
4. "installation of PV capacities tends to decrease price variance more than the installation of wind turbines, since the infeed from the former has a pronounced positive correlation with demand, while the infeed from the latter shows no such clear correlation pattern." (Sec. 4)
5. "market-based incentives for investments in flexibility alone might not result in sufficient capacities built in time to ensure network stability. Policies that require producers to provide flexibility, the build-up of infrastructure such as a smart grid, capacity markets, or direct subsidies for flexible generation and storage facilities might mitigate these potential market failures." (Sec. 5)
