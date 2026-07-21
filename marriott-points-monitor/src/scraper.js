// Playwright で Marriott の空室検索ページを開き、ページが裏で取得する
// API レスポンス(ポイントカレンダー)を傍受して必要ポイントを収集する。
// DOM を直接パースするより、レスポンス JSON の傍受のほうがサイト改修に強い。

import { chromium } from "playwright";
import { extractPointsByDate } from "./extract.js";

// ポイント表示のフレキシブル検索カレンダー。{code} はマーシャコード(例: TYOMC)、
// {fromDate} は MM/DD/YYYY。サイト改修で変わった場合は config.json の
// urlTemplate で上書きできる。
const DEFAULT_URL_TEMPLATE =
  "https://www.marriott.com/reservation/availabilitySearch.mi" +
  "?propertyCode={code}&isRateCalendar=true&useRewardsPoints=true" +
  "&flexibleDateSearch=true&fromDate={fromDate}&numAdultsPerRoom={guests}";

// この正規表現に URL が一致したレスポンスだけを解析対象にする
const API_URL_RE =
  /phoenixShop|lowestAvailableRates|rateCalendar|availabilitySearch|aries-search|\/mi\/query\//i;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function formatDateUS(date) {
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${mm}/${dd}/${date.getFullYear()}`;
}

function buildUrl(template, hotel, fromDate, guests) {
  return template
    .replaceAll("{code}", hotel.code)
    .replaceAll("{fromDate}", encodeURIComponent(formatDateUS(fromDate)))
    .replaceAll("{guests}", String(guests));
}

async function fetchHotelMonth(page, url, timeoutMs) {
  const collected = {};
  const onResponse = async (response) => {
    if (!API_URL_RE.test(response.url())) return;
    try {
      const contentType = response.headers()["content-type"] ?? "";
      if (!contentType.includes("json")) return;
      const body = await response.json();
      Object.assign(collected, mergeMin(collected, extractPointsByDate(body)));
    } catch {
      // JSON でない・読み取り失敗のレスポンスは無視
    }
  };
  page.on("response", onResponse);
  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    // カレンダーの XHR が出揃うのを待つ
    await page.waitForLoadState("networkidle", { timeout: timeoutMs }).catch(() => {});
    await sleep(3000);
  } finally {
    page.off("response", onResponse);
  }
  return collected;
}

function mergeMin(base, extra) {
  const merged = { ...base };
  for (const [date, points] of Object.entries(extra)) {
    if (merged[date] === undefined || points < merged[date]) merged[date] = points;
  }
  return merged;
}

/**
 * 設定された全ホテルについて「日付 → 必要ポイント」を取得する。
 * 戻り値: { [hotelCode]: { "YYYY-MM-DD": points } }
 * 取得に失敗したホテルは結果に含めず、エラーを errors に積む。
 */
export async function fetchAllHotels(config, { log = console.error } = {}) {
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const context = await browser.newContext({
    locale: "ja-JP",
    timezoneId: "Asia/Tokyo",
    viewport: { width: 1280, height: 900 },
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
  });

  const template = config.urlTemplate ?? DEFAULT_URL_TEMPLATE;
  const months = config.searchMonths ?? 3;
  const guests = config.guests ?? 2;
  const delay = config.requestDelayMs ?? 5000;
  const timeoutMs = config.pageTimeoutMs ?? 60000;

  const results = {};
  const errors = [];
  try {
    const page = await context.newPage();
    for (const hotel of config.hotels) {
      let byDate = {};
      try {
        for (let i = 0; i < months; i++) {
          const from = new Date();
          from.setDate(1);
          from.setMonth(from.getMonth() + i);
          if (i === 0) from.setTime(Date.now()); // 当月は今日から
          const url = buildUrl(template, hotel, from, guests);
          log(`[scraper] ${hotel.code}: ${url}`);
          byDate = mergeMin(byDate, await fetchHotelMonth(page, url, timeoutMs));
          await sleep(delay);
        }
        if (Object.keys(byDate).length === 0) {
          throw new Error("ポイントデータを含むレスポンスを検出できませんでした");
        }
        results[hotel.code] = byDate;
        log(`[scraper] ${hotel.code}: ${Object.keys(byDate).length} 日分を取得`);
      } catch (err) {
        errors.push({ hotel: hotel.code, message: err.message });
        log(`[scraper] ${hotel.code}: 失敗 - ${err.message}`);
      }
    }
  } finally {
    await browser.close();
  }
  return { results, errors };
}
