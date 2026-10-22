// 研究内容の理解のためのデッキ（2026-10-21）— 原稿 v0.4 の全分析を「問い・データ・手法・結果」で整理
// ユーザーの既存フォーマット準拠（白背景・青緑パレット・青ヘッダー表・左青バー見出し。build_deck_20260817_v3.js と同じ部品）
// フォントは Office（Mac/Windows）に同梱の游ゴシックを使う（Noto Sans JP が無い環境での置換を避ける）
// 実行: NODE_PATH=<scratchpad>/ppt/node_modules node build_deck.js deck_spec.json out.pptx
// スライドの中身はすべて deck_spec.json（このスクリプトは描画だけ）。

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const specPath = process.argv[2] || path.join(__dirname, "deck_spec.json");
const outPath = process.argv[3] || path.join(__dirname, "research_overview.pptx");
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const ROOT = path.resolve(__dirname, "..", "..");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = spec.author || "";
pres.title = spec.title || "";

const F = "Yu Gothic";
const FB = "Yu Gothic";
const C = {
  green: "70B437", blue: "0079C2", lightblue: "5DB6E7", teal: "176871", amber: "FFC000",
  coral: "F27750", orange: "D95B20", black: "000000", text: "262626", gray: "595959",
  line: "D9D9D9", tint: "F0F6FB", warm: "FDF0E8", white: "FFFFFF", navy: "14213D",
};
const W = 13.333;

let pageNo = 0;
function newSlide(opts) {
  opts = opts || {};
  const s = pres.addSlide();
  s.background = { color: C.white };
  pageNo += 1;
  if (pageNo > 1) s.addText(String(pageNo), { x: 12.65, y: 7.05, w: 0.47, h: 0.25, fontSize: 9, color: C.gray, fontFace: F, align: "right", margin: 0 });
  if (opts.section) s.addText(opts.section, { x: 0.37, y: 7.05, w: 9, h: 0.25, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
  if (opts.notes) s.addNotes(opts.notes);
  return s;
}
function header(s, title, msg) {
  s.addText(title, { x: 0.37, y: 0.22, w: 12.6, h: 0.44, fontSize: 20, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "middle" });
  s.addShape(pres.ShapeType.line, { x: 0.37, y: 0.68, w: 12.6, h: 0, line: { color: C.line, width: 0.75 } });
  if (msg) s.addText(msg, { x: 0.37, y: 0.74, w: 12.6, h: 0.62, fontSize: 13, color: C.teal, bold: true, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.1 });
}
function secLabel(s, x, y, label, w, color) {
  s.addShape(pres.ShapeType.rect, { x, y: y + 0.03, w: 0.05, h: 0.26, fill: { color: color || C.blue } });
  s.addText(label, { x: x + 0.13, y, w: w || 5.5, h: 0.32, fontSize: 12.5, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "middle" });
}
function runs(items, opts) {
  opts = opts || {};
  return items.map((it) => {
    if (typeof it === "string") it = { t: it };
    return {
      text: it.t,
      options: {
        bullet: opts.nobullet ? false : (it.sub ? { code: "2013", indent: 10 } : { code: "25A0", indent: 11 }),
        indentLevel: it.sub ? 1 : 0, bold: !!it.b, color: it.c ? (C[it.c] || it.c) : C.text,
        breakLine: true, paraSpaceAfter: it.gap === 0 ? 0 : (it.gap || opts.gap || 4),
      },
    };
  });
}
function bullets(s, items, x, y, w, h, opts) {
  opts = opts || {};
  s.addText(runs(items, opts), { x, y, w, h, fontSize: opts.size || 12, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: opts.lsm || 1.15, color: C.text, fit: "shrink" });
}
function tbl(s, rows, x, y, w, colW, opts) {
  opts = opts || {};
  const tr = rows.map((r, ri) => r.map((cell) => {
    const base = typeof cell === "object" && cell !== null ? cell : { text: String(cell) };
    const o = Object.assign({}, base.options || {});
    if (base.b) o.bold = true;
    if (base.c) o.color = C[base.c] || base.c;
    if (base.fill) o.fill = { color: C[base.fill] || base.fill };
    if (ri === 0) Object.assign(o, { bold: true, color: C.white, fill: { color: C.blue }, fontSize: opts.hSize || 10.5, valign: "middle" });
    else Object.assign(o, { color: o.color || C.text, fill: o.fill || { color: ri % 2 === 0 ? C.tint : C.white }, fontSize: o.fontSize || opts.bSize || 10, valign: "middle" });
    if (base.align) o.align = base.align;
    return { text: base.text !== undefined ? String(base.text) : "", options: o };
  }));
  s.addTable(tr, Object.assign({ x, y, w, colW, fontFace: F, border: { type: "solid", color: C.line, pt: 0.5 }, margin: 0.05, autoPage: false }, opts.tbl || {}));
}
function img(s, rel, x, y, w, h) {
  const p = path.isAbsolute(rel) ? rel : path.join(ROOT, rel);
  if (!fs.existsSync(p)) { s.addText("（図なし: " + rel + "）", { x, y, w, h, fontSize: 10, color: C.coral, fontFace: F }); return; }
  s.addImage({ path: p, x, y, w, h, sizing: { type: "contain", w, h } });
}
function card(s, x, y, w, h, label, items, opts) {
  opts = opts || {};
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: opts.fill ? (C[opts.fill] || opts.fill) : C.tint }, line: { color: opts.fill === "warm" ? "F3D2BE" : "D6E6F3", width: 0.5 } });
  s.addText(label, { x: x + 0.12, y: y + 0.06, w: w - 0.24, h: 0.27, fontSize: 11, bold: true, color: opts.labelColor ? (C[opts.labelColor] || opts.labelColor) : C.blue, fontFace: FB, margin: 0 });
  bullets(s, items, x + 0.14, y + 0.36, w - 0.28, h - 0.42, { size: opts.size || 10.5, gap: 2, lsm: 1.08, nobullet: opts.nobullet });
}
function kpis(s, list, x, y, w, h) {
  const n = list.length; const gap = 0.15; const cw = (w - gap * (n - 1)) / n;
  list.forEach((k, i) => {
    const cx = x + i * (cw + gap);
    s.addShape(pres.ShapeType.rect, { x: cx, y, w: cw, h, fill: { color: k.warm ? C.warm : C.tint } });
    s.addText(k.n, { x: cx + 0.12, y: y + 0.08, w: cw - 0.24, h: h * 0.48, fontSize: k.size || 18, bold: true, color: k.warm ? C.orange : C.teal, fontFace: FB, margin: 0, valign: "middle", fit: "shrink" });
    s.addText(k.l, { x: cx + 0.12, y: y + h * 0.52, w: cw - 0.24, h: h * 0.44, fontSize: 9.5, color: C.text, fontFace: F, margin: 0, valign: "top", fit: "shrink" });
  });
}
function flow(s, steps, x, y, w, h) {
  const n = steps.length; const gap = 0.22; const bw = (w - gap * (n - 1)) / n;
  steps.forEach((st, i) => {
    const bx = x + i * (bw + gap);
    s.addShape(pres.ShapeType.rect, { x: bx, y, w: bw, h, fill: { color: st.warm ? C.warm : C.tint }, line: { color: st.warm ? "F3D2BE" : "D6E6F3", width: 0.5 } });
    s.addText(st.head, { x: bx + 0.08, y: y + 0.06, w: bw - 0.16, h: 0.5, fontSize: 11.5, bold: true, color: st.warm ? C.orange : C.blue, fontFace: FB, margin: 0, valign: "top", fit: "shrink" });
    s.addText(st.body, { x: bx + 0.08, y: y + 0.6, w: bw - 0.16, h: h - 0.68, fontSize: 9.5, color: C.text, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.08, fit: "shrink" });
    if (i < n - 1) s.addText("▶", { x: bx + bw, y: y + h / 2 - 0.15, w: gap, h: 0.3, fontSize: 10, color: C.gray, align: "center", margin: 0 });
  });
}

// ---- スライド型 ----
const R = {
  title(sl) {
    const s = newSlide({ notes: sl.notes });
    s.addText(sl.title, { x: 0.9, y: 2.2, w: 11.6, h: 1.2, fontSize: 30, bold: true, color: C.black, fontFace: FB, margin: 0, valign: "bottom", fit: "shrink" });
    s.addShape(pres.ShapeType.rect, { x: 0.95, y: 3.55, w: 1.9, h: 0.06, fill: { color: C.blue } });
    if (sl.subtitle) s.addText(sl.subtitle, { x: 0.9, y: 3.8, w: 11.6, h: 0.5, fontSize: 15, color: C.text, fontFace: F, margin: 0 });
    if (sl.author) s.addText(sl.author, { x: 0.9, y: 4.5, w: 8, h: 0.4, fontSize: 13, color: C.text, fontFace: F, margin: 0 });
    if (sl.date) s.addText(sl.date, { x: 0.9, y: 4.9, w: 8, h: 0.35, fontSize: 11, color: C.gray, fontFace: F, margin: 0 });
    if (sl.footer) s.addText(sl.footer, { x: 0.9, y: 6.2, w: 11.6, h: 0.5, fontSize: 10.5, color: C.gray, fontFace: F, margin: 0 });
  },
  section(sl) {
    const s = newSlide({ notes: sl.notes });
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: W, h: 7.5, fill: { color: C.tint } });
    if (sl.kicker) s.addText(sl.kicker, { x: 0.9, y: 2.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: C.blue, fontFace: FB, margin: 0 });
    s.addText(sl.title, { x: 0.9, y: 2.75, w: 11.6, h: 0.9, fontSize: 28, bold: true, color: C.black, fontFace: FB, margin: 0, fit: "shrink" });
    s.addShape(pres.ShapeType.rect, { x: 0.95, y: 3.75, w: 1.9, h: 0.06, fill: { color: C.blue } });
    if (sl.body) bullets(s, sl.body, 0.95, 4.05, 11.4, 2.6, { size: 13 });
  },
  bullets(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    let y = sl.msg ? 1.45 : 0.95;
    (sl.blocks || []).forEach((b) => {
      const h = b.h || 1.4;
      if (b.label) { secLabel(s, 0.55, y, b.label, 12); y += 0.38; }
      bullets(s, b.items, 0.7, y, 12.1, h, { size: b.size || 12 });
      y += h + 0.1;
    });
  },
  // 分析スライド: 左に問い・データ・手法、右に図、下に結果
  analysis(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    const top = 1.45; const hasFig = !!sl.figure;
    const lw = hasFig ? 5.55 : 12.6;
    const ch = sl.cardH || [0.95, 1.25, 1.55];
    card(s, 0.37, top, lw, ch[0], "問い", sl.question, { size: 10.5 });
    card(s, 0.37, top + ch[0] + 0.1, lw, ch[1], "データ", sl.data, { size: 10 });
    card(s, 0.37, top + ch[0] + ch[1] + 0.2, lw, ch[2], "手法", sl.method, { size: 10 });
    const ry = top + ch[0] + ch[1] + ch[2] + 0.3;
    if (hasFig) img(s, sl.figure, 6.1, top, 6.85, Math.min(3.95, ry - top - 0.05));
    if (sl.figcap && hasFig) s.addText(sl.figcap, { x: 6.1, y: top + Math.min(3.95, ry - top - 0.05), w: 6.85, h: 0.28, fontSize: 8.5, color: C.gray, fontFace: F, margin: 0 });
    card(s, 0.37, ry, 12.6, 6.95 - ry, "結果", sl.results, { size: 10.5, fill: "warm", labelColor: "orange" });
  },
  table(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    const y = sl.msg ? 1.5 : 1.0;
    tbl(s, sl.rows, 0.37, y, 12.6, sl.colW, { bSize: sl.bSize || 9.5, hSize: sl.hSize || 10 });
    if (sl.note) s.addText(sl.note, { x: 0.37, y: 6.75, w: 12.6, h: 0.3, fontSize: 9, color: C.gray, fontFace: F, margin: 0 });
  },
  flow(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    flow(s, sl.steps, 0.37, sl.msg ? 1.55 : 1.05, 12.6, sl.h || 3.6);
    if (sl.below) bullets(s, sl.below, 0.55, (sl.msg ? 1.55 : 1.05) + (sl.h || 3.6) + 0.25, 12.3, 6.95 - ((sl.msg ? 1.55 : 1.05) + (sl.h || 3.6) + 0.25), { size: 11 });
  },
  kpi(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    let y = sl.msg ? 1.5 : 1.0;
    kpis(s, sl.kpis, 0.37, y, 12.6, 1.35);
    y += 1.55;
    (sl.blocks || []).forEach((b) => {
      const h = b.h || 1.3;
      if (b.label) { secLabel(s, 0.55, y, b.label, 12); y += 0.38; }
      bullets(s, b.items, 0.7, y, 12.1, h, { size: b.size || 11.5 });
      y += h + 0.08;
    });
  },
  twocol(sl) {
    const s = newSlide({ section: sl.section, notes: sl.notes });
    header(s, sl.title, sl.msg);
    const y = sl.msg ? 1.5 : 1.0; const cw = 6.2;
    [sl.left, sl.right].forEach((col, i) => {
      const x = 0.37 + i * (cw + 0.2);
      if (!col) return;
      if (col.figure) { img(s, col.figure, x, y, cw, col.figH || 3.3); if (col.figcap) s.addText(col.figcap, { x, y: y + (col.figH || 3.3), w: cw, h: 0.28, fontSize: 8.5, color: C.gray, fontFace: F, margin: 0 }); }
      const by = col.figure ? y + (col.figH || 3.3) + 0.35 : y;
      if (col.label) secLabel(s, x, by, col.label, cw);
      if (col.items) bullets(s, col.items, x + 0.12, by + (col.label ? 0.4 : 0), cw - 0.12, 6.95 - by - (col.label ? 0.4 : 0), { size: col.size || 11 });
      if (col.rows) tbl(s, col.rows, x, by + (col.label ? 0.4 : 0), cw, col.colW, { bSize: col.bSize || 9.5 });
    });
  },
};

(spec.slides || []).forEach((sl, i) => {
  const fn = R[sl.type];
  if (!fn) throw new Error("unknown slide type: " + sl.type + " at " + i);
  fn(sl);
});

pres.writeFile({ fileName: outPath }).then((f) => console.log("saved " + f + " (" + pageNo + " slides)"));
