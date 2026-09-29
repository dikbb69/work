# Atherton, J., Akroyd, J., Farazi, F., Mosbach, S., Lim, M. Q., & Kraft, M. (2023) British wind farm ESS attachments: curtailment reduction vs. price arbitrage
- 書誌: *Energy & Environmental Science* 16, 4020–4040. DOI 10.1039/d3ee01355c（CC BY）。コード: TheWorldAvatar
- 出所: ユーザー提供PDF（2026-09-29 精読）→ Drive SetE

## 1. 問いと貢献
- 英国の風力発電所に併設する市場連動型 ESS の経済性と抑制削減を、47サイトについてナレッジグラフ基盤のデジタルツインで評価。価格裁定と抑制削減のどちらが回収を担うかを切り分ける。

## 2. データ・設定
- BMRS の30分値（価格・出力・抑制）、2021年、容量50MW以上の47風力（Table 2）。ESS は各サイト 1MWh（感応度で 2〜4MWh、Table 5）、DOD 80%、寿命12年・4,996サイクル、資本費 £271,712/MWh、割引率10%。

## 3. 手法
- 収益最大化のディスパッチ（裁定＋抑制電力の充電）。ESS あり／なしの差分で流量・回収・排出を評価。

## 4. 主要結果
- Table 3（国別合計）: 抑制削減による獲得 スコットランド 1,116 MWh vs イングランド 133 MWh；裁定損失 2,117 vs 1,055 MWh。**47サイト中3サイトのみ**で抑制削減が損失を上回り純輸出増。
- Table 4: **全サイトで回収達成、ほぼ全て2〜3年**（寿命の16.75〜33.25%）、3,000〜3,500サイクル（限度の61〜83%）。回収の主因は価格裁定で、抑制率の低いイングランド・ウェールズの洋上サイトが最速。
- Table 5: 1MWh の年間収益は上位サイトで約 £143〜144千/MWh（2021年の高価格・高ボラ年である点に注意）。
- 放電は水力が限界電源の時間帯に偏り、置換排出原単位は不均衡市場平均より低い。

## 5. 限界
- 単年（2021）、サイト単位の価格テイカー評価、価格平準化や水力との競合など系統側の二次効果は対象外。ESS 仕様の文献値依存。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.2.3、第9章9.3.2（併設価値＝①裁定＋②抑制回避の二層）。
- 支持: 併設の価値は主に裁定で、抑制回避は系統制約の強い地域で上乗せされる。本研究の π=①+②+③ の分解と同型。
- 注意: 英国はゾーン価格（単一）で、抑制は制約支払い（constraint payments）を通じて発電側に補償される制度。日本のように補償なしで「価格に映らない損失」とは制度が異なるため、9.3 では「ゾーン価格＋補償あり（英国）」「ノーダル（ERCOT）」「ゾーン価格＋補償なし（日本）」の3類型として位置づける。
- 新規性チェック: サイト別の技術経済評価。本研究は均衡・政策ウェッジの文脈で位置づける点が新しい。

## 7. 引用に使える原文
- "While all ESSs achieved payback due primarily to price arbitrage, results indicate English/Welsh sites (typically with offshore wind) had quicker payback times ... batteries co-located with Scottish wind farms attained slower payback times, they accomplished greater curtailment reductions"（Abstract）
- "For economic returns, and therefore payback, price arbitrage was more significant."（§6）
- "At 3 of the 47 sites, curtailment reduction was significant enough for a net increase in energy exports to occur"（§7）
