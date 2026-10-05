# スライド様式（2026-10-05 ゼミ進捗報告デッキ）— 全スライド共通、厳守

## 書式の制約（Slides 型）
- 1ファイル = `project/slides/<id>.html`、中身はちょうど1つの `<section id="<id>" style="…">`（前後に何も書かない。`<html>` `<style>` `<link>` 禁止）。id = ファイル名。
- キャンバス 1920×1080px 固定。スタイルはすべてインライン。使える CSS は px（または無単位数値）、hex 色のみ。`margin`・`em`・`rem`・`%`（pinned と flex 子の幅以外）・`var()`・`z-index`・クラスは禁止。
- 使える要素: h1 h2 h3 p ul ol li br b i u span(色だけ) div img table tr th td svg hr x-icon x-shape x-connector aside。各テキストに font-size を明示（**24px 未満は禁止**）。h1〜h3 は font-size・font-weight を必ず明示。
- `<ul>`/`<ol>` は1階層の `<li>` のみ（入れ子禁止）。span にサイズ・フォントは付けない（色・太字のみ）。
- position:absolute の要素には left/top/width（必要なら height）を与える。1枚あたり要素は200個以下。div の入れ子は15段以下。
- 画像は `<img src="/_blob/…" alt="…" style="width:…px;height:…px;object-fit:contain">`（下の資産表の URL をそのまま）。図は object-fit:contain。図の背景を少し区別したいときは図を `background:#FDFDFB;border:1px solid #D5DAE1;border-radius:12px` の div に入れる。
- 表: `<table style="font-size:26px;…">`、1行目は `<th>`、各列の幅は1行目の全セルに `width:N%`。セル内は平文のみ（b/span 可）。rowspan/colspan 禁止。行の背景は `<tr style="background:#…">`。
- 話す内容（台本）は最後の子要素 `<aside>…</aside>` に平文で（4,000字以内）。台本には「何を見せ、何を言うか」と、根拠（章・表・数値）を書く。

## 色（これ以外は使わない）
- 濃紺 NAVY `#14213D`（見出し、暗い背景）
- 本文 INK `#2B3445`
- 補助 MUTED `#5B6575`（注・出典・ページ番号）
- 背景1 `#F7F6F2`（通常）／背景2 `#EDF1F6`（章扉以外の「まとめ」「議論」系）／カード `#FDFDFB`／罫線 `#D5DAE1`
- アクセント青 BLUE `#0B6FB0`（太陽光・風力の図の青に合わせる。見出し上の小見出し＝eyebrow、強調）
- アクセント橙 ORANGE `#C2511A`（要点メッセージ、強調数値）
- 暗い背景（章扉・表紙）の上: 文字 `#F3F1EA`、補助 `#B9C3D3`、強調 `#F2A65A`
- 薄い強調面: 青の面 `#E3EEF7`、橙の面 `#F8E9DF`（その上の文字は INK か NAVY）

## 書体
- 本文・見出し: `font-family:'Noto Sans JP', Arial, sans-serif`（section に設定して継承）
- 表紙と章扉のタイトルだけ: `font-family:'Noto Serif JP', Georgia, serif`
- 字の大きさは次の5段階だけ: 88（表紙）／52（スライド題）／34（大きな数値・強調文）／28（本文）／24（注・出典・表の小さい文字・ページ番号）。表本文は 26 も可。
- 強調は太字（700）か色で。サイズを変えて強調しない。

## 通常スライドの骨格（コピーして使う）
```html
<section id="ID" style="background:#F7F6F2;color:#2B3445;font-family:'Noto Sans JP', Arial, sans-serif;padding:88px 120px 150px;display:flex;flex-direction:column;gap:32px">
<div style="display:flex;flex-direction:column;gap:10px">
<p style="font-size:24px;font-weight:700;color:#0B6FB0;letter-spacing:2px">EYEBROW（例: 第6章 実証I ｜ 価格形成）</p>
<h2 style="font-size:52px;font-weight:700;color:#14213D;line-height:1.2">スライドの題（1行、28字以内）</h2>
<p style="font-size:30px;font-weight:500;color:#C2511A;line-height:1.4">要点メッセージ（1〜2行）</p>
</div>
<div style="flex:1;display:flex;gap:48px">
  … 本文（下の部品を使う）…
</div>
<p style="position:absolute;left:120px;top:990px;width:1500px;font-size:24px;color:#5B6575">出典: 本論文 表6.2（data/processed/…）／JEPX・北海道電力NW</p>
<p style="position:absolute;left:1700px;top:990px;width:100px;font-size:24px;color:#5B6575;text-align:right">##</p>
<aside>台本…</aside>
</section>
```
- ページ番号は `##` のまま書く（最後にまとめて置換する）。
- 縦の予算: 上下パディングを除いて 842px。見出しブロック ≈ 34+10+62+10+(42×行数) ≈ 160〜200px。本文に使えるのは約 600px。はみ出しそうなら文字を減らす（サイズは下げない）。
- 横: 本文幅 1680px。
- p は 30 字/行（28px で約 1,000px 幅）程度を目安に。日本語は文字単位で折り返すので長い英単語だけ注意。

## 部品
- **データ／分析／結果の3点セット**（実証スライドの左カラム、幅 620px）:
```html
<div style="width:620px;display:flex;flex-direction:column;gap:20px">
<div style="display:flex;flex-direction:column;gap:6px;border-left:6px solid #0B6FB0;padding:4px 0 4px 20px">
<p style="font-size:24px;font-weight:700;color:#0B6FB0">データ</p>
<p style="font-size:26px;line-height:1.45">北海道 FY2023〜25 の時間値（JEPXエリアプライス、制御前の太陽光・風力出力）</p>
</div>
<div style="… border-left:6px solid #5B6575 …"><p …>分析</p><p …>…</p></div>
<div style="… border-left:6px solid #C2511A …"><p …color:#C2511A>結果</p><p …>…</p></div>
</div>
```
  右カラム: 図（`flex:1` の div の中に img。width は 1012px 前後、height は図の縦横比から計算し 560px 以下）。
- **カード行**: `display:flex;gap:28px` の中に `flex:1;background:#FDFDFB;border:1px solid #D5DAE1;border-radius:14px;padding:28px 32px;display:flex;flex-direction:column;gap:10px` のカード。カードの見出しは `<h3 style="font-size:28px;font-weight:700;color:#14213D">`、本文 26〜28px。高さは固定しない。
- **大きな数値**: `<p style="font-size:34px;font-weight:700;color:#C2511A">K* = 0</p>` ＋ 下に 24〜26px の説明。
- **注意書き・限界**: 橙の面 `background:#F8E9DF;border-radius:12px;padding:20px 28px` の p（26px）。
- 図の脚注は図の下に 24px・MUTED で1行。

## 章扉スライド（各パートの最初）
```html
<section id="ID" style="background:#14213D;color:#F3F1EA;font-family:'Noto Sans JP', Arial, sans-serif;padding:128px 160px;display:flex;flex-direction:column;justify-content:center;gap:28px">
<p style="font-size:28px;font-weight:700;color:#F2A65A;letter-spacing:4px">PART 3</p>
<h1 style="font-family:'Noto Serif JP', Georgia, serif;font-size:88px;font-weight:700;line-height:1.2;color:#F3F1EA">データと分析方法</h1>
<p style="font-size:30px;color:#B9C3D3;line-height:1.5">このパートで答える問い（1〜2行）</p>
<aside>…</aside>
</section>
```

## 用語（HANDOFF §8。使用禁止の造語）
政策ウェッジ→「均衡からの乖離（数量）」「市場外収入（原因）」／政策層・二層参入→「市場外収入に依存する容量（契約型）とマーチャント容量」／純市場→「マーチャント（スポット裁定のみ）」／BTM→「併設蓄電池」、FTM→「系統用蓄電池」／裾補正→「裾の補正」／風力中立性→「風力が日内形状を変えない性質」／break-even フロンティア→「損益分岐面」／均衡面→「2次元の感応度面」。K（フリート容量）と K*（均衡容量）。
主張は条件付きで（「必然」と言わない）。厚生分析はスコープ外。
10/5 追加: 「床」は使わない → 価格そのものは「下限価格（0.01円/kWh）」、張り付いた状態・時間・コマは「下限張り付き（時間・コマ）」、機構は「下限での打ち切り」。「PF価値」「PF粗利」は使わない → 「完全予見の裁定粗利」（略称「完全予見粗利」。表の列見出し・図の凡例でのみ PF を残し、ノートで一度定義する）。完全予見の値は常に「前日スポット・1日1サイクルでの上界」と限定する。

## 資産（図）の URL 表 — これ以外の画像は使わない
| 図 | ファイル | URL | 縦横比 |
|---|---|---|---|
| 図6.1 太陽光大小×3季節の価格カーブ | price_curve_shapes_fy2023-25.png | /_blob/fee92822474fc8d8dc34af881d502623 | 2.65 |
| 図6.2 風力大小×3季節の価格カーブ | wind_price_curves_fy2023-25.png | /_blob/b90fc9163b347b40852ec48ed16ce4c1 | 2.65 |
| 図6.3 帯域分解の年度別推移 | wind_bands_timeseries.png | /_blob/0aee6c495f4b23353813934305885fad | 1.86 |
| 図6.4 発電量五分位×水準・TB4h | gen_vs_price_shape.png | /_blob/231e10eab811d2f6f4c9bd7b9b359dc6 | 1.58 |
| 図6.5 空間分散シミュレーション | spatial_dispersion.png | /_blob/06ef6b72910e569a289b6191316f2242 | 2.37 |
| 図7.1 年間裁定粗利の時系列 | annual_backtest_series.png | /_blob/b9e9442482c8556134b2c4d01146f0b9 | 1.86 |
| 図8.1 風力導入量スイープ | kwind_sweep.png | /_blob/bee90690b6a65da237a25579a2276e43 | 2.35 |
| 図8.2 π(K)曲線（基本仕様） | pi_k_curve.png | /_blob/8e8f7a58a825d332b866a812ee2cd634 | 1.80 |
| 図8.3 π(K)の価格水準感応度 | pi_k_curve_v2.png | /_blob/8611a4a3be0a093250096c91bf31ac5c | 1.73 |
| 図8.4 π(K; K_wind) | equilibrium_surface.png | /_blob/117ad2198d1d0fd36394b6f85d788a7a | 1.73 |
| 図9.1 損益分岐面 | breakeven_frontier.png | /_blob/1109321a3e23dcf2caec740b7b18446a | 1.58 |
| 図10.1 下限価格シナリオ別 π(K) | negative_price_pi_k.png | /_blob/592e255311e3bb4edcdf85f0bb3b5893 | 1.76 |
| 補助図 帯域分解の比較（北海道風力 vs 九州太陽光） | band_comparison.png | /_blob/3e3ab33c90040d5949760f1dbc06a537 | 2.39 |
| 補助図 帯域分解（北海道） | band_comparison_hokkaido.png | /_blob/919d9197d8bc48a56fe7153719a41be8 | 2.39 |
| 補助図 併設の根拠（10/5 再描画: 下限価格の表記） | btm_case.png | /_blob/5af12fd0b22fb0e7d625f6912249d08e | 2.41 |
| 風力導入量と連系線（北海道） | fig1-wind-vs-interconnection.png | /_blob/c7a711c46c51375942987d94ccf50704 | 1.39 |
| 九州 ダックカーブ | kyushu/f1-duck-curve.png | /_blob/f993539aef7fd17c6ebc72505f6cd6d9 | 1.66 |
| 九州 床（0.01円）コマ | kyushu/f2-floor-koma.png | /_blob/4b25eee86f2f152214ba2b1809c326c8 | 1.64 |
| 九州 TB4h スプレッド | kyushu/f3-tb4h-spread.png | /_blob/add87cea3494dca8866307cadf5b5afa | 1.66 |
| 九州 風力の時間スケール | kyushu/f15-wind-timescale.png | /_blob/09ad7c322999a324693e8a27e93c038d | 2.50 |
| 九州 価格帯域 | kyushu/f13-price-bands.png | /_blob/6a44e59dc930edeb13bb737e6937901a | 1.70 |
| 九州 年次バックテスト | kyushu/f7-backtest-annual.png | /_blob/fb04289eb90c44d527b33fe15a765437 | 1.63 |
