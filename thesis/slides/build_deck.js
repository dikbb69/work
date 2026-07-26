// ゼミ発表スライド生成スクリプト
// 設計書: thesis/presentation-outline.md（本編15枚＋Appendix）
// 実行: node build_deck.js → ゼミ発表_九州実証と北海道転換.pptx

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in

const FONT = "Yu Gothic";
const FIG = "/home/user/work/thesis/figures";

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
function fig(s, file, x, y, w, aspect) {
  const h = w / aspect;
  s.addImage({ path: `${FIG}/${file}`, x, y, w, h });
  return y + h;
}
function stat(s, x, y, w, num, label, o) {
  o = o || {};
  s.addText(num, { x, y, w, h: o.numH || 0.55, fontSize: o.numSize || 26, bold: true, color: o.numColor || C.navy, fontFace: FONT, margin: 0 });
  s.addText(label, { x, y: y + (o.numH || 0.55), w, h: o.labelH || 0.5, fontSize: o.labelSize || 9.5, color: C.gray, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
}
function circleNum(s, x, y, d, n, fill) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill || C.orange } });
  s.addText(String(n), { x, y, w: d, h: d, fontSize: d * 72 * 0.48, bold: true, color: "FFFFFF", fontFace: FONT, align: "center", valign: "middle", margin: 0 });
}
function downArrow(s, cx, y) {
  s.addShape(pres.ShapeType.downArrow, { x: cx - 0.14, y, w: 0.28, h: 0.24, fill: { color: C.blue } });
}

// =====================================================================
// P1. 表紙＋結論3行（ダーク）
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.dark };
  s.addText("修士論文 中間報告｜ゼミ発表　　2026年◯月◯日", { x: 0.55, y: 0.3, w: 12.2, h: 0.3, fontSize: 11, bold: true, color: C.light, fontFace: FONT, margin: 0, charSpacing: 1.5 });

  card(s, 0.55, 0.78, 12.23, 0.62, C.darkCard);
  s.addText([
    { text: "前回のNext Action：", options: { bold: true, color: C.light } },
    { text: "九州を題材に、太陽光普及と市場価格構造の変化（過去実績ベース）／蓄電池のオプション価格算定", options: { color: C.light } },
  ], { x: 0.8, y: 0.78, w: 11.8, h: 0.62, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });

  s.addText("太陽光は増え続けているのに、蓄電池の裁定価値は減り始めた", { x: 0.55, y: 1.72, w: 12.23, h: 0.62, fontSize: 26, bold: true, color: C.white, fontFace: FONT, margin: 0, align: "center" });
  s.addText("— 九州10年半の実証と、北海道×風力への展開 —", { x: 0.55, y: 2.36, w: 12.23, h: 0.45, fontSize: 16, color: C.light, fontFace: FONT, margin: 0, align: "center" });

  const cards = [
    {
      h: "床と裁定価値は反転減少",
      b: "太陽光は右肩上がり（発電量2.1倍・シェア17%）だが、床（0.01円）と裁定価値はピーク年FY2023比で減少（単調な下降トレンドではない）",
    },
    {
      h: "スポット単独では投資不成立",
      b: "蓄電池のスポット裁定価値は約1万円/kW-年。単独では資本費（約2万円/kW-年）に届かない — Butters (2025, Econometrica) のCAISOと整合",
    },
    {
      h: "減少の内訳が転換の根拠",
      b: "構造要因（需要増・揚水の面的拡大）＋一時要因（原発定検・天候）。この分解が北海道×風力への転換の根拠になる",
    },
  ];
  cards.forEach((c0, i) => {
    const x = 0.55 + i * 4.145;
    card(s, x, 3.3, 3.94, 2.85, C.darkCard);
    circleNum(s, x + 0.28, 3.58, 0.46, i + 1);
    s.addText(c0.h, { x: x + 0.88, y: 3.52, w: 2.9, h: 0.6, fontSize: 13, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.1 });
    s.addText(c0.b, { x: x + 0.28, y: 4.3, w: 3.4, h: 1.7, fontSize: 10.5, color: C.light, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });

  s.addText("宿題への回答と、そこから導かれる方向転換の提案までをセットでお話しします", { x: 0.55, y: 6.65, w: 12.23, h: 0.4, fontSize: 11.5, italic: true, color: C.light, fontFace: FONT, margin: 0, align: "center" });
  s.addNotes("冒頭宣言:「宿題への回答＋そこから導かれる方向転換の提案までがセット」。結論3行を先に示す。");
}

// =====================================================================
// P2. データと分析基盤
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜データと分析基盤", "10年半×2系統の公開データ — 全図表がコード一発で再現可能");

  stat(s, 0.55, 1.75, 4.2, "18.1万コマ", "JEPXスポット30分値（FY2016〜26・欠損ゼロを確認）", { numSize: 28, numH: 0.55 });
  stat(s, 0.55, 2.75, 4.2, "61ファイル", "九州エリア需給実績（60分／30分粒度の混在を統一）", { numSize: 28, numH: 0.55 });

  card(s, 0.55, 3.85, 4.3, 2.6, C.tint);
  s.addText("検証で発見・修正したデータ不具合 2件", { x: 0.8, y: 4.05, w: 3.85, h: 0.35, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "連系線潮流の符号反転（新旧形式で定義が逆）", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
    { text: "2026年4〜5月の列構成変更（22列化）", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
    { text: "→ ヘッダー名ベースの読込に変更して解消。FY2016〜25の結果への影響なし（詳細: data/README.md）", options: {} },
  ], { x: 0.85, y: 4.45, w: 3.8, h: 1.9, fontSize: 10, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  // 系譜図（raw → パネル → 分析 → 図表）
  const dx = 5.25, dw = 7.5;
  card(s, dx, 1.75, 3.62, 0.85, C.tint, C.line);
  s.addText([
    { text: "JEPXスポット約定価格（30分値）", options: { bold: true, color: C.navy, breakLine: true } },
    { text: "FY2016〜2026｜約18.1万コマ", options: { color: C.gray, fontSize: 9 } },
  ], { x: dx + 0.15, y: 1.75, w: 3.35, h: 0.85, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });
  card(s, dx + 3.88, 1.75, 3.62, 0.85, C.tint, C.line);
  s.addText([
    { text: "九州電力 エリア需給実績", options: { bold: true, color: C.navy, breakLine: true } },
    { text: "60分→30分粒度｜61ファイル", options: { color: C.gray, fontSize: 9 } },
  ], { x: dx + 4.03, y: 1.75, w: 3.35, h: 0.85, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });

  downArrow(s, dx + dw / 2, 2.68);
  card(s, dx, 2.98, dw, 0.78, C.tint, C.line);
  s.addText([
    { text: "01_build_panel.py — 検証・統合パネル　", options: { bold: true, color: C.navy } },
    { text: "符号・単位・粒度の統一／整合チェック", options: { color: C.gray, fontSize: 9.5 } },
  ], { x: dx + 0.15, y: 2.98, w: dw - 0.3, h: 0.78, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });

  downArrow(s, dx + dw / 2, 3.84);
  card(s, dx, 4.14, dw, 0.78, C.tint, C.line);
  s.addText([
    { text: "分析スクリプト 02〜08　", options: { bold: true, color: C.navy } },
    { text: "記述統計・バックテスト・モンテカルロ・要因分解・反実仮想・帯域分解", options: { color: C.gray, fontSize: 9.5 } },
  ], { x: dx + 0.15, y: 4.14, w: dw - 0.3, h: 0.78, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle" });

  downArrow(s, dx + dw / 2, 5.0);
  card(s, dx, 5.3, dw, 0.7, C.navy);
  s.addText("図表 f1〜f15 ＋ 数表（本日の全スライドの裏付け）", { x: dx + 0.15, y: 5.3, w: dw - 0.3, h: 0.7, fontSize: 11, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle", align: "center" });

  footnote(s, "長期比較は60分粒度に統一。FY2026は部分年度（4〜7月）。全手法の定義・限界の一覧は kyushu-methods-data.md");
  pageNum(s, "2");
  s.addNotes("検証過程でデータ不具合2件（連系線の符号反転・2026年の列構成変更）を発見し修正 — 品質管理の証として一言。");
}

// =====================================================================
// P3. 事実①: 太陽光は失速していない
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜事実①", "太陽光は失速していない — 発電量2.1倍・シェア17%へ");

  stat(s, 0.55, 1.78, 4.2, "15.0 TWh", "FY2025の太陽光発電量（過去最高）", { numSize: 30, numH: 0.6, labelH: 0.35 });
  stat(s, 0.55, 2.78, 4.2, "2.1倍", "FY2016比（7.1 → 15.0 TWh）", { numSize: 30, numH: 0.6, labelH: 0.35 });
  stat(s, 0.55, 3.78, 4.2, "8.2 → 17.3%", "発電量シェア（対エリア需要）。FY2023のみ小幅減、趨勢として増加", { numSize: 24, numH: 0.55, labelH: 0.55 });

  card(s, 0.55, 4.95, 4.2, 1.15, C.tint);
  s.addText([
    { text: "出力制御：", options: { bold: true, color: C.navy } },
    { text: "FY2018に開始。制御実施日は年間約4割、制御率のピークはFY2023の8.7%", options: { color: C.text } },
  ], { x: 0.8, y: 4.95, w: 3.75, h: 1.15, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });

  s.addText([
    { text: "→ 後で見る「床の減少」の犯人は、", options: { breakLine: true } },
    { text: "太陽光の失速ではない", options: {} },
  ], { x: 0.55, y: 6.35, w: 4.3, h: 0.7, fontSize: 12, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  fig(s, "kyushu/f4-solar-vs-floor.png", 5.05, 1.72, 7.75, 1.58);
  pageNum(s, "3");
  s.addNotes("後で見る「床の減少」の犯人は太陽光の失速ではない、と先に潰す。");
}

// =====================================================================
// P4. 事実②: 価格構造は激変
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜事実②", "価格構造は激変した — ダックカーブの深化と「床」の出現→反転");

  fig(s, "kyushu/f1-duck-curve.png", 0.55, 1.72, 5.95, 1.66);   // h=3.59
  fig(s, "kyushu/f2-floor-koma.png", 6.8, 1.72, 5.95, 1.64);    // h=3.63

  s.addText([
    { text: "夕方ランプ（昼の谷→夕ピーク）：", options: { color: C.text } },
    { text: "約3円 → 約10円", options: { bold: true, color: C.navy } },
  ], { x: 0.55, y: 5.5, w: 5.95, h: 0.35, fontSize: 12, fontFace: FONT, margin: 0, align: "center" });
  s.addText([
    { text: "床（0.01円）コマ数：", options: { color: C.text } },
    { text: "0 → 2,178（FY2023）→ 983（FY2025）", options: { bold: true, color: C.navy } },
  ], { x: 6.8, y: 5.5, w: 5.95, h: 0.35, fontSize: 12, fontFace: FONT, margin: 0, align: "center" });

  card(s, 0.55, 6.05, 12.2, 0.8, C.orangeTint);
  s.addText("太陽光は増え続けているのに、床は減っている — おかしくないですか？　→ P7〜P9で回収します", { x: 0.75, y: 6.05, w: 11.8, h: 0.8, fontSize: 13.5, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0, valign: "middle", align: "center" });
  pageNum(s, "4");
  s.addNotes("ここでフックを掛ける。「太陽光は増え続けているのに床は減っている。おかしくないですか？」→ P7-9で回収すると予告。");
}

// =====================================================================
// P5. 蓄電池価値①: バックテスト
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜蓄電池価値①", "スポット裁定は約1万円/kW-年 — 単独では投資が成立しない");

  fig(s, "kyushu/f7-backtest-annual.png", 0.55, 1.72, 7.25, 1.63); // h=4.45

  const rx = 8.1, rw = 4.7;
  stat(s, rx, 1.72, rw, "1.0〜1.25万円/kW-年", "完全予見の年間裁定粗利（FY2023〜25）", { numSize: 19, numH: 0.42, labelH: 0.32, labelSize: 9.5 });
  stat(s, rx, 2.52, rw, "0.8〜1.05万円/kW-年", "実行可能戦略（捕捉率 約8割）", { numSize: 19, numH: 0.42, labelH: 0.32, labelSize: 9.5 });

  card(s, rx, 3.35, rw, 0.95, C.tint);
  s.addText([
    { text: "年換算資本費 約2万円/kW-年", options: { bold: true, color: C.navy } },
    { text: " に対しスポット単独では損益分岐に届かない", options: { color: C.text } },
  ], { x: rx + 0.2, y: 3.35, w: rw - 0.4, h: 0.95, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.2 });

  card(s, rx, 4.45, rw, 2.0, C.orangeTint);
  s.addText("戦略b（残余需要予測）の逆転", { x: rx + 0.2, y: 4.6, w: rw - 0.4, h: 0.32, fontSize: 12, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "捕捉率 約4割（FY2016〜17）→ 80〜84%（FY2021以降）", options: { bold: true, color: C.text } },
    { text: " で前日価格ナイーブを一貫して逆転 ＝ 価格形状が太陽光（残余需要）で予測できる構造になった証拠", options: { color: C.text } },
  ], { x: rx + 0.2, y: 4.95, w: rw - 0.4, h: 1.4, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  footnote(s, "仕様: 1MW/4MWh・往復効率85%・1日1サイクル・劣化無視（考慮で▲27%規模; Butters 2025）。需給調整・容量市場収益を含まない下限推定");
  pageNum(s, "5");
  s.addNotes("逆転は「価格形状が太陽光（残余需要）で予測できる構造になった」ことの運用成績による証明 — 金融工学の聴衆に一番刺さる1枚。スポット単独で未達は Butters (2025, Econometrica) と整合。");
}

// =====================================================================
// P6. 蓄電池価値②: 水準効果の分離
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜蓄電池価値②", "価値拡大は価格水準のせいだけではない — 規格化しても約2倍、直近の縮小はより鮮明");

  fig(s, "kyushu/f9-relative-spread.png", 0.55, 1.72, 6.7, 1.66); // h=4.04

  const rx = 7.5, rw = 5.3;
  const rows = [
    ["FY2022の突出は水準効果が大", "絶対スプレッド3.6倍 → 規格化後は2.5倍に縮小"],
    ["FY2023は形状（太陽光）由来", "平均価格9.1円/kWhと安い年なのに相対スプレッド1.27"],
    ["直近の縮小は相対でより鮮明", "FY2023→25: 絶対−16%に対し相対は 1.27→0.86（−32%）"],
  ];
  rows.forEach((r, i) => {
    const y = 1.72 + i * 0.72;
    s.addText([
      { text: r[0], options: { bold: true, color: C.navy, breakLine: true } },
      { text: r[1], options: { color: C.text, fontSize: 10 } },
    ], { x: rx, y, w: rw, h: 0.68, fontSize: 11, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
  });

  fig(s, "kyushu/f8-montecarlo.png", rx, 4.0, 4.55, 1.63); // h=2.79
  footnote(s, "規格化ベースの代替（システムプライス・燃料指数）は感応度候補。モンテカルロ（右下）は年度間の構造ドリフトを過小評価 — HAR型長期記憶の導入が本番課題（第2報§2.3）");
  pageNum(s, "6");
  s.addNotes("「価値は価格水準に引っ張られているだけでは」への先回り。MCモデルが年度間変動を過小評価する検証結果 → HAR型長期記憶が本番課題、と伏線。時間超過時はこの1枚をAppendixへ。");
}

// =====================================================================
// P7. パズル: 床とスプレッドの縮小
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜パズル", "出力制御は続いているのに、床とスプレッドが縮む — 縮小は「底上げ型」");

  fig(s, "kyushu/f12-top-bottom.png", 0.55, 1.72, 6.7, 1.69); // h=3.96

  const rx = 7.55, rw = 5.2;
  s.addText("Top4h（最高4時間）中央値", { x: rx, y: 1.72, w: rw, h: 0.28, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "14.2 → 14.0円　", options: { bold: true, color: C.navy } },
    { text: "ほぼ不変", options: { color: C.gray, fontSize: 11 } },
  ], { x: rx, y: 2.0, w: rw, h: 0.38, fontSize: 17, fontFace: FONT, margin: 0 });
  s.addText("Bottom4h（最安4時間）中央値", { x: rx, y: 2.5, w: rw, h: 0.28, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "3.2 → 6.9円　", options: { bold: true, color: C.orangeDark } },
    { text: "+3.7円の底上げ", options: { bold: true, color: C.orangeDark, fontSize: 11 } },
  ], { x: rx, y: 2.78, w: rw, h: 0.38, fontSize: 17, fontFace: FONT, margin: 0 });

  s.addText("制御時間中の床約定率（物理と市場の連動）", { x: rx, y: 3.45, w: rw, h: 0.3, fontSize: 10.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addTable([
    ["FY2019", "FY2022", "FY2023", "FY2024", "FY2025"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center", fontSize: 9.5 } })),
    [
      { text: "33%", options: { align: "center" } },
      { text: "50%", options: { align: "center" } },
      { text: "74%", options: { bold: true, color: C.orangeDark, fill: { color: C.orangeTint }, align: "center" } },
      { text: "51%", options: { align: "center" } },
      { text: "40%", options: { bold: true, color: C.orangeDark, fill: { color: C.orangeTint }, align: "center" } },
    ],
  ], { x: rx, y: 3.78, colW: [1.04, 1.04, 1.04, 1.04, 1.04], rowH: 0.36, fontSize: 11.5, fontFace: FONT, color: C.text, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle" });

  s.addText("制御は続くのに床では約定しなくなった — 物理（制御）と市場（床）の連動低下という観察。制御の内訳・入札行動変化など複数仮説があり、内訳確認は今後", { x: rx, y: 4.75, w: rw, h: 1.0, fontSize: 10, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  s.addText("平均のダックカーブは深いまま、「典型日の底」が上がった — 平均と分布の区別が鍵", { x: 0.55, y: 5.95, w: 12.2, h: 0.4, fontSize: 13, bold: true, color: C.navy, fontFace: FONT, margin: 0, align: "center" });
  pageNum(s, "7");
  s.addNotes("「ダックカーブの形は深いまま（平均）だが典型日の底は上がった（中央値）」— 平均と分布の区別。物理（制御）と市場（床）の連動低下は観察として提起（断定しない）。");
}

// =====================================================================
// P8. 要因分解
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜要因分解", "誰が底を持ち上げたのか — 需要と揚水、ただし場面で役割が違う");

  fig(s, "kyushu/f11-absorption.png", 0.55, 1.68, 8.55, 2.36); // h=3.62

  const rx = 9.35, rw = 3.4;
  s.addText("昼間10〜14時の変化（FY2023→25、MW平均）", { x: rx, y: 1.68, w: rw, h: 0.45, fontSize: 10, bold: true, color: C.navy, fontFace: FONT, margin: 0, lineSpacingMultiple: 1.1 });
  const dRows = [
    ["太陽光（制御前）", "+466"],
    ["需要", "+243"],
    ["　うちフラット新規負荷", "+141〜196"],
    ["揚水＋蓄電池充電", "+306"],
    ["　うち蓄電池単独", "±10"],
    ["原子力", "−338"],
    ["火力", "−356"],
    ["域外送電", "−351"],
  ].map(r => ([
    { text: r[0], options: { align: "left" } },
    { text: r[1], options: { align: "right", bold: true, color: r[1].startsWith("+") ? C.orangeDark : C.navy } },
  ]));
  s.addTable(dRows, { x: rx, y: 2.15, colW: [2.3, 1.1], rowH: 0.36, fontSize: 9.5, fontFace: FONT, color: C.text, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle" });

  const cond = [
    ["典型日", "揚水充電が +306MW の底上げ — 「運転の面」の拡大が主役"],
    ["限界帯（0.01〜3円）", "+553MW — 床すれすれのコマを救出し 0.01円を回避"],
    ["深い余剰日", "+86MWどまり（p90 約2.0GWで実効上限）→ 床は消せない"],
  ];
  cond.forEach((c0, i) => {
    const x = 0.55 + i * 4.145;
    card(s, x, 5.5, 3.94, 1.3, i === 2 ? C.orangeTint : C.tint);
    s.addText(c0[0], { x: x + 0.2, y: 5.62, w: 3.55, h: 0.3, fontSize: 11, bold: true, color: i === 2 ? C.orangeDark : C.navy, fontFace: FONT, margin: 0 });
    s.addText(c0[1], { x: x + 0.2, y: 5.94, w: 3.55, h: 0.8, fontSize: 9.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });
  });

  footnote(s, "会計的分解であり因果ではない（火力・域外送電は価格への内生反応を含む）。条件付き分解の詳細は第3報追補§6");
  pageNum(s, "8");
  s.addNotes("「平均でなく条件付きで見る」と役割が判明 — 揚水は典型日の底上げと床すれすれの救出の主役だが、深い余剰日の床は消せない。");
}

// =====================================================================
// P9. 構造と一時の切り分け
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜構造と一時の切り分け", "原発復帰で床は反転増加 — 「構造」と「一時」を分けて主張する");

  card(s, 0.55, 1.68, 5.95, 1.95, C.tint);
  s.addText("整合的観察：原発4機フル復帰のFY2026（4〜7月・同期間比）", { x: 0.8, y: 1.82, w: 5.5, h: 0.35, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  stat(s, 0.95, 2.25, 2.6, "床コマ +33%", "", { numSize: 21, numColor: C.orangeDark, numH: 0.45, labelH: 0.1 });
  stat(s, 3.6, 2.25, 2.7, "制御量 +62%", "", { numSize: 21, numColor: C.orangeDark, numH: 0.45, labelH: 0.1 });
  s.addText("→ 原子力（定検サイクル）＝一時要因と整合。単年・4ヶ月の観察につき年度末に通年で再検証", { x: 0.8, y: 2.85, w: 5.5, h: 0.65, fontSize: 10, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  card(s, 6.8, 1.68, 5.95, 1.95, C.tint);
  s.addText("反実仮想：需要増なし・原子力FY2023水準なら", { x: 7.05, y: 1.82, w: 5.5, h: 0.35, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "床コマは +20〜33% 頻発", options: { bold: true, color: C.orangeDark, breakLine: true } },
    { text: "一方、裁定価値への影響は小さい（−1.5%、モデル再現誤差の範囲内の示唆）— フラット負荷は山と底を同時に動かすため", options: { color: C.text } },
  ], { x: 7.05, y: 2.25, w: 5.5, h: 1.3, fontSize: 10.5, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  fig(s, "kyushu/f14-counterfactual.png", 0.55, 3.82, 7.15, 2.35); // h=3.04 → 6.86

  card(s, 8.0, 3.82, 4.75, 3.0, C.navy);
  s.addText("整理", { x: 8.25, y: 3.98, w: 4.25, h: 0.32, fontSize: 12, bold: true, color: C.white, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "構造：", options: { bold: true, color: C.white } },
    { text: "需要増と揚水の面的拡大が底を支える", options: { color: C.light, breakLine: true, paraSpaceAfter: 6 } },
    { text: "一時：", options: { bold: true, color: C.white } },
    { text: "原発定検と太陽光の年次条件が床コマ数を振らす", options: { color: C.light, breakLine: true, paraSpaceAfter: 8 } },
    { text: "昼だけ効く吸収（揚水、そして将来の蓄電池）だけが蓄電池価値を侵食する", options: { bold: true, color: "F7C4A8" } },
  ], { x: 8.25, y: 4.35, w: 4.25, h: 2.3, fontSize: 11, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });

  footnote(s, "反実仮想は部分均衡（吸収側固定）につき床頻度は上限方向の評価。モデル内比較（再現 vs 反実仮想）で変化分のみ解釈");
  pageNum(s, "9");
  s.addNotes("整理 —「構造＝需要増と揚水の面的拡大が底を支える／一時＝原発定検と太陽光の年次条件が床コマ数を振らす」。昼だけ効く吸収だけが蓄電池価値を侵食する。");
}

// =====================================================================
// P10. 前半まとめ: 3つの教訓
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "前半：九州×太陽光｜まとめ", "九州が教えてくれた3つのこと");

  const lessons = [
    ["「昼だけ効く吸収」が価値を侵食する", "揚水の運用拡大は蓄電池カニバリゼーションの予行演習。蓄電池本体はまだ±10MWで、いま侵食の主役は揚水"],
    ["床・スプレッドは「底側」で決まる", "低価格帯の買い側（揚水・蓄電池充電・産業需要）のモデリングが価値評価の一級論点"],
    ["会計的分解では因果が閉じない", "外生ドライバーの識別には構造（均衡）モデルが必要 → 修論本体の仕事"],
  ];
  lessons.forEach((l, i) => {
    const x = 0.55 + i * 4.145;
    card(s, x, 1.95, 3.94, 2.95, C.tint);
    circleNum(s, x + 0.28, 2.23, 0.5, i + 1);
    s.addText(l[0], { x: x + 0.28, y: 2.95, w: 3.4, h: 0.55, fontSize: 13.5, bold: true, color: C.navy, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
    s.addText(l[1], { x: x + 0.28, y: 3.55, w: 3.4, h: 1.25, fontSize: 10.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });

  card(s, 0.55, 5.45, 12.2, 1.0, C.navy);
  s.addText("この3つを最も鋭い形で問える市場はどこか？　→　後半：北海道×風力×蓄電池", { x: 0.8, y: 5.45, w: 11.7, h: 1.0, fontSize: 15, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle", align: "center" });
  pageNum(s, "10");
  s.addNotes("「この3つを最も鋭い形で問える市場はどこか？」→ 後半へ。");
}

// =====================================================================
// P11. 先行研究マップ
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "後半：北海道×風力への転換｜なぜ九州で書かないか", "九州×太陽光では修論を書かない — 先行研究は厚く、JEPX×風力は空白");

  card(s, 0.55, 1.78, 5.95, 3.3, C.tint);
  s.addText("太陽光×蓄電池 — 先行研究が厚い", { x: 0.8, y: 1.95, w: 5.5, h: 0.35, fontSize: 13, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "Butters, Dorsey & Gowrisankaran (2025, Econometrica) — CAISO蓄電池の参入均衡モデル（再現パッケージ公開）", options: { bullet: true, breakLine: true, paraSpaceAfter: 7 } },
    { text: "Lamp & Samano (2022) — 蓄電池普及によるスプレッドの自己侵食（カニバリゼーション）", options: { bullet: true, breakLine: true, paraSpaceAfter: 7 } },
    { text: "Fuke & Ohashi (2025) — 九州の太陽光と市場価格", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
    { text: "→ 前半はこの系譜の追試＋日本版としては成立するが、修論の新規性の核にはならない", options: { italic: true, color: C.gray } },
  ], { x: 0.85, y: 2.4, w: 5.4, h: 3.5, fontSize: 10.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  card(s, 6.8, 1.78, 5.95, 3.3, C.orangeTint);
  s.addText("風力×市場価格（JEPX）— ほぼ空白", { x: 7.05, y: 1.95, w: 5.5, h: 0.35, fontSize: 13, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0 });
  s.addText([
    { text: "Sakaguchi & Fujii (2021) — FY2016〜19・北海道で高分位の風力メリットオーダー効果を検出", options: { bullet: true, breakLine: true, paraSpaceAfter: 7 } },
    { text: "越境効果研究（Applied Economics 2023） — エリア間の風力越境影響", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
    { text: "風力が倍増した2023年以降のデータでの分析は、学術・業界レポートとも見当たらない（notes/12で棚卸し済み）", options: { bold: true, color: C.orangeDark } },
  ], { x: 7.1, y: 2.4, w: 5.4, h: 3.5, fontSize: 10.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  card(s, 0.55, 5.55, 12.2, 0.8, C.navy);
  s.addText("右列の空白 ＝ 「風力主導 × 連系線制約」 → 北海道へ", { x: 0.8, y: 5.55, w: 11.7, h: 0.8, fontSize: 13.5, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "middle", align: "center" });
  pageNum(s, "11");
  s.addNotes("「前半はこの左列の追試＋日本版としては成立するが、修論の新規性の核にはならない。右列の空白＝風力主導×連系線制約へ向かう」。");
}

// =====================================================================
// P12. なぜ北海道か①
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "後半：北海道×風力への転換｜なぜ北海道か①", "「風力大×融通小」は全国で北海道だけ — しかも倍増は直近2年");

  fig(s, "fig1-wind-vs-interconnection.png", 0.55, 1.72, 5.5, 1.39); // h=3.96

  s.addText("「最近まで風力は少なかった」が正しい — だからこそ今。影響がこれから顕在化する初期段階で、事前の均衡推定の価値が最大", { x: 0.55, y: 5.85, w: 5.5, h: 0.95, fontSize: 11, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });

  // 風力設備の時系列
  const tx = 6.4, tw = 6.35;
  s.addText("風力設備の推移（導入量・JWPA）", { x: tx, y: 1.72, w: tw, h: 0.3, fontSize: 10.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  const steps = [["36万kW", "2010年代"], ["83万kW", "2023年末"], ["128万kW", "2024年末・全国1位"]];
  steps.forEach((st, i) => {
    const x = tx + i * 2.2;
    card(s, x, 2.08, 1.85, 0.85, i === 2 ? C.orangeTint : C.tint);
    s.addText([
      { text: st[0], options: { bold: true, fontSize: 14, color: i === 2 ? C.orangeDark : C.navy, breakLine: true } },
      { text: st[1], options: { fontSize: 8.5, color: C.gray } },
    ], { x, y: 2.08, w: 1.85, h: 0.85, fontFace: FONT, margin: 0, align: "center", valign: "middle" });
    if (i < 2) s.addShape(pres.ShapeType.rightArrow, { x: x + 1.9, y: 2.38, w: 0.25, h: 0.24, fill: { color: C.blue } });
  });
  s.addText("単年 +45.5万kW ＝ 全国増の約7割（石狩湾新港洋上112MWを含む）", { x: tx, y: 3.0, w: tw, h: 0.3, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0 });

  const chips = [
    ["風力/需要比 32%", "次点の東北は19%"],
    ["連系線容量の1.5倍", "風力接続量が上回るのは全国唯一"],
    ["洋上5海域 最大+380万kW", "実現なら風力/需要比 約90%へ"],
    ["蓄電池の接続申込 1.6GW", "平均需要の約5割"],
  ];
  chips.forEach((c0, i) => {
    const x = tx + (i % 2) * 3.25, y = 3.45 + Math.floor(i / 2) * 1.1;
    card(s, x, y, 3.1, 0.98, C.tint);
    s.addText([
      { text: c0[0], options: { bold: true, fontSize: 12, color: C.navy, breakLine: true } },
      { text: c0[1], options: { fontSize: 9, color: C.gray } },
    ], { x: x + 0.18, y, w: 2.8, h: 0.98, fontFace: FONT, margin: 0, valign: "middle", lineSpacingMultiple: 1.15 });
  });
  s.addText("北海道→東北の間接送電権が2026年度に商品化 ＝ 余剰閉じ込め型の市場分断の制度的認定", { x: tx, y: 5.75, w: tw, h: 0.55, fontSize: 10, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  footnote(s, "導入量（JWPA: 2024年末128万kW）と接続量（系統WG資料: 136万kW）は定義・時点の異なる統計（使い分けは notes/11 §1.2）");
  pageNum(s, "12");
  s.addNotes("「最近まで風力は少なかった、が正しい。だからこそ今」— 価格影響がこれから顕在化する初期段階であり、事後検証でなく事前の均衡推定に最も価値があるタイミング。");
}

// =====================================================================
// P13. なぜ北海道か②: 浸透率アンカー
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "後半：北海道×風力への転換｜なぜ北海道か②", "風力はスポット価格に効くのか — 浸透率は「検出水準」に到達しつつある");

  const hdr = ["市場", "風力シェア（エネルギーベース）", "検出された効果", "出典"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5 } }));
  function row(cells, hl) {
    return cells.map(t => ({ text: t, options: hl ? { fill: { color: C.orangeTint }, bold: true, color: C.orangeDark } : {} }));
  }
  s.addTable([
    hdr,
    row(["ERCOT（米テキサス）", "5〜8%", "価格水準・ボラティリティへの効果を検出", "Woo et al. (2011)"]),
    row(["ドイツ", "6〜8%", "日前価格のボラティリティ増を検出", "Ketterer (2014)"]),
    row(["北海道（FY2016〜19）", "現在の半分以下の設備", "高分位（価格上位帯）で風力の価格押下げを検出", "Sakaguchi & Fujii (2021)"]),
    row(["北海道（現在）", "実績 約5〜7%／現行設備の年換算 8〜10%", "検出水準に到達しつつある段階", "本分析（notes/11）"], true),
    row(["デンマーク／南豪州", "54%／（負値価格が四半期の46%）", "洋上導入後の北海道（45〜50%）の参照領域", "OWID・AEMO"]),
  ], { x: 0.55, y: 1.8, colW: [2.5, 3.3, 4.0, 2.4], rowH: 0.62, fontSize: 10.5, fontFace: FONT, color: C.text, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle" });

  card(s, 0.55, 5.9, 12.2, 0.85, C.tint);
  s.addText("「効くかどうか」はもう論点ではない — 「どれだけ・どの時間構造で効くか」が問い", { x: 0.8, y: 5.9, w: 11.7, h: 0.85, fontSize: 15, bold: true, color: C.navy, fontFace: FONT, margin: 0, valign: "middle", align: "center" });

  footnote(s, "出典の詳細と数値の由来は notes/11 §1（OWID・AEMO・各論文）。北海道のシェアは発電実績ベースの概算");
  pageNum(s, "13");
  s.addNotes("欧米ではエネルギーシェア5〜10%で効果検出。北海道は到達しつつあり、しかも Sakaguchi & Fujii は設備が今の半分以下の時期に検出済み。想定反論への回答Ⅰ。");
}

// =====================================================================
// P14. なぜ北海道か③: 帯域分解と揚水カウンター
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "後半：北海道×風力への転換｜なぜ北海道か③", "打ち消し合いでボラは消えない — 変動の主戦場は「数日帯域」");

  fig(s, "kyushu/f15-wind-timescale.png", 0.55, 1.68, 8.7, 2.5); // h=3.48

  const rx = 9.45, rw = 3.3;
  s.addText("風力分散のシェア（フリート集約後・九州実測）", { x: rx, y: 1.68, w: rw, h: 0.45, fontSize: 10, bold: true, color: C.navy, fontFace: FONT, margin: 0, lineSpacingMultiple: 1.1 });
  const bands = [["<6時間", "1.9%"], ["6〜24時間", "8.7%"], ["1〜7日", "43.7%"]];
  bands.forEach((b, i) => {
    const y = 2.2 + i * 0.52;
    s.addText(b[0], { x: rx, y, w: 1.5, h: 0.45, fontSize: 11, color: C.text, fontFace: FONT, margin: 0, valign: "middle" });
    s.addText(b[1], { x: rx + 1.5, y, w: 1.7, h: 0.45, fontSize: i === 2 ? 20 : 13, bold: true, color: i === 2 ? C.orangeDark : C.navy, fontFace: FONT, margin: 0, align: "right", valign: "middle" });
  });
  s.addText("太陽光は6〜24時間帯が66%と対照的。低出力イベントは最長158時間", { x: rx, y: 3.85, w: rw, h: 0.9, fontSize: 9.5, color: C.gray, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  card(s, 0.55, 5.3, 5.95, 1.6, C.tint);
  s.addText("空間平滑化が消すのは高周波だけ", { x: 0.8, y: 5.42, w: 5.5, h: 0.3, fontSize: 11.5, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  s.addText("総観規模（数百km）の変動は相関が残る（St. Martin 2015。デンマーク〜ドイツ間でも0.65: Malvaldi 2017）。北海道の風力は日本海側の約300km帯に集中", { x: 0.8, y: 5.74, w: 5.5, h: 1.05, fontSize: 10, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });

  card(s, 6.8, 5.3, 5.95, 1.6, C.orangeTint);
  s.addText("揚水カウンター論 → 研究の問いへ", { x: 7.05, y: 5.42, w: 5.5, h: 0.3, fontSize: 11.5, bold: true, color: C.orangeDark, fontFace: FONT, margin: 0 });
  s.addText("九州＝太陽光（日内周期）×揚水230万kW（日次サイクル）の好相性ペア。北海道は京極40万kW（約1/6）で、数日帯域に日次サイクル貯蔵は原理的にミスマッチ → 空隙を蓄電池が埋め得るか・均衡でいくら入るか。4h電池も同じミスマッチ＝duration内生化が研究対象", { x: 7.05, y: 5.74, w: 5.5, h: 1.1, fontSize: 9.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });

  footnote(s, "「数日周期」ではなく「変動エネルギーの中心が数日帯域にある確率的変動」。帯域分解は移動平均カスケードによる非直交分解（交差項約2割、シェア合計≠100%）");
  pageNum(s, "14");
  s.addNotes("「単一サイトの波形は時間レベルでギザギザ（実務感覚は正しい）。しかし市場が見るのは集約出力で、そこでは数日帯域が支配的」。揚水カウンター論から duration 内生化へ。想定反論への回答Ⅱ。");
}

// =====================================================================
// P15. 研究計画とNext Action
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "後半：北海道×風力への転換｜研究計画", "研究の3段構成とNext Action — 分析装置はエリア名を変えるだけで移植できる");

  const stages = [
    ["① 実証", "ボラティリティ生成関数（HAR-CV-JV-X）— 風力・太陽光の寄与を分離"],
    ["② 構造", "残余需要×経験的供給曲線＋蓄電池の動的計画 — 底側（買い吸収）のモデリングを重視"],
    ["③ 均衡", "自由参入のゼロ利潤均衡 K*(R) — duration選択の内生化"],
  ];
  stages.forEach((st, i) => {
    const x = 0.55 + i * 4.1;
    card(s, x, 1.78, 3.7, 1.7, C.tint);
    s.addText(st[0], { x: x + 0.2, y: 1.92, w: 3.3, h: 0.35, fontSize: 13, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
    s.addText(st[1], { x: x + 0.2, y: 2.3, w: 3.3, h: 1.1, fontSize: 10.5, color: C.text, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.25 });
    if (i < 2) s.addShape(pres.ShapeType.rightArrow, { x: x + 3.72, y: 2.5, w: 0.35, h: 0.28, fill: { color: C.blue } });
  });

  card(s, 0.55, 3.75, 12.2, 0.9, C.navy);
  s.addText([
    { text: "最終的な主張の形：", options: { color: C.light } },
    { text: "「市場構造から、北海道では蓄電池 K* GW/GWh までの増加が経済合理的」", options: { bold: true, color: C.white } },
    { text: "（シナリオ束での下限主張）", options: { color: C.light } },
  ], { x: 0.8, y: 3.75, w: 11.7, h: 0.9, fontSize: 13.5, fontFace: FONT, margin: 0, valign: "middle", align: "center" });

  s.addText("Next Action", { x: 0.55, y: 4.95, w: 4.0, h: 0.35, fontSize: 13, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  const actions = [
    "北海道・東北の需給実績CSVの取得（掲載ローリング対策で至急｜担当：本人）",
    "風力×エリアプライスの分位点回帰＋帯域分解の北海道版（データ到着後すぐ｜第一弾実証）",
    "出力制御の内訳・需要帰属の一次資料確認",
  ];
  actions.forEach((a, i) => {
    const y = 5.35 + i * 0.52;
    circleNum(s, 0.6, y, 0.36, i + 1, C.blue);
    s.addText(a, { x: 1.1, y: y - 0.03, w: 11.6, h: 0.45, fontSize: 11.5, color: C.text, fontFace: FONT, margin: 0, valign: "middle" });
  });

  footnote(s, "手法は九州パイプライン＋Butters (2025) 枠組み（再現パッケージ公開済み）を北海道仕様（市場分断・下限価格・数日帯域・泊/ラピダスのシナリオ行列）へ拡張");
  pageNum(s, "15");
  s.addNotes("締め:「前半の分析装置（パイプライン・指標・帯域分解・バックテスト）はエリア名を変えるだけで移植できる。手戻りはない」。");
}

// =====================================================================
// Appendix 扉
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.dark };
  s.addText("Appendix", { x: 0.55, y: 2.5, w: 12.23, h: 0.85, fontSize: 40, bold: true, color: C.white, fontFace: FONT, margin: 0, align: "center" });
  s.addText("質疑対応資料", { x: 0.55, y: 3.4, w: 12.23, h: 0.45, fontSize: 16, color: C.light, fontFace: FONT, margin: 0, align: "center" });
  s.addText([
    { text: "A1  キーナンバー総括表", options: { breakLine: true, paraSpaceAfter: 5 } },
    { text: "A2  スプレッド分布・制御日比較（f3・f5）", options: { breakLine: true, paraSpaceAfter: 5 } },
    { text: "A3  価格分位点・価格帯構成（f6・f13）", options: { breakLine: true, paraSpaceAfter: 5 } },
    { text: "A4  等価時間・昼間需給の分解（f10）", options: { breakLine: true, paraSpaceAfter: 5 } },
    { text: "A5  想定問答", options: {} },
  ], { x: 4.7, y: 4.3, w: 5.0, h: 2.3, fontSize: 12, color: C.light, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.2 });
}

// =====================================================================
// A1. キーナンバー総括表
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "Appendix A1", "キーナンバー総括表（この1枚で質疑に耐える）");

  const bold = t => ({ text: t, options: { bold: true, color: C.orangeDark } });
  const c = t => ({ text: t, options: {} });
  const hdrRow = ["指標", "FY2016", "FY2019", "FY2022※", "FY2023", "FY2024", "FY2025"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center", fontSize: 10 } }));
  const label = t => ({ text: t, options: { align: "left" } });
  function r(name, vals, boldIdx) {
    return [label(name)].concat(vals.map((v, i) => {
      const cell = (boldIdx || []).includes(i) ? bold(v) : c(v);
      cell.options.align = "center";
      return cell;
    }));
  }
  s.addTable([
    hdrRow,
    r("太陽光発電量 (GWh)", ["7,086", "10,438", "13,737", "13,455", "14,221", "15,014"], [5]),
    r("太陽光シェア（対エリア需要）", ["8.2%", "12.4%", "16.3%", "15.9%", "16.2%", "17.3%"], [5]),
    r("出力制御量 (GWh)／制御率", ["0", "459／4.2%", "449／3.2%", "1,290／8.7%", "751／5.0%", "979／6.1%"], [3]),
    r("0.01円コマ数（30分）", ["0", "693", "1,909", "2,178", "1,167", "983"], [3]),
    r("制御時間中の床約定率", ["—", "33%", "50%", "74%", "51%", "40%"], [3, 5]),
    r("TB4hスプレッド中央値 (円/kWh)", ["5.5", "4.6", "19.8", "10.8", "10.8", "9.2"], []),
    r("相対スプレッド（÷当日平均価格）", ["0.63", "0.64", "1.59", "1.27", "0.97", "0.86"], [3, 5]),
    r("蓄電池PF裁定価値 (円/kW-年)", ["5,823", "5,945", "24,367", "12,521", "12,402", "10,366"], [3]),
    r("同・実行可能戦略b (円/kW-年)", ["2,400", "4,295", "19,394", "10,405", "10,199", "8,712"], []),
  ], { x: 0.55, y: 1.75, colW: [3.5, 1.35, 1.4, 1.5, 1.5, 1.4, 1.4], rowH: 0.44, fontSize: 10, fontFace: FONT, color: C.text, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle" });

  footnote(s, "※FY2022は燃料危機（価格水準効果が大）。年度＝4月〜翌3月。PF＝完全予見。定義・出典は kyushu-methods-data.md", 6.5);
  pageNum(s, "A1");
}

// =====================================================================
// A2. f3 + f5
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "Appendix A2", "TB4hスプレッドの分布と、制御日 vs 非制御日");
  fig(s, "kyushu/f3-tb4h-spread.png", 0.55, 2.35, 5.95, 1.66);
  fig(s, "kyushu/f5-curtail-days.png", 6.8, 2.35, 5.95, 1.66);
  pageNum(s, "A2");
}

// =====================================================================
// A3. f6 + f13
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "Appendix A3", "価格分位点の推移と、価格帯構成の変化");
  fig(s, "kyushu/f6-quantiles.png", 0.55, 2.35, 5.95, 1.66);
  fig(s, "kyushu/f13-price-bands.png", 6.8, 2.35, 5.95, 1.7);
  pageNum(s, "A3");
}

// =====================================================================
// A4. f10 + 昼間需給の分解表
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "Appendix A4", "等価時間（価格水準で規格化した価値）と、昼間需給の変化");
  fig(s, "kyushu/f10-normalized-value.png", 0.55, 1.9, 6.55, 1.66); // h=3.95

  const rx = 7.55, rw = 5.2;
  s.addText("FY2023→25の変化（昼間10〜14時、MW平均）", { x: rx, y: 1.9, w: rw, h: 0.32, fontSize: 11, bold: true, color: C.navy, fontFace: FONT, margin: 0 });
  const rows2 = [
    ["太陽光（制御前）", "+466"],
    ["需要", "+243"],
    ["　うちフラット新規負荷（夜間帯で識別）", "+141〜196"],
    ["揚水＋蓄電池充電", "+306"],
    ["　うち蓄電池単独", "±10"],
    ["原子力", "−338"],
    ["火力", "−356"],
    ["域外送電", "−351"],
  ].map(r0 => ([
    { text: r0[0], options: { align: "left" } },
    { text: r0[1], options: { align: "right", bold: true, color: r0[1].startsWith("+") ? C.orangeDark : C.navy } },
  ]));
  s.addTable(rows2, { x: rx, y: 2.3, colW: [3.9, 1.3], rowH: 0.42, fontSize: 10, fontFace: FONT, color: C.text, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle" });
  footnote(s, "会計的分解であり因果ではない。夜間帯識別・条件付き分解の詳細は第3報（kyushu-factor-decomposition.md）");
  pageNum(s, "A4");
}

// =====================================================================
// A5. 想定問答
// =====================================================================
{
  const s = pres.addSlide();
  header(s, "Appendix A5", "想定問答");

  const qa = [
    ["床コマ減は太陽光の失速では？", "発電量はFY2025も過去最高（15.0TWh）。要因は吸収側（需要・揚水）＋一時要因（P8〜9）"],
    ["原発が要因なら一時的では？", "そのとおり。FY2026の4機復帰で床+33%と巻き戻り済み（P9）。構造要因とは区別して主張している"],
    ["揚水+300MWは太陽光5GW級に対して小さすぎないか？", "床の成否は限界的余剰（制御量1.3〜1.6GW）で決まる。限界帯（0.01〜3円）では+553MW。ただし深い余剰日は上限張り付きで、床変動の第一要因は原子力×天候（P8〜9）"],
    ["風力は打ち消し合ってボラが出ないのでは？", "消えるのは高周波のみ。フリートでは<6h成分は分散の2%、数日帯域44%が支配的（P14・f15）"],
    ["北海道にそんなに風力があったか？", "2010年代36万kW→2024年末128万kW・全国1位。倍増は直近2年（P12）"],
    ["なぜ蓄電池が吸収の主役になるのか？", "揚水は量1/6×日次サイクルで数日帯域とミスマッチ。ただし4h電池も同じ課題 → duration内生化が研究の問い（P14）"],
    ["反実仮想・モデルの信頼性は？", "部分均衡・モデル内比較のみ解釈。吸収側の内生化こそ本番の構造モデル（P9）"],
  ];
  qa.forEach((p, i) => {
    const col = i < 4 ? 0 : 1;
    const idx = col === 0 ? i : i - 4;
    const x = 0.55 + col * 6.25, w = 5.95;
    const y = 1.75 + idx * 1.32;
    s.addText([
      { text: "Q. " + p[0], options: { bold: true, color: C.navy, breakLine: true, paraSpaceAfter: 3 } },
      { text: "A. " + p[1], options: { color: C.text } },
    ], { x, y, w, h: 1.28, fontSize: 10, fontFace: FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.18 });
  });
  pageNum(s, "A5");
}

// =====================================================================
pres.writeFile({ fileName: "/home/user/work/thesis/slides/ゼミ発表_九州実証と北海道転換.pptx" }).then(() => {
  console.log("OK: ゼミ発表_九州実証と北海道転換.pptx");
});
