// 価格スナップショットと通知済み記録の読み書き。
//   data/latest.json    … 前回スナップショット(値下がり検知の比較対象)
//   data/history.jsonl  … 全実行の追記ログ(1 行 1 実行)。後から傾向分析に使える
//   data/notified.json  … 通知済みアラートのキー(再通知の抑止)

import { promises as fs } from "node:fs";
import path from "node:path";

export function dataPaths(baseDir) {
  const dataDir = path.join(baseDir, "data");
  return {
    dataDir,
    latest: path.join(dataDir, "latest.json"),
    history: path.join(dataDir, "history.jsonl"),
    notified: path.join(dataDir, "notified.json"),
  };
}

async function readJson(file, fallback) {
  try {
    return JSON.parse(await fs.readFile(file, "utf8"));
  } catch (err) {
    if (err.code === "ENOENT") return fallback;
    throw err;
  }
}

export async function loadLatest(paths) {
  return readJson(paths.latest, null);
}

export async function loadNotified(paths) {
  return readJson(paths.notified, {});
}

export async function saveRun(paths, snapshot, notified) {
  await fs.mkdir(paths.dataDir, { recursive: true });
  await fs.writeFile(paths.latest, JSON.stringify(snapshot, null, 2) + "\n");
  await fs.appendFile(paths.history, JSON.stringify(snapshot) + "\n");
  await fs.writeFile(paths.notified, JSON.stringify(pruneNotified(notified), null, 2) + "\n");
}

// 過去日のアラートキーを捨てて notified.json の肥大化を防ぐ
export function pruneNotified(notified, today = new Date().toISOString().slice(0, 10)) {
  const pruned = {};
  for (const [key, value] of Object.entries(notified)) {
    const date = key.split("|")[2];
    if (date >= today) pruned[key] = value;
  }
  return pruned;
}
