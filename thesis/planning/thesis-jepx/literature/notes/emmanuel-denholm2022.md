# Emmanuel, M. I., & Denholm, P. (2022) A market feedback framework for improved estimates of the arbitrage value of energy storage using price-taker models
- 書誌: *Applied Energy* 310, 118250. DOI 10.1016/j.apenergy.2021.118250（NREL）
- 出所: ユーザー提供PDF（2026-09-29 精読）→ Drive SetE

## 1. 問いと貢献
- 価格テイカー（PT）モデルは蓄電が価格に与える影響（ピーク抑制・オフピーク上昇）を無視するため、導入量が増えると裁定価値を過大評価する。本論文は PT モデルに「市場フィードバック関数」を組み込み、生産費用モデル（PCM）を使わずに導入量の関数として価値の低下を推定する枠組みを提案（§1, §5）。

## 2. データ・市場・期間
- PJM と CAISO の時間値 LMP と負荷、2018・2019年。蓄電: 4時間、往復効率80%、100MW 刻みで 1,000MW まで追加（§4）。

## 3. 手法
- 標準 PT（RODeO、式(1)–(2)）に、勾配ブースティング回帰（GBR）で推定した価格–純負荷関係を接続。蓄電の充放電で純負荷を更新→価格を再予測→再最適化、を反復（Fig. 6）。

## 4. 主要結果
- Fig. 10（限界裁定価値）: 初期値 PJM $27.4（2018）/$15.9（2019）/kW-年、CAISO $51.0/$47.5。導入量とともに単調に低下。CAISO の低下が急なのは市場規模の相対差（1,000MW は CAISO 平均需要の約4.0%、PJM の0.6%）。
- 年換算資本費約 $93.2/kW-年 は裁定価値を上回る。容量収入等を加えると費用を超えうるが、導入が進むほど裁定分は減る（§4.1）。
- Fig. 13–14: 放電時の販売価格が低下し充電価格が上昇。価格の標準偏差も導入とともに低下。

## 5. 著者が挙げる限界
- GBR は外れ値に弱い。価格–負荷のレジーム識別は未実装。歴史的価格–負荷関係に依存し、需要・再エネ構成が変わる将来には PCM とのハイブリッドが必要（§5）。

## 6. 本研究との関係
- 引用予定箇所: 第5章5.4.2（増分投入の源流）、第8章8.3（π(K) の形状・市場規模依存）。
- 支持: 「小さい市場ほど早く枯渇」（CAISO vs PJM）＝北海道（需要3〜5GW）で1GWが飽和点になることの類推。「裁定単独では資本費に届かず容量収入が必要」＝二層参入の容量市場項。
- 相違: 本研究は供給曲線（純需要→価格）を季節別に推定した価格過程上で増分投入し、GBR は使わない。
- 新規性チェック: 手法の先行例。本研究は風力主導ゾーンで自由参入均衡（K\*）と政策ウェッジまで進める点で異なる。

## 7. 引用に使える原文
- "as greater amounts of energy storage are deployed on the grid, current PT models fail to predict the effects that energy storage itself can have on market prices. This can lead to an overestimation of the economic value of storage"（Abstract）
- "In each location, we add up to 1,000 MW in 100-MW blocks, assuming 80% round-trip efficiency and 4-hour-duration energy storage"（§4）
- "1,000 MW of storage represents approximately 4.0% of average demand in CAISO and 0.6% of average demand in PJM."（§4.1）
- "the revenue from arbitrage-only applications is less than the annualized cost of many storage systems ... However, adding other revenue streams (particularly capacity) can result in net revenues that exceed costs."（§4.1）
