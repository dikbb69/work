// 国土地理院 標高タイル（PNG形式）から任意地点の標高を取得するサービス
// 仕様: 標高 h は画素値 x = 2^16*R + 2^8*G + B から
//   x < 2^23   → h = 0.01x [m]
//   x = 2^23   → 無効値（海など）
//   x > 2^23   → h = 0.01(x - 2^24) [m]
// dem5a(5mメッシュ, z15) → dem(10mメッシュ, z14) の順に参照し、無ければフォールバック。
(function () {
  const FW = (window.FW = window.FW || {});

  const SOURCES = [
    { id: "dem5a", z: 15, url: (z, x, y) => `https://cyberjapandata.gsi.go.jp/xyz/dem5a_png/${z}/${x}/${y}.png` },
    { id: "dem10", z: 14, url: (z, x, y) => `https://cyberjapandata.gsi.go.jp/xyz/dem_png/${z}/${x}/${y}.png` },
  ];

  // 緯度経度 → タイル座標と、タイル内ピクセル位置（256px）
  function tilePixel(lat, lng, z) {
    const n = Math.pow(2, z);
    const x = ((lng + 180) / 360) * n;
    const latR = lat * Math.PI / 180;
    const y = ((1 - Math.log(Math.tan(latR) + 1 / Math.cos(latR)) / Math.PI) / 2) * n;
    const tx = Math.floor(x), ty = Math.floor(y);
    return { tx, ty, px: (x - tx) * 256, py: (y - ty) * 256 };
  }

  // RGBA配列の i 番目のピクセルを標高値にデコード（無効値は null）
  function decodePixel(data, i) {
    if (data[i + 3] === 0) return null;
    const v = data[i] * 65536 + data[i + 1] * 256 + data[i + 2];
    if (v === 8388608) return null; // 2^23 = 無効値
    return (v > 8388608 ? v - 16777216 : v) * 0.01;
  }

  class ElevationService {
    constructor() {
      this.tiles = new Map();    // key -> Uint8ClampedArray(RGBA)
      this.pending = new Map();  // key -> Promise
      this.missing = new Set();  // 404等で取得できなかったタイル
      this.netErrors = 0;
    }

    _key(s, x, y) { return `${s.id}/${x}/${y}`; }

    async _load(s, x, y) {
      const k = this._key(s, x, y);
      if (this.tiles.has(k)) return this.tiles.get(k);
      if (this.missing.has(k)) return null;
      if (this.pending.has(k)) return this.pending.get(k);
      const p = (async () => {
        try {
          const res = await fetch(s.url(s.z, x, y));
          if (!res.ok) { this.missing.add(k); return null; }
          const blob = await res.blob();
          let bmp;
          try {
            bmp = await createImageBitmap(blob, { premultiplyAlpha: "none", colorSpaceConversion: "none" });
          } catch (e) {
            bmp = await createImageBitmap(blob);
          }
          const cv = document.createElement("canvas");
          cv.width = cv.height = 256;
          const ctx = cv.getContext("2d", { willReadFrequently: true });
          ctx.drawImage(bmp, 0, 0);
          const img = ctx.getImageData(0, 0, 256, 256);
          this.tiles.set(k, img.data);
          return img.data;
        } catch (e) {
          this.netErrors++;
          this.missing.add(k);
          return null;
        } finally {
          this.pending.delete(k);
        }
      })();
      this.pending.set(k, p);
      return p;
    }

    // タイル内を双一次補間でサンプル（無効値が混じる場合は最近傍）
    _sample(data, px, py) {
      const x0 = Math.min(254, Math.max(0, Math.floor(px - 0.5)));
      const y0 = Math.min(254, Math.max(0, Math.floor(py - 0.5)));
      const fx = Math.min(1, Math.max(0, px - 0.5 - x0));
      const fy = Math.min(1, Math.max(0, py - 0.5 - y0));
      const v00 = decodePixel(data, (y0 * 256 + x0) * 4);
      const v10 = decodePixel(data, (y0 * 256 + x0 + 1) * 4);
      const v01 = decodePixel(data, ((y0 + 1) * 256 + x0) * 4);
      const v11 = decodePixel(data, ((y0 + 1) * 256 + x0 + 1) * 4);
      if (v00 != null && v10 != null && v01 != null && v11 != null) {
        return v00 * (1 - fx) * (1 - fy) + v10 * fx * (1 - fy) + v01 * (1 - fx) * fy + v11 * fx * fy;
      }
      const xi = Math.min(255, Math.max(0, Math.round(px - 0.5)));
      const yi = Math.min(255, Math.max(0, Math.round(py - 0.5)));
      return decodePixel(data, (yi * 256 + xi) * 4);
    }

    // 標高取得。取得不能（水面・データ外）なら null
    async get(lat, lng, { fine = true } = {}) {
      for (const s of SOURCES) {
        if (!fine && s.id === "dem5a") continue;
        const { tx, ty, px, py } = tilePixel(lat, lng, s.z);
        const data = await this._load(s, tx, ty);
        if (!data) continue;
        const v = this._sample(data, px, py);
        if (v != null) return v;
      }
      return null;
    }

    // キャッシュ済み dem10 タイルのみ参照する同期版（ヒートマップ用。事前に prefetch すること）
    getSync(lat, lng) {
      const s = SOURCES[1];
      const { tx, ty, px, py } = tilePixel(lat, lng, s.z);
      const data = this.tiles.get(this._key(s, tx, ty));
      if (!data) return null;
      return this._sample(data, px, py);
    }

    // 矩形範囲の dem10 タイルを並列プリフェッチ
    async prefetch(latMin, latMax, lngMin, lngMax, onProgress) {
      const s = SOURCES[1];
      const a = tilePixel(latMax, lngMin, s.z); // 北西 → 小さいタイルY
      const b = tilePixel(latMin, lngMax, s.z);
      const jobs = [];
      for (let x = a.tx; x <= b.tx; x++) for (let y = a.ty; y <= b.ty; y++) jobs.push([x, y]);
      const total = jobs.length;
      let done = 0;
      const workers = Array.from({ length: 8 }, async () => {
        while (jobs.length) {
          const [x, y] = jobs.shift();
          await this._load(s, x, y);
          done++;
          if (onProgress) onProgress(done, total);
        }
      });
      await Promise.all(workers);
      return total;
    }

    // 水面などで無効値の場合、周辺リングの中央値で代替する頑健版
    async getRobust(lat, lng, { fine = true } = {}) {
      const v = await this.get(lat, lng, { fine });
      if (v != null) return { h: v, estimated: false };
      const cosLat = Math.cos(lat * Math.PI / 180);
      for (const r of [150, 300, 600]) {
        const vals = [];
        for (let i = 0; i < 8; i++) {
          const th = (i * Math.PI) / 4;
          const p = { lat: lat + (r * Math.cos(th)) / 111320, lng: lng + (r * Math.sin(th)) / (111320 * cosLat) };
          const u = await this.get(p.lat, p.lng, { fine: false });
          if (u != null) vals.push(u);
        }
        if (vals.length) {
          vals.sort((p, q) => p - q);
          return { h: vals[Math.floor(vals.length / 2)], estimated: true };
        }
      }
      return { h: 0, estimated: true };
    }
  }

  FW.tilePixel = tilePixel;
  FW.demDecodePixel = decodePixel;
  FW.elev = new ElevationService();
})();
