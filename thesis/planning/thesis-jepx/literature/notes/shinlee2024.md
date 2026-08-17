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
