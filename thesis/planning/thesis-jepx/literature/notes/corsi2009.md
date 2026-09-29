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


## 原典精読（2026-09-29）

# Corsi (2009) A Simple Approximate Long-Memory Model of Realized Volatility
- 書誌: Journal of Financial Econometrics, 7(2), 174–196. DOI 10.1093/jjfinec/nbp001
- 出所: Google Drive 参考研究_20260728/SetD（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: ボラティリティの長期記憶・厚い裾・自己相似性を、真の長期記憶モデル（ARFIMA）のような煩雑さなしに再現・予測できるか。
- 貢献: 異質市場仮説（Müller et al. 1993）に基づき、異なる時間地平で定義されたボラティリティ成分の「加法的カスケード」を提案。これが実現ボラティリティ（RV）の単純な AR 型モデル HAR-RV に帰着する。「構造の単純さと真の長期記憶性の欠如にもかかわらず」主要な経験的特徴を再現し、予測力も高い（要旨 p.174）。

## 2. 設定・データ
- USD/CHF（1989年12月〜2003年12月、Reuters FXFX の tick）、S&P500 先物（1990年1月〜2007年7月）、30年米国債先物（1990年1月〜2003年10月）。日次 RV は two-scales 推定量（Zhang, Aït-Sahalia & Mykland 2005）で計算（3.1、p.186）。
- 多期間 RV は日次 RV の単純平均（式4、p.177）: RV^(w)_t=(1/5)Σ_{i=0}^{4}RV^(d)_{t−i}、月次は 22 日平均。

## 3. モデル・手法の要点
- 2.2（p.178–179）: 短期トレーダー（日次以下）、中期投資家（週次）、長期主体（月次以上）が異なるボラティリティ成分を知覚・生成。長期ボラティリティが短期に影響する非対称性 → 「低周波から高周波へのボラティリティ・カスケード」。
- 2.3（p.179–180）: 潜在部分ボラティリティ σ̃^(m), σ̃^(w), σ̃^(d) をそれぞれ「同じ地平の過去 RV の AR(1) 項＋一段長い地平の部分ボラティリティの期待値（階層項）」で表し、再帰代入すると
  σ^(d)_{t+1d}=c+β^(d)RV^(d)_t+β^(w)RV^(w)_t+β^(m)RV^(m)_t+ω̃^(d)_{t+1d}（式6）。
  「式(6)は、過去の RV を異なる周波数で見たものを直接ファクターとする3ファクター確率ボラティリティモデル」（p.180）。OLS で推定可能。成分は3つに限らず追加可能。
- 2.4（p.181–）: 2時間頻度（M=12）でシミュレーションし、日次集計で長期記憶・厚い裾・自己相似性を再現。

## 4. 主要結果・命題（数値）
- Table 4（1日先インサンプル、p.189）R²: HAR(3) 0.565（USD/CHF）、0.707（S&P500）、0.236（T-Bond）；AR(1) 0.493/0.648/0.109；ARFIMA(5,d,0) 0.559/0.703/0.237。
- Table 5（アウトオブサンプル、日次ローリング再推定、p.191）USD/CHF R²: HAR(3) 0.551（1日）、0.609（1週）、0.570（2週）；AR(1) 0.497/0.213/0.038；AR(3) 0.530/0.523/0.316；ARFIMA 0.546/0.611/0.576。
- 結論（p.193）: 「HAR(3) は考慮した全ホライズン（1日・1週・2週）で短期記憶モデルを安定的に上回り、はるかに複雑で推定が煩雑な長期記憶 ARFIMA と同等」。

## 5. 著者が挙げる限界・今後の課題
- 形式的には長期記憶モデルでない（近似）。3成分は説明の便宜で選択（追加可能）。係数制約の F 検定は棄却（fn.15）。ARFIMA の予測は d を全標本で推定しており真のアウトオブサンプルでない（fn.16）。拡張: ジャンプ成分、レバレッジ、非線形（平滑遷移・木構造）、多変量 Vector-HAR。

## 6. 本研究との関係
- 引用予定箇所: 第5章(a) ボラティリティの3分解（水準／日内形状 TB4h／複数日）と、風力・太陽光出力の移動平均カスケードによる帯域分解（<6h、6–24h、1–7d、>7d）。本研究の分解は「異質な地平の移動平均で定義した少数の加法的成分で多重スケールの持続性を近似する」という HAR の発想を、価格ボラティリティではなく出力・net load 系列のフィルタとして用いたもの。式(4)（地平別の単純平均）と式(6)（加法的3ファクター）を概念的源流として引用する。
- 「真の長期記憶モデルでなくても少数成分で長期記憶的挙動を再現できる」（p.174–175）は、本研究が ARFIMA や分数積分（Fanone の d）を用いず帯域分解で済ませることの根拠。
- 本研究が単純化した点: HAR は RV の予測回帰だが、本研究は予測ではなく分散の帰属（どの帯域がスプレッドの変動を担うか）に用いる。第10章の拡張: 日次スプレッドの RV に HAR 型回帰を当て、短期／週次／月次成分の寄与を推定する。

## 7. 引用に使える原文
- p.174（要旨）: "The paper proposes an additive cascade model of volatility components defined over different time periods. This volatility cascade leads to a simple AR-type model in the realized volatility with the feature of considering different volatility components realized over different time horizons."
- p.174（要旨）: "In spite of the simplicity of its structure and the absence of true long-memory properties, simulation results show that the HAR-RV model successfully achieves the purpose of reproducing the main empirical features of financial returns (long memory, fat tails, and self-similarity) in a very tractable and parsimonious way."
- p.178: "The main idea is that agents with different time horizons perceive, react to, and cause different types of volatility components."
- p.179: "The overall pattern that emerges is a volatility cascade from low frequencies to high frequencies."
- p.180: "Equation (6) can be seen as a three-factor stochastic volatility model, where the factors are directly the past realized volatilities viewed at different frequencies."
- p.193: "the HAR(3) model steadily outperforms the short-memory models at all the time horizons considered (one day, one week, and two weeks) and is comparable to the much more complicated and tedious to estimate long-memory ARFIMA model."
