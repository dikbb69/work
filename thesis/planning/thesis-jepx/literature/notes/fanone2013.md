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


## 原典精読（2026-09-29）

# Fanone, Gamba & Prokopczuk (2013) The case of negative day-ahead electricity prices
- 書誌: Energy Economics, 35, 22–34. DOI 10.1016/j.eneco.2011.12.006（オンライン公開 2011 年のため SciSpace ログでは 2011 と表記）
- 出所: Google Drive 参考研究_20260728/SetD（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: ドイツ EEG による再エネ拡大で日前市場に負値価格・負のスパイクが定常的に現れる。対数変換が使えない下で、時間別（hourly）日前価格を記述できる確率過程は何か。
- 貢献: 算術（加法）型 Lévy ベースの分数自己回帰（FAR）モデルを提案し、季節性・平均回帰・長期記憶・過剰尖度・負値価格、そして「最も重要な点として正負両方向の極端なスパイク」を同時に再現する（要旨 p.22、結論 p.34）。実務向けの4段階推定手続きとシミュレーション法を与える。

## 2. 設定・データ
- EPEX ドイツ TSO ゾーンの日前時間別価格、2007年1月〜2010年9月（第5.1節、Table 1 p.28）。
- 負値の実態（Table 1、非正値の個数/割合）: 2007年 28件(0.32%、最小 0)、2008年Q4 最小 −101.52 €/MWh、2009年 73件(0.83%、最小 −500.02、Q4 で 34件 1.54%)、2010年Q1 最小 −18.10。負スパイク（閾値超過）は 2008年 483件、2009年 114件。
- 制度: EPEX はドイツ TSO ゾーンに −3000 €/MWh の下限を導入（p.24）。fn.10（p.24）: フランス TSO ゾーンの下限は 0.01 €/MWh であり、規制と電源構成の構造差が負値の発生可能性を分ける、と明記。
- Genoese et al. (2010) の引用（p.24）: 低負荷＋中程度の風力、または中負荷＋高風力で負値が発生 → 負値は残差的現象でなく市場構造に由来。

## 3. モデル・手法の要点
- E(t)=s(t)+S̃(t)、s(t) は長期変動＋季節性の確定項。S̃(t)=μ S̃(t−1)+(1−L)^{−d}(ΔL(t)+ΔJ(t))（式1、p.25）、0<d<0.5 が多重スケールの自己相関（長期記憶）を担う。
- L(t): 長期水準まわりの変動、周辺分布は一般化双曲型（GH; 推定では NIG/HYP）。J(t)=J⁺(t)+J⁻(t): 正負のスパイクを独立な2つの斉時複合ポアソン過程で表し、ジャンプサイズは一般化パレート分布（GPD）（式8–9、p.26）。
- 負値の扱いの核心（p.25）: 「対数変換はしない（負値を許すため）。対数変換で極端値を均せないので、スパイクには非常に裾の重い分布が必要で、L(t) だけでは捕捉できず J(t) を分離する」。
- 推定4段階（p.34）: (1) POT 法で正負スパイクを識別・除去（閾値は標本平均超過関数で選ぶ、右裾・左裾それぞれ、p.27）、(2) クラスタリング平均週で時間別季節性を除去、(3) FAR(1) を回帰で推定、(4) 残差に NIG を当てる。シミュレーションは NIG（IG 時間変更ブラウン運動）＋2本の複合ポアソン（GPD ジャンプ）。

## 4. 主要結果・命題
- 第6節 Table 5（p.33–34）: 単一 Lévy の AR（Lucia–Schwartz 型）や負スパイク成分を欠く L-PS（Klüppelberg et al. 2010, Meyer-Brandis–Tankov 2008 型）と比較し、L-FAR が平均・標準偏差・尖度の一致で優る。「時間別価格は単一の Lévy 過程では記述できず、正負2つの極端スパイク成分が必要」（p.33）、「負値とスパイクを捉える Lévy 過程が最初の4次モーメントの良い適合に必要」（p.34）。
- 残差の非正規性は Jarque–Bera で確認（第5.5節）。

## 5. 著者が挙げる限界・今後の課題
- 標本は 2010年Q3 まで（その後も負値は継続と注記、p.24）。ポアソン強度は斉時（風況・負荷に連動する時変強度なし）で、風力等の基礎要因は明示的に入らない縮約型。
- 同時推定（MCMC）は非ガウス成分が多く計算不能として段階推定を採用（fn.24、p.26）。
- Weron (2014, p.1056) は本論文の固定閾値によるスパイク識別を「趨勢・季節性を無視する」として非推奨と評している点に注意。

## 6. 本研究との関係
- 引用予定箇所: 第5章（価格過程モデル、床の扱い）。JEPX の 0.01 円/kWh 床は、Fanone らが fn.10 で挙げたフランス（下限 0.01 €/MWh）と同型の「規制床のある市場」であり、ドイツ型の負スパイク過程 J⁻ ではなく潜在価格 g(net load) の床での打ち切り（censoring）として扱うことの根拠として引用する。
- モデル類型の対応: Fanone の「通常変動 L」と「スパイク J⁺/J⁻」の分離は、本研究の3レジーム混合（床レジーム／通常／逼迫スパイク）に対応する。分数積分 d による多重スケール自己相関は本研究の帯域分解（<6h, 6–24h, 1–7d, >7d）と発想を共有。
- 本研究が単純化した点: Lévy/GH 分布・複合ポアソンは用いず、需給（net load）を説明変数とする構造的な g(・) と時間帯プレミアムで代替。第10章の拡張: 負値解禁時は J⁻ の複合ポアソン＋GPD がそのまま雛形になる。

## 7. 引用に使える原文
- p.22（要旨）: "The EEG substantially impacts the dynamics of intra-day electricity prices by increasing the likelihood of negative prices. ... Most importantly, our model is able to generate extreme positive and negative spikes."
- p.24: "Therefore negative prices and spikes must be considered when modeling the process of electricity prices. Overlooking this phenomenon would make a substantial difference in valuations (e.g., when valuing a power off-peak position). Moreover, since the standard logarithmic conversion is not possible with negative prices, they pose a serious problem to electricity price modeling."
- p.24 fn.10: "Interestingly, the lower price limit for delivery in the French TSO zone is 0.01€/MWh, documenting the structural differences in terms of regulations and composition of generating sources between these two markets and the ensuing possibility that negative prices will occur."
- p.25: "We do not model a logarithmic transformation of the price, as is often done with other asset prices in order to allow for potentially negative prices. Since there is no logarithmic transformation to somehow smooth out extreme prices, a very heavy-tailed distribution must be used for spikes."
- p.33: "Thus, hourly electricity prices cannot be described by a single Lévy process only. The two extreme spike components (positive and negative) are necessary to capture the extreme positive and negative price spikes."
