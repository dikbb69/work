// 実サイトに接続せずパイプライン全体を検証するためのモックデータ生成。
// ホテルコード+日付から決定的に値を作るので、同じ日に実行すれば同じ結果になる。
// MOCK_SEED を変えると値が変わり、値下がり検知の動作確認ができる。

function hash(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function fetchAllHotelsMock(config) {
  const seed = process.env.MOCK_SEED ?? "0";
  const months = config.searchMonths ?? 3;
  const results = {};

  for (const hotel of config.hotels) {
    const byDate = {};
    const start = new Date();
    const end = new Date();
    end.setMonth(end.getMonth() + months);
    for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().slice(0, 10);
      const h = hash(`${seed}:${hotel.code}:${dateStr}`);
      if (h % 13 === 0) {
        byDate[dateStr] = null; // 満室(ポイント宿泊不可)
        continue;
      }
      // ベース 40k〜80k、1 割弱の日に「オフピーク級」の安値を混ぜる
      const base = 40000 + (h % 5) * 10000;
      byDate[dateStr] = h % 11 === 0 ? Math.round(base * 0.6) : base;
    }
    results[hotel.code] = byDate;
  }
  return { results, errors: [] };
}
