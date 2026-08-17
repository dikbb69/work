# Sioshansi et al. (2009) Energy Economics 31 — 価格テイカーLP裁定の原型

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Analysis of Price-Taking Storage Arbitrage and Welfare Impacts

This study examines the welfare impacts of electricity storage, focusing on the incentives of different ownership structures and the effects on price spreads. It models storage operation and analyzes how large-scale storage can influence market dynamics.

### Optimization Problem for Price-Taking Storage Arbitrageur

The optimization problem for a price-taking storage arbitrageur involves maximizing the arbitrage value, which is the difference between the revenue from discharging and the cost of charging, subject to technical constraints. The paper models this within a two-period electricity market framework.
- Objective Function: The arbitrageur aims to maximize the net profit from buying energy when prices are low and selling it when prices are high. This is represented by the total net profit of the owner(s) of the storage devices, given by the equation: Π_arb (δ) = δp(l₂ – δ) – φδp(l₁ + φδ) which simplifies to δ[c₀ (1–φ) + c₁ (l₂ – φl₁)] – δ²c₁ (1 + φ²)  (Sioshansi, 2010). Here, δ represents the amount of energy discharged, p(l) is the price-load relationship, l₁ and l₂ are loads in off-peak and on-peak periods, respectively, and φ = 1/η where η is the roundtrip efficiency  .
- Constraints: The storage device operates within specific technical limits:
- Discharge Capacity: The storage device has a discharge capacity of δ MW  (Sioshansi, 2010).
- Charging Capacity: Its total charging capacity is δ/η MW, allowing one hour of charging at full capacity to provide enough energy for one hour of full-capacity discharge  (Sioshansi, 2010).
- Energy Balance: If x MWh of energy is put into storage, at most ηx MWh can be taken out, reflecting energy losses  (Sioshansi, 2010).
- Operational Limits: The amount of energy discharged, δ, must be between 0 and the maximum storage capacity δ (0 ≤ δ ≤ δ)  (Sioshansi, 2010).
- Notation: The key notations include:
- p(l): Electricity price as a function of generating load l  (Sioshansi, 2010).
- c₀ + c₁l: Linear relationship for electricity prices  (Sioshansi, 2010).
- η: Roundtrip efficiency of the storage device (0 < η < 1)  (Sioshansi, 2010).
- x: MWh of energy put into storage  (Sioshansi, 2010).
- δ: Discharge capacity of the storage device in MW, and also the amount of energy discharged in MWh  (Sioshansi, 2010) .
- δ/η: Total charging capacity in MW  (Sioshansi, 2010).
- l₁: Load in the off-peak period (period 1)  (Sioshansi, 2010).
- l₂: Load in the on-peak period (period 2)  (Sioshansi, 2010).
- φ: Defined as 1/η  (Sioshansi, 2010).

### Change in Arbitrage Value with Storage Duration

The provided text does not explicitly detail how arbitrage value changes with storage duration (hours of capacity) using specific numerical values. However, it mentions that the price-smoothing effect of large-scale storage can reduce the arbitrage value. Specifically, the analysis in Sioshansi et al. (2009) shows that the price-smoothing effect of large-scale storage can reduce the arbitrage value of 1 GW of storage by more than 20%, compared to the arbitrage value for a price-taker  (Sioshansi, 2010). This indicates that as storage capacity increases, the per-unit arbitrage value can decrease due to market response.

### Effect of Large-Scale Storage on Price Spread (Self-Cannibalization)

Large-scale electricity storage affects the price spread through a mechanism often referred to as "self-cannibalization." This occurs because the very act of arbitrage by large storage units tends to smooth out the price differences they exploit.
- Mechanism: Larger utility-scale storage can smooth the load pattern by lowering on-peak and increasing off-peak generating loads. This action results in a similar smoothing of on- and off-peak price patterns, which in turn reduces arbitrage opportunities for the storage device itself  (Sioshansi, 2010).
- Impact on Arbitrage Value: While this load smoothing reduces the arbitrage value for the storage operator, it generates significant external welfare effects by reducing energy prices for consumers and increasing profits for electricity generators  (Sioshansi, 2010). The paper notes that this price-smoothing effect can reduce the arbitrage value of 1 GW of storage by over 20% .

### Assumed Round-Trip Efficiency and Other Technical Parameters

The model assumes a roundtrip efficiency and other technical parameters for the storage device:
- Roundtrip Efficiency (η): The storage device has a roundtrip efficiency, η, which captures energy losses during the storage cycle. It is assumed that 0 < η < 1  (Sioshansi, 2010).
- Discharge Capacity (δ): The storage device has a discharge capacity of δ MW  (Sioshansi, 2010).
- Charging Capacity (δ/η): The total charging capacity is δ/η MW, designed to allow one hour of full-capacity charging to provide enough energy for one hour of full-capacity discharge  (Sioshansi, 2010).
- Price-Load Relationship: Electricity prices are assumed to respond to generating loads based on a linear relationship: p(l) = c₀ + c₁l, where c₀ ≥ 0 and c₁ > 0  (Sioshansi, 2010).
- Price-Inelastic Loads: Consumer loads (l₁ and l₂) are assumed to be price-inelastic because consumers face a time-invariant retail rate of electricity  (Sioshansi, 2010).
In essence, the study highlights that while storage can reduce price volatility and offer welfare gains, the arbitrage value for storage operators can diminish as storage capacity increases due to its own price-smoothing effect. The model simplifies market operations to analyze these fundamental economic incentives and their implications for different ownership structures.
