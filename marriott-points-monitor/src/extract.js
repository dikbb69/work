// Marriott の API レスポンス JSON から「日付 → 必要ポイント」を抽出する。
// レスポンススキーマの変更に耐えるため、特定の構造を決め打ちせず
// オブジェクトツリーを再帰的に走査して日付とポイントのペアを探す。

const DATE_KEY_RE = /^(date|checkin|checkIn|startDate|arrivalDate|day)/i;
const POINTS_KEY_RE = /point/i;
const DATE_VALUE_RE = /^(\d{4})-(\d{2})-(\d{2})/;

function findDate(obj) {
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === "string" && DATE_KEY_RE.test(key)) {
      const m = value.match(DATE_VALUE_RE);
      if (m) return `${m[1]}-${m[2]}-${m[3]}`;
    }
  }
  return null;
}

function findPoints(obj) {
  for (const [key, value] of Object.entries(obj)) {
    if (!POINTS_KEY_RE.test(key)) continue;
    if (typeof value === "number" && Number.isFinite(value) && value > 0) {
      return value;
    }
    if (typeof value === "object" && value !== null) {
      // 例: { points: { value: 50000 } } のようなネスト
      for (const inner of Object.values(value)) {
        if (typeof inner === "number" && Number.isFinite(inner) && inner > 0) {
          return inner;
        }
      }
    }
  }
  return null;
}

/**
 * 任意の JSON 値を走査し、{ "YYYY-MM-DD": points } のマップを返す。
 * 同じ日付が複数見つかった場合は最小値(=最安)を採用する。
 */
export function extractPointsByDate(root) {
  const result = {};
  const stack = [root];
  while (stack.length > 0) {
    const node = stack.pop();
    if (node === null || typeof node !== "object") continue;
    if (Array.isArray(node)) {
      for (const item of node) stack.push(item);
      continue;
    }
    const date = findDate(node);
    if (date) {
      const points = findPoints(node);
      if (points !== null && (result[date] === undefined || points < result[date])) {
        result[date] = points;
      }
    }
    for (const value of Object.values(node)) stack.push(value);
  }
  return result;
}
