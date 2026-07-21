#!/usr/bin/env node
// 使い方:
//   node src/index.js check           … 実サイトから取得して判定・通知
//   node src/index.js check --mock    … モックデータでパイプラインを検証

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { analyze, dedupeAlerts, alertKey } from "./analyze.js";
import { dataPaths, loadLatest, loadNotified, saveRun } from "./history.js";
import { notify } from "./notify.js";

const baseDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  if (command !== "check") {
    console.error("使い方: node src/index.js check [--mock] [--config <path>]");
    process.exit(2);
  }
  const useMock = args.includes("--mock");
  const configIdx = args.indexOf("--config");
  const configPath =
    configIdx !== -1 ? args[configIdx + 1] : path.join(baseDir, "config.json");

  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  const paths = dataPaths(baseDir);

  console.error(`[main] ${useMock ? "モック" : "実サイト"}モードで ${config.hotels.length} ホテルをチェックします`);

  let fetched;
  if (useMock) {
    const { fetchAllHotelsMock } = await import("./mock.js");
    fetched = fetchAllHotelsMock(config);
  } else {
    const { fetchAllHotels } = await import("./scraper.js");
    fetched = await fetchAllHotels(config);
  }
  const { results, errors } = fetched;

  if (Object.keys(results).length === 0) {
    console.error("[main] 全ホテルの取得に失敗しました:", JSON.stringify(errors));
    process.exit(1);
  }

  const prev = await loadLatest(paths);
  const notified = await loadNotified(paths);

  const alerts = analyze(config, prev, results);
  const newAlerts = dedupeAlerts(alerts, notified);
  console.error(
    `[main] アラート ${alerts.length} 件(うち新規 ${newAlerts.length} 件、通知済み ${alerts.length - newAlerts.length} 件)`
  );

  const sentChannels = await notify(newAlerts);
  if (sentChannels.length > 0) {
    const now = new Date().toISOString();
    for (const alert of newAlerts) notified[alertKey(alert)] = now;
  }

  // 取得に失敗したホテルは前回値を引き継ぐ(次回の値下がり比較が途切れないように)
  const snapshotHotels = { ...(prev?.hotels ?? {}) };
  for (const [code, byDate] of Object.entries(results)) snapshotHotels[code] = byDate;

  await saveRun(paths, { fetchedAt: new Date().toISOString(), hotels: snapshotHotels }, notified);
  console.error(`[main] スナップショットを保存しました: ${paths.latest}`);

  if (errors.length > 0) {
    console.error(`[main] 一部ホテルの取得に失敗: ${errors.map((e) => e.hotel).join(", ")}`);
  }
}

main().catch((err) => {
  console.error("[main] エラー:", err);
  process.exit(1);
});
