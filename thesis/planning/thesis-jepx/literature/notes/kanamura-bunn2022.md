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

## 原典精読（2026-09-29）
- 書誌: Energy Economics, 107, 105765, doi:10.1016/j.eneco.2021.105765（受理 2021-12-09、公開 2022-01-05、京都大学 GSAIS／London Business School）
- 出所: Google Drive 参考研究_20260728/SetC（原文精読 2026-09-29）
- **上の SciSpace ログへの訂正**: 「Data Needed for Volatility Regression Control」節に列挙された変数（Wind/PV 発電量、Oil、Gross bidding／Implicit auction ダミー等）は Sakaguchi & Fujii (2021) の変数であり、Kanamura & Bunn (2022) には含まれない。本論文の変数は価格、買い入札量、売り入札量、気温のみ（Table 26）。引用時は混同しないこと。

### 1. 問いと貢献（著者の主張する新規性）
- 問い: 2017 年 4 月のマーケットメイク介入（旧一電によるグロスビディング）は JEPX の「ファンダメンタルな価格形成」を改善したか。ビッドアスク・参加者数・チャーンといった通常指標は板寄せ市場では観察しにくいため、モデルベースで「価格がファンダメンタルズ（需給・気温）により整合的に反応するようになったか」を検定する。
- 主張する新規性: 買い−売り入札量差（scarcity）を Inverse Box–Cox 関数で価格に写像し、気温依存の遷移確率をもつ2レジーム切替でモデル化（"The main novelty of the formulation however is the modelling of buy–sell volumes"）。結論: 2017 年以降「the buy and sell volumes had more intuitive and distinct effects upon price formation」、気温情報が価格とボラティリティに整合的に埋め込まれた。

### 2. データ・市場・期間
- JEPX 前日市場システムプライス、買い入札量 B_t、売り入札量 S_t（コマ別）、東京気温。FY2015–FY2019（2019 年は 2020-03-08 まで、脚注9）。介入前 = FY2015–16、介入後 = FY2017–19。
- Table 3: 買い超過（B_t > S_t）のコマの比率 FY2015 5.36%、2016 20.63%、2017 33.56%、2018 51.77%、2019 60.08%。買い超過の最大値 6.8 → 20.2 百万 kWh。30℃超の比率（6–9月）10.04／7.51／8.78／15.71／10.69%。
- 脚注23: グロスビディングは任意で強制力がない。脚注25: METI (2018) によれば 2017 年 8–12 月に平均約 960 MWh/コマのグロスビディング売り入札が買い戻されなかった。

### 3. 手法
- scarcity BS_t = B_t − S_t。価格 P_t = f(BS_t) = (1 + θ BS_t/…)^{1/θ} 型の IBC 関数（式1、抽出テキストで記号が崩れているため原 PDF 参照）。
- BS_t は年次正弦波＋日内・週内周期をもつ平均回帰過程で、レジーム1／2で平均回帰係数・ボラティリティが異なる（式2）。遷移確率は気温の 18℃ からの乖離に依存（TDTP モデル）。比較モデル: 定数遷移確率（CTP）、MS-GARCH(1,1)、発電スタックモデル（Table 10）。
- 「変動性」は BS_t のレジーム別 σ とそれを IBC で変換した価格ボラティリティ。Table 11 で気温と価格がボラティリティに与える符号を解析。
- 検証: FY2018 のローリング予測で MAE 1.611、RMSE 2.204（§4）。

### 4. 主要結果（数値）
- Table 9（レジームの期待持続時間、コマ数）: FY2015 需要主導 2.255／供給主導 16.893；FY2016 2.556／17.402；FY2017 供給主導 2.869／需要主導 25.464；FY2018 3.679／31.283；FY2019 3.852／37.320。→ 介入前は供給主導レジームが長く、介入後は需要主導レジームが長い（「市場メイクが小売の買い参加を引き出した」）。
- Table 11（気温→ボラティリティの符号、夏）: FY2015 +、2016 −、2017 +、2018 +、2019 +。介入後は一貫して正。
- FY2018・19 の夏（猛暑）に売り側レジームが散在するのは「reduction of the buyback from the generators under gross bidding scheme during spiky price periods」（§4, 脚注25）。
- 結論（§5）: 「In 2015 and 2016, there was an excess of sell-side volumes and throughout the years the model indicated no predominance of the buy-side driver. With market-making requiring the generators to post both buy and sell volumes from 2017, the market dynamic revealed a more balanced and interspersed sequence of buy and sell side pressures.」

### 5. 著者が挙げる限界・今後の課題
- レジーム切替モデルは過学習・誤特定に脆弱。レジーム確率のパターン差に他の理由がありうる。
- モデルベース分析は「市場がどう機能しているかの indication」に過ぎず、流動性の伸び・新規参入・派生商品の活性化など他の証拠と併せて評価すべき。
- ファンダメンタル変数の透明性が限られ気温を代理に用いる（脚注21: 全国の気温差は無視）。FY2019 後半は COVID-19 の影響。

### 6. 本研究との関係（精読後の更新）
- 引用予定箇所: 第3章制度（グロスビディング＝マーケットメイクの制度史と、任意性・買戻し行動の実態；Table 3 の買い超過比率の推移で「JEPX が売り手市場から買い手市場へ転じた」事実）、第2章2.3（右裾のボラティリティが需給逼迫（scarcity）と気温で説明されるという構造の先行例）、第6章（政策くさびとしての市場メイク：市場の「信頼」が参加を呼ぶという議論）。
- 支持する点: 本研究が FY2016–19 と FY2023–25 を分ける際、FY2017 の介入で価格形成の構造が変わった（Sakaguchi & Fujii の Gross bidding ダミー +1.547 と併読）ことの根拠。「気温→ボラティリティが介入後に一貫して正」は、本研究の右裾（τ=0.9）が需要側要因で動くという解釈と整合。
- 対立点／注意: システムプライスのみで北海道は対象外。再エネ変数なし。2021 年 1 月危機は対象外（データは 2020-03 まで）。Rassi & Kanamura (2023) が同モデル系統で FY2020–21 を扱う。
- 手法の源流: 板データ（B_t − S_t）を scarcity 指標に使う発想。本研究では制御変数候補（北海道エリアの売り／買い入札量は JEPX 公開データで入手可）。
- 新規性チェック: 本論文は市場メイクの効果検証。本研究は再エネ（風力）と蓄電池の価値・参入を扱い、市場メイクは制度背景として引用するのみ。

### 7. 引用に使える原文
1. "The result is clarity that after a market-making intervention in 2017, the buy and sell volumes had more intuitive and distinct effects upon price formation, compared to previously."（Abstract）
2. "the durations of supply-driven regimes are longer than those of demand-driven regimes before the year 2017, resulting from insufficient market making. In contrast, the durations of supply-driven regimes became shorter than those of demand-driven regimes after the year 2017."（§4, p.8）
3. "This is mainly due to the reduction of the buyback from the generators under gross bidding scheme during spiky price periods."（§4, p.8）
4. "regime switching models are prone to overfitting and misspecification. There could be other reasons why the regime probabilities exhibit different patterns in the sample years."（§5）
5. "it was found that approximately 960 MWh per half hour trading frame of gross bidding sales bids on average were not repurchased as a result."（脚注25, METI 2018 の引用）
