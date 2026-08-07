// 「見えやすさマップ」: 打上地点の周囲を格子状にサンプルし、各地点からの可視率を色で表示
// 高速化のため dem10（z14）タイルを事前取得し、同期参照のみで計算する。建物は考慮しない。
(function () {
  const FW = (window.FW = window.FW || {});
  const N = 61; // 片側グリッド数（N×N セル）

  function colorFor(fraction) {
    // 0=赤 → 0.5=黄 → 1=緑
    const hue = fraction * 120;
    const c = (1 - Math.abs(2 * 0.45 - 1)) * 0.8; // HSL(hue, 80%, 45%) 相当
    const x = c * (1 - Math.abs(((hue / 60) % 2) - 1));
    const m = 0.45 - c / 2;
    let rgb;
    if (hue < 60) rgb = [c, x, 0];
    else if (hue < 120) rgb = [x, c, 0];
    else rgb = [0, c, x];
    return rgb.map((v) => Math.round((v + m) * 255));
  }

  // 戻り値 { canvas, bounds } / キャンセル時 null
  async function build({ launch, shellSpec, eyeHeight, radius, onProgress, signal }) {
    const g = FW.geo;
    const el = FW.elev;
    const dLat = radius / 111320;
    const dLng = radius / (111320 * Math.cos(launch.lat * g.D2R));
    const m = 1.1; // プリフェッチ余白

    let prefDone = 0;
    await el.prefetch(
      launch.lat - dLat * m, launch.lat + dLat * m,
      launch.lng - dLng * m, launch.lng + dLng * m,
      (done, total) => { prefDone = done; if (onProgress) onProgress(0.35 * (done / total)); }
    );
    if (signal && signal.cancelled) return null;

    const le = await el.getRobust(launch.lat, launch.lng, { fine: false });
    const launchElev = le.h;
    const burstHeight = shellSpec.height;
    const burstRadius = shellSpec.diameter / 2;
    const top = launchElev + burstHeight + burstRadius;
    const bottom = Math.max(launchElev, launchElev + burstHeight - burstRadius);

    const cv = document.createElement("canvas");
    cv.width = cv.height = N;
    const ctx = cv.getContext("2d");
    const img = ctx.createImageData(N, N);

    for (let row = 0; row < N; row++) {
      if (signal && signal.cancelled) return null;
      const lat = launch.lat + dLat * (1 - (2 * row) / (N - 1)); // row 0 = 北端
      for (let col = 0; col < N; col++) {
        const lng = launch.lng + dLng * ((2 * col) / (N - 1) - 1);
        const viewer = { lat, lng };
        const D = g.dist(viewer, launch);
        let fraction;
        if (D < 250) {
          fraction = 1; // 会場至近
        } else {
          let ve = el.getSync(lat, lng);
          if (ve == null) ve = launchElev; // 水面は打上水面と同じ高さとみなす
          const viewerAlt = ve + eyeHeight;
          const nearSkip = Math.min(60, D * 0.1);
          const farSkip = Math.min(150, D * 0.2);
          const step = Math.max(40, D / 150);
          let S = -Infinity;
          for (let d = nearSkip; d <= D - farSkip; d += step) {
            const p = g.interp(viewer, launch, d / D);
            let h = el.getSync(p.lat, p.lng);
            if (h == null) h = launchElev;
            const slope = (h - g.curvatureDrop(d) - viewerAlt) / d;
            if (slope > S) S = slope;
          }
          const cutoff = S === -Infinity ? -Infinity : viewerAlt + S * D + g.curvatureDrop(D);
          fraction = Math.max(0, Math.min(1, (top - Math.max(bottom, cutoff)) / (top - bottom)));
        }
        const [r8, g8, b8] = colorFor(fraction);
        const i = (row * N + col) * 4;
        img.data[i] = r8; img.data[i + 1] = g8; img.data[i + 2] = b8;
        img.data[i + 3] = 145;
      }
      if (onProgress) onProgress(0.35 + 0.65 * ((row + 1) / N));
      await new Promise((r) => setTimeout(r, 0)); // UI を固めない
    }
    ctx.putImageData(img, 0, 0);

    const bounds = [
      [launch.lat - dLat, launch.lng - dLng],
      [launch.lat + dLat, launch.lng + dLng],
    ];
    return { canvas: cv, bounds };
  }

  FW.heatmap = { build, N };
})();
