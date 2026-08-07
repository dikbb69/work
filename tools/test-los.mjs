// 見通し計算コアのユニットテスト（ブラウザ不要・依存なし）
//   node tools/test-los.mjs
import { readFileSync } from "node:fs";

globalThis.window = globalThis;
for (const f of ["geo.js", "elevation.js", "los.js"]) {
  const src = readFileSync(new URL(`../public/js/${f}`, import.meta.url), "utf8");
  new Function(src)();
}
const FW = globalThis.FW;
const core = FW.los._core;

let failed = 0;
function check(name, cond, detail = "") {
  if (cond) {
    console.log(`  ok: ${name}`);
  } else {
    failed++;
    console.error(`FAIL: ${name} ${detail}`);
  }
}
function approx(a, b, tol) { return Math.abs(a - b) <= tol; }

function flatSamples(D, h = 0, step = 25) {
  const out = [];
  for (let d = Math.min(60, D * 0.1); d <= D - Math.min(150, D * 0.2); d += step) out.push({ d, h });
  return out;
}

// --- タイル座標・デコード ---
{
  const t = FW.tilePixel(35.3606, 138.7274, 14); // 富士山頂付近
  check("tilePixel 富士山 z14", t.tx === 14505 && t.ty === 6469, JSON.stringify(t));

  const px = new Uint8ClampedArray(8);
  px.set([0, 4, 210, 255], 0); // x=1234 → 12.34m
  check("decode 正値", approx(FW.demDecodePixel(px, 0), 12.34, 1e-9));
  px.set([128, 0, 0, 255], 0); // 2^23 → 無効値
  check("decode 無効値", FW.demDecodePixel(px, 0) === null);
  px.set([255, 255, 156, 255], 0); // x=2^24-100 → -1.00m
  check("decode 負値", approx(FW.demDecodePixel(px, 0), -1.0, 1e-9));
  px.set([0, 0, 50, 0], 0); // alpha=0 → 無効
  check("decode 透明", FW.demDecodePixel(px, 0) === null);
}

// --- 平坦地・近距離: 全部見える ---
{
  const r = core({
    D: 2000, viewerAlt: 1.5, launchElev: 0, burstHeight: 330, burstRadius: 160,
    samples: flatSamples(2000), buildings: [],
  });
  check("平坦2km: 可視率1", r.fraction === 1, `fraction=${r.fraction}`);
  check("平坦2km: 地面まで見える", r.groundVisible, `cutoff=${r.cutoffAlt}`);
}

// --- 尾根が下部を隠す ---
{
  // 格子上の d=510 のサンプルを標高45mの尾根にする
  const samples = flatSamples(3000).map((s) => (s.d === 510 ? { d: s.d, h: 45 } : s));
  const r = core({
    D: 3000, viewerAlt: 1.5, launchElev: 0, burstHeight: 330, burstRadius: 160,
    samples, buildings: [],
  });
  // 手計算: slope=(45-drop(510)-1.5)/510=0.0852598
  // cutoff=1.5+slope*3000+drop(3000)=257.886m → fraction=(490-257.886)/320=0.72536
  check("尾根45m@510m: 可視率≈0.725", approx(r.fraction, 0.72536, 0.005), `fraction=${r.fraction}`);
  check("尾根45m@510m: 遮蔽要因は地形@510m", r.blocker.type === "terrain" && r.blocker.d === 510, JSON.stringify(r.blocker));
  check("尾根45m@510m: カテゴリC", FW.los.categorize(r.fraction, r.groundVisible).key === "C");
}

// --- 高い尾根で全遮蔽 ---
{
  const samples = flatSamples(3000).map((s) => (approx(s.d, 500, 12.5) ? { d: s.d, h: 200 } : s));
  const r = core({
    D: 3000, viewerAlt: 1.5, launchElev: 0, burstHeight: 330, burstRadius: 160,
    samples, buildings: [],
  });
  check("尾根200m@500m: 可視率0", r.fraction === 0, `fraction=${r.fraction}`);
  check("尾根200m@500m: カテゴリF", FW.los.categorize(r.fraction, r.groundVisible).key === "F");
}

// --- 建物が支配的な遮蔽になる ---
{
  const r = core({
    D: 3000, viewerAlt: 1.5, launchElev: 0, burstHeight: 330, burstRadius: 160,
    samples: flatSamples(3000),
    buildings: [{ d: 300, top: 40 }],
  });
  // slope=(40-drop(300)-1.5)/300=0.12831 → cutoff=1.5+384.9+0.6=386.9 → fraction=(490-386.9)/320=0.322
  check("建物40m@300m: 可視率≈0.322", approx(r.fraction, 0.322, 0.01), `fraction=${r.fraction}`);
  check("建物40m@300m: 遮蔽要因は建物", r.blocker.type === "building", JSON.stringify(r.blocker));
}

// --- 地球の湾曲: 10km 先では地面付近が水平線下に隠れる ---
{
  const r = core({
    D: 10000, viewerAlt: 1.5, launchElev: 0, burstHeight: 330, burstRadius: 160,
    samples: flatSamples(10000), buildings: [],
  });
  // 目の高さ1.5mの水平線は約4.7km。10km先では地面から約1.9mより下は見えない
  check("平坦10km: 湾曲で下端≈1.9m", approx(r.cutoffAlt, 1.9, 1.0), `cutoff=${r.cutoffAlt}`);
  check("平坦10km: 花火自体はほぼ全部見える", r.fraction > 0.99, `fraction=${r.fraction}`);
}

// --- 高台の観覧者: 打上地点まで完全に見通せる ---
{
  const r = core({
    D: 4000, viewerAlt: 101.5, launchElev: 0, burstHeight: 190, burstRadius: 75,
    samples: flatSamples(4000), buildings: [],
  });
  check("高台100m: 可視率1・地面可視", r.fraction === 1 && r.groundVisible, `cutoff=${r.cutoffAlt}`);
  check("高台100m: カテゴリA", FW.los.categorize(r.fraction, r.groundVisible).key === "A");
}

if (failed) {
  console.error(`\n${failed} 件のテストが失敗しました`);
  process.exit(1);
}
console.log("\n全テスト成功 🎆");
