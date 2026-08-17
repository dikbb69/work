# SciSpaceクレジット使い切りプラン（期限: 約1週間）

作成: 2026-07-28。修論（research-plan-v2）の文献レビュー工程を前倒しで完了させるためにSciSpaceクレジットを投下する計画。

## 原則

1. **エクスポート最優先**: クレジット切れ後もSciSpace上の成果物にアクセスできなくなる可能性がある。作業のたびにCSV / BibTeX / Markdownで書き出してこのフォルダに保存する（`thesis-jepx\literature\` を作って格納）。
2. **使う機能の優先順位**: ①Literature Review表（複数論文からの一括データ抽出）→ ②Chat with PDF（コア論文の精読代行）→ ③Deep Review（見落とし論文の発見）。**AI Writer・Paraphraserには使わない**（修論の文章生成への利用は研究倫理・一橋の規程上リスク。文献処理に全振りする）。
3. **抽出結果は「ポインタ」扱い**: SciSpaceの抽出には誤りが混ざる。数値・命題は必ず原文スニペットで確認してから計画書・論文に転記する。
4. 質問は**英語で投げる**方が抽出精度が高い（下に貼り付け用テンプレートを用意）。

## 1週間の配分

| 日 | 作業 | 成果物 |
|---|---|---|
| Day 1 | PDF収集（一橋の図書館アクセスでDL）→ SciSpaceにアップロード | 論文PDF一式（手元にも保存） |
| Day 2–3 | Literature Review表を4セット作成（下記A〜D、列定義は§3） | CSV × 4 → 修論2章の文献整理表の原型 |
| Day 3–4 | コア5論文のChat with PDF精読（§4の質問バッテリー） | 論文別Q&Aノート（md保存） |
| Day 5 | ギャップ検索（§5のクエリ）＋パラメータ抽出（§6） | 新規性チェックメモ、パラメータ表 |
| Day 6–7 | 残クレジットで追加深掘り＋**全成果物のエクスポート確認** | BibTeX全文献、CSV/mdの最終保存 |

---

## 2. 論文リスト（アップロード対象）

### セットA: 再エネ→価格ボラティリティ（実証の柱）
1. Ketterer (2014) Energy Economics 44 — 10.1016/j.eneco.2014.04.003
2. Woo et al. (2011) Energy Policy 39(7)
3. Rintamäki, Siddiqui & Salo (2017) Energy Economics 62
4. Kyritsis, Andersson & Serletis (2017) Energy Policy 101
5. Wozabal, Graf & Hirschmann (2016) OR Spectrum 38
6. Schöniger & Morawetz (2022) Energy Economics 111, 105960
7. Maciejowska (2020) Energy Economics 85, 104532
8. Paraschiv, Erni & Pietsch (2014) Energy Policy 73
9. Hagfors et al. (2016) Quantitative Finance 16(12)
10. Mwampashi et al. (2021) Energy Economics 100, 105317
11. Navia Simon & Diaz Anadon (2025) Nature Energy 10

### セットB: 蓄電池の経済学・均衡（構造モデルの柱）
1. **Butters, Dorsey & Gowrisankaran (2025) Econometrica 93(3)**（NBER WP29133版でも可）
2. **Karaduman (2023) WP** — Stanford GSB/MIT CEEPRサイトから無料DL
3. **Schmalensee (2022) The Energy Journal 43(2)**（MIT CEEPR WP 2020-012版でも可）
4. Andrés-Cerezo & Fabra (2023) RAND Journal of Economics 54(1)
5. Sioshansi et al. (2009) Energy Economics 31(2)
6. Sioshansi (2010) The Energy Journal 31(2)
7. Lamont (2013) IEEE Trans. Power Systems 28(2)
8. Lamp & Samano (2022) Energy Economics
9. Hirth (2013) Energy Economics 38
10. Brown & Reichenberg (2021) Energy Economics 100
11. López Prol & Schill (2021) Annual Review of Resource Economics 13（arXiv:2012.15371）
12. Zhao et al. (2022) Applied Energy 325
13. Mercier, Olivier & De Jaeger (2023) Energy Economics 122

### セットC: 日本・JEPX
1. **Fuke & Ohashi (2025) J. Commodity Markets 40**（SSRN 4990073版でも可）※最重要
2. Sakaguchi & Fujii (2021) Frontiers in Sustainability 2:770045
3. Kanamura & Bunn (2022) Energy Economics 107
4. Rassi & Kanamura (2023) Energy Policy 177
5. Ma et al. (2023) Applied Economics 55(18)
6. Ikeda (2019) J. Commodity Markets（RIETI DP 17-E-107版でも可）
7. Li et al. (2024) Energy 307, 132607
8. Maekawa et al. (2018) Energies 11(9):2215
9. Li, Bu, Kopsakangas-Savolainen & Goto (2025) Energy Policy

### セットD: 手法・投資評価
1. Weron (2014) IJF 30(4)
2. Lago et al. (2021) Applied Energy 293
3. Corsi (2009) J. Financial Econometrics（HAR-RV原典）
4. Shin & Lee (2024) Energies 17(9):2019
5. Jiang & Powell (2015) INFORMS J. Computing 27(3)
6. Leahy (1993) QJE 108(4) ＋ Grenadier (2002) RFS 15(3)
7. Fanone, Gamba & Prokopczuk (2013) Energy Economics 35

---

## 3. Literature Review表の列定義（コピペ用・英語）

セットA・C用（実証系）:
```
Market and sample period / Data granularity (hourly, half-hourly, daily) /
Dependent variable (price level, realized volatility, spread, spike probability) /
Volatility definition and construction /
Econometric method (GARCH variant, quantile regression, panel) /
Treatment of solar vs wind (separate coefficients?) /
Identification strategy and instruments /
Control variables (fuel prices, demand, interconnectors) /
Treatment of negative prices or price floors /
Key quantitative result (coefficient magnitudes) /
Stated limitations and future research
```

セットB用（均衡・構造系）:
```
Market and period / Storage treatment (price-taker vs price-maker; exogenous vs endogenous entry) /
Equilibrium concept (zero-profit free entry, cost minimization, Cournot, none) /
Price impact estimation method /
Revenue streams included (arbitrage only? ancillary? capacity payments?) /
Cost assumptions (CAPEX, WACC or discount rate, lifetime, round-trip efficiency, degradation) /
Key quantitative result (equilibrium capacity, revenue decline rate, welfare effects) /
Computational method / Data requirements / Stated limitations
```

## 4. コア5論文のChat with PDF質問バッテリー（コピペ用・英語）

### 4.1 Butters, Dorsey & Gowrisankaran (2025)
```
1. Write out the exact free-entry equilibrium condition (equation numbers) that pins down battery investment. What is the zero-profit condition mathematically?
2. How is the battery's price impact on the wholesale price distribution modeled and estimated? Report the key elasticities (e.g., price effect of first 5,000 MWh vs 25,000-50,000 MWh).
3. What cost assumptions are used: capital cost per kWh, discount rate, lifetime, degradation? Make a table.
4. How do the authors handle the interaction between renewable penetration and battery profitability? At what renewable share does the first battery break even without subsidies?
5. What is computed in the dynamic model vs calibrated vs estimated? List each parameter and its source.
6. What do the authors say about ancillary service revenues and capacity payments — are they included?
7. What are the stated limitations, and what extensions do the authors suggest?
```

### 4.2 Karaduman (WP, South Australia)
```
1. How exactly is the price impact function of storage estimated? What data and what functional form?
2. How is the best response of incumbent (thermal) generators to storage entry modeled?
3. What is the size of the market (average demand) and how does storage size relative to demand map into equilibrium effects?
4. Report the main quantitative findings on private profitability vs social value of storage.
5. What features of South Australia (interconnector limits, renewable share) drive the results? Make a table I can compare with Hokkaido.
```

### 4.3 Schmalensee (2022)
```
1. State the main propositions verbatim with their exact conditions (especially the role of price caps).
2. Under what assumptions does long-run competitive equilibrium coincide with expected-system-cost minimization?
3. How is storage revenue related to fixed cost recovery in equilibrium? Write the condition.
4. What does the paper say about multiple equilibria or non-uniqueness?
```

### 4.4 Fuke & Ohashi (2025) ※差別化メモ用・最重要
```
1. What is the exact definition of "price variability" used? Which quantiles or dispersion measures?
2. Write out the full econometric specification: dependent variable, regressors, interaction terms, estimation method, standard errors.
3. What is the sample: area, period, time granularity? Kyushu only, or other areas too?
4. What are the main findings by season, and what mechanism do the authors propose (correlation between demand and PV output)?
5. Do the authors discuss wind power, batteries, storage, or other flexibility resources at all? Quote any such passages.
6. What do the authors list as limitations or future research directions?
7. Does the paper make any claims about Hokkaido or about equilibrium/entry of flexibility resources?
```
→ 回答は「同じ点/違う点/本研究が埋める点」の3列表に整理して`literature\fuke-ohashi-differentiation.md`に保存（大橋教授との面談資料の素材）。

### 4.5 Andrés-Cerezo & Fabra (2023)
```
1. How do market power and vertical integration distort storage operation and investment? State the two channels.
2. What is the markup rule used by the strategic storage owner? Any closed-form expression?
3. How large are the quantified distortions in the Spanish calibration?
4. What ownership structures are compared, and which is worst for welfare?
```

## 5. ギャップ検索（Deep Review / 検索クエリ）

新規性の最終確認。各クエリの結果は「ヒットした論文＋本研究との距離」を1行ずつメモ:
```
1. battery storage arbitrage JEPX Japan wholesale electricity
2. energy storage free entry equilibrium capacity wholesale market 2024-2026
3. battery storage cannibalization spread compression empirical
4. nuclear restart wholesale electricity price distribution Japan
5. data center electricity demand wholesale price volatility
6. Hokkaido electricity market renewable curtailment
7. storage entry real options grid connection queue
8. capture ratio battery revenue perfect foresight backtest
```
※日本語文献（CiNii・J-STAGE）はSciSpaceのカバレッジ外の可能性が高いので、ここでは英文のみ。和文は別途CiNiiで手動確認。

## 6. パラメータ抽出（Data Extraction機能）

レポート系PDFをアップロードして数値表を抽出:
- Lazard LCOE+ (2025年6月版) → LCOS範囲、資本構成、前提
- NREL Storage Futures 手法文書（NREL/TP-6A20-77449）→ 容量価値とシフト価値の扱い
- （持っていれば）自然エネルギー財団「系統用蓄電池事業の可能性」(2025.7) → 日本のコスト・収益実務値

## 7. エクスポート・チェックリスト（Day 6–7に必ず）

- [ ] Literature Review表 4本 → CSV → `thesis-jepx\literature\`
- [ ] 全文献のBibTeX/RIS → `thesis-jepx\literature\references.bib`
- [ ] Chat with PDFのQ&Aノート → 論文ごとにmd化
- [ ] Fuke & Ohashi差別化メモ → `fuke-ohashi-differentiation.md`
- [ ] ギャップ検索の結果メモ → `novelty-check.md`
- [ ] アップロードしたPDF原本が手元フォルダに残っているか確認
