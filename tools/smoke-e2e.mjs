// ブラウザE2Eスモークテスト（合成地形版）
// GSI標高タイル・地図タイル・Overpass APIをすべてローカル合成データで差し替え、
// アプリの全経路（タイル取得→デコード→LOS→建物→ヒートマップ→UI）をオフラインで検証する。
//
// 実行方法:
//   npm install playwright-core pngjs   （任意の場所でOK。このファイルの隣でも可）
//   node tools/smoke-e2e.mjs
// Chromium の場所は PW_CHROMIUM 環境変数で指定（未指定なら Playwright の既定探索）。
import { chromium } from "playwright-core";
import { PNG } from "pngjs";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP_DIR = fileURLToPath(new URL("../public", import.meta.url));
const SHOTS = process.env.SHOTS_DIR || fileURLToPath(new URL("./shots", import.meta.url));
fs.mkdirSync(SHOTS, { recursive: true });

// ---------- 合成地形 ----------
// 打上地点 (35.5, 138.0) を中心とした架空の湖＋外輪山＋東側に峠（切れ目）
const LAUNCH = { lat: 35.5, lng: 138.0 };
const COS = Math.cos((35.5 * Math.PI) / 180);
function terrain(lat, lng) {
  const dx = (lng - LAUNCH.lng) * 111320 * COS;
  const dy = (lat - LAUNCH.lat) * 111320;
  const r = Math.hypot(dx, dy);
  const thetaDeg = (Math.atan2(dx, dy) * 180) / Math.PI; // 北=0, 東=90
  let base = r < 1800 ? 300 : 302 + 0.001 * (r - 1800);
  // 外輪山（東90°方向は峠で低い）
  const dth = Math.min(Math.abs(thetaDeg - 90), 360 - Math.abs(thetaDeg - 90));
  const gap = 1 - 0.85 * Math.exp(-((dth / 18) ** 2));
  const ridge = 480 * Math.exp(-(((r - 3800) / 700) ** 2)) * gap;
  // 南西の小さな丘
  const dth2 = Math.min(Math.abs(thetaDeg + 135), 360 - Math.abs(thetaDeg + 135));
  const hill = 60 * Math.exp(-(((r - 1500) / 250) ** 2)) * Math.exp(-((dth2 / 12) ** 2));
  return base + ridge + hill;
}

function tileLatLng(z, x, y, px, py) {
  const n = 2 ** z;
  const lng = ((x + px / 256) / n) * 360 - 180;
  const latR = Math.atan(Math.sinh(Math.PI * (1 - (2 * (y + py / 256)) / n)));
  return { lat: (latR * 180) / Math.PI, lng };
}

const tileCache = new Map();
function demTile(z, x, y) {
  const key = `dem/${z}/${x}/${y}`;
  if (tileCache.has(key)) return tileCache.get(key);
  const png = new PNG({ width: 256, height: 256 });
  for (let py = 0; py < 256; py++) {
    for (let px = 0; px < 256; px++) {
      const { lat, lng } = tileLatLng(z, x, y, px + 0.5, py + 0.5);
      const v = Math.round(terrain(lat, lng) * 100);
      const i = (py * 256 + px) * 4;
      png.data[i] = (v >> 16) & 255;
      png.data[i + 1] = (v >> 8) & 255;
      png.data[i + 2] = v & 255;
      png.data[i + 3] = 255;
    }
  }
  const buf = PNG.sync.write(png);
  tileCache.set(key, buf);
  return buf;
}

function baseTile(z, x, y) {
  const key = `base/${z}/${x}/${y}`;
  if (tileCache.has(key)) return tileCache.get(key);
  const png = new PNG({ width: 256, height: 256 });
  for (let py = 0; py < 256; py++) {
    for (let px = 0; px < 256; px++) {
      const { lat, lng } = tileLatLng(z, x, y, px + 0.5, py + 0.5);
      const h = terrain(lat, lng);
      let rgb;
      if (h <= 300.5) rgb = [165, 200, 232];            // 湖
      else if (h < 340) rgb = [225, 238, 210];          // 平地
      else if (h < 500) rgb = [200, 220, 180];
      else if (h < 650) rgb = [214, 202, 170];          // 山腹
      else rgb = [188, 168, 142];                        // 山頂部
      const i = (py * 256 + px) * 4;
      png.data[i] = rgb[0]; png.data[i + 1] = rgb[1]; png.data[i + 2] = rgb[2]; png.data[i + 3] = 255;
    }
  }
  const buf = PNG.sync.write(png);
  tileCache.set(key, buf);
  return buf;
}

// 視点(東2.8km)と打上点の間に置く 55m のビル
const BLD_C = { lat: 35.5, lng: 138.0308 - 350 / (111320 * COS) };
const dLng30 = 30 / (111320 * COS), dLat20 = 20 / 111320;
const OVERPASS_JSON = {
  elements: [
    {
      type: "way", id: 1,
      tags: { building: "yes", height: "45", name: "テストタワー" },
      geometry: [
        { lat: BLD_C.lat - dLat20, lon: BLD_C.lng - dLng30 },
        { lat: BLD_C.lat - dLat20, lon: BLD_C.lng + dLng30 },
        { lat: BLD_C.lat + dLat20, lon: BLD_C.lng + dLng30 },
        { lat: BLD_C.lat + dLat20, lon: BLD_C.lng - dLng30 },
        { lat: BLD_C.lat - dLat20, lon: BLD_C.lng - dLng30 },
      ],
    },
  ],
};

// ---------- 静的サーバ ----------
const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png" };
const server = http.createServer((req, res) => {
  const p = path.join(APP_DIR, decodeURIComponent(req.url.split("?")[0]).replace(/^\/+/, "") || "index.html");
  try {
    const data = fs.readFileSync(p.endsWith("/") ? p + "index.html" : p);
    res.writeHead(200, { "Content-Type": MIME[path.extname(p)] || "application/octet-stream" });
    res.end(data);
  } catch {
    res.writeHead(404); res.end("nf");
  }
});
await new Promise((r) => server.listen(8123, "127.0.0.1", r));

// ---------- テスト ----------
let failed = 0;
const check = (name, cond, detail = "") => {
  if (cond) console.log(`  ok: ${name}`);
  else { failed++; console.error(`FAIL: ${name} ${detail}`); }
};

const browser = await chromium.launch({
  executablePath: process.env.PW_CHROMIUM || undefined,
  args: ["--no-sandbox"],
});
const ctx = await browser.newContext({ viewport: { width: 1400, height: 880 }, deviceScaleFactor: 2 });
const errors = [];
ctx.on("weberror", (e) => errors.push(String(e.error())));

await ctx.route(/cyberjapandata\.gsi\.go\.jp/, async (route) => {
  const m = route.request().url().match(/xyz\/([^/]+)\/(\d+)\/(\d+)\/(\d+)\.png/);
  if (!m) return route.fulfill({ status: 404, body: "" });
  const [, layer, z, x, y] = m;
  const body = layer.startsWith("dem") ? demTile(+z, +x, +y) : baseTile(+z, +x, +y);
  await route.fulfill({ body, contentType: "image/png" });
});
await ctx.route(/tile\.openstreetmap\.org/, async (route) => {
  const m = route.request().url().match(/\/(\d+)\/(\d+)\/(\d+)\.png/);
  await route.fulfill({ body: baseTile(+m[1], +m[2], +m[3]), contentType: "image/png" });
});
await ctx.route(/overpass/, (route) => route.fulfill({ json: OVERPASS_JSON }));

const page = await ctx.newPage();
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });

await page.goto("http://127.0.0.1:8123/index.html", { waitUntil: "load" });
await page.waitForFunction(() => window.__fwDebug != null);

// カスタム打上地点（架空の湖の中心）を設定し、尺玉に変更
await page.evaluate(({ lat, lng }) => window.__fwDebug.setCustomLaunch(lat, lng), LAUNCH);
await page.evaluate(() => window.__fwDebug.setShell("10"));

// 1. 標高タイルのデコード（合成地形との一致）
const e1 = await page.evaluate(() => window.__fwDebug.getElev(35.5, 138.0));
check("標高デコード: 湖面300m", Math.abs(e1 - 300) < 0.6, `got ${e1}`);
const e2 = await page.evaluate(() => window.__fwDebug.getElev(35.5, 137.958));
check("標高デコード: 外輪山西側は高い", e2 > 700, `got ${e2}`);

// 2. 湖岸（東1.2km・建物OFF）→ 絶好スポット
await page.evaluate(() => window.__fwDebug.setBuildings(false));
const rA = await page.evaluate(() => window.__fwDebug.analyzeAt(35.5, 138.0135));
check("湖岸: カテゴリA・可視率1", rA && rA.category === "A" && rA.fraction === 1, JSON.stringify(rA));

// 3. 外輪山の外側（西5.4km）→ 見えない
const rF = await page.evaluate(() => window.__fwDebug.analyzeAt(35.5, 137.9400));
check("山の外側: カテゴリF・可視率0", rF && rF.category === "F" && rF.fraction === 0, JSON.stringify(rF));

// 4a. 外輪山の内側斜面（西2.5km・標高約430m）→ 見下ろす絶好スポット
const rSlope = await page.evaluate(() => window.__fwDebug.analyzeAt(35.5, 137.9669));
check("内側斜面: カテゴリA", rSlope && rSlope.category === "A", JSON.stringify(rSlope));

// 4b. 稜線の頂上 → 丸い肩に打上地点の下端だけ隠れる（ほぼ全体は見える）
const rTop = await page.evaluate(() => window.__fwDebug.analyzeAt(35.5, 137.9580));
check("稜線頂上: 可視率0.8以上", rTop && rTop.fraction >= 0.8, JSON.stringify(rTop));

// 5. 東の峠側平地（2.8km)・建物ON → 45mビルが下部を遮る
await page.evaluate(() => window.__fwDebug.setBuildings(true));
const rB = await page.evaluate(() => window.__fwDebug.analyzeAt(35.5, 138.0308));
check("ビル遮蔽: 建物1棟を検出", rB && rB.buildings === 1, JSON.stringify(rB));
check("ビル遮蔽: 可視率0.35〜0.62（上部のみ）", rB && rB.fraction > 0.35 && rB.fraction < 0.62, JSON.stringify(rB));
check("ビル遮蔽: カテゴリD", rB && rB.category === "D", JSON.stringify(rB));

// パネル表示の確認
const badge = await page.textContent("#resBadge");
check("結果バッジ表示", /可視率/.test(badge), badge);
const tableText = await page.textContent("#resTable");
check("結果テーブルに距離表示", /km/.test(tableText), tableText.slice(0, 80));
await page.screenshot({ path: `${SHOTS}/demo-point.png`, clip: { x: 0, y: 0, width: 420, height: 880 } });

// 6. ヒートマップ（半径5km）
await page.evaluate(() => window.__fwDebug.runHeatmap());
await page.waitForFunction(() => window.__fwDebug.state.heatLayer != null, { timeout: 60000 });
await page.waitForTimeout(2500); // タイル描画待ち
check("ヒートマップ生成", true);
await page.screenshot({ path: `${SHOTS}/demo-heatmap.png` });

check("コンソール/ページエラーなし", errors.length === 0, errors.join(" | "));

await browser.close();
server.close();

if (failed) { console.error(`\n${failed} 件失敗`); process.exit(1); }
console.log("\nスモークテスト全成功 🎆");
