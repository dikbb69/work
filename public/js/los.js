// 見通し（Line of Sight）解析
// 観覧地点から打上地点方向を見たとき、地形と建物が花火をどこまで隠すかを計算する。
// 地球の湾曲＋大気屈折は「実効高さ z_eff = 標高 - d^2/(2*R_eff)」の座標系で直線視線として扱う。
(function () {
  const FW = (window.FW = window.FW || {});

  // 中核計算（純関数・テスト対象）
  // samples: [{d, h}] 視線に沿った地表, buildings: [{d, top}] 視線を横切る建物
  // 戻り値: 視線限界の傾き S、打上位置で見通せる下限標高 cutoffAlt、可視率 fraction など
  function core({ D, viewerAlt, launchElev, burstHeight, burstRadius, samples, buildings }) {
    const g = FW.geo;
    const top = launchElev + burstHeight + burstRadius;
    const bottom = Math.max(launchElev, launchElev + burstHeight - burstRadius);
    let S = -Infinity;
    let blocker = null;
    for (const s of samples) {
      const zEff = s.h - g.curvatureDrop(s.d);
      const slope = (zEff - viewerAlt) / s.d;
      if (slope > S) { S = slope; blocker = { type: "terrain", d: s.d, alt: s.h }; }
    }
    if (buildings) {
      for (const b of buildings) {
        const zEff = b.top - g.curvatureDrop(b.d);
        const slope = (zEff - viewerAlt) / b.d;
        if (slope > S) { S = slope; blocker = { type: "building", d: b.d, alt: b.top, ref: b }; }
      }
    }
    // 遮蔽が全く無い場合は打上地点の地面まで見える
    const cutoffAlt = S === -Infinity ? -Infinity : viewerAlt + S * D + g.curvatureDrop(D);
    const visBottom = Math.max(bottom, cutoffAlt);
    const fraction = Math.max(0, Math.min(1, (top - visBottom) / (top - bottom)));
    const groundVisible = cutoffAlt <= launchElev + 5;
    return { S, cutoffAlt, fraction, groundVisible, blocker, top, bottom, burstCenterAlt: launchElev + burstHeight };
  }

  const CATEGORIES = [
    { key: "A", test: (f, gv) => f >= 0.98 && gv, label: "打上地点まで見通せる（絶好スポット）", color: "#1a9850", emoji: "🌟" },
    { key: "B", test: (f) => f >= 0.98,           label: "花火全体がよく見える",                 color: "#66bd63", emoji: "😀" },
    { key: "C", test: (f) => f >= 0.65,           label: "ほぼ全体が見える（下部が少し欠ける）", color: "#a6d96a", emoji: "🙂" },
    { key: "D", test: (f) => f >= 0.25,           label: "花火の上のほうだけ見える",             color: "#fdae61", emoji: "😐" },
    { key: "E", test: (f) => f > 0.02,            label: "頂点付近がわずかに見える程度",         color: "#f46d43", emoji: "😕" },
    { key: "F", test: () => true,                 label: "この場所からは見えない",               color: "#d73027", emoji: "🙈" },
  ];
  function categorize(fraction, groundVisible) {
    return CATEGORIES.find((c) => c.test(fraction, groundVisible));
  }

  // 総合解析（標高取得・建物取得込み）
  async function analyze({ viewer, launch, shellSpec, eyeHeight = 1.5, useBuildings = true, onStatus }) {
    const g = FW.geo;
    const el = FW.elev;
    const status = (m) => { if (onStatus) onStatus(m); };
    const notes = [];

    const D = g.dist(viewer, launch);
    const bearingDeg = g.bearing(viewer, launch);

    status("標高データを取得中…");
    const [ve, le] = await Promise.all([
      el.getRobust(viewer.lat, viewer.lng),
      el.getRobust(launch.lat, launch.lng),
    ]);
    const viewerElev = ve.h, launchElev = le.h;
    if (ve.estimated) notes.push("観覧地点が水面などのため、標高は周辺からの推定値です。");
    if (le.estimated) notes.push("打上地点が水面のため、標高は周辺（岸など）からの推定値です。");
    const viewerAlt = viewerElev + eyeHeight;

    // 視線に沿って地形をサンプリング（観覧点直近と打上場所周辺は除外）
    const nearSkip = Math.min(60, D * 0.1);
    const farSkip = Math.min(150, D * 0.2);
    const step = Math.max(25, Math.min(50, D / 300));
    const ds = [];
    for (let d = nearSkip; d <= D - farSkip; d += step) ds.push(d);
    const samples = await Promise.all(
      ds.map(async (d) => {
        const p = g.interp(viewer, launch, d / D);
        const h = await el.get(p.lat, p.lng);
        // 水面(無効値)は打上地点の水面高で代替（湖・海・川はほぼ同一水面のため）
        return { d, h: h == null ? launchElev : h };
      })
    );
    if (el.netErrors > 0 && samples.every((s) => s.h === launchElev)) {
      notes.push("⚠️ 標高タイルを取得できませんでした。ネットワーク接続を確認してください（結果は不正確です）。");
    }

    // 建物（OSM）
    let buildingHits = [];
    let buildingInfo = { used: false, count: 0, truncated: false, failed: false };
    if (useBuildings) {
      status("建物データを取得中…（OpenStreetMap）");
      const bres = await FW.buildings.fetchCorridor(viewer, launch);
      if (bres.error && bres.list.length === 0) {
        buildingInfo.failed = true;
        notes.push("建物データの取得に失敗したため、地形のみで判定しています（Overpass API 混雑の可能性）。");
      } else {
        buildingInfo.used = true;
        buildingInfo.truncated = bres.truncated;
        const hits = [];
        for (const b of bres.list) {
          if (FW.buildings.viewerInside(viewer, b)) {
            notes.push("指定地点は建物の中のようです。屋上から見る場合は「目の高さ」に建物の高さを足してください。");
            continue;
          }
          const t = FW.buildings.intersectSight(viewer, launch, b);
          if (!t) continue;
          const d0 = t.t0 * D, d1 = t.t1 * D;
          if (d1 < nearSkip || d0 > D - farSkip) continue;
          const p = g.interp(viewer, launch, t.t0);
          let gh = await el.get(p.lat, p.lng, { fine: false });
          if (gh == null) gh = launchElev;
          hits.push({
            d: Math.max(d0, nearSkip), d0, d1,
            ground: gh, top: gh + b.height,
            name: b.name, height: b.height, heightEstimated: b.heightEstimated,
          });
        }
        buildingHits = hits;
        buildingInfo.count = bres.list.length;
        if (bres.truncated) notes.push("視線上の建物が非常に多いため、一部のみ考慮しています。");
        if (D > FW.buildings.MAX_LEN) notes.push(`建物は手前${(FW.buildings.MAX_LEN / 1000).toFixed(0)}kmの範囲のみ考慮しています。`);
      }
    }

    status("見通しを計算中…");
    const res = core({
      D, viewerAlt, launchElev,
      burstHeight: shellSpec.height, burstRadius: shellSpec.diameter / 2,
      samples, buildings: buildingHits,
    });

    const category = categorize(res.fraction, res.groundVisible);
    const elevAngleDeg =
      Math.atan2(res.burstCenterAlt - g.curvatureDrop(D) - viewerAlt, D) / g.D2R;
    const apparentDeg = (2 * Math.atan((shellSpec.diameter / 2) / D)) / g.D2R;

    if (res.fraction < 0.98 && res.blocker) {
      const b = res.blocker;
      if (b.type === "building") {
        const nm = b.ref && b.ref.name ? `「${b.ref.name}」` : "建物";
        notes.push(`約${Math.round(b.d)}m先の${nm}（高さ約${Math.round(b.ref.height)}m${b.ref.heightEstimated ? "・推定" : ""}）が視界を遮っています。`);
      } else {
        notes.push(`約${(b.d / 1000).toFixed(1)}km先の地形（標高約${Math.round(b.alt)}m）が視界を遮っています。`);
      }
    }
    if (elevAngleDeg > 40) notes.push("かなり見上げる角度になります（首が疲れるかも）。");
    if (D > 10000 && res.fraction > 0.25) notes.push("距離が遠いため、空気の澄み具合によっては霞んで見えます。音は約" + Math.round(D / 340) + "秒遅れて届きます。");

    return {
      viewer, launch, D, bearingDeg, dirName: g.dirName(bearingDeg),
      viewerElev, launchElev, viewerAlt, eyeHeight,
      shellSpec, samples, buildingHits, buildingInfo,
      ...res,
      burstRadius: shellSpec.diameter / 2,
      category, elevAngleDeg, apparentDeg, moonRatio: apparentDeg / 0.52,
      notes,
    };
  }

  FW.los = { analyze, categorize, _core: core, CATEGORIES };
})();
