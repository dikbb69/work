# Kanamura & Bunn (2022) Energy Economics 107 — 2021年1月高騰とマーケットメイク

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Analysis of JEPX Price Spikes, Market Making, and Data Considerations

This paper delves into the dynamics of electricity price formation in the Japan Electric Power Exchange (JEPX), particularly focusing on market-making interventions, price spikes, and data considerations.

### Mechanism Behind January 2021 JEPX Price Spike

The paper does not explicitly identify a specific mechanism behind a January 2021 JEPX price spike. The data used in the study covers up to March 31, 2020, and the analysis of market-making intervention and price formation dynamics is focused on the period between 2015 and 2019, with some data for 2020  (Kanamura & Bunn, 2022) . Therefore, information regarding a January 2021 price spike is outside the scope of this particular document.

### Modeling of Market Making and Its Estimated Effect on Price Formation

Market making in the JEPX is modeled through a dynamic regime switching formulation that accounts for the distinct effects of buy-side and sell-side volumes on price formation, with temperature acting as a regime switching driver  (Kanamura & Bunn, 2022).
- Modeling Approach: The model uses a nonlinear functionality to effectively fit the spiky time series of prices  (Kanamura & Bunn, 2022). It aims to establish if a market-making intervention improved the fundamental price formation dynamics . The core idea is that with low liquidity, price formation may reflect marginal discretionary activity, whereas with greater liquidity, main fundamental drivers should be better represented .
- Estimated Effect: The study found that after a market-making intervention in 2017, the buy and sell volumes had "more intuitive and distinct effects upon price formation, compared to previously"  (Kanamura & Bunn, 2022). This intervention involved the nine large Regional Electric Power Companies (REPCs) promoting market-making by placing bids and offers at competitive prices (gross bidding) for at least 10% of their transaction volume in the day-ahead auction . This led to a "more balanced market with buy and sell side regime drivers behaving more consistently with improved market efficiency" . The intervention also resulted in temperature information being "more coherently embedded in price and volatility fundamental modelling" . The authors conclude that the market-making intervention led to a "more fundamental price formation model" .

### Buy-Back Bidding Behavior by Incumbent Utilities

The paper discusses the buy-back bidding behavior of incumbent utilities, particularly in the context of "gross bidding" and potential strategic actions:
- Gross Bidding and Repurchase: The former general electric utilities were directed to promote market-making by placing bids and offers at competitive prices ("gross bidding")  (Kanamura & Bunn, 2022). However, these utilities sometimes act in a profit-maximizing manner by selling positions to JEPX but "without fulfilling their obligated repurchase positions due to high JEPX market prices" .
- Impact on Price Spikes: This behavior, specifically the "reduction of the buyback from the generators under gross bidding scheme during spiky price periods," is cited as a reason for increased interspersed showing of the sell-side regime during heat waves (e.g., summer 2018 and 2019)  (Kanamura & Bunn, 2022). This suggests that utilities might strategically avoid buying back energy at high prices, thereby exacerbating price spikes.

### Implications for Treating 2021 Episode as Fuel-Driven vs. Renewables-Driven

This paper's findings have several implications for how a 2021 episode might be interpreted:
- Market Structure and Imperfect Competition: The study highlights that the Japanese electricity market has historically been an oligopoly, with former general electric utilities monopolizing area markets. This imperfect competition could influence JEPX spot prices  (Kanamura & Bunn, 2022). If the market structure remained similar in 2021, price spikes could be influenced by strategic behavior of market participants rather than purely fuel or renewables dynamics.
- Market-Making Impact: The market-making intervention from 2017 onwards aimed to improve liquidity and fundamental price formation  (Kanamura & Bunn, 2022). If this intervention was successful, then price formation in 2021 should ideally reflect fundamentals more coherently. However, the study notes that variables used did not fully explain observed price changes, suggesting other factors determine electricity prices .
- Data Limitations: The study's data ends in March 2020, and it explicitly mentions that "the second half of FY 2019, power trading was unusually affected by COVID-19"  (Kanamura & Bunn, 2022). This implies that market conditions in 2020 and 2021 might have been subject to unique external shocks not fully captured by the model, making it difficult to solely attribute price movements to fuel or renewables without considering these other factors.

### Data Needed for Volatility Regression Control

To control for the effects discussed in a volatility regression, the authors' model incorporates several variables and parameters:
- JEPX Price Data: The independent variable is the JEPX day-ahead spot price, either as an hourly weighted average (national) or a simple average of 30-minute periods (area)  (Kanamura & Bunn, 2022).
- Renewable Output Data: Hourly wind and solar PV electricity generation data are included, calculated as the sum of generation from nine areas  (Kanamura & Bunn, 2022).
- Control Variables: The models include:
- Demand: Hourly electricity demand.
- Lagged Prices: Prices from 24 hours prior, 7 days prior, and the average of the previous day  (Kanamura & Bunn, 2022).
- Price Volatility: Standard deviation of spot prices for the same hour over the past five days  (Kanamura & Bunn, 2022).
- Fossil Fuel Price: A variable for fossil fuel prices  (Kanamura & Bunn, 2022).
- Dummy Variables: Indicators for Summer, Winter, Daytime, Holiday, Gross bidding, and Implicit auction  (Kanamura & Bunn, 2022).
- Temperature: Used as a regime switching driver and a surrogate variable for demand and supply, influencing transition probabilities between scarcity regimes  (Kanamura & Bunn, 2022) .
- Buy-Sell Volumes: The balance of buy-sell volumes submitted to the JEPX day-ahead auction, which determines whether price formation is predominantly driven by buyers or sellers  (Kanamura & Bunn, 2022).
In summary, the paper provides a detailed econometric framework for understanding JEPX price formation, emphasizing the role of market-making and strategic bidding behavior. While it doesn't directly address a January 2021 spike, its analysis of market structure, liquidity, and the impact of various control variables offers a robust foundation for future econometric studies on price volatility.
