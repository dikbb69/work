# 研究内容の理解のためのデッキ — 構成とスライド仕様の書き方

目的: 著者（と指導教員）が、本研究の全体像と各分析（何のデータを、どの手法で分析し、何が分かったか）を理解するための資料。発表用ではなく、読んで理解するためのデッキ。各スライドのノート（notes）に、スライドの内容を平易な日本語で説明する台本（200〜500字）を書く。

数値はすべて正式版の原稿（manuscript_v1/。章・節・図表の番号もこれに従う）に一致させ、分析カタログ（notes/34-analysis-catalog.md。番号は v0.4 のもの）で補う。用語: 下限価格（0.01円/kWh）・下限張り付き、完全予見の裁定粗利（完全予見粗利）、実現率（capture率）、実績整合ケース。「床」「PF価値」「必然」「ヘアカット」「負価格」（→負の価格）は使わない。

## 構成（約50枚）

| 区分 | 内容 |
|---|---|
| 0 導入（8枚） | 表紙／この資料の見方／全体像を1枚で（主要な答えの KPI）／研究の問いと答え（主RQ・サブRQ）／論理の流れ（6段）／データの全体像／分析の一覧（章・手法の地図）／ファイナンス手法の使いどころ |
| A 第5章 再生可能エネルギーと価格形成（9枚） | 区切り／価格カーブ／帯域分解／日次回帰と頑健な推論／分位点回帰（MOE の減衰の撤回）／市場分断の分類／空間分散／先行研究仕様の再現（時間スケールで符号が変わる）／主成分分解 |
| B 第6章 蓄電池のスポット裁定価値（6枚） | 区切り／完全予見粗利／実行可能戦略と capture率／オプションとしての層分解／戦略の検定／脚・duration・風力三分位 |
| C 第7章 構造型価格モデルと自由参入均衡（7枚） | 区切り／構造型の価格モデルと検証（仕様A と仕様A′）／フリートの内生化と π(K)／K* と θ*（実績整合への訂正）／感応度（風力・泊・容量収入）／価格モデルの曲線と下限価格の機構／実物オプションの参入閾値 |
| D 第8章 均衡からの乖離と契約の評価（6枚） | 区切り／事実と乖離の勘定（kW）／市場外収入（容量市場・LTDA・補助金）／リスク・リターン（IRR・資本コスト・APV・確実性等価）／CFaR とヘッジ／併設と抑制・損益分岐面 |
| E 第9章 下限価格と負の価格（3枚） | 区切り／下限価格は充電脚のプットの売り／負価格の反実仮想 |
| F 厳密性の確保（5枚） | 区切り／監査の方法（全分析・チェックリスト）／主な訂正と結果（訂正前→訂正後）／ゼミの指摘への対応／前提・捨象と限界 |
| G 結論（4枚） | 結論と含意／今後の課題／用語集／スクリプトと出力の対応 |

## スライドの型（deck_spec.json の slides の要素）

共通の任意フィールド: `section`（左下に出る区分名、例 "第5章 再生可能エネルギーと価格形成"）、`notes`（台本）。文字列の配列（items）の要素は、文字列か `{"t": 文字列, "sub": true（字下げ）, "b": true（太字）, "c": "orange"（色）}`。

- `title`: `title`, `subtitle`, `author`, `date`, `footer`
- `section`: `kicker`（例 "PART A"）, `title`, `body`（items、3〜5行）
- `bullets`: `title`, `msg`（見出しの下の結論の一文、60字以内）, `blocks`: [{`label`, `items`, `h`（高さ in、既定1.4）, `size`（既定12）}]（全体で高さ5.4in 以内）
- `analysis`（各分析の標準形）: `title`（例 "5.3 日次回帰と頑健な推論"）, `msg`, `question`（items、1〜2行）, `data`（items、2〜3行）, `method`（items、2〜4行）, `results`（items、3〜5行）, `figure`（リポジトリからの相対パス。無ければ省略し左の列が全幅になる）, `figcap`, `cardH`（[問い, データ, 手法] の高さ、既定 [0.95,1.25,1.55]）
- `table`: `title`, `msg`, `rows`（1行目が見出し。セルは文字列か {text, b, c, fill, align}）, `colW`（列幅 in、合計12.6）, `bSize`（既定9.5）, `note`
- `flow`: `title`, `msg`, `steps`: [{`head`, `body`, `warm`}]（4〜6個）, `h`（既定3.6）, `below`（items）
- `kpi`: `title`, `msg`, `kpis`: [{`n`（大きな数字・短い答え、14字以内）, `l`（説明、40字以内）, `warm`}]（3〜5個）, `blocks`
- `twocol`: `title`, `msg`, `left`/`right`: {`figure`, `figH`, `figcap`, `label`, `items` か `rows`+`colW`, `size`}

## 字数の目安（はみ出し防止。check_fit.py で検査する）

- analysis の各カード: 問い 1行40字×2行まで、データ 3行、手法 4行、結果 5行（1行は全幅で約95字、図ありの左列は約45字）。
- 結果カードは、図がある場合でも全幅（約120字/行）で、高さに応じて4〜5行。
- 表は1枚に12行程度まで、セルは短く。

## 使える図（figures/hokkaido/）

価格カーブ price_curve_shapes_fy2023-25.png・wind_price_curves_fy2023-25.png、帯域 wind_bands_timeseries.png・band_comparison_hokkaido.png、五分位 gen_vs_price_shape.png、頑健推論 robust_inference_ci.png、空間分散（47 の新しい図があればそれ）、主成分 price_curve_pca.png、完全予見 annual_backtest_series.png、層分解 option_layers.png、戦略 strategy_capture_ci.png、π(K) pi_k_curve_v3.png、感応度 equilibrium_surface.png、供給曲線 supply_curve_net_dist.png、ベースロード baseload_shift_response.png、実物オプション real_option_threshold.png、乖離の勘定 gap_ledger.png、APV apv_decomposition.png、CFaR cfar_decomposition.png、損益分岐 breakeven_frontier.png（または 42 の新しい図）、負価格 negative_price_pi_k.png（または 43 の新しい図）。新しい図は analysis/41〜51 の出力を ls で確かめる。
