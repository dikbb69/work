// OpenStreetMap (Overpass API) から視線コリドー内の建物を取得する
// 建物の高さは height タグ → building:levels×3.3m → 種別ごとの既定値 の順で推定。
(function () {
  const FW = (window.FW = window.FW || {});
  const g = () => FW.geo;

  const ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
  ];
  const HALF_WIDTH = 40;   // コリドー半幅 [m]
  const MAX_LEN = 8000;    // 建物を探す最大距離 [m]（それ以遠の建物は遮蔽への寄与が小さい）
  const LIMIT = 1500;      // 取得建物数の上限

  function estimateHeight(tags) {
    if (!tags) return { h: 8, estimated: true };
    const ht = parseFloat(tags.height);
    if (Number.isFinite(ht) && ht > 0) return { h: ht, estimated: false };
    const lv = parseFloat(tags["building:levels"]);
    if (Number.isFinite(lv) && lv > 0) return { h: lv * 3.3 + 1.5, estimated: true };
    const t = tags.building;
    if (t === "house" || t === "detached" || t === "hut" || t === "shed" || t === "garage") {
      return { h: 6.5, estimated: true };
    }
    return { h: 8, estimated: true };
  }

  // viewer→launch の視線に沿ったコリドー矩形ポリゴンを作る
  function corridorPoly(viewer, launch) {
    const geo = g();
    const D = geo.dist(viewer, launch);
    const len = Math.min(D, MAX_LEN);
    const end = geo.interp(viewer, launch, len / D);
    const cosLat = Math.cos(viewer.lat * geo.D2R);
    // 単位進行ベクトル（度単位換算）と、その法線
    const ux = (launch.lng - viewer.lng) * cosLat, uy = launch.lat - viewer.lat;
    const norm = Math.hypot(ux, uy) || 1;
    const nx = -uy / norm, ny = ux / norm; // 左法線（正規化済み・平面近似）
    const wLat = (HALF_WIDTH / 111320) * ny;
    const wLng = (HALF_WIDTH / (111320 * cosLat)) * nx;
    const pts = [
      { lat: viewer.lat + wLat, lng: viewer.lng + wLng },
      { lat: viewer.lat - wLat, lng: viewer.lng - wLng },
      { lat: end.lat - wLat,    lng: end.lng - wLng },
      { lat: end.lat + wLat,    lng: end.lng + wLng },
    ];
    return pts.map((p) => `${p.lat.toFixed(6)} ${p.lng.toFixed(6)}`).join(" ");
  }

  // コリドー内の建物を取得。戻り値 { list, truncated, error }
  async function fetchCorridor(viewer, launch) {
    const poly = corridorPoly(viewer, launch);
    const query = `[out:json][timeout:25];way["building"](poly:"${poly}");out geom ${LIMIT};`;
    let lastError = null;
    for (const ep of ENDPOINTS) {
      try {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), 15000);
        const res = await fetch(ep, {
          method: "POST",
          body: "data=" + encodeURIComponent(query),
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          signal: ctrl.signal,
        });
        clearTimeout(timer);
        if (!res.ok) { lastError = new Error(`HTTP ${res.status}`); continue; }
        const json = await res.json();
        const list = (json.elements || [])
          .filter((e) => e.type === "way" && Array.isArray(e.geometry) && e.geometry.length >= 3)
          .map((e) => {
            const est = estimateHeight(e.tags);
            return {
              pts: e.geometry.map((p) => ({ lat: p.lat, lng: p.lon })),
              height: est.h,
              heightEstimated: est.estimated,
              name: (e.tags && (e.tags.name || e.tags["name:ja"])) || null,
            };
          });
        return { list, truncated: list.length >= LIMIT, error: null };
      } catch (e) {
        lastError = e;
      }
    }
    return { list: [], truncated: false, error: lastError };
  }

  // 視線（viewer→launch, 2D）と建物ポリゴンの交差を調べ、交差区間 [t0,t1]（0..1）を返す
  function intersectSight(viewer, launch, building) {
    const geo = g();
    const L = geo.toXY(viewer, launch); // 視線終点（原点は viewer）
    const poly = building.pts.map((p) => geo.toXY(viewer, p));
    let t0 = Infinity, t1 = -Infinity;
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i], b = poly[(i + 1) % poly.length];
      // セグメント (0,0)-(L) と (a)-(b) の交差
      const d1x = L.x, d1y = L.y;
      const d2x = b.x - a.x, d2y = b.y - a.y;
      const den = d1x * d2y - d1y * d2x;
      if (Math.abs(den) < 1e-12) continue;
      const t = (a.x * d2y - a.y * d2x) / den;
      const u = (a.x * d1y - a.y * d1x) / den;
      if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
        t0 = Math.min(t0, t);
        t1 = Math.max(t1, t);
      }
    }
    if (t0 === Infinity) return null;
    return { t0, t1 };
  }

  // 点がポリゴン内にあるか（レイキャスティング）
  function pointInPoly(pt, ptsXY) {
    let inside = false;
    for (let i = 0, j = ptsXY.length - 1; i < ptsXY.length; j = i++) {
      const xi = ptsXY[i].x, yi = ptsXY[i].y, xj = ptsXY[j].x, yj = ptsXY[j].y;
      if ((yi > pt.y) !== (yj > pt.y) && pt.x < ((xj - xi) * (pt.y - yi)) / (yj - yi) + xi) {
        inside = !inside;
      }
    }
    return inside;
  }

  function viewerInside(viewer, building) {
    const geo = g();
    const poly = building.pts.map((p) => geo.toXY(viewer, p));
    return pointInPoly({ x: 0, y: 0 }, poly);
  }

  FW.buildings = { fetchCorridor, intersectSight, viewerInside, MAX_LEN };
})();
