// 通知の送信。環境変数で設定されたチャネルすべてに送る:
//   DISCORD_WEBHOOK_URL … Discord の Webhook
//   SLACK_WEBHOOK_URL   … Slack の Incoming Webhook
//   SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS / MAIL_TO (/ MAIL_FROM) … メール
// どれも未設定の場合は標準出力に表示するだけ(ローカル実行時の確認用)。

import nodemailer from "nodemailer";

const fmt = new Intl.NumberFormat("ja-JP");

export function buildMessage(alerts) {
  const byHotel = new Map();
  for (const alert of alerts) {
    if (!byHotel.has(alert.hotelCode)) byHotel.set(alert.hotelCode, []);
    byHotel.get(alert.hotelCode).push(alert);
  }

  const lines = ["🏨 Marriott ポイント宿泊アラート"];
  for (const hotelAlerts of byHotel.values()) {
    const { hotelName, hotelCode } = hotelAlerts[0];
    lines.push("", `■ ${hotelName} (${hotelCode})`);
    for (const a of hotelAlerts) {
      if (a.type === "threshold") {
        lines.push(
          `  ${a.date}: ${fmt.format(a.points)}pt (上限 ${fmt.format(a.maxPoints)}pt 以下)`
        );
      } else {
        lines.push(
          `  ${a.date}: ${fmt.format(a.prevPoints)}pt → ${fmt.format(a.points)}pt に値下がり`
        );
      }
    }
  }
  return lines.join("\n");
}

async function postWebhook(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Webhook 送信失敗: HTTP ${res.status} ${await res.text()}`);
  }
}

async function sendMail(message) {
  const transport = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT ?? 587),
    secure: process.env.SMTP_PORT === "465",
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });
  await transport.sendMail({
    from: process.env.MAIL_FROM ?? process.env.SMTP_USER,
    to: process.env.MAIL_TO,
    subject: "Marriott ポイント宿泊アラート",
    text: message,
  });
}

/** @returns {Promise<string[]>} 送信に成功したチャネル名 */
export async function notify(alerts, { log = console.error } = {}) {
  if (alerts.length === 0) return [];
  const message = buildMessage(alerts);
  const sent = [];

  const channels = [
    {
      name: "discord",
      enabled: !!process.env.DISCORD_WEBHOOK_URL,
      send: () => postWebhook(process.env.DISCORD_WEBHOOK_URL, { content: message.slice(0, 1900) }),
    },
    {
      name: "slack",
      enabled: !!process.env.SLACK_WEBHOOK_URL,
      send: () => postWebhook(process.env.SLACK_WEBHOOK_URL, { text: message }),
    },
    {
      name: "email",
      enabled: !!(process.env.SMTP_HOST && process.env.MAIL_TO),
      send: () => sendMail(message),
    },
  ];

  for (const channel of channels.filter((c) => c.enabled)) {
    try {
      await channel.send();
      sent.push(channel.name);
      log(`[notify] ${channel.name} へ送信しました`);
    } catch (err) {
      log(`[notify] ${channel.name} への送信に失敗: ${err.message}`);
    }
  }

  if (channels.every((c) => !c.enabled)) {
    console.log(message);
    log("[notify] 通知チャネル未設定のため標準出力に表示しました");
    sent.push("stdout");
  }
  return sent;
}
