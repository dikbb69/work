// 視線断面図（観覧地点 → 打上地点の地形プロファイルと視線・花火の位置関係）を canvas に描画
(function () {
  const FW = (window.FW = window.FW || {});

  function niceStep(range, target) {
    const raw = range / target;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    for (const m of [1, 2, 5, 10]) if (raw <= m * mag) return m * mag;
    return 10 * mag;
  }

  function draw(canvas, r) {
    const g = FW.geo;
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth || 360;
    const H = 230;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);

    const padL = 46, padR = 12, padT = 12, padB = 24;
    const xMax = r.D + r.burstRadius * 1.25;
    const terrainMax = Math.max(...r.samples.map((s) => s.h), r.viewerElev, r.launchElev);
    const yMin = Math.min(r.viewerAlt, Math.min(...r.samples.map((s) => s.h), r.launchElev)) - 15;
    const yMax = Math.max(r.top, terrainMax) + 30;
    const xm = (d) => padL + (d / xMax) * (W - padL - padR);
    const ym = (a) => padT + ((yMax - a) / (yMax - yMin)) * (H - padT - padB);

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, W, H);

    // 軸とグリッド
    ctx.font = "10px sans-serif";
    ctx.fillStyle = "#889";
    ctx.strokeStyle = "#e3e6ec";
    ctx.lineWidth = 1;
    const yStep = niceStep(yMax - yMin, 4);
    for (let a = Math.ceil(yMin / yStep) * yStep; a <= yMax; a += yStep) {
      ctx.beginPath(); ctx.moveTo(padL, ym(a)); ctx.lineTo(W - padR, ym(a)); ctx.stroke();
      ctx.textAlign = "right";
      ctx.fillText(`${Math.round(a)}m`, padL - 4, ym(a) + 3);
    }
    const xStep = niceStep(xMax, 5);
    for (let d = 0; d <= xMax; d += xStep) {
      ctx.textAlign = "center";
      ctx.fillText(d >= 1000 ? `${(d / 1000).toFixed(d % 1000 ? 1 : 0)}km` : `${d}m`, xm(d), H - 8);
    }

    // 地形
    ctx.beginPath();
    ctx.moveTo(xm(0), ym(r.viewerElev));
    for (const s of r.samples) ctx.lineTo(xm(s.d), ym(s.h));
    ctx.lineTo(xm(r.D), ym(r.launchElev));
    ctx.lineTo(xm(r.D), ym(yMin));
    ctx.lineTo(xm(0), ym(yMin));
    ctx.closePath();
    ctx.fillStyle = "#d8cfba";
    ctx.fill();
    ctx.strokeStyle = "#a89a7c";
    ctx.stroke();

    // 建物
    for (const b of r.buildingHits || []) {
      const x0 = xm(b.d0), x1 = Math.max(xm(b.d1), x0 + 2);
      ctx.fillStyle = "#8d7b6a";
      ctx.fillRect(x0, ym(b.top), x1 - x0, Math.max(2, ym(b.ground) - ym(b.top)));
    }

    // 視線限界（この線より上が見える）: z(d) = viewerAlt + S*d + drop(d)
    if (r.S !== -Infinity) {
      ctx.beginPath();
      for (let i = 0; i <= 60; i++) {
        const d = (i / 60) * r.D;
        const z = r.viewerAlt + r.S * d + g.curvatureDrop(d);
        if (i === 0) ctx.moveTo(xm(d), ym(z)); else ctx.lineTo(xm(d), ym(z));
      }
      ctx.strokeStyle = "#e6762e";
      ctx.setLineDash([6, 4]);
      ctx.lineWidth = 1.6;
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#e6762e";
      ctx.textAlign = "left";
      ctx.fillText("見通し限界", xm(r.D * 0.42), ym(r.viewerAlt + r.S * r.D * 0.42 + g.curvatureDrop(r.D * 0.42)) - 5);
    }

    // 花火（開花球）: 見える部分をピンク、隠れる部分をグレーで
    const cx = xm(r.D), cy = ym(r.burstCenterAlt);
    const rx = (r.burstRadius / xMax) * (W - padL - padR);
    const ry = (r.burstRadius / (yMax - yMin)) * (H - padT - padB);
    const sparkle = (color) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.4;
      for (let i = 0; i < 12; i++) {
        const th = (i / 12) * 2 * Math.PI;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(th) * rx * 0.25, cy + Math.sin(th) * ry * 0.25);
        ctx.lineTo(cx + Math.cos(th) * rx * 0.9, cy + Math.sin(th) * ry * 0.9);
        ctx.stroke();
      }
    };
    const drawBurst = (fill, stroke) => {
      ctx.beginPath();
      ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI);
      ctx.fillStyle = fill;
      ctx.fill();
      sparkle(stroke);
    };
    drawBurst("rgba(150,150,160,0.30)", "rgba(140,140,150,0.55)"); // 隠れている部分（下地）
    const cutY = r.cutoffAlt === -Infinity ? ym(yMin) : ym(Math.max(r.cutoffAlt, yMin));
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, W, cutY);
    ctx.clip();
    drawBurst("rgba(236,72,153,0.32)", "rgba(219,39,119,0.85)"); // 見えている部分
    ctx.restore();

    // 見える下限ライン
    if (r.cutoffAlt > r.bottom && r.cutoffAlt < r.top) {
      ctx.strokeStyle = "#db2777";
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(cx - rx * 1.3, ym(r.cutoffAlt));
      ctx.lineTo(cx + rx * 1.1, ym(r.cutoffAlt));
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#db2777";
      ctx.textAlign = "right";
      ctx.fillText(`見える下限 ${Math.round(r.cutoffAlt)}m`, cx - rx * 1.3 - 3, ym(r.cutoffAlt) + 3);
    }

    // 打上筒と観覧地点
    ctx.fillStyle = "#c0392b";
    ctx.fillRect(xm(r.D) - 2, ym(r.launchElev) - 7, 4, 7);
    ctx.beginPath();
    ctx.arc(xm(0), ym(r.viewerAlt), 3.5, 0, 2 * Math.PI);
    ctx.fillStyle = "#2563eb";
    ctx.fill();
    ctx.textAlign = "left";
    ctx.fillStyle = "#2563eb";
    ctx.fillText("観覧地点", xm(0) + 6, ym(r.viewerAlt) - 6);

    // 遮蔽物マーカー
    if (r.fraction < 0.98 && r.blocker && r.blocker.type === "terrain") {
      ctx.fillStyle = "#b45309";
      ctx.textAlign = "center";
      ctx.fillText("▲遮蔽", xm(r.blocker.d), ym(r.blocker.alt) - 6);
    }
  }

  FW.profile = { draw };
})();
