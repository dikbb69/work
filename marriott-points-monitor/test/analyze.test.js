import { test } from "node:test";
import assert from "node:assert/strict";
import { analyze, dedupeAlerts, alertKey } from "../src/analyze.js";

const future = (days) => {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

const config = {
  hotels: [{ code: "TEST", name: "テストホテル", maxPoints: 50000 }],
  notifyOnDrop: true,
  dropRatio: 0.15,
};

test("しきい値以下の日を threshold アラートとして検出する", () => {
  const alerts = analyze(config, null, { TEST: { [future(10)]: 45000, [future(11)]: 60000 } });
  assert.equal(alerts.length, 1);
  assert.equal(alerts[0].type, "threshold");
  assert.equal(alerts[0].points, 45000);
});

test("dropRatio 以上の値下がりを drop アラートとして検出する", () => {
  const date = future(10);
  const prev = { hotels: { TEST: { [date]: 80000 } } };
  const alerts = analyze(config, prev, { TEST: { [date]: 60000 } });
  assert.equal(alerts.length, 1);
  assert.equal(alerts[0].type, "drop");
  assert.equal(alerts[0].prevPoints, 80000);
});

test("わずかな値下がり(dropRatio 未満)は通知しない", () => {
  const date = future(10);
  const prev = { hotels: { TEST: { [date]: 60000 } } };
  const alerts = analyze(config, prev, { TEST: { [date]: 58000 } });
  assert.equal(alerts.length, 0);
});

test("過去の日付と満室 (null) は無視する", () => {
  const alerts = analyze(config, null, { TEST: { "2020-01-01": 10000, [future(5)]: null } });
  assert.equal(alerts.length, 0);
});

test("通知済みのアラートは dedupeAlerts で除外され、さらに値下がりすると再通知される", () => {
  const date = future(10);
  const alerts = analyze(config, null, { TEST: { [date]: 45000 } });
  const notified = { [alertKey(alerts[0])]: "2026-01-01T00:00:00Z" };
  assert.equal(dedupeAlerts(alerts, notified).length, 0);

  const cheaper = analyze(config, null, { TEST: { [date]: 40000 } });
  assert.equal(dedupeAlerts(cheaper, notified).length, 1);
});
