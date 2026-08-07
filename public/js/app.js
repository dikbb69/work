// UI とマップのオーケストレーション
(function () {
  const FW = (window.FW = window.FW || {});
  const $ = (id) => document.getElementById(id);

  // ---------- 地図 ----------
  const gsiAttr = '地図・標高: <a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>';
  const pale = L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png", { maxZoom: 18, attribution: gsiAttr });
  const std = L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png", { maxZoom: 18, attribution: gsiAttr });
  const photo = L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.png", { maxZoom: 18, attribution: gsiAttr });
  const osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap contributors" });

  const map = L.map("map", { layers: [pale], zoomControl: true });
  L.control.layers({ "淡色地図": pale, "標準地図": std, "航空写真": photo, "OpenStreetMap": osm }).addTo(map);
  L.control.scale({ imperial: false }).addTo(map);

  // ---------- 状態 ----------
  const state = {
    launch: null,          // {lat,lng}
    customMode: false,     // 地図クリックで打上地点を設定するモード
    busy: false,
    heatSignal: null,
    markers: [],           // 解析済み地点マーカー
    launchMarker: null,
    burstCircle: null,
    sightLine: null,
    heatLayer: null,
  };

  // ---------- コントロール ----------
  const festivalSelect = $("festivalSelect");
  const shellSelect = $("shellSelect");

  for (const f of FW.FESTIVALS) {
    const o = document.createElement("option");
    o.value = f.id;
    o.textContent = `${f.name}（${f.pref}）`;
    festivalSelect.appendChild(o);
  }
  const custom = document.createElement("option");
  custom.value = "custom";
  custom.textContent = "🔧 カスタム（地図クリックで打上地点を指定）";
  festivalSelect.appendChild(custom);

  for (const k of Object.keys(FW.SHELL_SPECS)) {
    const o = document.createElement("option");
    o.value = k;
    o.textContent = FW.SHELL_SPECS[k].label;
    shellSelect.appendChild(o);
  }

  function currentShell() {
    return FW.SHELL_SPECS[shellSelect.value];
  }
  function currentEye() {
    const v = parseFloat($("eyeHeight").value);
    return Number.isFinite(v) ? Math.max(0.5, Math.min(300, v)) : 1.5;
  }

  function setStatus(msg, isError) {
    const s = $("status");
    if (!msg) { s.classList.add("hidden"); return; }
    s.textContent = msg;
    s.classList.toggle("error", !!isError);
    s.classList.remove("hidden");
  }

  function setLaunch(latlng, { pan = true, zoom = null } = {}) {
    state.launch = { lat: latlng.lat, lng: latlng.lng };
    if (state.launchMarker) map.removeLayer(state.launchMarker);
    if (state.burstCircle) map.removeLayer(state.burstCircle);
    const icon = L.divIcon({ className: "launch-icon", html: "🎆", iconSize: [34, 34], iconAnchor: [17, 17] });
    state.launchMarker = L.marker(state.launch, { icon, draggable: state.customMode, zIndexOffset: 1000 })
      .addTo(map)
      .bindTooltip("打上地点", { direction: "top", offset: [0, -14] });
    if (state.customMode) {
      state.launchMarker.on("dragend", () => {
        const p = state.launchMarker.getLatLng();
        state.launch = { lat: p.lat, lng: p.lng };
        updateBurstCircle();
        clearResults();
        setStatus("打上地点を移動しました。地図をクリックして見え方を判定できます。");
      });
    }
    updateBurstCircle();
    if (pan) map.setView(state.launch, zoom || Math.max(map.getZoom() || 0, 13));
  }

  function updateBurstCircle() {
    if (state.burstCircle) map.removeLayer(state.burstCircle);
    state.burstCircle = L.circle(state.launch, {
      radius: currentShell().diameter / 2,
      color: "#a855f7", weight: 1.5, dashArray: "6 5", fillColor: "#a855f7", fillOpacity: 0.08,
      interactive: false,
    }).addTo(map).bindTooltip("開花直径の目安", { sticky: true });
  }

  function clearResults() {
    for (const m of state.markers) map.removeLayer(m);
    state.markers = [];
    if (state.sightLine) { map.removeLayer(state.sightLine); state.sightLine = null; }
    if (state.heatLayer) { map.removeLayer(state.heatLayer); state.heatLayer = null; }
    if (state.heatSignal) state.heatSignal.cancelled = true;
    $("heatLegend").classList.add("hidden");
    $("heatProgress").classList.add("hidden");
    $("result").classList.add("hidden");
    setStatus(null);
  }

  function applyFestival(id) {
    clearResults();
    if (id === "custom") {
      state.customMode = true;
      $("festivalNote").textContent = "地図を一度クリックすると、その場所が打上地点になります（ドラッグで微調整可）。";
      if (!state.launch) {
        setStatus("地図をクリックして打上地点を設定してください。");
      } else {
        setLaunch(state.launch, { pan: false });
      }
      return;
    }
    state.customMode = false;
    const f = FW.FESTIVALS.find((x) => x.id === id);
    $("festivalNote").textContent = `${f.note}／座標・玉サイズはデモ用の概略値`;
    shellSelect.value = f.shell;
    setLaunch({ lat: f.lat, lng: f.lng }, { pan: true, zoom: 13 });
    setStatus("地図をクリックすると、その場所からの見え方を判定します。");
  }

  // ---------- 地点解析 ----------
  async function analyzePoint(latlng) {
    if (!state.launch) { setStatus("先に打上地点を設定してください。", true); return null; }
    if (state.busy) return null;
    state.busy = true;
    document.body.classList.add("busy");
    try {
      const res = await FW.los.analyze({
        viewer: { lat: latlng.lat, lng: latlng.lng },
        launch: state.launch,
        shellSpec: currentShell(),
        eyeHeight: currentEye(),
        useBuildings: $("useBuildings").checked,
        onStatus: (m) => setStatus(m),
      });
      setStatus(null);
      renderResult(res);
      addResultMarker(res);
      drawSightLine(res);
      return res;
    } catch (e) {
      console.error(e);
      setStatus("解析に失敗しました: " + e.message, true);
      return null;
    } finally {
      state.busy = false;
      document.body.classList.remove("busy");
    }
  }

  function addResultMarker(res) {
    const m = L.circleMarker(res.viewer, {
      radius: 8, color: "#fff", weight: 2, fillColor: res.category.color, fillOpacity: 1,
    }).addTo(map);
    m.bindTooltip(`${res.category.emoji} ${Math.round(res.fraction * 100)}% ${res.category.label}`, { direction: "top" });
    m.on("click", () => { renderResult(res); drawSightLine(res); });
    state.markers.push(m);
  }

  function drawSightLine(res) {
    if (state.sightLine) map.removeLayer(state.sightLine);
    state.sightLine = L.polyline([res.viewer, res.launch], {
      color: res.category.color, weight: 2.5, dashArray: "7 6", interactive: false,
    }).addTo(map);
  }

  function fmtDist(m) {
    return m >= 1000 ? (m / 1000).toFixed(2) + " km" : Math.round(m) + " m";
  }

  function renderResult(res) {
    $("result").classList.remove("hidden");
    const badge = $("resBadge");
    badge.textContent = `${res.category.emoji} ${res.category.label}（可視率 ${Math.round(res.fraction * 100)}%）`;
    badge.style.background = res.category.color;

    const rows = [
      ["打上地点までの距離", `${fmtDist(res.D)}（${res.dirName}の方角）`],
      ["観覧地点の標高", `${res.viewerElev.toFixed(1)} m（目の高さ +${res.eyeHeight}m）`],
      ["打上地点の標高", `${res.launchElev.toFixed(1)} m`],
      ["花火の中心の仰角", `${res.elevAngleDeg.toFixed(1)}°`],
      ["見かけの大きさ", `約${res.apparentDeg.toFixed(1)}°（満月の約${res.moonRatio < 20 ? res.moonRatio.toFixed(1) : Math.round(res.moonRatio)}倍）`],
      ["開花の高さ（標高）", `${Math.round(res.bottom)}〜${Math.round(res.top)} m`],
      ["見える下限（標高）", res.cutoffAlt === -Infinity ? "遮蔽なし" : `${Math.round(res.cutoffAlt)} m`],
      ["建物データ", res.buildingInfo.used ? `視線付近 ${res.buildingInfo.count} 棟を考慮` : (res.buildingInfo.failed ? "取得失敗（地形のみ）" : "未使用（地形のみ）")],
      ["クリック地点", `${res.viewer.lat.toFixed(5)}, ${res.viewer.lng.toFixed(5)}`],
    ];
    $("resTable").innerHTML = rows
      .map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`)
      .join("");
    $("resNotes").innerHTML = res.notes.map((n) => `<li>${n}</li>`).join("");
    FW.profile.draw($("profileCanvas"), res);
  }

  // ---------- ヒートマップ ----------
  async function runHeatmap() {
    if (!state.launch) { setStatus("先に打上地点を設定してください。", true); return; }
    if (state.heatSignal) state.heatSignal.cancelled = true;
    const signal = { cancelled: false };
    state.heatSignal = signal;
    const btn = $("heatmapBtn");
    btn.disabled = true;
    $("heatProgress").classList.remove("hidden");
    setStatus("見えやすさマップを計算中…（地形のみ・建物は未考慮）");
    try {
      const out = await FW.heatmap.build({
        launch: state.launch,
        shellSpec: currentShell(),
        eyeHeight: currentEye(),
        radius: parseInt($("heatRadius").value, 10),
        signal,
        onProgress: (p) => { $("heatBar").style.width = Math.round(p * 100) + "%"; },
      });
      if (!out || signal.cancelled) return;
      if (state.heatLayer) map.removeLayer(state.heatLayer);
      state.heatLayer = L.imageOverlay(out.canvas.toDataURL(), out.bounds, {
        opacity: 1, interactive: false, className: "heatmap-img",
      }).addTo(map);
      map.fitBounds(out.bounds);
      $("heatLegend").classList.remove("hidden");
      setStatus(null);
    } catch (e) {
      console.error(e);
      setStatus("マップ計算に失敗しました: " + e.message, true);
    } finally {
      btn.disabled = false;
      $("heatProgress").classList.add("hidden");
      $("heatBar").style.width = "0%";
    }
  }

  // ---------- イベント ----------
  map.on("click", (ev) => {
    if (state.customMode && !state.launch) {
      setLaunch(ev.latlng, { pan: false });
      setStatus("打上地点を設定しました。地図をクリックすると見え方を判定します。");
      return;
    }
    analyzePoint(ev.latlng);
  });

  festivalSelect.addEventListener("change", () => applyFestival(festivalSelect.value));
  shellSelect.addEventListener("change", () => {
    clearResults();
    if (state.launch) updateBurstCircle();
    setStatus("玉サイズが変わったため、判定結果をクリアしました。");
  });
  $("eyeHeight").addEventListener("change", () => {
    clearResults();
    setStatus("目の高さが変わったため、判定結果をクリアしました。");
  });
  $("heatmapBtn").addEventListener("click", runHeatmap);
  $("clearBtn").addEventListener("click", () => {
    const keepLaunch = state.launch;
    clearResults();
    if (keepLaunch) setStatus("結果をクリアしました。");
  });

  // ---------- 初期化 ----------
  applyFestival(FW.FESTIVALS[0].id);

  // 自動テスト・デバッグ用フック
  window.__fwDebug = {
    map,
    setFestival(id) {
      festivalSelect.value = id;
      applyFestival(id);
    },
    setCustomLaunch(lat, lng) {
      festivalSelect.value = "custom";
      state.customMode = true;
      $("festivalNote").textContent = "カスタム打上地点";
      setLaunch({ lat, lng }, { pan: true, zoom: 13 });
    },
    async analyzeAt(lat, lng) {
      const r = await analyzePoint({ lat, lng });
      if (!r) return null;
      return {
        category: r.category.key, label: r.category.label,
        fraction: r.fraction, cutoffAlt: r.cutoffAlt,
        viewerElev: r.viewerElev, launchElev: r.launchElev, D: r.D,
        buildings: r.buildingHits.length,
      };
    },
    async getElev(lat, lng) { return FW.elev.get(lat, lng); },
    runHeatmap,
    setBuildings(on) { $("useBuildings").checked = !!on; },
    setShell(k) { shellSelect.value = k; if (state.launch) updateBurstCircle(); },
    state,
  };
})();
