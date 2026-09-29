# Shin & Lee (2024) Energies — LSMCパイプライン

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Least Squares Monte Carlo (LSMC) for Battery Investment Timing

The paper utilizes the Least Squares Monte Carlo (LSMC) method to determine the optimal investment timing for Battery Energy Storage Systems (BESSs), considering various factors like investment costs and revenue uncertainty  (Shin & Lee, 2024).

### Full LSMC Pipeline for Battery Investment Timing Decision

The LSMC method involves several steps to simulate revenue paths and make investment decisions:
- Setting Energy Storage System Parameters (Step 1):
- This initial step involves defining the ESS type, capacity, discharge duration, round-trip efficiency, and depth of discharge. These parameters are crucial for conducting the research using the collected information  (Shin & Lee, 2024).
- Calculating ESS Revenue Using Scheduling (Step 2):
- An objective function is employed to maximize revenue from arbitrage trading  (Shin & Lee, 2024).
- Constraints include the initial state of charge, PCS/ESS capacity, charge/discharge capacity, and 1-day/1-cycle limits  (Shin & Lee, 2024).
- The scheduling uses System Marginal Price (SMP) and Capacity Payment (CP) data to calculate annual revenue  (Shin & Lee, 2024).
- Modeling ESS Revenue with Uncertainty (Step 3):
- The uncertain ESS revenue is modeled using the Geometric Brownian Motion (GBM) model  (Shin & Lee, 2024).
- A 20-year ESS revenue process is generated in a risk-neutral world using the GBM model  (Shin & Lee, 2024).
- Calculating Investment Value and Holding Value (Step 4):
- The investment value is determined by considering the ESS investment cost, calculated as ESS revenue - Investment Cost  (Shin & Lee, 2024).
- The holding value is calculated as Investment Value × e^(risk-free interest)  (Shin & Lee, 2024).
- Estimating Investment Value Using Least-Squares Regression Analysis (Step 5):
- Least-squares regression is performed to minimize the sum of residual squares between actual and estimated values  (Shin & Lee, 2024).
- The regression model uses Laguerre Polynomials as basis functions  (Shin & Lee, 2024). The equation for the regression model is Valhold = aL0(R) + bL1(R) + cL2(R) + dL3(R), where a, b, c, d are correlation coefficients and L0(R), L1(R), L2(R), L3(R) are Laguerre Polynomials of R     .
- This process involves calculating the holding value just before maturity and then reversing the process to the initial year to determine the optimal investment timing  (Shin & Lee, 2024).
- Determining the ESS Investment Decision (Steps 6 & 7):
- Investment decisions are made by comparing the recalculated investment and holding values  (Shin & Lee, 2024).
- If the investment value is greater than the holding value, ESS investment is carried out; otherwise, if the holding value is more significant, investment is not made  (Shin & Lee, 2024).
- This process is repeated to calculate the holding value for each revenue path, and the final investment and holding values are compared to determine the optimal timing  (Shin & Lee, 2024).

### Revenue Process Assumption and Estimated Parameters

- Revenue Process Assumption: The paper assumes that the ESS arbitrage revenue follows a Geometric Brownian Motion (GBM) stochastic process to reflect its uncertainty  (Shin & Lee, 2024) . The GBM model is expressed as dR = µRdt + σ₁Rdz, where R is revenue, µ is the expected rate of return, t is the period, σ₁ is the volatility, and z reflects revenue change uncertainty . In a risk-neutral world, this becomes dR = rRdt + σ₁Rdz .
- Estimated Parameters:
- Initial Revenue (R₁): Set at $349,631.05 in 2023  (Shin & Lee, 2024).
- Risk-Free Interest Rate (r): 3.627%, based on the 180-day average for the Korea Overnight Financing Repo Rate  (Shin & Lee, 2024).
- Annual Revenue Volatility (σ₁): 43.368%, calculated from the annual returns presented in the paper  (Shin & Lee, 2024).

### Size of Option Value Relative to NPV

The paper does not explicitly calculate a traditional Net Present Value (NPV) and then compare the option value to it. Instead, the LSMC method directly determines the optimal investment timing by comparing the arbitrage revenue (which can be seen as the potential payoff) against the ESS investment cost. The Valact (activation value function for the LSMC option) is defined as max(R – ESScost, 0), where R is the arbitrage revenue and ESScost is the investment cost  (Shin & Lee, 2024). This formulation inherently incorporates the investment cost into the decision-making process, effectively determining when the option to invest becomes profitable (i.e., when R > ESScost).
The results show an "option activate rate" over years, indicating the percentage of simulated paths where investment is optimal. For instance, the highest option activate rate is 30.1% in 2027, and it decreases over time  (Shin & Lee, 2024). For the years 2024 and 2025, the LSMC option is not activated, meaning the earned profit does not exceed the installed cost .

### Limitations of the Revenue Process Assumption

The authors acknowledge that previous studies using option theory for ESS investment timing have limitations:
- Simplified Investment Delay: Prior research often simply concludes that investment is delayed as the operating period increases due to higher volatility in revenue  (Shin & Lee, 2024).
- Incomplete Cost Consideration: Earlier studies also indicated that investment is delayed as ESS investment costs increase, but without adequately considering the learning rate and actual investment costs  (Shin & Lee, 2024).
The current paper aims to address these limitations by using the LSMC simulation model, which explicitly considers the learning rate and actual investment costs in its determination of optimal investment timing  (Shin & Lee, 2024).


## 原典精読（2026-09-29）

# Shin & Lee (2024) Investment Decision for Long-Term Battery Energy Storage System Using Least Squares Monte Carlo
- 書誌: Energies, 17(9), 2019 (pp.1–15). DOI 10.3390/en17092019
- 出所: Google Drive 参考研究_20260728/SetD（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 燃料費ベースの韓国電力市場（SMP＋容量支払 CP）で BESS の投資が進まない中、裁定収入の不確実性と投資費用（学習率込み）を考慮した最適投資時期をどう決めるか。
- 貢献（p.3, p.12）: (i) 中央給電 ESS（10 MW/40 MWh、4時間）の裁定収入を LP スケジューリングで算出、(ii) 収入を GBM で確率過程化、(iii) 実際の設置費用と学習率を組み込んだ LSMC で投資時期を決定。先行研究 [18] は「ボラティリティが高いと投資が遅れる」「費用が高いと遅れる」を示しただけで学習率・実費用を考慮していない、と差別化。

## 2. 設定・データ
- 韓国 SMP・CP の時間別データ 2002–2023 年（22年）。ESS パラメータ（Table 3、p.8）: DoD 80%、RTE 85%、Li-ion、PCS 10 MW、容量 40 MWh（済州の長期 BESS 契約市場に準拠）。
- 設置費用（Table 4、p.8）: 2021 年 $1,854,320（固定 O&M $102,200、保証 $246,400）→ 2030 年 $1,399,800（O&M $86,800、保証 $160,800）。CRF 換算の年額 $311,880.37、学習率 2.76%（2030 年以降は一定）。
- 年間裁定収入（Table 6、p.10）: 最大 $403,451.64（2010 年）、最小 $54,903.17（2016 年）、2023 年 $349,631.05（GBM の初期値 R1）。年次対数収益率のボラティリティ σ=43.368%、無リスク金利 r=3.627%（KOFR 180 日平均）。GBM パスは 20 年×1,000,000 本。

## 3. モデル・手法の要点
- スケジューリング LP（式17–25、p.5–6）: max Σ_t[(SMP_D,t+CP_D,t)·EP_D,t·RTE − SMP_C,t·EP_C,t]、制約は SOC_init=SOC_final、0≤EP≤PCS_max·DoD、日内充放電量≤ESS_max·DoD、1日1サイクル、放電≤充電。
- 収入過程（式2–9、p.4）: リスク中立 GBM dR=rRdt+σRdz、ln(R_{t+dt}/R_t)=(r−σ²/2)dt+σε√dt。
- LSMC（式10–16、p.4–5）: 行使価値 max(R−ESScost, 0)、保有価値を Laguerre 多項式 L0–L3 で収入に回帰、満期から後ろ向きに初年度まで判定、年別の「オプション行使率」を出力。

## 4. 主要結果・命題
- Table 8（p.12）: 行使率 2024 年 0%、2025 年 0%、2026 年 21.0%、2027 年 30.1%（最大）、2028 年 15.3%、2029 年 8.8%、2030 年 5.5%、以降逓減（2043 年 0.4%）。「2024–2025 年はオプションが行使されない。得られる利益が設置費用を超えない」（p.11–12）。
- 2022 年 1 月 1 日の例: 12–15 時に充電、19–21・23 時に放電（Table 5、p.9）。

## 5. 著者が挙げる限界・今後の課題（p.13）
- Li-ion 4 時間のみ。短期・長期・季節間 ESS で役割が異なるため、複数の持続時間での適用・シミュレーションが必要。
- （本文に明示はないが構造上の限界）収入は外生 GBM で、他社参入による値幅圧縮（内生性）や自社の価格影響を含まない。Laguerre 4 項の回帰、劣化なし、リスク中立評価。

## 6. 本研究との関係
- 引用予定箇所: 第9章（投資）における実物オプション評価の参照。Shin–Lee は「収入過程が外生」＝Grenadier (2002) の言う「投資機会への独占的アクセス」に相当し、待つオプションの価値が侵食されない設定である。本研究は逆に、収入（スプレッド）が累積参入量に内生的に依存する自由参入均衡を組み、K*=0 を得る。9.2(e) では「競争を無視した LSMC は 2024–25 年に 0% 行使（待機）を予測するが、北海道では参入が続いている」という対比を置き、Leahy/Grenadier の「競争によるオプション価値の消失」で説明する。
- 第5章(c): Shin–Lee の LP（1日1サイクル、RTE 85%、DoD 80%）は本研究の完全予見 LP と同型の上限計算であり、パラメータの比較対象として引用。
- 本研究が単純化した点: LSMC は用いず、確定的均衡＋感応度分析で代替。GBM の σ=43% という収入ボラティリティは、本研究の価格過程シミュレーション（common random numbers）から得る収入分布と対比可能。

## 7. 引用に使える原文
- p.1（要旨）: "The ESS revenue with uncertainty is modeled as a stochastic process using Geometric Brownian Motion (GBM), and the optimal time to invest in an ESS is determined using an LSMC simulation considering investment costs."
- p.10: "The highest revenue is $403,451.64 in 2010, and the lowest revenue is $54,903.17 in 2016."
- p.10: "The annual revenue volatility σ_rt for ESS arbitrage is 43.368%, as calculated from the annual returns in Table 6."
- p.11–12: "Among the 1 million simulations, the highest option activate rate is 30.1% in 2027, and the frequency of option occurrence decreases as the years go on. From 2024 to 2025, the LSMC option is not activated. The earned profit does not exceed the installed cost."
- p.12: "Previous study has shown some limitations in using option theory to find the timing of ESS investments. It has simply found that investment is delayed as the operating period increases due to higher volatility in revenue."
