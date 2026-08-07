// 測地系ヘルパー（〜20km程度の局所計算用の簡易近似）
(function () {
  const FW = (window.FW = window.FW || {});
  const R = 6371000;      // 地球半径 [m]
  const R_EFF = 7420000;  // 大気屈折を織り込んだ実効地球半径 [m]（屈折係数k≒0.14）
  const D2R = Math.PI / 180;

  // 2点間の水平距離 [m]（正距円筒近似）
  function dist(a, b) {
    const x = (b.lng - a.lng) * D2R * Math.cos(((a.lat + b.lat) / 2) * D2R) * R;
    const y = (b.lat - a.lat) * D2R * R;
    return Math.hypot(x, y);
  }

  // origin を原点とした局所平面座標 [m]（x=東, y=北）
  function toXY(origin, p) {
    return {
      x: (p.lng - origin.lng) * D2R * Math.cos(origin.lat * D2R) * R,
      y: (p.lat - origin.lat) * D2R * R,
    };
  }

  function interp(a, b, t) {
    return { lat: a.lat + (b.lat - a.lat) * t, lng: a.lng + (b.lng - a.lng) * t };
  }

  // a から b への方位角 [deg, 北=0 時計回り]
  function bearing(a, b) {
    const p1 = a.lat * D2R, p2 = b.lat * D2R, dl = (b.lng - a.lng) * D2R;
    const th = Math.atan2(
      Math.sin(dl) * Math.cos(p2),
      Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl)
    );
    return (th / D2R + 360) % 360;
  }

  const DIRS = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東",
                "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"];
  function dirName(deg) {
    return DIRS[Math.round(deg / 22.5) % 16];
  }

  // 距離 d [m] 先での地球の湾曲による沈み込み量 [m]（視線解析用・屈折込み）
  function curvatureDrop(d) {
    return (d * d) / (2 * R_EFF);
  }

  FW.geo = { R, R_EFF, D2R, dist, toXY, interp, bearing, dirName, curvatureDrop };
})();
