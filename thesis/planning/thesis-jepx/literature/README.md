# literature フォルダの内容と品質チェック記録

更新: 2026-07-29

## ファイル構成

| ファイル | 内容 | 由来 |
|---|---|---|
| `doi-list.md` | コア41本の検証済みDOIリスト | Crossref照合済み（A6・A10は7/28修正済み） |
| `unified_review.csv` | 統一スキーマ13列×41本のSciSpace抽出表（全体） | `2026-07-28_09_29_38_export.xlsx` から変換（UTF-8 BOM） |
| `setA_review.csv` 〜 `setD_review.csv` | 上記のセット別分割（A11・B13・C9・D8本） | 同上 |
| `notes/*.md` | Chat with PDFのQ&Aログを論文別に分割した15ファイル | `ChatLog.docx` から機械分割 |

原本（xlsx/docx）は `Downloads\参考研究_20260728\` に残置。PDF本体も同フォルダのSetA〜D。

## 品質チェック結果（2026-07-29実施）

**構成チェック**: 41本すべて表に存在し、セット割当も完全一致。列は統一スキーマ13列＋TL;DR。

**幻覚スポットチェック（コア11本のKey Quantitative Result）**: 事前調査の把握値と整合、うち2件は原文PDFと突合して**完全一致を確認**:
- Wozabal (2016)「PVの分散への影響は風力の約12倍（削減83 vs 7）」→ 原文の該当文と一致
- Karaduman (2023)「価格インパクト無視は収益性を2倍過大評価」→ 原文の該当文と一致
- ほかKetterer（風力シェア+1pp→価格-1.46%）、BDG（再エネ50%で2024年に無補助損益分岐）、Fuke & Ohashi（春夏は変動性低下・秋冬は低下せず）等も既知の値と整合

**既知の弱点**:
- 空セル14件。大半は「Wind vs Solar Effects」×蓄電池/理論論文（n/a相当なので実害なし）。Andrés-Cerezo & Fabraの「Market & Sample」が空（正しくはスペイン市場で定量化）、Rintamäki・Kyritsisの「Cost & Financial Assumptions」が空（実証論文なのでn/a相当）
- SchmalenseeのKey Quantitative Result列が周辺的な記述（S<θRのケースに注目、のみ）。**中心命題（競争均衡＝費用最小化）は個別チャット未実施のため未取得** → 残タスクへ
- `notes/` の数式はdocxエクスポートで崩れている。**式を引用する際は必ず原PDFで確認**

## 残タスク（クレジット期限内に実施すべきもの）

1. **コア5本の個別チャット（最優先・未実施）** — scispace-prompts.md / scispace-credit-plan.md §4.1〜4.5:
   - Butters, Dorsey & Gowrisankaran（均衡条件の式・価格インパクト弾性・パラメータ表）
   - Karaduman（価格インパクト推定法・北海道比較表）
   - Schmalensee（命題の正確な条件）
   - **Fuke & Ohashi（7問 → 差別化3列表の素材。大橋教授面談用）**
   - Andrés-Cerezo & Fabra（市場支配力の2経路・マークアップ）
2. ギャップ検索8クエリ（§5、Deep Review推奨）→ `novelty-check.md` に保存
3. BibTeX/RISの一括エクスポート → `references.bib`
4. （任意）パラメータ抽出: Lazard LCOS等（§6）

## notes/ の対応表

| ファイル | 論文 |
|---|---|
| ketterer2014.md | Ketterer (2014) — GARCH-X仕様・2010年制度変更・データ処理 |
| rintamaki2017.md | Rintamäki et al. (2017) — RV定義式・SARMA仕様・DK/DE機構 |
| wozabal2016.md | Wozabal et al. (2016) — U字理論・メリットオーダー凸性 |
| schoniger-morawetz2022.md | Schöniger & Morawetz (2022) — U字実証・最小分散10–40% |
| lamp-samano2022.md | Lamp & Samano (2022) — イベントスタディ設計・実運用vs最適裁定 |
| sioshansi2009.md | Sioshansi et al. (2009) — LP定式化・duration感応度・自己共食い |
| sakaguchi-fujii2021.md | Sakaguchi & Fujii (2021) — 地域別MOE・分位点結果・データ構築 |
| kanamura-bunn2022.md | Kanamura & Bunn (2022) — 2021年1月機構・999円買い戻し・統制変数 |
| weron2014.md | Weron (2014) — 5類型・RS/ジャンプの注意点 |
| lago2021.md | Lago et al. (2021) — 検証作法チェックリスト・epftoolbox |
| corsi2009.md | Corsi (2009) — HAR-RV仕様・OLS推定 |
| shinlee2024.md | Shin & Lee (2024) — LSMCパイプライン・GBM仮定の限界 |
| leahy-grenadier.md | Leahy (1993)＋Grenadier (2002) — 競争によるオプション価値侵食・蓄電池への応用考察 |
| fanone2013.md | Fanone et al. (2013) — 負値価格過程・0.01円床への読み替え考察 |
| _references.md | チャットの参照文献リスト |
