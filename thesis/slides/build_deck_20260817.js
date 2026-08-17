// 進捗報告デッキ生成（2026-08-17）
// 設計書: slides/20260817_進捗報告_構成案.md（10枚: 実証4＋先行研究3＋方針・討議）
// 実行: NODE_PATH=<scratchpad>/node_modules node build_deck_20260817.js

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in

const FONT = "Yu Gothic";

const C = {
  navy: "184F95",
  dark: "0F2D5C",
  darkCard: "1E4478",
  blue: "2A78D6",
  light: "CDE2FB",
  tint: "EEF4FB",
  orangeTint: "FDEDE4",
  orange: "EC835A",
  orangeDark: "B44E24",
  text: "222B36",
  gray: "68758A",
  white: "FFFFFF",
  line: "D5E2F2",
};

// ---------- helpers ----------
function header(s, kicker, title, titleSize) {
  s.addText(kicker, { x: 0.55, y: 0.26, w: 12.2, h: 0.3, fontSize: 10.5, bold: true, color: C.blue, fontFace: FONT, margin: 0, charSpacing: 1.5 });
  s.addText(title, { x: 0.55, y: 0.56, w: 12.25, h: 0.95, fontSize: titleSize || 20, bold: true, color: C.navy, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.08 });
}
function pageNum(s, label) {
  s.addText(label, { x: 12.35, y: 7.14, w: 0.8, h: 0.28, fontSize: 9, color: C.gray, fontFace: FONT, align: "right", margin: 0 });
}
function footnote(s, text, y) {
  s.addText(text, { x: 0.55, y: y || 7.02, w: 11.7, h: 0.42, fontSize: 8.5, color: C.gray, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.1 });
}
function card(s, x, y, w, h, fill, borderColor) {
  const opts = { x, y, w, h, fill: { color: fill }, rectRadius: 0.07 };
  if (borderColor) opts.line = { color: borderColor, width: 0.75 };
  s.addShape(pres.ShapeType.roundRect, opts);
}
function circleNum(s, x, y, d, n, fill) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill || C.orange } });
  s.addText(String(n), { x, y, w: d, h: d, fontSize: d * 72 * 0.48, bold: true, color: "FFFFFF", fontFace: FONT, align: "center", valign: "middle", margin: 0 });
}
function bullets(s, items, x, y, w, h, opts) {
  opts = opts || {};
  const arr = items.map((it, i) => ({
    text: it.t,
    options: {
      bullet: it.sub ? { code: "2013", indent: 12 } : { code: "25A0", indent: 14 },
      indentLevel: it.sub ? 1 : 0,
      bold: !!it.b,
      color: it.c || C.text,
      breakLine: true,
      paraSpaceAfter: it.gap === 0 ? 0 : (it.gap || opts.gap || 8),
    },
  }));
  s.addText(arr, { x, y, w, h, fontSize: opts.size || 12, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: opts.lsm || 1.22, color: C.text });
}
function sectionTag(s, x, y, label, fill) {
  card(s, x, y, 1.62, 0.34, fill || C.navy);
  s.addText(label, { x, y, w: 1.62, h: 0.34, fontSize: 10.5, bold: true, color: C.white, fontFace: FONT, align: "center", valign: "middle", margin: 0 });
}
function quietChart(extra) {
  return Object.assign({
    fontFace: FONT,
    chartColors: [C.blue],
    showLegend: false,
    showTitle: false,
    catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
    catAxisLabelFontSize: 9.5, valAxisLabelFontSize: 9,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" },
    dataLabelFontSize: 10, dataLabelColor: C.navy, dataLabelFontFace: FONT,
    catAxisLineColor: C.line, valAxisLineColor: C.line,
  }, extra || {});
}

// =====================================================================
// S1. 表紙（ダーク）
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.dark };
  s.addText("修士論文 進捗報告｜ゼミ発表　　2026年8月17日", { x: 0.55, y: 0.32, w: 12.2, h: 0.3, fontSize: 11, bold: true, color: C.light, fontFace: FONT, margin: 0, charSpacing: 1.5 });

  card(s, 0.55, 0.82, 12.23, 0.62, C.darkCard);
  s.addText([
    { text: "前回：", options: { bold: true, color: C.light } },
    { text: "九州実データによる簡易（完全情報）オプション価値算定 → 対象を北海道へ展開する方針を宣言", options: { color: C.light } },
  ], { x: 0.8, y: 0.82, w: 11.8, h: 0.62, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });

  s.addText("北海道の初期実証と、先行研究の中の空白", { x: 0.55, y: 1.8, w: 12.23, h: 0.62, fontSize: 27, bold: true, color: C.white, fontFace: FONT, margin: 0, align: "center" });
  s.addText("— 実証・文献レビューの報告と、均衡容量K*へ向けた今後の方針 —", { x: 0.55, y: 2.44, w: 12.23, h: 0.45, fontSize: 15, color: C.light, fontFace: FONT, margin: 0, align: "center" });

  const cards = [
    { h: "北海道の初期実証", b: "床コマは九州の約半分なのに、裁定価値（PF）は九州並み。価値の源泉が「昼の床」から「夕方スパイク」へ交代。風力変動は3/4が1日超の長周期" },
    { h: "先行研究の調査", b: "コア41本をDOI検証・抽出表まで整備。均衡分析はすべて太陽光・海外市場。「北海道×風力×蓄電池の均衡容量」が空白と確認" },
    { h: "今後の方針", b: "無裁定・均衡整合性命題（頑健下限コリドー）で均衡容量K*を推計。部品（AFC・容量市場・LTDA）は実測済み、予備試算も手応え" },
  ];
  cards.forEach((c0, i) => {
    const x = 0.55 + i * 4.145;
    card(s, x, 3.35, 3.94, 3.0, C.darkCard);
    circleNum(s, x + 0.28, 3.63, 0.46, i + 1);
    s.addText(c0.h, { x: x + 0.88, y: 3.57, w: 2.9, h: 0.6, fontSize: 13.5, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle" });
    s.addText(c0.b, { x: x + 0.28, y: 4.35, w: 3.4, h: 1.85, fontSize: 10.5, color: C.light, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });
  s.addText("データ: 北海道・東北の需給実績＋JEPX 2016/4〜2026/6（自前構築パネル）", { x: 0.55, y: 6.72, w: 12.2, h: 0.3, fontSize: 9.5, color: C.light, fontFace: FONT, margin: 0, align: "center" });
}

// =====================================================================
// S2. 実証(1) データ基盤
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "北海道の初期実証（1/4）｜データ基盤", "需給実績×価格の10年パネルを自前構築 — 検証アンカーで品質を確認");
  sectionTag(s, 11.15, 0.28, "実証 1/4", C.blue);

  bullets(s, [
    { t: "北海道・東北の需給実績（TSO公表・新旧様式を統合）＋JEPXエリアプライスの時間パネル: 2016/4〜2026/6", b: true },
    { t: "FIT/FIP認定量（B表45四半期分）から太陽光・風力の導入量系列を構築 → 設備利用率（cf）過程を抽出", gap: 14 },
    { t: "検証アンカー（外部情報との突合）", b: true },
    { t: "出力制御の初発生日が公表と一致（北海道 2022/5/8・東北 2022/4/10）", sub: true },
    { t: "2018/9の価格欠測480時間 ＝ 胆振東部地震ブラックアウト（データ欠陥ではなく史実）", sub: true },
    { t: "風力導入量がJWPA年末値と整合（32/86/130万kW）・太陽光が系統WG接続量と整合（234万kW）", sub: true },
  ], 0.55, 1.62, 7.3, 4.4, { size: 12, gap: 10 });

  const stats = [
    { n: "約9万時間", l: "パネルの規模（2エリア×10年半）" },
    { n: "太陽光 234万kW", l: "北海道の導入量（2025/3末）" },
    { n: "風力 130万kW", l: "同（2024年末）— 直近2年で倍増" },
    { n: "風力/需要比 全国最大級", l: "洋上5海域が控える「風力の実験場」" },
  ];
  stats.forEach((st, i) => {
    const y = 1.62 + i * 1.22;
    card(s, 8.15, y, 4.6, 1.08, i === 3 ? C.orangeTint : C.tint);
    s.addText(st.n, { x: 8.42, y: y + 0.12, w: 4.1, h: 0.42, fontSize: 16, bold: true, color: i === 3 ? C.orangeDark : C.navy, fontFace: FONT, margin: 0 });
    s.addText(st.l, { x: 8.42, y: y + 0.54, w: 4.1, h: 0.42, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0 });
  });
  footnote(s, "出所: 北海道電力NW・東北電力NW 需給実績、JEPXスポット、FIT/FIP情報公表用ウェブサイト、JWPA、系統WG資料");
  pageNum(s, "2");
}

// =====================================================================
// S3. 実証(2) 価格構造
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "北海道の初期実証（2/4）｜価格構造", "床コマは九州の約半分、しかし裁定価値は九州並み — 価値の源泉が違う");
  sectionTag(s, 11.15, 0.28, "実証 2/4", C.blue);

  bullets(s, [
    { t: "床コマ（0.01円/kWh）は年473コマ ＝ 九州の約半分。ダックカーブも形成途上（昼の窪みが浅い）", b: true },
    { t: "それでも完全予見4h裁定価値（PF）は0.96〜1.15万円/kW-年で九州と同水準", b: true },
    { t: "九州: 昼の床（安値側）が価値の源泉 ／ 北海道: 夕方スパイク（高値側）が源泉", sub: true },
    { t: "市場分断の方向が逆転しつつある", b: true, gap: 4 },
    { t: "高値分断（道内＞本州）87〜92% → 約60%へ。安値分断が1〜5% → 約30%に拡大", sub: true },
    { t: "＝ 余剰の輸出制約（北本連系線）が顕在化し始めた", sub: true },
  ], 0.55, 1.62, 6.5, 4.6, { size: 12, gap: 9 });

  card(s, 0.55, 5.62, 6.5, 1.15, C.orangeTint);
  s.addText([
    { text: "含意：", options: { bold: true, color: C.orangeDark } },
    { text: "北海道は「九州の後追い」ではない。風力・スパイク・分断という別の構造 — 九州の枠組みをそのまま当てはめられない", options: { color: C.text } },
  ], { x: 0.82, y: 5.62, w: 6.0, h: 1.15, fontSize: 11.5, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });

  // 右: 分断構成の変化（グループ棒）
  card(s, 7.35, 1.62, 5.4, 5.15, C.white, C.line);
  s.addText("市場分断の方向転換（コマ構成比）", { x: 7.62, y: 1.78, w: 4.9, h: 0.32, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addChart(pres.ChartType.bar, [
    { name: "FY2016-19", labels: ["高値分断", "連系", "安値分断"], values: [89.5, 7.5, 3.0] },
    { name: "FY2023-25", labels: ["高値分断", "連系", "安値分断"], values: [60.0, 11.0, 29.0] },
  ], quietChart({
    x: 7.55, y: 2.2, w: 5.0, h: 3.9,
    chartColors: [C.light, C.blue],
    barGrouping: "clustered",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"",
    valAxisMaxVal: 100, valAxisMajorUnit: 25, valAxisFormatCode: "0",
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: C.gray,
  }));
  s.addText("薄い＝FY2016-19 / 濃い＝FY2023-25（システムプライス±0.01円で判定）", { x: 7.62, y: 6.32, w: 4.9, h: 0.4, fontSize: 8.5, color: C.gray, fontFace: FONT, margin: 0 });

  footnote(s, "床コマ・分断はエリアプライス30分値から集計。PF価値＝完全予見・4時間・往復効率0.85。九州比較は前回発表の同一手法による");
  pageNum(s, "3");
}

// =====================================================================
// S4. 実証(3) 予見可能性
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "北海道の初期実証（3/4）｜予見可能性と運用戦略", "北海道の裁定価値は「取りにくい」— 予測技術の価値が九州より大きい");
  sectionTag(s, 11.15, 0.28, "実証 3/4", C.blue);

  bullets(s, [
    { t: "実行可能戦略のcapture率（完全予見比・60分粒度）", b: true },
    { t: "戦略a（過去N日の価格ランクで充放電枠を固定）: 66〜69% — 九州の同戦略は77〜80%", sub: true },
    { t: "戦略b（前日の残余需要予測で並べ替え）: 77〜81%まで回復", sub: true },
    { t: "戦略b′（風力の持続性シグナルを追加）: 改善なし — 日次配置では風力予報の付加価値が出ない", sub: true },
    { t: "厳密DP解との比較: 空SoC起点で順序実行不能の日が約25%あるが、年間価値の差は−0.3〜−1.7%（ランク法は頑健）", gap: 4 },
    { t: "太陽光主導（形が毎日似る）の九州と違い、風力主導の価格形状は日次の再現性が低い", b: true },
  ], 0.55, 1.62, 6.5, 4.9, { size: 12, gap: 9 });

  // 右: captureバー
  card(s, 7.35, 1.62, 5.4, 5.15, C.white, C.line);
  s.addText("capture率（PF＝100%）", { x: 7.62, y: 1.78, w: 4.9, h: 0.32, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addChart(pres.ChartType.bar, [
    { name: "capture", labels: ["完全予見PF", "九州 戦略a", "北海道 戦略a", "北海道 戦略b"], values: [100, 78.5, 67.5, 79.0] },
  ], quietChart({
    x: 7.55, y: 2.2, w: 5.0, h: 3.9,
    chartColors: [C.navy, C.light, C.orange, C.blue],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 110,
    valGridLine: { style: "none" },
    barGapWidthPct: 60, varyColors: true,
  }));
  s.addText("棒は各年度レンジの中央値（a: 66-69% / b: 77-81% / 九州a: 77-80%）", { x: 7.62, y: 6.32, w: 4.9, h: 0.4, fontSize: 8.5, color: C.gray, fontFace: FONT, margin: 0 });

  footnote(s, "capture率＝実行可能戦略の粗利 ÷ 完全予見の粗利（年度別）。DP＝SoC制約下の厳密最適（充放電順序を保証）");
  pageNum(s, "4");
}

// =====================================================================
// S5. 実証(4) 風力の構造
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "北海道の初期実証（4/4）｜風力の構造", "風力変動の3/4は「数日〜週」の長周期 — 4h蓄電池の日次シフトでは吸収できない");
  sectionTag(s, 11.15, 0.28, "実証 4/4", C.blue);

  bullets(s, [
    { t: "風力（フリート集約出力）の分散の帯域分解", b: true },
    { t: "日内（24h未満）は約25% ／ 1〜7日帯 35.7% ＋ 7日超帯 38.6% ＝ 分散の約3/4が長周期", sub: true },
    { t: "太陽光（6-24h帯中心）と対照的 → 蓄電池のduration価値・貯蔵技術選択に直結する基礎事実", sub: true },
    { t: "風力の電力量シェアは実測10.2〜10.3%（FY2024-25）", b: true, gap: 4 },
    { t: "先行研究がMOEを検出した水準（Woo 5-8%・Ketterer 6-8%）を既に超過", sub: true },
    { t: "分位点回帰（Sakaguchi & Fujii 2021 の再現・延長）", b: true, gap: 4 },
    { t: "高分位ほど強い風力MOE: τ0.9で−11.2円/kWh/GW（FY2016-19）→ FY2023-25は−4〜−7円に減衰", sub: true },
    { t: "減衰は連系線増強・市場統合の効果と整合 ＝ 分断逆転（実証2）と表裏", sub: true },
  ], 0.55, 1.62, 6.5, 5.1, { size: 11.5, gap: 8 });

  // 右: 帯域分解バー
  card(s, 7.35, 1.62, 5.4, 5.15, C.white, C.line);
  s.addText("風力変動の帯域分解（分散シェア）", { x: 7.62, y: 1.78, w: 4.9, h: 0.32, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addChart(pres.ChartType.bar, [
    { name: "分散シェア", labels: ["日内（<24h）", "1〜7日", "7日超"], values: [25.7, 35.7, 38.6] },
  ], quietChart({
    x: 7.55, y: 2.2, w: 5.0, h: 3.7,
    chartColors: [C.light, C.blue, C.navy],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0\"%\"",
    valAxisMaxVal: 50, valAxisMajorUnit: 10, valAxisFormatCode: "0",
    barGapWidthPct: 60, varyColors: true,
  }));
  card(s, 7.55, 6.0, 5.0, 0.62, C.orangeTint);
  s.addText("4h蓄電池が主に食えるのは左端の帯だけ", { x: 7.72, y: 6.0, w: 4.7, h: 0.62, fontSize: 10.5, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0, valign: "middle" });

  footnote(s, "帯域分解＝制御前出力のバンドパス分散分解（FY2024-25）。分位点回帰＝価格を被説明変数、風力・太陽光出力等を説明変数とする時間別推定");
  pageNum(s, "5");
}

// =====================================================================
// S6. 先行研究(1) 全体地図
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "先行研究の調査（1/3）｜全体地図", "コア41本を6つの系譜で整理 — DOI検証・抽出表・数値チェックまで完了");
  sectionTag(s, 11.15, 0.28, "文献 1/3", C.navy);

  card(s, 0.55, 1.56, 12.23, 0.66, C.tint);
  s.addText([
    { text: "41本 ", options: { bold: true, color: C.navy, fontSize: 14 } },
    { text: "（A: 再エネ→ボラ実証 11 ／ B: 蓄電池の価値・均衡 13 ／ C: 日本・JEPX 9 ／ D: 手法 8）　DOI照合・13列統一スキーマの抽出表・引用数値の幻覚チェック済み", options: { color: C.text, fontSize: 10.5 } },
  ], { x: 0.82, y: 1.56, w: 11.7, h: 0.66, fontFace: FONT, margin: 0, valign: "middle" });

  const streams = [
    { tag: "A", h: "メリットオーダー効果", b: "再エネは価格水準を下げる。Woo (2011)・Ketterer (2014): 風力+1pp→価格−1.46%。検出水準5〜8%", },
    { tag: "B", h: "ボラティリティの非対称性", b: "電源種で符号が異なる。Rintamäki (2017)・Wozabal (2016): PVの分散影響は風力の約12倍", },
    { tag: "C", h: "日本・JEPXの実証", b: "Maekawa (2018)・Sakaguchi & Fujii (2021, 北海道風力)・Fuke & Ohashi (2025, 九州の季節性)", },
    { tag: "D", h: "蓄電池の価値・カニバリ・均衡", b: "Sioshansi (2009)・Lamp & Samano (2022)・Karaduman (2023)・Butters et al. (2025, Econometrica)・Schmalensee", },
    { tag: "E", h: "風力の空間平滑化・時間構造", b: "St. Martin (2015)・Malvaldi (2017): 集約で消えるのは高周波のみ。Ohlendorf & Schill (2020): 数日規模の低風力", },
    { tag: "F", h: "計量手法", b: "HAR系（Corsi 2009・Ciarreta 2017）・打ち切り分位点回帰（0.01円床の処理）", },
  ];
  streams.forEach((st, i) => {
    const x = 0.55 + (i % 3) * 4.145;
    const y = 2.5 + Math.floor(i / 3) * 2.12;
    const hot = st.tag === "D";
    card(s, x, y, 3.94, 1.95, hot ? C.orangeTint : C.white, hot ? C.orange : C.line);
    circleNum(s, x + 0.22, y + 0.2, 0.4, st.tag, hot ? C.orange : C.blue);
    s.addText(st.h, { x: x + 0.74, y: y + 0.16, w: 3.05, h: 0.52, fontSize: 12, bold: true, color: C.navy, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.05 });
    s.addText(st.b, { x: x + 0.24, y: y + 0.76, w: 3.5, h: 1.1, fontSize: 9.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.22 });
  });

  footnote(s, "系譜D（オレンジ）が本研究の背骨。抽出表の数値はWozabal・Karaduman等を原文突合で確認済み");
  pageNum(s, "6");
}

// =====================================================================
// S7. 先行研究(2) 対応表
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "先行研究の調査（2/3）｜北海道の結果はどう位置づくか", "追試で接続し（審査上安全）、拡張・新規で差別化する");
  sectionTag(s, 11.15, 0.28, "文献 2/3", C.navy);

  const rows = [
    ["北海道の観察", "型", "対応する先行研究と位置づけ"],
    ["床は九州の半分・PF価値は同等（価値源泉が床→スパイクへ）", "新規", "床由来／スパイク由来の価値構成の対照は文献に見当たらない"],
    ["capture 66-69% → 残余需要予測で77-81%", "整合", "Butters (2025)「不確実性下は完全予見の約7割」の日本版確認。風力地域は下限側"],
    ["風力分散の約3/4が1日超の長周期", "追試・拡張", "St. Martin・Malvaldi「集約で消えるのは高周波のみ」— duration価値の理論上限という読み替えが本研究の視点"],
    ["風力シェア実測10%超え", "拡張", "Woo・Ketterer の検出水準に到達。洋上風力後はデンマーク（54%）水準への入口"],
    ["高分位MOEの再現と減衰（−11.2 → −4〜−7円/kWh/GW）", "追試・更新", "唯一の直接先行 Sakaguchi & Fujii（FY2016-19・設備半分）を倍増後まで延長。Fuke & Ohashi の高分位効果と同型"],
    ["市場分断の方向逆転（高値87-92% → 60%）", "新規", "越境効果研究（Applied Economics 2023）が参照点。北本増強・本州側変化の複合"],
  ];
  const typeColor = { "新規": C.orange, "拡張": C.navy, "追試・拡張": C.navy, "追試・更新": C.blue, "整合": C.blue };
  const tableRows = rows.map((r, ri) => r.map((cell, ci) => ({
    text: cell,
    options: ri === 0
      ? { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5, valign: "middle", align: ci === 1 ? "center" : "left" }
      : {
          color: ci === 1 ? C.white : C.text,
          fill: ci === 1 ? { color: typeColor[cell] || C.blue } : { color: ri % 2 === 0 ? C.tint : C.white },
          bold: ci === 1,
          fontSize: 10,
          valign: "middle",
          align: ci === 1 ? "center" : "left",
        },
  })));
  s.addTable(tableRows, {
    x: 0.55, y: 1.66, w: 12.23,
    colW: [4.55, 1.25, 6.43],
    fontFace: FONT,
    border: { type: "solid", color: C.line, pt: 0.5 },
    rowH: 0.72,
    margin: 0.06,
  });

  footnote(s, "「新規」は現時点の棚卸しに基づく分類 — 投稿前に後方引用の系統的検索で再確認する（レビュー文書に明記）");
  pageNum(s, "7");
}

// =====================================================================
// S8. 先行研究(3) ギャップ
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "先行研究の調査（3/3）｜ギャップと本研究の位置づけ", "空白 ＝「北海道 × 風力 × 蓄電池の均衡容量」");
  sectionTag(s, 11.15, 0.28, "文献 3/3", C.navy);

  bullets(s, [
    { t: "均衡分析（系譜D）はすべて太陽光・海外市場", b: true },
    { t: "Butters et al. (2025) は CAISO・太陽光。curtailment・duration選択・連系線分断・マルチマーケット収益を「限界」と自ら明記", sub: true },
    { t: "その限界がまさに北海道では一次的に重要（床・帯域分解・北本・容量市場）＝ 本研究の拡張ポイント", sub: true },
    { t: "日本の実証（系譜C）は誘導形のみ — 蓄電池を内生化した均衡分析は見当たらない", b: true, gap: 4 },
    { t: "METIの2030年見通し（14.1〜23.8GWh）も接続申込の実現率外挿であり、均衡概念ではない", sub: true },
  ], 0.55, 1.62, 6.6, 4.4, { size: 11.5, gap: 9 });

  // 右: FO差別化カード
  card(s, 7.45, 1.62, 5.33, 4.55, C.tint);
  s.addText("最類似研究 Fuke & Ohashi (2025) との差別化", { x: 7.72, y: 1.8, w: 4.85, h: 0.36, fontSize: 12, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  const diffs = [
    { k: "対象", a: "九州・太陽光・季節性", b: "北海道・風力（高分位MOEの追試で接続済み）" },
    { k: "手法", a: "誘導形の変動性記述", b: "構造モデル＋自由参入均衡" },
    { k: "問い", a: "変動性はどう変わったか", b: "蓄電池は何GWまでが均衡整合的か（K*）" },
  ];
  diffs.forEach((d, i) => {
    const y = 2.3 + i * 1.28;
    card(s, 7.72, y, 4.85, 1.12, C.white, C.line);
    s.addText(d.k, { x: 7.9, y: y + 0.1, w: 0.9, h: 0.9, fontSize: 11, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0, valign: "middle" });
    s.addText([
      { text: d.a + "\n", options: { color: C.gray, fontSize: 9.5 } },
      { text: "→ " + d.b, options: { color: C.navy, fontSize: 10, bold: true } },
    ], { x: 8.8, y: y + 0.08, w: 3.65, h: 0.98, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.18 });
  });

  card(s, 0.55, 6.2, 12.23, 0.72, C.orangeTint);
  s.addText([
    { text: "本研究の空白ポジション：", options: { bold: true, color: C.orangeDark } },
    { text: "風力主導エリアの卸市場で、蓄電池の均衡容量を制度（容量市場・LTDA）込みで定量する研究は国内外に見当たらない", options: { color: C.text } },
  ], { x: 0.82, y: 6.2, w: 11.7, h: 0.72, fontSize: 12, fontFace: FONT, margin: 0, valign: "middle" });
  pageNum(s, "8");
}

// =====================================================================
// S9. 今後の方針
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "今後の方針｜実証と文献の帰結として", "「均衡容量K*」へ — 主張の型を確定し、部品は実測済み、予備試算にも手応え");
  sectionTag(s, 11.15, 0.28, "方針", C.orange);

  // 左列: 主張の型＋均衡式
  card(s, 0.55, 1.6, 6.35, 2.6, C.tint);
  s.addText("主張の型（研究計画v2で確定）", { x: 0.82, y: 1.74, w: 5.9, h: 0.32, fontSize: 12, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  bullets(s, [
    { t: "「必然」は使わない。無裁定・均衡整合性命題2つ:" },
    { t: "命題1: 現状容量K₀で限界参入者の利潤が非ゼロ → K₀は自由参入均衡でない", sub: true },
    { t: "命題2: 全シナリオで K* ≥ K_min（確率なしの頑健下限コリドー）", sub: true },
    { t: "二層参入: LTDA・補助＝政策層（外生）／マーチャント層のみゼロ利潤", sub: true, gap: 0 },
  ], 0.82, 2.12, 5.85, 2.0, { size: 10.5, gap: 6, lsm: 1.18 });

  card(s, 0.55, 4.35, 6.35, 0.62, C.navy);
  s.addText("π_spot(K) ＋ κ(h)·P_cap(K) − c_req ＝ 0　を解いて K*", { x: 0.82, y: 4.35, w: 5.85, h: 0.62, fontSize: 13, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle" });
  bullets(s, [
    { t: "部品は実測済み: κ(4h)=73→84%・P_cap=公表需要曲線の閉形式・LTDA道内43.7万kW〜（政策層）" },
    { t: "AFC(4h)=2.5〜3.0万円/kW-年（METI実勢6.8万円/kWh）＋託送等0.69万 → c_req ≈ 3.2〜3.7万" },
  ], 0.55, 5.12, 6.35, 1.3, { size: 10.5, gap: 6, lsm: 1.2 });

  // 右列: 予備試算2つ
  card(s, 7.15, 1.6, 5.63, 2.15, C.white, C.line);
  s.addText("予備試算① 現状の純市場マージンは負", { x: 7.42, y: 1.74, w: 5.1, h: 0.32, fontSize: 12, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "収入 約2.25万（スポット1.0＋容量1.25） ＜ c_req 3.2〜3.7万円/kW-年\n", options: { color: C.text } },
    { text: "→ 足元の参入ラッシュは政策層駆動の可能性。「頑健下限」でも「政策による過剰参入」でも論文が立つ2枝設計", options: { color: C.orangeDark, bold: true } },
  ], { x: 7.42, y: 2.1, w: 5.1, h: 1.55, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  card(s, 7.15, 3.95, 5.63, 2.5, C.white, C.line);
  s.addText("予備試算② 泊3号×DC需要は「ほぼ完全相殺」", { x: 7.42, y: 4.09, w: 5.1, h: 0.32, fontSize: 12, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  const t2 = [
    [{ text: "シナリオ（FY2023-25パス）", options: { bold: true, fill: { color: C.tint }, color: C.navy } }, { text: "PF価値の変化", options: { bold: true, fill: { color: C.tint }, color: C.navy, align: "center" } }],
    ["泊3号再稼働のみ", { text: "＋1,184円/kW-年", options: { align: "center", bold: true, color: C.navy } }],
    ["DC需要+80万kWのみ", { text: "−797円/kW-年", options: { align: "center", bold: true, color: C.orangeDark } }],
    [{ text: "両方", options: { bold: true } }, { text: "−11円 ≈ ±0（相殺）", options: { align: "center", bold: true, color: C.orange } }],
  ];
  s.addTable(t2, { x: 7.42, y: 4.5, w: 5.1, colW: [3.0, 2.1], fontFace: FONT, fontSize: 10, border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.4, margin: 0.05, valign: "middle", color: C.text });
  s.addText("相殺のネットの構造定量化が中心貢献になり得る", { x: 7.42, y: 6.14, w: 5.1, h: 0.3, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0 });

  // 工程
  card(s, 0.55, 6.55, 12.23, 0.6, C.dark);
  s.addText("工程：フェーズC（蓄電池フリートを価格過程に内生化 → π(K)曲線 → K*初回推計）→ HVDCワーストセルで主張のgo/no-go → 前提フリーズ（2027/3末）", { x: 0.82, y: 6.55, w: 11.7, h: 0.6, fontSize: 10.5, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle" });
  pageNum(s, "9");
}

// =====================================================================
// S10. 討議事項（ダーク）
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.dark };
  s.addText("討議いただきたい点", { x: 0.55, y: 0.55, w: 12.2, h: 0.55, fontSize: 24, bold: true, color: C.white, fontFace: FONT, margin: 0 });

  const items = [
    { h: "実証第一弾の切り出し方", b: "分位点回帰の更新と風力帯域分解を、独立の実証貢献としてどこまで厚く書くか。あるいは構造モデルへの入力推定（マークアップ・打ち切り挙動・capture率）に徹するか" },
    { h: "主張の2枝の構成方針", b: "「頑健下限（K*>K₀）」と「政策による過剰参入（純市場K*<パイプライン）」— go/no-go判定前の現段階で、どちらを軸に論文構成を進めるべきか" },
    { h: "最類似研究との差別化書面", b: "対象（九州太陽光→北海道風力）・手法（誘導形→構造＋均衡）・問い（変動性→均衡容量K*）の3点整理で、指導体制との擦り合わせに進んでよいか" },
  ];
  items.forEach((it, i) => {
    const y = 1.5 + i * 1.62;
    card(s, 0.55, y, 12.23, 1.42, C.darkCard);
    circleNum(s, 0.85, y + 0.44, 0.52, i + 1);
    s.addText(it.h, { x: 1.6, y: y + 0.14, w: 10.9, h: 0.45, fontSize: 14.5, bold: true, color: C.white, fontFace: FONT, margin: 0 });
    s.addText(it.b, { x: 1.6, y: y + 0.6, w: 10.9, h: 0.72, fontSize: 11, color: C.light, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });
  });

  s.addText("（時間があれば）容量市場の参加区分想定（安定電源1.25万 vs 発動指令0.83万円/kW-年）・WACCの設定方針（PF実務条件ベース）", { x: 0.55, y: 6.5, w: 12.2, h: 0.4, fontSize: 10.5, color: C.light, fontFace: FONT, margin: 0 });
  s.addText("10", { x: 12.35, y: 7.14, w: 0.8, h: 0.28, fontSize: 9, color: C.light, fontFace: FONT, align: "right", margin: 0 });
}

pres.writeFile({ fileName: "進捗報告_20260817.pptx" }).then(() => console.log("written"));
