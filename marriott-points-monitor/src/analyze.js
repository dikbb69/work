// 取得結果と前回スナップショットを比較し、通知すべき「安い日」を抽出する。
//
// アラートの種類:
//   threshold … 必要ポイントが設定した上限 (maxPoints) 以下
//   drop      … 前回より dropRatio 以上値下がりした

/**
 * @param {object} config config.json の内容
 * @param {object|null} prev 前回スナップショット { hotels: { CODE: { date: points } } }
 * @param {object} current 今回の取得結果 { CODE: { date: points } }
 * @returns {Array<{type, hotelCode, hotelName, date, points, prevPoints?, maxPoints?}>}
 */
export function analyze(config, prev, current) {
  const alerts = [];
  const dropRatio = config.dropRatio ?? 0.15;
  const today = new Date().toISOString().slice(0, 10);

  for (const hotel of config.hotels) {
    const byDate = current[hotel.code];
    if (!byDate) continue;
    const prevByDate = prev?.hotels?.[hotel.code] ?? {};

    for (const [date, points] of Object.entries(byDate)) {
      if (points === null || points === undefined || date < today) continue;

      if (hotel.maxPoints && points <= hotel.maxPoints) {
        alerts.push({
          type: "threshold",
          hotelCode: hotel.code,
          hotelName: hotel.name,
          date,
          points,
          maxPoints: hotel.maxPoints,
        });
      }

      const prevPoints = prevByDate[date];
      if (
        config.notifyOnDrop !== false &&
        typeof prevPoints === "number" &&
        points <= prevPoints * (1 - dropRatio)
      ) {
        alerts.push({
          type: "drop",
          hotelCode: hotel.code,
          hotelName: hotel.name,
          date,
          points,
          prevPoints,
        });
      }
    }
  }

  alerts.sort((a, b) =>
    a.hotelCode === b.hotelCode ? a.date.localeCompare(b.date) : a.hotelCode.localeCompare(b.hotelCode)
  );
  return alerts;
}

/**
 * 通知済みのアラートを除外する。「同じホテル・同じ日・同じポイント数」は再通知しない。
 * ポイントがさらに下がった場合はキーが変わるので改めて通知される。
 */
export function dedupeAlerts(alerts, notified) {
  return alerts.filter((a) => notified[alertKey(a)] === undefined);
}

export function alertKey(alert) {
  return `${alert.type}|${alert.hotelCode}|${alert.date}|${alert.points}`;
}
