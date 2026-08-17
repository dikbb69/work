// 進捗報告デッキ v2（2026-08-17）— ユーザーの既存フォーマット（進捗報告_20260727様式）に準拠
// 白背景・Noto Sans JP・青緑パレット・青ヘッダー表・左青バーのセクション見出し
// 文献セクションを8枚に拡充。実行: NODE_PATH=<scratchpad>/node_modules node build_deck_20260817_v2.js

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const F = "Noto Sans JP";
const FB = "Noto Sans JP SemiBold";

const C = {
  green: "70B437",
  lime: "C3D60B",
  blue: "0079C2",
  lightblue: "5DB6E7",
  teal: "176871",
  amber: "FFC000",
  coral: "F27750",
  black: "000000",
  text: "262626",
  gray: "595959",
  line: "D9D9D9",
  tint: "F0F6FB",
  white: "FFFFFF",
};
const PAL = [C.lime, C.teal, C.blue, C.green, C.amber, C.lightblue, C.coral];

let pageNo = 0;
function newSlide() {
  const s = pres.addSlide();
  s.background = { color: C.white };
  pageNo += 1;
  if (pageNo > 1) s.addText(String(pageNo), { x: 12.65, y: 6.95, w: 0.47, h: 0.25, fontSize: 9, color: C.gray, fontFace: F, align: "right", margin: 0 });
  return s;
}
function header(s, title, msg) {
  s.addText(title, { x: 0.37, y: 0.24, w: 12.6, h: 0.42, fontSize: 19, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "middle" });
  if (msg) s.addText(msg, { x: 0.37, y: 0.68, w: 12.6, h: 0.6, fontSize: 13.5, color: C.text, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
  s.addShape(pres.ShapeType.line, { x: 0.37, y: 0.66, w: 12.6, h: 0, line: { color: C.line, width: 0.75 } });
}
function secLabel(s, x, y, label, w) {
  s.addShape(pres.ShapeType.rect, { x, y: y + 0.02, w: 0.05, h: 0.3, fill: { color: C.blue } });
  s.addText(label, { x: x + 0.14, y, w: w || 4.5, h: 0.34, fontSize: 13, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "middle" });
}
function bullets(s, items, x, y, w, h, opts) {
  opts = opts || {};
  const arr = items.map((it) => ({
    text: it.t,
    options: {
      bullet: it.sub ? { code: "2013", indent: 10 } : { code: "25A0", indent: 12 },
      indentLevel: it.sub ? 1 : 0,
      bold: !!it.b,
      color: it.c || C.text,
      breakLine: true,
      paraSpaceAfter: it.gap === 0 ? 0 : (it.gap || opts.gap || 6),
    },
  }));
  s.addText(arr, { x, y, w, h, fontSize: opts.size || 12, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: opts.lsm || 1.2, color: C.text });
}
function litTable(s, rows, x, y, w, colW, opts) {
  opts = opts || {};
  const tr = rows.map((r, ri) => r.map((cell, ci) => {
    const base = typeof cell === "object" ? cell : { text: cell };
    const o = Object.assign({}, base.options);
    if (ri === 0) Object.assign(o, { bold: true, color: C.white, fill: { color: C.blue }, fontSize: opts.hSize || 10.5, valign: "middle" });
    else Object.assign({}, o), Object.assign(o, { color: o.color || C.text, fill: o.fill || { color: ri % 2 === 0 ? C.tint : C.white }, fontSize: o.fontSize || opts.bSize || 10, valign: "middle" });
    return { text: base.text, options: o };
  }));
  s.addTable(tr, Object.assign({ x, y, w, colW, fontFace: F, border: { type: "solid", color: C.line, pt: 0.5 }, margin: 0.05, autoPage: false }, opts.tbl || {}));
}
function quietChart(extra) {
  return Object.assign({
    fontFace: F,
    chartColors: [C.blue],
    showLegend: false, showTitle: false,
    catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
    catAxisLabelFontSize: 9.5, valAxisLabelFontSize: 9,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" },
    dataLabelFontSize: 10, dataLabelColor: C.teal, dataLabelFontFace: F,
    catAxisLineColor: C.line, valAxisLineColor: C.line,
  }, extra || {});
}

// =====================================================================
// 1. 表紙（ユーザー様式: 白・左寄せ・シンプル）
// =====================================================================
{
  const s = newSlide();
  s.addText("修士論文　進捗報告", { x: 0.9, y: 2.7, w: 11.5, h: 0.8, fontSize: 32, bold: true, color: C.black, fontFace: FB, margin: 0 });
  s.addShape(pres.ShapeType.rect, { x: 0.95, y: 3.62, w: 1.9, h: 0.06, fill: { color: C.blue } });
  s.addText("松葉 大希", { x: 0.9, y: 3.95, w: 6, h: 0.4, fontSize: 14, color: C.text, fontFace: F, margin: 0 });
  s.addText("2026.08.17", { x: 0.9, y: 4.35, w: 6, h: 0.4, fontSize: 12, color: C.gray, fontFace: F, margin: 0 });
  s.addText("北海道の初期実証と先行研究の整理 — 均衡容量K*へ向けた今後の方針", { x: 0.9, y: 5.1, w: 11.5, h: 0.4, fontSize: 13, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 2. 現在の課題（ユーザー様式: 3ブロック）
// =====================================================================
{
  const s = newSlide();
  header(s, "現在の課題");

  secLabel(s, 0.6, 1.05, "前回までの発表内容");
  bullets(s, [
    { t: "テーマ: JEPXスポット市場における蓄電池のオプション価値算定。前日10時の一括約定（48コマ同時決定）という情報構造をどう扱うかが論点" },
    { t: "九州10年半（FY2016〜26）の実績で、完全予見ベースの価値算定＋価値減少の要因分解を実施。対象を北海道×風力へ転換する方針を宣言" },
  ], 0.75, 1.45, 11.9, 1.15, { size: 12.5 });

  secLabel(s, 0.6, 2.75, "前回からの進捗（本日の報告範囲）");
  bullets(s, [
    { t: "① 北海道の初期実証: 需給実績×価格の10年パネルを構築し、九州の分析一式を移植＋風力向けに拡張", b: true },
    { t: "② 先行研究の体系的整理: コア41本（DOI検証・PDF収集・抽出表・数値チェック済み）を6系譜で整理し、本結果と対応づけ", b: true },
    { t: "③ 均衡推定の部品の実測: 容量市場（調整係数・需要曲線）・LTDA約定・蓄電池資本費（METI実勢価格）を一次資料で確定", b: true },
  ], 0.75, 3.15, 11.9, 1.55, { size: 12.5 });

  secLabel(s, 0.6, 4.85, "本日の発表の位置づけ");
  bullets(s, [
    { t: "実証と文献の両面から「北海道×風力×蓄電池の均衡容量」という空白を確認し、主張の型（無裁定・均衡整合性命題）と今後の工程について討議いただく" },
    { t: "今後: 蓄電池フリートを価格過程に内生化 → π(K)曲線 → 均衡容量K*の初回推計へ" },
  ], 0.75, 5.25, 11.9, 1.3, { size: 12.5 });
}

// =====================================================================
// 3. 実証1: データ基盤
// =====================================================================
{
  const s = newSlide();
  header(s, "北海道の初期実証（1/4）データ基盤", "需給実績×価格の10年パネルを自前構築し、外部情報との突合（検証アンカー）で品質を確認した");

  secLabel(s, 0.6, 1.4, "構築したデータ");
  bullets(s, [
    { t: "北海道・東北の需給実績（TSO公表・新旧様式を統合）＋JEPXエリアプライス: 2016/4〜2026/6・約9万時間" },
    { t: "FIT/FIP認定量（B表45四半期分）から太陽光・風力の導入量系列を構築 → 設備利用率（cf）過程を抽出" },
    { t: "北海道の現在地: 太陽光234万kW（2025/3末）・風力130万kW（2024年末、直近2年で倍増）・風力/需要比は全国最大級", b: true },
  ], 0.75, 1.8, 11.9, 1.6, { size: 12.5 });

  secLabel(s, 0.6, 3.55, "検証アンカー（外部情報との突合）");
  litTable(s, [
    ["検証項目", "パネル側", "外部情報", "判定"],
    ["出力制御の初発生日", "北海道 2022/5/8・東北 2022/4/10", "各TSO公表", "一致"],
    ["2018/9 価格欠測480時間", "9/6〜9/26に欠測集中", "胆振東部地震ブラックアウト（史実）", "整合"],
    ["風力導入量（2016/23/24年末）", "32.0 / 86.4 / 130.0万kW", "JWPA: 36 / 83 / 128万kW", "整合"],
    ["太陽光導入量（2025/3末）", "234.3万kW", "系統WG 接続量 236万kW", "整合"],
  ], 0.6, 3.95, 12.13, [3.1, 3.4, 4.1, 1.53], { hSize: 11, bSize: 10.5, tbl: { rowH: 0.42 } });

  s.addText("出所: 北海道電力NW・東北電力NW 需給実績、JEPX、FIT/FIP情報公表用ウェブサイト、JWPA、次世代電力系統WG", { x: 0.6, y: 6.55, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 4. 実証2: 価格構造
// =====================================================================
{
  const s = newSlide();
  header(s, "北海道の初期実証（2/4）価格構造", "床コマは九州の約半分だが、裁定価値は九州並み — 価値の源泉が「昼の床」から「夕方スパイク」に交代している");

  bullets(s, [
    { t: "床コマ（0.01円/kWh）は年473コマ ＝ 九州の約半分。ダックカーブは形成途上（昼の窪みが浅い）", b: true },
    { t: "完全予見4h裁定価値（PF）は0.96〜1.15万円/kW-年で九州と同水準", b: true },
    { t: "九州: 昼の床（安値側）が源泉 ／ 北海道: 夕方スパイク（高値側）が源泉", sub: true },
    { t: "市場分断の方向が逆転しつつある（右図）", b: true, gap: 4 },
    { t: "高値分断（道内＞本州）87〜92% → 約60%。安値分断が1〜5% → 約30%に拡大", sub: true },
    { t: "＝ 余剰の輸出制約（北本連系線）の顕在化。連系線と蓄電池は同じスプレッドを食い合う競合", sub: true },
  ], 0.6, 1.5, 6.7, 3.6, { size: 12, gap: 8 });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 5.5, w: 6.6, h: 1.1, fill: { color: C.tint } });
  s.addText([
    { text: "含意: ", options: { bold: true, color: C.teal } },
    { text: "北海道は「九州の後追い」ではない。風力・スパイク・分断という別の構造 — 九州の枠組みをそのまま当てはめられない", options: { color: C.text } },
  ], { x: 0.85, y: 5.5, w: 6.15, h: 1.1, fontSize: 11.5, fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });

  secLabel(s, 7.6, 1.45, "市場分断の方向転換（コマ構成比・%）", 5.2);
  s.addChart(pres.ChartType.bar, [
    { name: "FY2016-19", labels: ["高値分断", "連系", "安値分断"], values: [89.5, 7.5, 3.0] },
    { name: "FY2023-25", labels: ["高値分断", "連系", "安値分断"], values: [60.0, 11.0, 29.0] },
  ], quietChart({
    x: 7.6, y: 1.95, w: 5.1, h: 4.3,
    chartColors: [C.lightblue, C.teal],
    barGrouping: "clustered",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"",
    valAxisMaxVal: 100, valAxisMajorUnit: 25, valAxisFormatCode: "0",
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: C.gray,
  }));
  s.addText("システムプライス±0.01円で判定。グラフデータは別添Excel「分断方向転換」シートで編集可", { x: 7.6, y: 6.35, w: 5.1, h: 0.4, fontSize: 8.5, color: C.gray, fontFace: F, margin: 0 });
  s.addText("床コマ・分断はエリアプライス30分値から集計。PF価値＝完全予見・4時間・往復効率0.85", { x: 0.6, y: 6.85, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 5. 実証3: 予見可能性
// =====================================================================
{
  const s = newSlide();
  header(s, "北海道の初期実証（3/4）予見可能性と運用戦略", "北海道の裁定価値は「取りにくい」— 実行可能戦略の捕捉率は九州より約10pt低く、予測技術の価値が大きい");

  bullets(s, [
    { t: "実行可能戦略のcapture率（完全予見比・60分粒度）", b: true },
    { t: "戦略a（過去N日の価格ランクで充放電枠を固定）: 66〜69% — 九州の同戦略は77〜80%", sub: true },
    { t: "戦略b（前日の残余需要予測で並べ替え）: 77〜81%まで回復", sub: true },
    { t: "戦略b′（風力の持続性シグナルを追加）: 改善なし — 日次配置では風力予報の付加価値が出ない", sub: true },
    { t: "厳密DP解との比較: 空SoC起点で順序実行不能の日が約25%あるが、年間価値の差は−0.3〜−1.7%（ランク法は頑健）", gap: 4 },
    { t: "太陽光主導（形が毎日似る）の九州と違い、風力主導の価格形状は日次の再現性が低い", b: true },
  ], 0.6, 1.5, 6.7, 4.8, { size: 12, gap: 8 });

  secLabel(s, 7.6, 1.45, "capture率（完全予見PF＝100%）", 5.2);
  s.addChart(pres.ChartType.bar, [
    { name: "capture", labels: ["完全予見PF", "九州 戦略a", "北海道 戦略a", "北海道 戦略b"], values: [100, 78.5, 67.5, 79.0] },
  ], quietChart({
    x: 7.6, y: 1.95, w: 5.1, h: 4.3,
    chartColors: [C.teal, C.lightblue, C.coral, C.blue],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 110,
    valGridLine: { style: "none" },
    barGapWidthPct: 60, varyColors: true,
  }));
  s.addText("棒は各年度レンジの中央値（a: 66-69% / b: 77-81% / 九州a: 77-80%）。別添Excel「capture率」シートで編集可", { x: 7.6, y: 6.35, w: 5.1, h: 0.4, fontSize: 8.5, color: C.gray, fontFace: F, margin: 0 });
  s.addText("capture率＝実行可能戦略の粗利÷完全予見の粗利（年度別）。DP＝SoC制約下の厳密最適（充放電順序を保証）", { x: 0.6, y: 6.85, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 6. 実証4: 風力の構造
// =====================================================================
{
  const s = newSlide();
  header(s, "北海道の初期実証（4/4）風力の構造", "風力変動の約3/4は「数日〜週」の長周期 — 4h蓄電池の日次シフトでは吸収できない帯域に分散が集中する");

  bullets(s, [
    { t: "風力（フリート集約出力）の分散の帯域分解", b: true },
    { t: "日内（24h未満）約25% ／ 1〜7日帯 35.7% ＋ 7日超帯 38.6% ＝ 約3/4が長周期", sub: true },
    { t: "太陽光（6-24h帯中心）と対照的 → 蓄電池のduration価値・貯蔵技術選択に直結", sub: true },
    { t: "風力の電力量シェアは実測10.2〜10.3%（FY2024-25）", b: true, gap: 4 },
    { t: "先行研究がMOEを検出した水準（Woo 5-8%・Ketterer 6-8%）を既に超過", sub: true },
    { t: "分位点回帰（Sakaguchi & Fujii 2021の再現・延長）", b: true, gap: 4 },
    { t: "高分位ほど強い風力MOE: τ0.9で−11.2円/kWh/GW（FY2016-19）→ FY2023-25は−4〜−7円に減衰", sub: true },
    { t: "減衰は連系線増強・市場統合と整合 ＝ 分断逆転（実証2）と表裏", sub: true },
  ], 0.6, 1.5, 6.7, 5.0, { size: 11.5, gap: 7 });

  secLabel(s, 7.6, 1.45, "風力変動の帯域分解（分散シェア・%）", 5.2);
  s.addChart(pres.ChartType.bar, [
    { name: "分散シェア", labels: ["日内（<24h）", "1〜7日", "7日超"], values: [25.7, 35.7, 38.6] },
  ], quietChart({
    x: 7.6, y: 1.95, w: 5.1, h: 3.9,
    chartColors: [C.lime, C.green, C.teal],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0\"%\"",
    valAxisMaxVal: 50, valAxisMajorUnit: 10, valAxisFormatCode: "0",
    barGapWidthPct: 60, varyColors: true,
  }));
  s.addShape(pres.ShapeType.rect, { x: 7.6, y: 6.0, w: 5.1, h: 0.5, fill: { color: C.tint } });
  s.addText("4h蓄電池が主に食えるのは左端の帯だけ", { x: 7.75, y: 6.0, w: 4.85, h: 0.5, fontSize: 10.5, bold: true, color: C.teal, fontFace: FB, margin: 0, valign: "middle" });
  s.addText("帯域分解＝制御前出力のバンドパス分散分解（FY2024-25）。別添Excel「帯域分解」シートで編集可", { x: 0.6, y: 6.85, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 7. 文献1: 調査の設計と全体地図
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（1/8）設計と全体地図", "コア41本を4セット・6系譜で体系化 — DOI検証からPDF収集・統一スキーマ抽出・数値チェックまで完了");

  secLabel(s, 0.6, 1.45, "調査プロセス（完了済み）");
  bullets(s, [
    { t: "選定 → Crossref照合でDOI41本を検証 → PDF収集（41/41）→ 13列統一スキーマの抽出表 → 引用数値の幻覚チェック（Wozabal・Karaduman等は原文突合で完全一致を確認）" },
    { t: "残タスク: コア5本の個別精読（BDG均衡条件の式・Fuke & Ohashi差別化7問 等）・系統的ギャップ検索・BibTeX化", sub: true },
  ], 0.75, 1.85, 11.9, 1.25, { size: 12 });

  secLabel(s, 0.6, 3.2, "6つの系譜（→ 各論は次頁以降）");
  litTable(s, [
    ["系譜", "内容", "代表論文", "本研究での役割"],
    ["A 再エネ→価格・ボラ実証", "MOE・分散への影響（11本）", "Woo 2011・Ketterer 2014・Wozabal 2016", "検出水準・非対称性のアンカー"],
    ["B 蓄電池の経済学・均衡", "裁定価値・カニバリ・均衡（13本）", "Butters 2025・Karaduman・Schmalensee", "均衡枠組みの背骨"],
    ["C 日本・JEPX", "国内実証（9本）", "Fuke & Ohashi 2025・Sakaguchi & Fujii 2021", "接続先・差別化の基準点"],
    ["D 手法・投資評価", "HAR・予測・censoring・実物オプション（8本）", "Corsi 2009・Fanone 2013・Leahy/Grenadier", "計量・評価の道具箱"],
    ["E 風力の時間構造（追加候補）", "空間平滑化・帯域", "St. Martin 2015・Ohlendorf & Schill 2020", "帯域分解の解釈（41本外・整理中）"],
  ], 0.6, 3.6, 12.13, [2.6, 3.15, 3.6, 2.78], { hSize: 10.5, bSize: 9.5, tbl: { rowH: 0.44 } });

  s.addText("セット構成: A11＋B13＋C9＋D8＝41本。系譜EはB表・帯域分解の作業に伴い related-work-review で別途整理中（コア集合への追加候補）", { x: 0.6, y: 6.65, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 8. 文献2: 系譜A
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（2/8）系譜A: 再エネは価格に何をするか", "水準は下げ（MOE）、分散への効果は電源種・市場で符号が異なる — 「風力と太陽光は別物」が実証の相場観");

  litTable(s, [
    ["論文", "市場・手法", "主要な結果", "北海道への含意"],
    ["Woo et al. (2011) Energy Policy", "ERCOT・回帰", "風力は価格水準を下げ、分散を高める（シェア5-8%で検出）", "検出水準の目安①"],
    ["Ketterer (2014) Energy Econ", "ドイツ・GARCH", "風力シェア+1pp → 価格−1.46%。ボラティリティは増加", "検出水準の目安②・GARCH系の代表"],
    ["Rintamäki et al. (2017) Energy Econ", "デンマーク/ドイツ", "同じ風力でも市場で符号が逆（デンマーク日次ボラ減・ドイツ日中ボラ増）", "「市場構造依存」の根拠 → 構造モデルの動機"],
    ["Wozabal et al. (2016) OR Spectrum", "ドイツ", "同一導入量あたりの分散影響はPVが風力の約12倍", "電源種の非対称性（原文突合済み）"],
    ["Schöniger & Morawetz (2022) Energy Econ", "欧州複数国", "変動再エネが必ずしも分散を増やさない（What comes down must go up）", "「風力増＝ボラ増」と単純化しない根拠"],
    ["Maciejowska (2020) Energy Econ", "ドイツ・分位点回帰", "水準・変動性への影響を分位別に分解", "h7分位点回帰の手法アンカー"],
  ], 0.6, 1.5, 12.13, [2.9, 1.85, 4.6, 2.78], { hSize: 10.5, bSize: 9.5, tbl: { rowH: 0.68 } });

  s.addText("ほか: Kyritsis 2017（ドイツ・太陽光vs風力）・Paraschiv 2014（EEX時間別）・Hagfors 2016（極値価格）・Mwampashi 2021（豪州風力）・Navia Simon & Diaz Anadon 2025（Nature Energy・再エネの保険価値）", { x: 0.6, y: 6.35, w: 11.9, h: 0.55, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0, lineSpacingMultiple: 1.2 });
}

// =====================================================================
// 9. 文献3: 系譜C 日本
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（3/8）系譜C: 日本・JEPXの実証", "国内は誘導形の価格実証が蓄積 — 蓄電池を内生化した均衡分析は見当たらない");

  litTable(s, [
    ["論文", "対象", "主要な結果", "本研究との関係"],
    [{ text: "Fuke & Ohashi (2025) J. Commodity Markets", options: { bold: true } }, "九州・太陽光", "太陽光の価格水準・変動性への影響に季節性（春夏は変動性低下・秋冬は低下せず）", { text: "最類似・最重要。高分位効果を北海道×風力で追試済み", options: { bold: true, color: C.teal } }],
    ["Sakaguchi & Fujii (2021) Front. Sustain.", "北海道・東北 FY2016-19", "風力MOEを北海道で検出（当時の設備は現在の半分）", "唯一の直接先行 → 倍増後のFY2023-25まで延長・更新"],
    ["Maekawa et al. (2018) Energies", "JEPX全体", "再エネMOEの国内最初期の実証", "出発点"],
    ["Kanamura & Bunn (2022) Energy Econ", "JEPX", "マーケットメイキングと価格形成（流動性の構造）", "床・分断の市場微細構造の参照"],
    ["Rassi & Kanamura (2023) Energy Policy", "JEPX", "スパイク形成とLNG価格・グロスビディング", "供給曲線上側の非定常性（燃料連動）の参照"],
    ["Ma et al. (2023) Applied Economics", "日本・エリア間", "再エネの越境効果（エリア間の価格波及）", "北本分断・2ノード設計の参照点"],
    ["Li et al. (2024) Energy", "日本・PV浸透", "長時間貯蔵（LDES）の価値をシステムモデルで評価", "duration論点の国内参照"],
  ], 0.6, 1.5, 12.13, [3.05, 1.75, 4.35, 2.98], { hSize: 10.5, bSize: 9.2, tbl: { rowH: 0.6 } });

  s.addText("ほか: Ikeda (2019・JEPX流動性)・Li et al. (2025・2021年1月スパイク事件の再検証)。METIの2030年見通し（14.1〜23.8GWh）は接続申込の実現率外挿であり均衡概念ではない", { x: 0.6, y: 6.5, w: 11.9, h: 0.4, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 10. 文献4: 系譜B前半（価値・カニバリ実証）
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（4/8）系譜B前半: 蓄電池の価値とカニバリゼーション", "「参入が価値を食う」は世界共通の実証 — ただし対象はすべて太陽光系市場");

  litTable(s, [
    ["論文", "市場", "主要な結果", "本研究との関係"],
    ["Sioshansi et al. (2009) Energy Econ", "PJM", "裁定価値評価の古典。貯蔵の増加は自らの裁定原資を侵食", "カニバリゼーションの原点"],
    ["Sioshansi (2010) Energy Journal", "理論/PJM", "厚生効果は所有構造に依存（発電事業者保有は歪み得る）", "厚生分析を主張から切り離す根拠"],
    ["Lamont (2013) IEEE Trans. Power Syst.", "理論", "大規模貯蔵の限界価値と最適構成の解析枠組み", "π(K)逓減の理論形"],
    ["Lamp & Samano (2022) Energy Econ", "CAISO", "蓄電池導入がスプレッドを実測で縮小", "九州の揚水先行圧縮（#6）と同型"],
    ["Zhao et al. (2022) Applied Energy", "CAISO", "戦略的な蓄電池投資のシミュレーション評価", "参入シミュレーションの参照"],
    ["Mercier et al. (2023) Energy Econ", "欧州横断", "DA市場の裁定価値を国際比較（市場設計で大差）", "エリア別価値比較の参照"],
  ], 0.6, 1.5, 12.13, [3.15, 1.5, 4.6, 2.88], { hSize: 10.5, bSize: 9.5, tbl: { rowH: 0.62 } });

  s.addText("補助線: Hirth (2013)・Brown & Reichenberg (2021)＝再エネ自身の市場価値低下（カニバリの再エネ側）／López Prol & Schill (2021)＝変動再エネ×貯蔵経済学のレビュー", { x: 0.6, y: 6.4, w: 11.9, h: 0.45, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0, lineSpacingMultiple: 1.2 });
}

// =====================================================================
// 11. 文献5: 系譜B後半（均衡・コア4本）
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（5/8）系譜B後半: 均衡分析のコア4本", "均衡枠組みは輸入可能 — ただし全て太陽光・海外市場で、北海道で一次的な論点が「限界」として残されている");

  litTable(s, [
    ["論文", "市場", "枠組みと主要な結果", "本研究が引き継ぐ点／拡張する点"],
    [{ text: "Butters, Dorsey & Gowrisankaran (2025) Econometrica", options: { bold: true } }, "CAISO・太陽光", "自由参入均衡で蓄電池投資を内生化。再エネ50%下で2024年に無補助損益分岐。不確実性下の価値は完全予見の約7割", { text: "枠組みの本体。curtailment・duration選択・連系線・マルチマーケットを「限界」と自ら明記 → 北海道で全て一次的", options: { bold: true, color: C.teal } }],
    ["Karaduman (WP, MIT/Stanford)", "豪州NEM", "価格インパクトを無視すると蓄電池収益を約2倍過大評価", "π(K)内生化（fleet feedback）の必然性の根拠"],
    ["Schmalensee (2022) Energy Journal", "理論", "競争的貯蔵とダックカーブ。価格上限なしなら競争均衡＝システム費用最小化", "PyPSA型クロスチェックの均衡解釈を与える命題"],
    ["Andrés-Cerezo & Fabra (2023) RAND", "スペイン", "貯蔵の価値・厚生は市場構造（支配力）に依存", "競争的参入の仮定の限界を明示する参照"],
  ], 0.6, 1.5, 12.13, [2.95, 1.45, 4.35, 3.38], { hSize: 10.5, bSize: 9.5, tbl: { rowH: 0.88 } });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.15, w: 12.13, h: 0.62, fill: { color: C.tint } });
  s.addText([
    { text: "読み方: ", options: { bold: true, color: C.teal } },
    { text: "BDGの「限界5点」（curtailment／duration固定／連系線・分断／0.01円床／マルチマーケット収益）は、北海道ではどれも一次的に重要 — ここが拡張の主戦場", options: { color: C.text } },
  ], { x: 0.85, y: 6.15, w: 11.6, h: 0.62, fontSize: 11, fontFace: F, margin: 0, valign: "middle" });
}

// =====================================================================
// 12. 文献6: 系譜D 手法・投資評価
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（6/8）系譜D: 手法・投資評価の道具箱", "計量・評価の部品はすべて棚にある — Leahy/Grenadierが「均衡×リアルオプション」の橋になる");

  litTable(s, [
    ["論文", "道具", "内容", "論文のどこで使うか"],
    ["Corsi (2009) J. Fin. Econometrics", "HAR", "実現ボラティリティの長期記憶近似", "第1部: 価格・ボラの計量（HAR-CV-JV-Xに拡張）"],
    ["Weron (2014)・Lago et al. (2021)", "価格予測", "電力価格予測のSOTAレビュー・ベンチマーク", "capture率の予測則設計・上界とのギャップ評価"],
    ["Fanone et al. (2013) Energy Econ", "負値価格", "負のDA価格の日次モデル化", "JEPXは0.01円床 → 打ち切り（Tobit・打ち切り分位点）への翻訳"],
    ["Jiang & Powell (2015) INFORMS JoC", "ADP", "蓄電池の時間先行入札の近似動的計画", "運用の上界・実装の参照"],
    ["Shin & Lee (2024) Energies", "LSMC", "最小二乗モンテカルロで蓄電池投資評価", "前回までのオプション価値算定の系譜"],
    [{ text: "Leahy (1993) QJE・Grenadier (2002) RFS", options: { bold: true } }, "実物オプション均衡", "競争均衡下では近視眼的（ゼロNPV）参入が最適／競争が待機オプション価値を侵食", { text: "「ゼロ利潤K*」とリアルオプションの理論接続 — 審査対策の要", options: { bold: true, color: C.teal } }],
  ], 0.6, 1.5, 12.13, [3.15, 1.45, 4.05, 3.48], { hSize: 10.5, bSize: 9.5, tbl: { rowH: 0.66 } });

  s.addText("使い分け: 第1部（実証）＝A系の手法＋D系の計量／第2部（均衡）＝B系の枠組み＋D系の投資評価。全部品が既存文献でカバーされ、新規性は「組み合わせる対象」（北海道×風力×制度）に集中する", { x: 0.6, y: 6.4, w: 11.9, h: 0.45, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0, lineSpacingMultiple: 1.2 });
}

// =====================================================================
// 13. 文献7: 対応表
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（7/8）北海道の結果はどう位置づくか", "追試で接続し（審査上安全）、拡張・新規で差別化する");

  const typeColor = { "新規": C.coral, "拡張": C.teal, "追試・拡張": C.teal, "追試・更新": C.blue, "整合": C.blue };
  const rows = [
    ["北海道の観察（本日の実証1〜4）", "型", "対応する先行研究と位置づけ"],
    ["床は九州の半分・PF価値は同等（価値源泉が床→スパイクへ）", "新規", "床由来／スパイク由来の価値構成の対照は文献に見当たらない"],
    ["capture 66-69% → 残余需要予測で77-81%", "整合", "Butters (2025)「不確実性下は完全予見の約7割」の日本版確認。風力地域は下限側"],
    ["風力分散の約3/4が1日超の長周期", "追試・拡張", "St. Martin・Malvaldi「集約で消えるのは高周波のみ」→ duration価値の理論上限という読み替えが本研究の視点"],
    ["風力シェア実測10%超え", "拡張", "Woo・Kettererの検出水準に到達。洋上風力後はデンマーク（54%）水準への入口"],
    ["高分位MOEの再現と減衰（−11.2 → −4〜−7円/kWh/GW）", "追試・更新", "Sakaguchi & Fujii（FY2016-19・設備半分）を倍増後まで延長。Fuke & Ohashiの高分位効果と同型"],
    ["市場分断の方向逆転（高値87-92% → 60%）", "新規", "越境効果研究（Ma et al. 2023）が参照点。北本増強・本州側変化の複合"],
  ];
  const tr = rows.map((r, ri) => r.map((cell, ci) => ({
    text: cell,
    options: ri === 0
      ? { bold: true, color: C.white, fill: { color: C.blue }, fontSize: 10.5, valign: "middle", align: ci === 1 ? "center" : "left" }
      : ci === 1
        ? { bold: true, color: C.white, fill: { color: typeColor[cell] || C.blue }, fontSize: 10, valign: "middle", align: "center" }
        : { color: C.text, fill: { color: ri % 2 === 0 ? C.tint : C.white }, fontSize: 10, valign: "middle" },
  })));
  s.addTable(tr, { x: 0.6, y: 1.5, w: 12.13, colW: [4.5, 1.25, 6.38], fontFace: F, border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.68, margin: 0.06 });

  s.addText("「新規」は現時点の棚卸しに基づく分類 — 投稿前に後方引用の系統的検索で再確認する（レビュー文書に明記）", { x: 0.6, y: 6.65, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 14. 文献8: ギャップとFO差別化
// =====================================================================
{
  const s = newSlide();
  header(s, "先行研究の調査（8/8）ギャップと本研究の位置づけ", "空白 ＝「北海道 × 風力 × 蓄電池の均衡容量」— 制度（容量市場・LTDA）込みの定量研究は国内外に見当たらない");

  bullets(s, [
    { t: "均衡分析（系譜B）はすべて太陽光・海外市場", b: true },
    { t: "BDGの限界5点（curtailment・duration・連系線・床・マルチマーケット）が北海道では一次的 ＝ 拡張の主戦場", sub: true },
    { t: "日本の実証（系譜C）は誘導形のみ — 蓄電池を内生化した均衡分析はない", b: true, gap: 4 },
    { t: "実証面の空白: 風力「主導」市場の価格構造・貯蔵価値の実証も手薄（欧州は連系が強く、豪州は太陽光と混合）", b: true, gap: 4 },
  ], 0.6, 1.5, 6.6, 3.3, { size: 12, gap: 8 });

  secLabel(s, 7.55, 1.45, "最類似 Fuke & Ohashi (2025) との差別化", 5.2);
  litTable(s, [
    ["軸", "Fuke & Ohashi", "本研究"],
    ["対象", "九州・太陽光・季節性", { text: "北海道・風力（高分位MOEの追試で接続済み）", options: { bold: true } }],
    ["手法", "誘導形の変動性記述", { text: "構造モデル＋自由参入均衡", options: { bold: true } }],
    ["問い", "変動性はどう変わったか", { text: "蓄電池は何GWまでが均衡整合的か（K*）", options: { bold: true } }],
  ], 7.55, 1.9, 5.18, [0.8, 1.9, 2.48], { hSize: 10, bSize: 9.5, tbl: { rowH: 0.62 } });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 5.15, w: 12.13, h: 1.35, fill: { color: C.tint } });
  s.addText([
    { text: "接続と差別化の作法: ", options: { bold: true, color: C.teal } },
    { text: "①追試（S&Fの分位点回帰・Buttersのcapture水準）で信頼を作る → ②Butters限界5点＋風力の長周期という「対象の性質」で新規性を主張 → ③均衡容量K*という「問い」で決定的に分ける。差別化3点の書面化 → 指導体制との擦り合わせが次の対人アクション", options: { color: C.text } },
  ], { x: 0.85, y: 5.15, w: 11.6, h: 1.35, fontSize: 11.5, fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.3 });
}

// =====================================================================
// 15. 今後の方針
// =====================================================================
{
  const s = newSlide();
  header(s, "今後の方針 — 均衡容量K*へ", "主張の型（無裁定・均衡整合性命題）を確定し、均衡条件の部品は実測済み。予備試算も方針を支持");

  secLabel(s, 0.6, 1.4, "主張の型（研究計画v2）");
  bullets(s, [
    { t: "「必然」は使わない。命題1: 現状容量K₀で限界参入者の利潤が非ゼロ → K₀は自由参入均衡でない ／ 命題2: 全シナリオで K* ≥ K_min（確率なしの頑健下限コリドー）" },
    { t: "二層参入: LTDA・補助＝政策層（外生）／マーチャント層のみゼロ利潤。主結果は純市場ケース", sub: true },
  ], 0.75, 1.8, 11.9, 1.15, { size: 11.5 });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 3.0, w: 6.55, h: 0.55, fill: { color: C.blue } });
  s.addText("π_spot(K) ＋ κ(h)·P_cap(K) − c_req ＝ 0　→ K*", { x: 0.85, y: 3.0, w: 6.2, h: 0.55, fontSize: 13, bold: true, color: C.white, fontFace: FB, margin: 0, valign: "middle" });
  bullets(s, [
    { t: "κ(4h)＝73→84%（公表調整係数）・P_cap＝公表需要曲線の閉形式・LTDA道内43.7万kW〜（政策層）" },
    { t: "AFC(4h)＝2.5〜3.0万円/kW-年（METI実勢6.8万円/kWh）＋託送等0.69万 → c_req≈3.2〜3.7万円/kW-年" },
  ], 0.6, 3.7, 6.55, 1.6, { size: 11, gap: 6 });

  secLabel(s, 7.4, 3.0, "予備試算（価格過程モデルv1）", 5.3);
  litTable(s, [
    ["試算", "結果"],
    ["① 現状の純市場マージン", { text: "収入約2.25万 ＜ c_req 3.2〜3.7万円/kW-年 → 足元の参入は政策層駆動の可能性（2枝設計で対応）", options: { fontSize: 9.5 } }],
    ["② 泊3号のみ", { text: "PF価値 ＋1,184円/kW-年（床6倍・充電コスト≈0）", options: { fontSize: 9.5 } }],
    ["③ DC需要+80万kWのみ", { text: "−797円/kW-年", options: { fontSize: 9.5 } }],
    ["④ 泊＋DC", { text: "−11円 ≈ ±0 — ほぼ完全相殺。相殺ネットの定量化が中心貢献候補", options: { fontSize: 9.5, bold: true, color: C.teal } }],
  ], 7.4, 3.45, 5.33, [1.85, 3.48], { hSize: 10, bSize: 9.5, tbl: { rowH: 0.56 } });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.35, w: 12.13, h: 0.62, fill: { color: C.tint } });
  s.addText("工程: フェーズC（蓄電池フリートを価格過程に内生化 → π(K)曲線 → K*初回推計）→ HVDCワーストセルで主張のgo/no-go → 前提フリーズ（2027/3末）", { x: 0.85, y: 6.35, w: 11.6, h: 0.62, fontSize: 11, bold: true, color: C.teal, fontFace: FB, margin: 0, valign: "middle" });
}

// =====================================================================
// 16. 討議事項
// =====================================================================
{
  const s = newSlide();
  header(s, "討議いただきたい点");

  const items = [
    { h: "① 実証第一弾の切り出し方", b: "分位点回帰の更新と風力帯域分解を、独立の実証貢献としてどこまで厚く書くか。あるいは構造モデルへの入力推定（マークアップ・打ち切り挙動・capture率）に徹するか" },
    { h: "② 主張の2枝の構成方針", b: "「頑健下限（K*>K₀）」と「政策による過剰参入（純市場K*<パイプライン）」— go/no-go判定前の現段階で、どちらを軸に論文構成を進めるべきか" },
    { h: "③ 最類似研究との差別化書面", b: "対象（九州太陽光→北海道風力）・手法（誘導形→構造＋均衡）・問い（変動性→均衡容量K*）の3点整理で、指導体制との擦り合わせに進んでよいか" },
  ];
  items.forEach((it, i) => {
    const y = 1.5 + i * 1.5;
    secLabel(s, 0.6, y, it.h, 11.5);
    s.addText(it.b, { x: 0.79, y: y + 0.4, w: 11.7, h: 0.95, fontSize: 12, color: C.text, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.1, w: 12.13, h: 0.72, fill: { color: C.tint } });
  s.addText("（時間があれば）容量市場の参加区分想定（安定電源1.25万 vs 発動指令0.83万円/kW-年）・WACCの設定方針（プロジェクトファイナンス実務条件ベース）", { x: 0.85, y: 6.1, w: 11.6, h: 0.72, fontSize: 11, color: C.text, fontFace: F, margin: 0, valign: "middle" });
}

pres.writeFile({ fileName: "進捗報告_20260817_v2.pptx" }).then(() => console.log("written"));
