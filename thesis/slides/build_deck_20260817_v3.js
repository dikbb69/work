// 進捗報告デッキ v3（2026-08-17）— 風力×蓄電池に全面フォーカス（先行研究セクションなし）
// ユーザーの既存フォーマット準拠（白背景・Noto Sans JP・青緑パレット・青ヘッダー表・左青バー見出し）
// 実行: NODE_PATH=<scratchpad>/node_modules node build_deck_20260817_v3.js

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const F = "Noto Sans JP";
const FB = "Noto Sans JP SemiBold";
const C = {
  green: "70B437", lime: "C3D60B", blue: "0079C2", lightblue: "5DB6E7",
  teal: "176871", amber: "FFC000", coral: "F27750", orange: "D95B20",
  black: "000000", text: "262626", gray: "595959", line: "D9D9D9",
  tint: "F0F6FB", white: "FFFFFF",
};

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
  s.addText(label, { x: x + 0.14, y, w: w || 5.5, h: 0.34, fontSize: 13, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "middle" });
}
function bullets(s, items, x, y, w, h, opts) {
  opts = opts || {};
  const arr = items.map((it) => ({
    text: it.t,
    options: {
      bullet: it.sub ? { code: "2013", indent: 10 } : { code: "25A0", indent: 12 },
      indentLevel: it.sub ? 1 : 0, bold: !!it.b, color: it.c || C.text,
      breakLine: true, paraSpaceAfter: it.gap === 0 ? 0 : (it.gap || opts.gap || 6),
    },
  }));
  s.addText(arr, { x, y, w, h, fontSize: opts.size || 12, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: opts.lsm || 1.2, color: C.text });
}
function tbl(s, rows, x, y, w, colW, opts) {
  opts = opts || {};
  const tr = rows.map((r, ri) => r.map((cell) => {
    const base = typeof cell === "object" ? cell : { text: cell };
    const o = Object.assign({}, base.options);
    if (ri === 0) Object.assign(o, { bold: true, color: C.white, fill: { color: C.blue }, fontSize: opts.hSize || 10.5, valign: "middle" });
    else Object.assign(o, { color: o.color || C.text, fill: o.fill || { color: ri % 2 === 0 ? C.tint : C.white }, fontSize: o.fontSize || opts.bSize || 10, valign: "middle" });
    return { text: base.text, options: o };
  }));
  s.addTable(tr, Object.assign({ x, y, w, colW, fontFace: F, border: { type: "solid", color: C.line, pt: 0.5 }, margin: 0.05, autoPage: false }, opts.tbl || {}));
}
function quietChart(extra) {
  return Object.assign({
    fontFace: F, chartColors: [C.blue], showLegend: false, showTitle: false,
    catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 8.5,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" },
    dataLabelFontSize: 9.5, dataLabelColor: C.teal, dataLabelFontFace: F,
    catAxisLineColor: C.line, valAxisLineColor: C.line,
  }, extra || {});
}

const HOURS = Array.from({ length: 24 }, (_, i) => String(i));
const WCURVE = {
  "夏": { hi: [11.31, 10.5, 10.68, 11.04, 11.05, 10.31, 9.62, 8.98, 9.7, 9.71, 8.6, 8.63, 8.1, 10.37, 12.05, 13.6, 16.32, 17.38, 18.49, 18.03, 16.63, 14.4, 12.88, 11.85], lo: [12.33, 11.34, 11.37, 11.84, 12.1, 11.41, 10.83, 10.01, 10.59, 10.41, 9.37, 9.72, 8.9, 11.46, 12.68, 15.2, 17.57, 18.7, 20.51, 19.38, 17.61, 15.62, 14.26, 13.05] },
  "冬": { hi: [10.92, 10.73, 10.85, 10.91, 11.0, 11.43, 12.42, 12.53, 11.92, 11.09, 9.54, 8.7, 7.79, 9.28, 10.02, 11.59, 13.42, 13.98, 13.79, 13.16, 12.99, 12.47, 11.5, 11.42], lo: [12.45, 12.27, 12.34, 12.5, 12.75, 12.91, 14.28, 14.25, 13.61, 12.22, 10.87, 9.88, 9.18, 10.49, 11.43, 13.69, 15.17, 15.82, 15.44, 14.65, 14.05, 13.26, 12.31, 12.13] },
  "不需要期": { hi: [11.33, 11.0, 11.22, 11.68, 11.87, 11.88, 11.61, 9.28, 7.87, 6.85, 5.62, 5.4, 4.73, 6.59, 8.27, 10.93, 14.05, 15.03, 15.47, 15.19, 14.17, 12.85, 12.06, 11.62], lo: [12.37, 11.88, 12.15, 12.64, 12.95, 13.03, 12.6, 10.36, 9.16, 8.04, 6.7, 6.36, 5.67, 8.16, 10.66, 13.37, 16.39, 17.22, 16.9, 16.51, 15.41, 14.22, 13.73, 12.87] },
};

// =====================================================================
// 1. 表紙
// =====================================================================
{
  const s = newSlide();
  s.addText("修士論文　進捗報告", { x: 0.9, y: 2.6, w: 11.5, h: 0.8, fontSize: 32, bold: true, color: C.black, fontFace: FB, margin: 0 });
  s.addShape(pres.ShapeType.rect, { x: 0.95, y: 3.52, w: 1.9, h: 0.06, fill: { color: C.blue } });
  s.addText("松葉 大希", { x: 0.9, y: 3.85, w: 6, h: 0.4, fontSize: 14, color: C.text, fontFace: F, margin: 0 });
  s.addText("2026.08.17", { x: 0.9, y: 4.25, w: 6, h: 0.4, fontSize: 12, color: C.gray, fontFace: F, margin: 0 });
  s.addText("風力 × 蓄電池 — 北海道市場の初期実証と、風力増加が蓄電池価値に与える影響", { x: 0.9, y: 5.0, w: 11.5, h: 0.4, fontSize: 13, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 2. 現在の課題
// =====================================================================
{
  const s = newSlide();
  header(s, "現在の課題");

  secLabel(s, 0.6, 1.05, "前回までの発表内容");
  bullets(s, [
    { t: "太陽光×蓄電池＠九州: 前日一括約定の情報構造の下、完全予見ベースの価値算定と価値減少の要因分解（太陽光は増え続けるのに裁定価値は減少に転じた）" },
  ], 0.75, 1.45, 11.9, 0.7, { size: 12.5 });

  secLabel(s, 0.6, 2.3, "今回の位置づけ: エリアと焦点の転換");
  bullets(s, [
    { t: "エリアを九州→北海道へ、焦点を太陽光→風力へ。「風力の増加は蓄電池の価値をどう変えるか」を北海道データで走り切る", b: true },
    { t: "北海道は風力/需要比が全国最大級・シェア実測10%超（先行研究のMOE検出水準を超過）・洋上5海域が控える「風力の実験場」", sub: true },
  ], 0.75, 2.7, 11.9, 1.15, { size: 12.5 });

  secLabel(s, 0.6, 4.0, "本日の構成");
  bullets(s, [
    { t: "① 風力は価格に何をしているか（価格カーブ・MOE・分断）" },
    { t: "② 蓄電池価値の実測（床・PF・風力依存・capture率）" },
    { t: "③ 風力の時間構造とduration（帯域分解・2/4/6/8h）" },
    { t: "④ 風力増加×蓄電池価値の反実仮想（K_windスイープ＝本日の中心図）", b: true },
    { t: "⑤ 今後の方針（均衡容量K*へ）" },
  ], 0.75, 4.4, 11.9, 2.2, { size: 12.5, gap: 5 });
}

// =====================================================================
// 3. データ基盤と風力の現在地
// =====================================================================
{
  const s = newSlide();
  header(s, "データ基盤と「風力の現在地」", "需給実績×価格の10年パネルを自前構築（検証アンカーで品質確認済み）— 北海道は日本初の風力主導市場になりつつある");

  secLabel(s, 0.6, 1.4, "データ");
  bullets(s, [
    { t: "北海道・東北の需給実績＋JEPXエリアプライス: 2016/4〜2026/6・約9万時間（新旧様式統合）" },
    { t: "FIT/FIP認定量から導入量系列を構築 → 設備利用率（cf）過程を抽出。検証アンカー: 制御初日一致・JWPA/系統WGと整合・2018/9欠測=胆振東部地震", sub: true },
  ], 0.75, 1.8, 11.9, 1.2, { size: 12 });

  secLabel(s, 0.6, 3.1, "風力の現在地（北海道）");
  const stats = [
    { n: "130万kW", l: "導入量（2024年末）— 直近2年で倍増" },
    { n: "10.2〜10.3%", l: "電力量シェア実測（FY2024-25）＝Woo(5-8%)・Ketterer(6-8%)のMOE検出水準を超過" },
    { n: "風力/需要比 全国最大級", l: "洋上5海域＋380万kWが控える。導入量は今後も外生的に増加" },
    { n: "抑制率 0.1%→1.35%", l: "FY2025→FY2026(4-6月)。抑制時代の入口" },
  ];
  stats.forEach((st, i) => {
    const x = 0.6 + (i % 2) * 6.2;
    const y = 3.5 + Math.floor(i / 2) * 1.35;
    s.addShape(pres.ShapeType.rect, { x, y, w: 5.95, h: 1.2, fill: { color: i === 3 ? "FDF0E8" : C.tint } });
    s.addText(st.n, { x: x + 0.25, y: y + 0.12, w: 5.5, h: 0.45, fontSize: 16, bold: true, color: i === 3 ? C.orange : C.teal, fontFace: FB, margin: 0 });
    s.addText(st.l, { x: x + 0.25, y: y + 0.58, w: 5.5, h: 0.55, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0, lineSpacingMultiple: 1.15 });
  });
  s.addText("太陽光も234万kWあり無視はしない（価格カーブの季節別・晴天日分析は別添Excel「価格カーブ形状」）。ただし本日は風力を主役に据える", { x: 0.6, y: 6.45, w: 11.9, h: 0.35, fontSize: 9.5, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 4. 風力は価格に何をするか① 価格カーブ
// =====================================================================
{
  const s = newSlide();
  header(s, "風力は価格に何をするか（1/2）— 一日全体が「平行に」沈む", "風力大の日は全時間帯で−1.1〜−1.4円/kWh。形はほぼ変えない — 昼だけ彫る太陽光と対照的で、これが蓄電池への効き方を決める");

  const titles = [["需要期・夏（7-8月）", "夏"], ["需要期・冬（12-2月）", "冬"], ["不需要期（4-5・10-11月）", "不需要期"]];
  titles.forEach(([ttl, key], i) => {
    const x = 0.5 + i * 4.2;
    s.addText(ttl, { x: x + 0.1, y: 1.5, w: 3.9, h: 0.3, fontSize: 11, bold: true, color: C.black, fontFace: FB, margin: 0 });
    s.addChart(pres.ChartType.line, [
      { name: "風力大の日", labels: HOURS, values: WCURVE[key].hi },
      { name: "風力小の日", labels: HOURS, values: WCURVE[key].lo },
    ], quietChart({
      x, y: 1.85, w: 4.1, h: 3.9,
      chartColors: [C.orange, C.blue],
      lineSize: 2.25, lineSmooth: false,
      catAxisLabelFrequency: 6,
      valAxisMinVal: 4, valAxisMaxVal: 21, valAxisMajorUnit: 4, valAxisFormatCode: "0",
      showLegend: i === 0, legendPos: "b", legendFontSize: 9, legendColor: C.gray,
    }));
  });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.0, w: 12.13, h: 0.75, fill: { color: C.tint } });
  s.addText([
    { text: "読み方: ", options: { bold: true, color: C.teal } },
    { text: "夕方スパイク（蓄電池の放電原資）は風力大の日でも高いまま残る。風力の日内振幅は平均の14〜18%しかなく（太陽光は数倍）、日内の「形」を作らない — 効くのは水準", options: { color: C.text } },
  ], { x: 0.85, y: 6.0, w: 11.6, h: 0.75, fontSize: 11, fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });
  s.addText("風力大/小＝各季節内で日次風力発電量（制御前）の上位/下位1/3の日（FY2023-25）。データは別添Excel「風力価格カーブ」で編集可", { x: 0.6, y: 6.85, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 5. 風力は価格に何をするか② MOEと分断
// =====================================================================
{
  const s = newSlide();
  header(s, "風力は価格に何をするか（2/2）— MOEの分位構造と、分断の駆動", "高い時間帯ほど強く効く風力MOEは連系線増強で減衰中 — 代わりに風力は「安値分断」を駆動し始めた");

  secLabel(s, 0.6, 1.45, "分位点回帰（Sakaguchi & Fujii 2021 の再現・延長）");
  bullets(s, [
    { t: "高分位ほど強い風力MOE: τ0.9で−11.2円/kWh/GW（FY2016-19）→ FY2023-25は−4〜−7円へ減衰", b: true },
    { t: "減衰の正体は北本増強・市場統合＝実効市場サイズの拡大。「シェアが増えるほどMOEが強まる」という単純な外挿は北海道では成立しない", sub: true },
    { t: "市場分断は方向が逆転: 高値分断87〜92% → 約60%、安値分断1〜5% → 約30%", sub: true },
  ], 0.75, 1.85, 11.9, 1.7, { size: 12 });

  secLabel(s, 0.6, 3.75, "風力は「安値分断」を駆動している（風力三分位別・時間/日、FY2023-25）");
  tbl(s, [
    ["季節", "風力小の日", "風力大の日", "変化"],
    ["需要期・夏", "8.1 h/日", "10.3 h/日", "+2.2"],
    ["需要期・冬", "3.1 h/日", "8.3 h/日", { text: "+5.2（2.7倍）", options: { bold: true, color: C.orange } }],
    ["不需要期", "4.6 h/日", "9.1 h/日", { text: "+4.5（2.0倍）", options: { bold: true, color: C.orange } }],
  ], 0.6, 4.15, 7.2, [1.9, 1.75, 1.75, 1.8], { hSize: 10.5, bSize: 10.5, tbl: { rowH: 0.42 } });

  s.addShape(pres.ShapeType.rect, { x: 8.1, y: 4.15, w: 4.63, h: 1.9, fill: { color: C.tint } });
  s.addText([
    { text: "含意: ", options: { bold: true, color: C.teal } },
    { text: "風力が吹くと北本の輸出が飽和し、道内価格が本州から下方に切り離される。連系線と蓄電池は同じ余剰を取り合う競合であり、輸出が飽和した先の受け皿が蓄電池", options: { color: C.text } },
  ], { x: 8.35, y: 4.15, w: 4.15, h: 1.9, fontSize: 10.5, fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.3 });

  s.addText("安値分断＝道内価格＜システムプライス−0.01円の時間。分位点回帰は打ち切り対応（0.01円床）。データ: 別添Excel「風力×裁定指標」", { x: 0.6, y: 6.5, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 6. 蓄電池価値の実測① 床・PF・九州比較
// =====================================================================
{
  const s = newSlide();
  header(s, "蓄電池価値の実測（1/3）— 床は九州の半分、価値は九州並み", "北海道の裁定価値の源泉は「昼の床」ではなく「夕方スパイク」— 風力がスパイクを削らないからこそ成立している構図");

  bullets(s, [
    { t: "床コマ（0.01円/kWh）は年473コマ ＝ 九州の約半分。ダックカーブは形成途上", b: true },
    { t: "完全予見4h裁定価値（PF）は0.96〜1.15万円/kW-年で九州と同水準", b: true },
    { t: "九州: 太陽光が作る昼の床（安値側）が源泉 ／ 北海道: 夕方スパイク（高値側）が源泉", sub: true },
    { t: "前頁の価格カーブが示す通り、風力はスパイクをほとんど削らない → 放電側の原資は当面頑健", sub: true },
    { t: "床がまだ少ない＝充電側の「タダ同然の電気」はこれから — 風力・泊がそれを作る（後段のスイープへ）", b: true, gap: 4 },
  ], 0.6, 1.5, 7.0, 3.6, { size: 12, gap: 9 });

  const stats = [
    { n: "473コマ/年", l: "床コマ（九州の約半分）" },
    { n: "0.96〜1.15万円/kW-年", l: "PF価値（九州と同水準）" },
    { n: "夕方スパイク", l: "価値の源泉（九州は昼の床）" },
  ];
  stats.forEach((st, i) => {
    const y = 1.5 + i * 1.35;
    s.addShape(pres.ShapeType.rect, { x: 8.0, y, w: 4.73, h: 1.2, fill: { color: C.tint } });
    s.addText(st.n, { x: 8.25, y: y + 0.15, w: 4.3, h: 0.5, fontSize: 17, bold: true, color: C.teal, fontFace: FB, margin: 0 });
    s.addText(st.l, { x: 8.25, y: y + 0.68, w: 4.3, h: 0.4, fontSize: 10, color: C.gray, fontFace: F, margin: 0 });
  });
  s.addText("PF＝完全予見・4時間・往復効率0.85・1日1サイクル。床コマはエリアプライス30分値。九州比較は前回発表と同一手法", { x: 0.6, y: 6.5, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 7. 蓄電池価値の実測② 風力三分位×裁定指標
// =====================================================================
{
  const s = newSlide();
  header(s, "蓄電池価値の実測（2/3）— 現在の風力水準では、風力大の日は価値を「やや下げる」", "平行シフトはスプレッドを微圧縮（冬は−19%）。床はまだほぼ出ない — 「床に届く前」の段階にいる");

  tbl(s, [
    ["季節", "風力三分位", "TB4hスプレッド", "PF粗利（円/kW-日）", "床時間（h/日）", "安値分断（h/日）"],
    ["需要期・夏", "風力小", "10.72円", "31.2", "0.13", "8.1"],
    ["", "風力大", "10.38円", "30.7", "0.06", "10.3"],
    ["需要期・冬", "風力小", "7.24円", "19.0", "0.02", "3.1"],
    ["", { text: "風力大", options: { bold: true } }, { text: "5.92円", options: { bold: true, color: C.orange } }, { text: "15.3（−19%）", options: { bold: true, color: C.orange } }, "0.04", { text: "8.3", options: { bold: true } }],
    ["不需要期", "風力小", "11.38円", "35.1", "0.89", "4.6"],
    ["", "風力大", "10.55円", "32.8", "1.37", "9.1"],
  ], 0.6, 1.5, 12.13, [1.75, 1.55, 2.2, 2.75, 1.85, 2.03], { hSize: 10.5, bSize: 10.5, tbl: { rowH: 0.46 } });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 5.0, w: 12.13, h: 1.5, fill: { color: C.tint } });
  s.addText([
    { text: "読み方: ", options: { bold: true, color: C.teal } },
    { text: "①風力大の日はスプレッドがやや縮む（平行シフト＋輸出飽和による全体安）＝ 目先の蓄電池には微マイナス。②しかし床時間はまだほぼゼロ — 風力は「タダの電気」をまだ作れていない。③安値分断だけが急増しており、輸出の受け皿が飽和した次に床が現れる。この転換を導入量の軸で見るのが次々頁のスイープ", options: { color: C.text } },
  ], { x: 0.85, y: 5.0, w: 11.6, h: 1.5, fontSize: 11.5, fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.3 });
  s.addText("風力三分位＝各季節内の日次風力発電量（制御前）による3等分（FY2023-25）。データ: 別添Excel「風力×裁定指標」", { x: 0.6, y: 6.65, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 8. 蓄電池価値の実測③ capture率と「平均化」の発見
// =====================================================================
{
  const s = newSlide();
  header(s, "蓄電池価値の実測（3/3）— 実行可能戦略と「風力ノイズは前日情報で取れない」", "捕捉率の最善は単純な平均化（気候値）の81〜83% — 風力主導の価格変動は前日時点でほぼ予測不能");

  bullets(s, [
    { t: "実行可能戦略のcapture率（完全予見PF=100%、FY2023-25）", b: true },
    { t: "a. 前日の実現価格ランク: 68.0〜69.3% — 昨日の風力ノイズを追いかけて自滅", sub: true },
    { t: "a2. 同曜日区分の直近日: 68.6〜70.4%（日タイプ補正は+1ptのみ）", sub: true },
    { t: "c. 過去28日・同区分の平均価格ランク（気候値）: 80.6〜82.6% ＝ 最善", sub: true, b: true },
    { t: "b. 予測残余需要ランク（需要28日−太陽光7日平均）: 77.3〜80.8%", sub: true },
    { t: "含意①: 価格形状＝安定した骨格＋ほぼ無相関の風力ノイズ。骨格は平均化で取り尽くせ、ノイズは前日情報では取れない（風力持続性の追加も改善ゼロ）", gap: 4 },
    { t: "含意②: 実現可能収益のヘアカットは約18〜19%（気候値ベース）— 均衡計算の校正係数に使用", b: true },
  ], 0.6, 1.5, 6.7, 5.0, { size: 11.5, gap: 7 });

  secLabel(s, 7.6, 1.45, "capture率（PF＝100%）", 5.1);
  s.addChart(pres.ChartType.bar, [
    { name: "capture", labels: ["完全予見PF", "a 前日価格", "a2 同区分前日", "c 平均価格(気候値)", "b 残余需要予測"], values: [100, 68.5, 69.4, 81.7, 78.8] },
  ], quietChart({
    x: 7.6, y: 1.9, w: 5.1, h: 4.3,
    chartColors: [C.teal, C.lightblue, C.lightblue, C.orange, C.blue],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0\"%\"",
    valAxisHidden: true, valGridLine: { style: "none" },
    barGapWidthPct: 55, varyColors: true,
  }));
  s.addText("棒はFY2023-25平均。分解実験: analysis/16（共通サンプル）", { x: 7.6, y: 6.3, w: 5.1, h: 0.3, fontSize: 8.5, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 9. 風力の時間構造とduration
// =====================================================================
{
  const s = newSlide();
  header(s, "風力の時間構造とduration — 4h電池が「食える帯域」は限られる", "風力分散の3/4は1日超の長周期。スポットの限界価値はhとともに逓減、容量市場のκ(h)は漸増 — 最適durationは両市場の合算で決まる");

  secLabel(s, 0.6, 1.45, "風力変動の帯域分解（分散シェア）");
  tbl(s, [
    ["帯域", "風力", "太陽光", "対応する貯蔵"],
    ["日内（<24h）", "25.7%", "約2/3", "4h蓄電池の主戦場"],
    [{ text: "1〜7日", options: { bold: true } }, { text: "35.7%", options: { bold: true, color: C.orange } }, "小", "数日貯蔵・連系線・火力"],
    [{ text: "7日超", options: { bold: true } }, { text: "38.6%", options: { bold: true, color: C.orange } }, "小", "季節間（P2G等）"],
  ], 0.6, 1.85, 6.4, [1.7, 1.2, 1.2, 2.3], { hSize: 10.5, bSize: 10.5, tbl: { rowH: 0.44 } });
  bullets(s, [
    { t: "移動平均カスケードによる帯域分解（FY2022-25、非直交・交差項あり）。風力の日内成分が小さい＝価格カーブの平行シフト・b′の空振りと同根", sub: true },
  ], 0.75, 3.85, 6.2, 0.9, { size: 10, gap: 4 });

  secLabel(s, 7.45, 1.45, "duration曲線（スポットPF価値・FY23-25平均）", 5.3);
  s.addChart(pres.ChartType.bar, [
    { name: "PF", labels: ["2h", "4h", "6h", "8h"], values: [6026, 10317, 13062, 14354] },
  ], quietChart({
    x: 7.45, y: 1.9, w: 5.25, h: 3.1,
    chartColors: [C.lightblue, C.blue, C.teal, C.green],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0",
    valAxisHidden: true, valGridLine: { style: "none" },
    barGapWidthPct: 55, varyColors: true,
  }));
  tbl(s, [
    ["", "2h", "4h", "6h", "8h"],
    ["スポット（4h比）", "0.58", "1.00", "1.27", "1.39"],
    ["容量市場 κ(h)", "—", "83.6%", "93.2%", "98.3%"],
  ], 7.45, 5.15, 5.25, [1.85, 0.85, 0.85, 0.85, 0.85], { hSize: 10, bSize: 10, tbl: { rowH: 0.38 } });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.35, w: 12.13, h: 0.6, fill: { color: C.tint } });
  s.addText("4h→6hでスポット+27%＋κ+9.6pt、6h→8hは+9%＋5.1pt — 長周期が支配的な風力市場ほど「longer durationの価値」が両市場で残る", { x: 0.85, y: 6.35, w: 11.6, h: 0.6, fontSize: 11, bold: true, color: C.teal, fontFace: FB, margin: 0, valign: "middle" });
}

// =====================================================================
// 10. 中心図: K_windスイープ
// =====================================================================
{
  const s = newSlide();
  header(s, "風力増加 × 蓄電池価値（本日の中心図）— 風力は蓄電池の敵ではなく「餌」", "K_windを0.5〜3倍に振ると蓄電池スポット価値は単調増加 — 0.01円の床が、風力の価値破壊を充電機会に変換する");

  const KW = ["61", "91", "121", "151", "182", "212", "242", "303", "363"];
  secLabel(s, 0.6, 1.45, "蓄電池スポット価値 PF（円/kW-年、FY23-25平均・仕様B）", 6.4);
  s.addChart(pres.ChartType.line, [
    { name: "泊なし（現状）", labels: KW, values: [8528, 8574, 8593, 8663, 8792, 9000, 9198, 9824, 10554] },
    { name: "泊3号再稼働", labels: KW, values: [9271, 9488, 9777, 10053, 10459, 10901, 11271, 12009, 12615] },
  ], quietChart({
    x: 0.6, y: 1.9, w: 6.3, h: 4.0,
    chartColors: [C.blue, C.orange],
    lineSize: 2.5, lineSmooth: false,
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: C.gray,
    catAxisTitle: "風力導入量 K_wind（万kW）※現状121", catAxisTitleFontSize: 9.5, showCatAxisTitle: true,
    valAxisMinVal: 8000, valAxisMaxVal: 13000, valAxisMajorUnit: 1000, valAxisFormatCode: "#,##0",
  }));

  secLabel(s, 7.35, 1.45, "メカニズムと読み方", 5.3);
  bullets(s, [
    { t: "現状近傍では微増（+70円/25%増）→ 2倍で+600円 → 3倍で+2,000円/kW-年。床時間は117→807h/年（泊ありなら2,247h）に立ち上がる" },
    { t: "なぜ増える: 風力は水準を下げるだけだが、0.01円床に当たると安い側だけが切り取られ（センサリング）、夕方スパイクは無傷 → スプレッド拡大", b: true },
    { t: "実測（前々頁）の「風力大の日は微マイナス」と矛盾しない: あれは床に届く前の姿。導入量が増えて床に届くと符号が反転する", sub: true },
    { t: "価値の上限を決めるのは風力ではなく蓄電池自身の競合（K↑→床を自分で埋める）— このfleet feedbackの内生化が次のフェーズC＝均衡容量K*", b: true, gap: 4 },
  ], 7.35, 1.9, 5.38, 4.3, { size: 10.5, gap: 7 });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.15, w: 12.13, h: 0.62, fill: { color: "FDF0E8" } });
  s.addText("留保: 部分均衡（蓄電池フリート応答・p_system・供給側の内生反応・連系線増強は未反映）。3倍はロジットの外挿域 — 水準は幅を持って、方向とメカニズムを主張", { x: 0.85, y: 6.15, w: 11.6, h: 0.62, fontSize: 10, color: C.text, fontFace: F, margin: 0, valign: "middle" });
  s.addText("価格過程v1: p=g(net;季節)+μ(時刻)・分断3レジーム混合・共通乱数。K_windはcf過程を保って一律スケール。データ: 別添Excel「風力スイープ」", { x: 0.6, y: 6.85, w: 11.9, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
}

// =====================================================================
// 11. 今後の方針
// =====================================================================
{
  const s = newSlide();
  header(s, "今後の方針 — 「風力×蓄電池の均衡容量K*」へ", "スイープの上限を決める蓄電池自身の競合を内生化し、自由参入均衡のK*を解く。部品は実測済み");

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 1.5, w: 6.55, h: 0.55, fill: { color: C.blue } });
  s.addText("π_spot(K) ＋ κ(h)·P_cap(K) − c_req ＝ 0　→ K*", { x: 0.85, y: 1.5, w: 6.2, h: 0.55, fontSize: 13, bold: true, color: C.white, fontFace: FB, margin: 0, valign: "middle" });
  bullets(s, [
    { t: "主張の型: 「必然」は使わない。①現状K₀の利潤の符号（自由参入均衡か否か）②全シナリオでK*≥K_min（頑健下限コリドー）" },
    { t: "二層参入: LTDA（道内43.7万kW〜）・補助＝政策層（外生）／マーチャント層のみゼロ利潤" },
    { t: "部品は実測済み: κ(4h)=73→84%・P_cap=公表需要曲線・AFC(4h)=2.5〜3.0万円/kW-年＋託送等0.69万 → c_req≈3.2〜3.7万" },
    { t: "現状の純市場収入 約2.25万円/kW-年 ＜ c_req → 足元の参入は政策層駆動の可能性（どちらに転んでも論文が立つ2枝設計）", b: true },
  ], 0.6, 2.25, 6.55, 3.3, { size: 11, gap: 8 });

  secLabel(s, 7.4, 1.5, "工程（次の3ヶ月）", 5.2);
  const steps = [
    { h: "フェーズC", b: "蓄電池フリートの充放電をnetに内生化 → π(K)曲線 → K*初回推計（充電側の託送・賦課金も控除）" },
    { h: "K_wind×K格子", b: "スイープを2次元化: 風力導入量×蓄電池容量の価値サーフェス＝「風力何万kWにつき蓄電池何万kWが均衡か」" },
    { h: "検証", b: "FY2026 OOSの再現改善（供給曲線上側の非定常対応）・九州でのout-of-sample" },
  ];
  steps.forEach((st, i) => {
    const y = 1.95 + i * 1.42;
    s.addShape(pres.ShapeType.rect, { x: 7.4, y, w: 5.33, h: 1.28, fill: { color: C.tint } });
    s.addText(st.h, { x: 7.62, y: y + 0.1, w: 4.9, h: 0.35, fontSize: 11.5, bold: true, color: C.teal, fontFace: FB, margin: 0 });
    s.addText(st.b, { x: 7.62, y: y + 0.45, w: 4.9, h: 0.8, fontSize: 9.5, color: C.text, fontFace: F, margin: 0, lineSpacingMultiple: 1.2 });
  });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.3, w: 12.13, h: 0.62, fill: { color: C.tint } });
  s.addText("本日の実証の役割: 価格カーブ（平行シフト）・床の生成・capture率（ヘアカット18-19%）・duration曲線が、そのまま均衡モデルの入力・校正材料になる", { x: 0.85, y: 6.3, w: 11.6, h: 0.62, fontSize: 10.5, bold: true, color: C.teal, fontFace: FB, margin: 0, valign: "middle" });
}

// =====================================================================
// 12. 討議事項
// =====================================================================
{
  const s = newSlide();
  header(s, "討議いただきたい点");

  const items = [
    { h: "① 「風力大の日は微マイナス／導入量が増えればプラス」の整理", b: "日次の実測（三分位）と反実仮想（スイープ）で符号が異なるのは床センサリングの有無による。この2つの見せ方・論文での書き分けについてご意見をいただきたい" },
    { h: "② 転換点（価値が減少に転じる点）は蓄電池の競合内生化後に現れる", b: "風力側をいくら振っても単調増（3倍まで）。減少に転じさせるのは蓄電池自身のfleet feedback — フェーズC（π(K)曲線→K*）を最優先とする進め方でよいか" },
    { h: "③ durationの扱い", b: "風力の長周期支配（分散の3/4）を踏まえると4h固定は保守的。スポット＋容量市場κ(h)の合算で4h/6h/8hを比較する分析を本論に含めるべきか" },
  ];
  items.forEach((it, i) => {
    const y = 1.5 + i * 1.55;
    secLabel(s, 0.6, y, it.h, 11.8);
    s.addText(it.b, { x: 0.79, y: y + 0.4, w: 11.7, h: 1.0, fontSize: 12, color: C.text, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.2, w: 12.13, h: 0.62, fill: { color: C.tint } });
  s.addText("（時間があれば）実証第一弾（分位点回帰・帯域分解）の切り出し方／容量市場の参加区分想定・WACC設定方針", { x: 0.85, y: 6.2, w: 11.6, h: 0.62, fontSize: 11, color: C.text, fontFace: F, margin: 0, valign: "middle" });
}

pres.writeFile({ fileName: "進捗報告_20260817_v3_風力蓄電池.pptx" }).then(() => console.log("written"));
