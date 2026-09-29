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

## 原典精読（2026-09-29）
- 書誌: Schöniger, F., Morawetz, U.B. (2022). What comes down must go up: Why fluctuating renewable energy does not necessarily increase electricity spot price variance in Europe. *Energy Economics* 111, 106069. DOI 10.1016/j.eneco.2022.106069
- 出所: Google Drive 参考研究_20260728/SetA/SchonigerMorawetz2022_RenewablesPriceVarianceUShapeEurope.pdf を全文読取。

### 1. 問いと貢献（著者の主張する新規性）
- 問い: 欧州で IRE（風力・太陽光）シェアの上昇は必ず日前価格分散を上げるのか。各国の柔軟性資源（連系・柔軟電源・水力貯蔵）はどう効くか。
- 貢献: Wozabal et al. (2016) を**9か国パネル**に拡張。(1) 固定効果・一階差分・プール・国別の4通りで U 字を検証。(2) 風力と太陽光を分離（Wind & Solar Model）。(3) 国別の残余需要分散係数を柔軟電源比率・連系容量と対応づけ、柔軟性の役割を示す。
- 主結論: 9か国中7か国で U 字。分散最小は IRE シェア **10〜40%**。IRE の水準・分散より輸出入容量・柔軟電源・水力（揚水）の方が重要。

### 2. データ・市場・期間
- 2015〜2019 年、EU で風力＋太陽光シェア上位の9か国（AT/DE/LU を1市場、DK, GB, GR, IT, PT, RO, ES, SE）、EU の風力の78%・太陽光の79%を包含。
- 時間別 → 日次。被説明変数＝**日次価格分散**（時間別日前価格の日内分散）。
- 説明変数は国別最大負荷に対する%で相対化（負荷、残余負荷、IRE、風力、太陽光、各分散・共分散）、ガス価格（現在・ラグ）、曜日・月ダミー。パネル観測 14,266（GB は分散が異常に高く除外）。

### 3. 手法（被説明変数、変動性の定義、推定式の要点）
- Basic: $\mathrm{Var}(P)_{it}=f(RL, RL^2, \mathrm{Var}(RL))$。Extended: 負荷と IRE を分離し交差項・共分散を追加。Wind & Solar: IRE を風力・太陽光に分離（$W_{it}$ は N×12: load, load², wind, wind², solar, solar², Var(load), Var(IRE), Cov, load×wind, load×solar, wind×solar）。
- 固定効果はクラスター標準誤差。Maddala–Wu パネル単位根検定（ガス価格以外は定常）。国別 OLS は柔軟性の違いを解釈するために併用。

### 4. 主要結果（数値を必ず。表番号を付す）
- Table 4 FE Basic: 残余負荷 **−5.19**、残余負荷² **+0.05**、残余負荷分散 0.19（全て p<0.001）。分散最小は残余負荷＝負荷の **51.2%**（IRE 48.8%）。残余負荷 −10%pt の効果: Q3 で −17.38、中央値で −8.84、Q1 で +0.57 (€/MWh)²。残余負荷分散の平均（118.6）での寄与 22.54 (€/MWh)²。
- Table 4 Extended: 負荷 −20.47、負荷² 0.17、IRE 13.47、IRE² 0.02、IRE 分散 0.11、IRE–負荷共分散 **−0.43**、負荷×IRE **−0.18** → 「負荷の U 字は IRE が低いときのみ、IRE の U 字は負荷が高いときのみ」（交差項が鍵）。
- Table 4 Wind & Solar: 風力 9.69、風力² 0.03、**太陽光 32.55、太陽光² 0.75**（p=0.007）、負荷×風力 −0.15、負荷×太陽光 **−0.64**、風力×太陽光 +0.65、ガス 14.67。$R^2$ 0.088〜0.113。
- Table 5–7（国別）: U 字は AT/DE, DK, GB, GR, IT, RO, SE の7か国。PT・ES は逆 U 字または平坦（水力揚水比率が高い）。DK は残余負荷への依存が極めて弱い（IRE シェア41%、連系容量最大）。Fig. 6: 柔軟電源比率・輸出入容量が高いほど残余負荷分散の係数が小さい。
- Fig. 7: 国別に風力・太陽光シェアと価格分散の U 字を図示、最小 10〜40%。

### 5. 著者が挙げる限界・今後の課題
- 回帰は価格分散を十分説明できない（供給逼迫、政策転換、報酬制度が未考慮）。$R^2$ が小さい。
- 柔軟性資源は観測期間中ほぼ一定のため国別モデルでは統制不能（FE で吸収）。
- 日次集約のため時間内の因果は扱わない。

### 6. 本研究との関係
- 引用予定箇所: 第2章2.1（U 字の多国間実証）、第2章2.3（柔軟性資源＝連系・貯蔵の役割）、第5章（「低分散期に市場ベースの柔軟性投資が失敗しうる」という政策論）。
- 何を言うために引用するか: (i) 被説明変数が**日内分散**であり、太陽光の係数（32.55、太陽光² 0.75、負荷×太陽光 −0.64）は「太陽光は低負荷・高出力の日に日内分散を押し上げる」ことを示す＝本研究のダックカーブ／TB4h 拡大と同方向。風力は 9.69 で曲率 0.03 と小さい＝本研究の「風力は日内スプレッドを拡げない」と整合。(ii) 「IRE の水準・分散より柔軟性資源が重要」＝北海道の北本連系容量・蓄電池ストックが日内スプレッドを圧縮する（π(K) のカニバリゼーション）本研究の枠組みの実証的裏付け。(iii) 「分散が上がる前の低分散期に柔軟性投資を政策で確保すべき」＝政策ウェッジの正当化。
- 支持する点: 風力の日内分散効果が小さい、太陽光の凸効果、柔軟性資源が分散を圧縮。
- 対立する点: DK（風力主導）で分散が残余負荷にほぼ依存しない → 北海道でも風力主導なら日内分散は小さいはず、という本研究の見立てを支持（対立ではない）。
- 手法の源流: 日次分散のパネル OLS。本研究は単一エリアの時系列で分位点回帰・帯域分解。
- 新規性チェック: Schöniger & Morawetz は貯蔵を外生の柔軟性資源として扱い、その参入を内生化しない。本研究は蓄電池の自由参入均衡と政策ウェッジの分解で拡張。

### 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "panel model and single country regression results for seven out of nine analyzed European countries confirm a U-shaped relationship between the share of renewable electricity production and price variance. While the minimum price variance for most countries is found to be between a 10% and 40% renewable electricity production share, price variance is higher for lower and higher shares." (Abstract)
2. "The availability of export and import capacities, flexible power plants, and hydro (pump) storage is more important for a country's ability to balance price variance than the level and variance of the renewable infeed itself." (Abstract)
3. "Consequently, we find a U-shaped effect of load only at a low level of IRE, and we find a U-shaped effect of IRE only at high levels of load. Thus, the interaction term is key to understanding whether a U-shape is found." (Sec. 4.1.2)
4. "The finding that the price variance decreases before it rises again in many European countries calls for policies to secure investments in flexibility options, such as grid expansion, storage facilities, flexible power plants, and demand-side management, in the period of low price variance when market-based solutions might fail" (Abstract)
5. "The minimum price variance is estimated to be reached if the residual load is 51.2% of the load (or when the IRE is 48.8% of the load)." (Sec. 4.1.1)
