# Marriott ポイント宿泊モニター

Marriott Bonvoy のポイント宿泊に必要なポイント数を定期的にチェックし、
**設定した上限以下の日** や **前回チェックから大きく値下がりした日** を見つけたら
Discord / Slack / メールに通知するシステムです。価格履歴も蓄積します。

## 仕組み

```
GitHub Actions (6時間ごとの cron)
  └─ src/index.js check
       ├─ scraper.js  … Playwright で Marriott の空室カレンダーを開き、
       │                ページが裏で取得する API レスポンスを傍受してポイントを収集
       ├─ analyze.js  … しきい値判定 + 前回スナップショットとの比較で値下がり検知
       ├─ notify.js   … Discord / Slack / メールへ通知(同内容の再通知は抑止)
       └─ history.js  … data/ に履歴を保存(Actions がリポジトリへコミット)
```

- DOM のスクレイピングではなく **API レスポンスの傍受 + 再帰的な JSON 走査**で
  ポイントを抽出するため、サイトの見た目やレスポンス構造の多少の変更に耐えます。
- `data/latest.json` が前回値、`data/history.jsonl` が全履歴(1 行 1 実行)、
  `data/notified.json` が通知済み記録です。

## セットアップ

### 1. 監視するホテルを設定する

`config.json` を編集します。`code` はマーシャコード(Marriott のホテル詳細ページ
URL に含まれる 5 文字のコード。例: 東京マリオット = `TYOMC`)です。

```json
{
  "hotels": [
    { "code": "TYOMC", "name": "東京マリオットホテル", "maxPoints": 50000 }
  ],
  "searchMonths": 3,        // 今日から何ヶ月先まで見るか
  "guests": 2,              // 人数
  "notifyOnDrop": true,     // 値下がり通知を有効にするか
  "dropRatio": 0.15,        // 15% 以上の値下がりで通知
  "requestDelayMs": 5000    // リクエスト間隔(サーバー負荷への配慮)
}
```

### 2. 通知先を設定する

GitHub リポジトリの **Settings → Secrets and variables → Actions** に、
使いたいチャネルのシークレットだけ登録します(未設定のチャネルはスキップ)。

| Secret | 内容 |
|---|---|
| `DISCORD_WEBHOOK_URL` | Discord の Webhook URL |
| `SLACK_WEBHOOK_URL` | Slack の Incoming Webhook URL |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASS` / `MAIL_TO` / `MAIL_FROM` | メール通知(Gmail なら `smtp.gmail.com` / `587` / アプリパスワード) |

### 3. 動かす

- 定期実行: `.github/workflows/marriott-monitor.yml` が 6 時間ごとに自動実行します。
- 手動実行: Actions タブ → 「Marriott ポイント監視」→ Run workflow。
  「モックデータで実行」にチェックを入れると実サイトに接続せず動作確認できます。

### ローカルでの実行

```bash
cd marriott-points-monitor
npm install
npx playwright install chromium   # 初回のみ

npm run check:mock   # モックで動作確認(通知未設定なら標準出力に表示)
npm run check        # 実サイトに対して実行
npm test             # ユニットテスト
```

## 通知の仕様

- **threshold**: 必要ポイントが `maxPoints` 以下の日
- **drop**: 前回チェックより `dropRatio`(既定 15%)以上値下がりした日
- 同じ「ホテル × 日付 × ポイント数」は一度しか通知しません。
  さらに値下がりした場合は改めて通知されます。過去日の記録は自動で掃除されます。

## 制約・注意点

- **Marriott に公式のポイント価格 API はありません。** このツールは Web サイトを
  ブラウザで開いて情報を読むアプローチのため、サイトの大幅改修で取得できなくなる
  可能性があります。その場合は `config.json` の `urlTemplate`(検索 URL の
  テンプレート。`{code}` `{fromDate}` `{guests}` を置換)や
  `src/scraper.js` の `API_URL_RE` を調整してください。
- Marriott はボット対策(Akamai)を導入しています。GitHub Actions の共有 IP から
  ブロックされる場合は、**自宅サーバー等での cron 実行**(`crontab` で
  `npm run check`)や **セルフホストランナー** への切り替えを検討してください。
  コード自体は実行場所に依存しません。
- 個人利用の範囲で、`requestDelayMs` による間隔を空けた節度あるアクセスを
  前提としています。
- 取得できなかったホテルの前回値はスナップショットに引き継がれ、次回の
  値下がり比較が途切れないようになっています。
