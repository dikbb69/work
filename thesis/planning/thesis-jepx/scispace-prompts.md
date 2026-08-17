# SciSpace貼り付け用プロンプト集（セットA〜D）

作成: 2026-07-28。[scispace-credit-plan.md](scispace-credit-plan.md) の§3〜4を実際の操作単位に展開した完全版。**このファイルからコピペして使う。**

## 0. 運用の基本

### DOIを渡して入手させられるか？
- **可能（ただし条件付き）**: Literature Review画面の論文検索・「Add papers」でDOIやタイトルを入れると、SciSpaceのコーパスから該当論文を表に追加できる。
- **限界**: SciSpaceが自力で読めるのは**オープンアクセス論文の本文＋有料論文の抄録まで**。ペイウォール論文（今回のリストの大半＝Elsevier系）はDOI追加だと**抄録ベースの浅い抽出**になる。
- **結論の使い分け**:
  - 有料論文（Energy Economics / Energy Policy / Econometrica等）→ **一橋アクセスでDLしたPDFをアップロード**（今やっている方法が正解）
  - OA論文（Maekawa=MDPI、Sakaguchi=Frontiers、Shin&Lee=MDPI、arXiv/SSRN/NBER版）→ DOI・タイトル追加でも本文まで読める
  - Karaduman WP → PDFを直接アップロード

### 操作手順（各セット共通）
1. My Libraryにフォルダ `SetA` 〜 `SetD` を作成し、PDFを振り分けてアップロード
2. フォルダを選択して Literature Review（一覧表）を開く
3. 「Add column」→ Custom column で、下の**列プロンプトを1列ずつ**追加（列名も英語のままにするとCSVが扱いやすい）
4. 表が埋まったら**その場でCSVエクスポート** → `thesis-jepx\literature\` に保存
5. コア論文だけ個別に Chat with PDF を開き、**質問バッテリー**を投げる → 回答をmdにコピペ保存

### 精度を上げるコツ
- 各列プロンプトの末尾に付けている `Quote the exact sentence(s) from the paper that support your answer.` は削らない（幻覚対策。引用が出ない回答は疑う）
- 回答を日本語にしたい場合は末尾に `Answer in Japanese.` を追加（抽出精度は英語出力の方が安定するので、まず英語で出して必要な列だけ日本語化を推奨）
- 数値・式は必ず原文PDFの該当ページで目視確認してから計画書・論文に転記

---

## 0.5 統一スキーマ（フォルダ別に列を分けられない場合の推奨解）

SciSpaceの列スキーマがライブラリ／レビュー間で共通化されてしまう場合は、**全41本を1つの表に入れ、以下の13列を一度だけ設定**する。該当しない論文には「n/a」と答えるよう各プロンプトに組み込み済み。セット別の分割・整形はエクスポート後にClaude側で実施。

| 列名 | プロンプト |
|---|---|
| Market & Sample | Which market(s), country, and sample period does this paper study? Include data frequency (hourly, half-hourly, daily). For theory/method papers with no data, answer "n/a (theory/method)". |
| Paper Type & Question | Classify the paper (empirical / theory / structural-equilibrium / methodology / review) and state its research question in one sentence. |
| Dependent Variable & Volatility Definition | What is the main dependent variable or object of analysis (price level, volatility, spread, spike probability, storage value, equilibrium capacity)? If volatility is analyzed, quote the exact definition and construction. Otherwise answer "n/a". |
| Method & Specification | What method is used (GARCH variant, quantile regression, LP/DP optimization, structural estimation, real options)? Name the exact specification or write the key equation. |
| Wind vs Solar Effects | Does the paper estimate separate effects of wind and solar on prices or volatility? Report sign and magnitude of each, quoting key coefficients. If not applicable, answer "n/a". |
| Storage Treatment | If the paper models storage: is it a price-taker or price-maker? Is capacity exogenous or endogenous (free entry)? Which revenue streams are included (arbitrage, ancillary, capacity payments)? If storage is not modeled, answer "n/a". |
| Equilibrium Concept | What equilibrium concept is used (zero-profit free entry, system cost minimization, Cournot/strategic, none)? Write the equilibrium condition if stated. If none, answer "n/a". |
| Cost & Financial Assumptions | What cost/financial assumptions are used: capital cost, discount rate or WACC, lifetime, round-trip efficiency, degradation? Make a compact list. If none, answer "n/a". |
| Identification & Endogeneity | How does the paper address endogeneity (instruments such as weather, natural experiments, structural assumptions)? How is curtailment treated, if at all? If not applicable, answer "n/a". |
| Institutional Features | Which institutional features are discussed: negative prices or price floors, interconnectors, market rules (for Japan: the 0.01 yen/kWh floor, gross bidding, the January 2021 spike)? Quote relevant passages. If none, answer "n/a". |
| Key Quantitative Result | State the single most important quantitative result in one sentence with numbers. Quote the exact supporting sentence from the paper. |
| Japan & Storage Relevance | Does the paper contain any results or discussion specific to Japan or Hokkaido, or any mention of batteries/storage/flexibility resources? Quote all such passages. If none, answer "none". |
| Limitations & Gap | What limitations and future research do the authors state (quote them)? In one sentence: what does this paper NOT do that a study of battery free-entry equilibrium and price volatility in Hokkaido would need? |

運用メモ:
- 1つの表に41本入れてこの13列を設定すると、41×13=533セルの抽出が走る。クレジット消化が目的なのでこれで良い
- エクスポートは列設定後に抽出が完了してから。**必ず当日中にCSV保存** → `literature\unified_review.csv`
- 個別チャット（§1.2, §2.2, §3.2, §4）はこの表とは別に、これまで通り論文単位で実施

---

## 1. セットA（再エネ→ボラティリティ実証・11本）

### 1.1 Literature Review表のカスタム列（11列）

| 列名 | プロンプト |
|---|---|
| Market & Period | Which electricity market(s) and sample period does this paper analyze? Include country, market operator, and data frequency (hourly, half-hourly, daily). |
| Dependent Variable | What is the dependent variable? Distinguish between price level, realized volatility, conditional variance, intraday spread, and spike probability. Quote the exact definition. |
| Volatility Definition | How exactly is volatility defined and constructed (e.g., GARCH conditional variance, realized volatility from intraday prices, daily range)? Quote the formula or definition sentence. |
| Method | What econometric method is used (GARCH variant, quantile regression, distributed lag, panel)? Name the exact specification (e.g., GARCH(1,1)-X with exogenous regressors in both mean and variance equations). |
| Wind vs Solar | Does the paper estimate separate effects for wind and solar? Summarize the sign and magnitude of each effect on price level and on volatility. Quote key coefficient values. |
| Identification | How does the paper address endogeneity between renewable output and prices? Any instruments (weather variables) or natural experiments? If none, say "none". |
| Controls | Which control variables are included (fuel prices, demand, interconnector flows, seasonality)? |
| Price Floor / Negative Prices | How does the paper handle negative prices or price floors (censoring, Tobit, separate probability models)? If not discussed, say "not discussed". |
| Time-Scale Decomposition | Does the paper distinguish volatility at different time scales (intraday vs daily vs weekly)? Summarize findings per scale. |
| Key Result | State the single most important quantitative result in one sentence with numbers. Quote the supporting sentence. |
| Limitations & Future Work | What limitations and future research directions do the authors state? Quote them. |

### 1.2 個別チャット（コア4本のみ）

**Ketterer (2014)** — 第1部GARCH-X設計の直接テンプレート:
```
1. Write out the full GARCH model specification including how wind generation enters the mean equation and the variance equation. Use the paper's own notation and equation numbers.
2. How is wind generation measured (level, share of demand, forecast vs actual)? Quote the definition.
3. Report the estimated coefficients on wind in the mean and variance equations with significance levels.
4. What does the paper find about the 2010 market design change (direct marketing) and volatility? Quote the passage.
5. What data cleaning steps are applied (outliers, negative prices, seasonality removal)? List them in order.
```

**Rintamäki, Siddiqui & Salo (2017)** — 時間スケール分解の設計:
```
1. How exactly are daily and weekly realized volatility constructed from hourly prices? Write the formulas with the paper's notation.
2. What model is used to relate wind/solar to volatility (SARMAX / distributed lag)? Write the specification.
3. Why does wind decrease daily volatility in Denmark but increase it in Germany? Summarize the mechanism the authors propose, with quotes.
4. What are the solar results for Germany, by time scale?
5. Which features of a market (interconnection, hydro, market size) do the authors say determine the sign of the effect? Quote the passages.
```

**Wozabal, Graf & Hirschmann (2016)** — U字型の理論的基礎:
```
1. Explain the theoretical model that generates a non-monotonic (U-shaped) relationship between intermittent renewable capacity and price variance. What role does the convexity of the merit order curve play? Quote key passages.
2. At what penetration levels does variance decrease vs increase according to the model and the empirical results?
3. What data and estimation approach are used for the empirical part?
4. What assumptions about demand and supply curves drive the results, and what would break them?
```

**Schöniger & Morawetz (2022)** — U字の実証とその決定要因:
```
1. How is the U-shaped relationship between the share of variable renewables and price variance specified and tested? Write the regression specification.
2. In which countries is the U-shape confirmed, and where is the minimum of the U located (renewable share range)?
3. How do exports/imports (interconnection) and flexible generation affect price variance relative to renewable output variability itself? Report the comparative magnitudes.
4. What policy conclusion do the authors draw about the timing of flexibility investment? Quote it.
```

---

## 2. セットB（蓄電池の経済学・均衡・13本）

### 2.1 Literature Review表のカスタム列（10列）

| 列名 | プロンプト |
|---|---|
| Market & Period | Which market and time period does this paper study? |
| Storage Treatment | Is storage modeled as a price-taker or price-maker? Is storage capacity exogenous or endogenously determined by entry/investment? Quote the modeling assumption. |
| Equilibrium Concept | What equilibrium concept is used (zero-profit free entry, system cost minimization, Cournot/strategic, none)? Write the equilibrium condition if stated as an equation. |
| Price Impact | How is storage's impact on the price distribution modeled or estimated? Report estimated magnitudes (e.g., price change per MWh of storage). |
| Revenue Streams | Which revenue streams are included: energy arbitrage only, ancillary services, capacity payments, subsidies? |
| Cost Assumptions | What cost assumptions are used: capital cost per kWh or kW, discount rate / WACC, lifetime, round-trip efficiency, degradation? Make a table. |
| Cannibalization | What does the paper find about declining marginal revenue as storage capacity grows? Report the rate of decline with numbers. |
| Key Result | The single most important quantitative result in one sentence with numbers, with a supporting quote. |
| Computation & Data | What computational method (LP, dynamic programming, structural estimation) and data are required to replicate the analysis? |
| Limitations | Stated limitations and future work, quoted. |

### 2.2 個別チャット

**Butters, Dorsey & Gowrisankaran (2025)**・**Karaduman**・**Schmalensee (2022)**・**Andrés-Cerezo & Fabra (2023)** の4本は [scispace-credit-plan.md](scispace-credit-plan.md) §4.1〜4.3・4.5 のバッテリーをそのまま使用。

**Lamp & Samano (2022)** — 蓄電池→スプレッド圧縮のイベントスタディ設計（第1部RQ2の直接のひな形）:
```
1. What is the empirical design for identifying the effect of battery storage on price spreads and short-term market outcomes? Specify the regression, treatment variable, and control group.
2. How large is the estimated spread compression, and over what horizon? Quote the numbers.
3. What do the authors find about the gap between actual battery operation and optimal arbitrage? How is "optimal" defined?
4. What data granularity is used, and what would be the minimum data needed to replicate this in another market?
5. What threats to identification do the authors discuss (battery siting endogeneity, concurrent policy changes)?
```

**Sioshansi et al. (2009)** — 価格テイカーLPバックテストの原型:
```
1. Write out the optimization problem for the price-taking storage arbitrageur (objective, constraints, notation).
2. How does arbitrage value change with storage duration (hours of capacity)? Report the numbers.
3. How does large-scale storage affect the price spread itself in their welfare analysis (the self-cannibalization mechanism)?
4. What round-trip efficiency and other technical parameters are assumed?
```

---

## 3. セットC（日本・JEPX・9本）

### 3.1 Literature Review表のカスタム列（10列）

| 列名 | プロンプト |
|---|---|
| Sample & Areas | Which JEPX areas (system price, Hokkaido, Kyushu, etc.) and fiscal years are analyzed? What data frequency (30-min slots, daily)? |
| Dependent Variable | Price level, volatility/variability, spike probability, or spread? Quote the exact definition. |
| Method | Econometric specification (OLS, quantile regression, GARCH, machine learning). Write the key equation. |
| Renewable Variables | How are solar and wind measured (actual output, share, potential output)? Are effects estimated separately by area? |
| Hokkaido-Specific Results | Report any results specific to the Hokkaido area, quoted. If none, say "none". |
| Storage / Flexibility | Does the paper mention batteries, pumped hydro, interconnectors, or other flexibility resources? Quote all such passages. |
| Institutional Features | Which JEPX institutional features are discussed (0.01 yen floor, gross bidding, market making, curtailment rules)? |
| 2021 Spike Treatment | How does the paper treat the January 2021 price spike episode (dummy, exclusion, main subject)? |
| Key Result | The single most important quantitative result with numbers and a supporting quote. |
| Gap for This Thesis | What does this paper NOT do that a study of battery-entry equilibrium and price volatility in Hokkaido would need to do? |

### 3.2 個別チャット

**Fuke & Ohashi (2025)** — [scispace-credit-plan.md](scispace-credit-plan.md) §4.4の7問をそのまま使用（回答は差別化3列表 `literature\fuke-ohashi-differentiation.md` に整理）。

**Sakaguchi & Fujii (2021)** — 北海道の先行係数の抽出:
```
1. Report the estimated merit-order effects of wind and solar by region, especially for Hokkaido, with coefficient values and units (yen/kWh per GWh).
2. How did the effects change between FY2016 and FY2019?
3. What do the quantile regression results say about effects on high-price quantiles (spikes) vs low-price quantiles, by technology?
4. What is the exact data construction: which JEPX price, which renewable output data source, what controls?
5. What limitations do the authors state, and do they mention batteries or storage at all?
```

**Kanamura & Bunn (2022)** — 2021年1月高騰の統制設計:
```
1. What mechanism do the authors identify behind the January 2021 JEPX price spike? Summarize with quotes.
2. How is market making modeled, and what is the estimated effect of market-making volumes on price formation?
3. What do the authors say about buy-back bidding behavior (e.g., 999 yen bids) by incumbent utilities?
4. What implications does this paper have for treating the 2021 episode as fuel-driven rather than renewables-driven in an econometric study? 
5. What data would be needed to control for these effects in a volatility regression?
```

---

## 4. セットD（手法・投資評価・8本）

比較表の価値が薄いセットなので、**表は作らず個別チャットのみ**にクレジットを使う（作るなら列は Market & Period / Method / Key Contribution / Applicability to JEPX の4列で十分）。

**Weron (2014)**:
```
1. Summarize the five model classes for electricity price modeling (multi-agent, fundamental, reduced-form, statistical, AI) with one representative model each.
2. Which model classes are recommended for volatility analysis rather than point forecasting?
3. What does the review say about regime-switching and jump-diffusion models for spike modeling — strengths and estimation pitfalls?
```

**Lago et al. (2021)** — 実証作法チェックリスト化:
```
1. List the best practices for electricity price model evaluation as a checklist: training window, rolling/recalibration scheme, test period length, benchmark models, statistical tests (Diebold-Mariano, Giacomini-White).
2. What open-access tools and datasets does the paper provide (epftoolbox)?
3. What common methodological mistakes in the literature do the authors identify?
```

**Corsi (2009)**:
```
1. Write out the HAR-RV model specification with notation, and explain the heterogeneous market hypothesis behind it.
2. How is realized volatility constructed from intraday data, and what sampling issues are discussed?
3. Why can HAR-RV be estimated by OLS, and how does forecast performance compare to GARCH-type and long-memory models?
```

**Shin & Lee (2024)**:
```
1. Describe the full LSMC pipeline for the battery investment timing decision: state variables, revenue process assumption, regression basis functions, exercise decision.
2. What revenue process is assumed (GBM?) and what are its estimated parameters?
3. What is the size of the option value relative to NPV in their results?
4. What limitations do the authors acknowledge about the revenue process assumption?
```

**Leahy (1993) ＋ Grenadier (2002)** — 競争がオプション価値を侵食する命題（両方アップロードして横断で質問）:
```
1. State precisely the result that competitive entry erodes the option value of waiting, and the conditions under which the myopic NPV rule becomes optimal in competitive equilibrium. Quote the propositions.
2. Under what deviations from perfect competition (finite firms, entry barriers) does option value survive?
3. How would these results apply to battery storage entry where each entrant's arbitrage compresses the price spread available to later entrants?
```
（3問目はSciSpaceに考察させる質問。回答は鵜呑みにせず、第2部§2.3の論理と突き合わせる）

**Fanone, Gamba & Prokopczuk (2013)**:
```
1. How are negative day-ahead prices modeled (which stochastic process, which distribution)? Write the model.
2. How is the model estimated and what are the key parameter estimates?
3. Which elements of this approach transfer to a market with a price floor at 0.01 yen/kWh instead of negative prices (censoring analogy)? What would need to change?
```
（3問目も考察質問。JEPXの下限打ち切り設計の壁打ち用）

**Jiang & Powell (2015)** は精読不要（第2部で完全予見LPを採る決定済みのため）。表の4列だけ埋めれば十分。

---

## 5. 保存先の対応表

| 成果物 | 保存先 |
|---|---|
| セットA〜C のLiterature Review表CSV | `literature\setA_review.csv` 〜 `setC_review.csv` |
| コア論文のチャットQ&A | `literature\notes\<第一著者年>.md`（例: `ketterer2014.md`） |
| Fuke & Ohashi差別化3列表 | `literature\fuke-ohashi-differentiation.md` |
| ギャップ検索の結果 | `literature\novelty-check.md` |
| BibTeX | `literature\references.bib` |
