import { test } from "node:test";
import assert from "node:assert/strict";
import { extractPointsByDate } from "../src/extract.js";

test("フラットな構造から日付とポイントを抽出する", () => {
  const body = {
    calendar: [
      { date: "2026-08-01", points: 50000 },
      { date: "2026-08-02", points: 40000 },
    ],
  };
  assert.deepEqual(extractPointsByDate(body), {
    "2026-08-01": 50000,
    "2026-08-02": 40000,
  });
});

test("ネストしたポイント値やキー名の揺れにも対応する", () => {
  const body = {
    data: {
      rates: [
        { checkinDate: "2026-08-01T00:00:00", pointsPerUnit: { value: 35000 } },
        { startDate: "2026-08-02", totalPoints: 45000 },
      ],
    },
  };
  assert.deepEqual(extractPointsByDate(body), {
    "2026-08-01": 35000,
    "2026-08-02": 45000,
  });
});

test("同じ日付が複数ある場合は最安値を採用する", () => {
  const body = [
    { date: "2026-08-01", points: 50000 },
    { date: "2026-08-01", points: 30000 },
  ];
  assert.deepEqual(extractPointsByDate(body), { "2026-08-01": 30000 });
});

test("ポイント情報のないレスポンスからは何も抽出しない", () => {
  assert.deepEqual(extractPointsByDate({ date: "2026-08-01", price: 300 }), {});
  assert.deepEqual(extractPointsByDate(null), {});
});
