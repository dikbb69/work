# Lamont (2013) Assessing the Economic Value and Optimal Structure of Large-Scale Electricity Storage
- 書誌: Alan D. Lamont (Lawrence Livermore National Laboratory), *IEEE Transactions on Power Systems*, Vol. 28, No. 2 (May 2013), pp. 911–921. DOI 10.1109/TPWRS.2012.2218135
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 2つの問い（§I）: (1) 蓄電の浸透は系統条件でどう決まり、発電・充電・放電・貯蔵容量の最も効率的な構成は何か、(2) 大規模蓄電は系統の価格パターンをどう変え、他技術（風力・太陽光）の経済的浸透にどう影響するか。
- 貢献: 容量最適化モデルのラグランジアンから、蓄電システムの各構成要素（充電装置 kW、放電装置 kW、貯蔵槽 kWh）の**限界価値の解析的表現**を導出し、蓄電が系統限界費用（SMC＝価格）のパターンに与える影響を特徴づける。先行研究 [9]–[16] は小規模（価格テイカー）蓄電で、[15][17]（Sioshansi et al. 2009）は価格影響を扱うが解析的な限界価値表現はない。
- 核心的洞察: 容量の限界価値は「その容量が完全に使われる回数×そのときの価値」で決まる（Fig.3–4）。貯蔵槽の限界価値は各サイクルの充電時 SMC と放電時 SMC の差（充電の限界時間と放電の限界時間の価格差）の年間合計。

## 2. データ・市場・期間
- 例示（§III）: カリフォルニアの時間依存価値研究 [21] の 2001 年時間値価格と CAISO 負荷。ピーク負荷を 60 GW に、年間発電 332,000 GWh にスケール。充放電各 90%（往復 81%）、同一装置で充放電。カリフォルニア系統のモデルではなく「a view of the results that could be obtained」。
- 価格–負荷関係: 日ごとの**双線形（bi-linear）フィット**（低負荷時間と高負荷時間で別の直線、夏季は閾値超で急騰、Fig.6）。Excel Solver で各日を解く。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 年間資本費＋運転費の最小化（式(1)–）。決定変数: 各発電機容量、充電容量、放電容量、貯蔵容量、各時間の出力・充放電。サイクル c ごとに「満充電時刻」「空になる時刻」を定義（Fig.2）。
- ラグランジアン導関数の解釈（§II-C）: (a) 充電の最適ディスパッチ: 充電中は SMC が充電の限界価値 λ_c に等しくなるまで充電し、充電装置がフル稼働になると SMC は λ_c を下回る（Fig.3）。(b) 放電: 各時間の放電の限界価値＝SMC − 放電時の蓄電エネルギーの限界価値（Fig.4）。(c) 容量条件（式(13)–(15)）: 各技術の容量は**限界価値＝限界資本費**まで追加（式(15): 貯蔵槽の限界価値は各サイクルの（放電時価値 − 充電時価値）の和）。
- 構成要素間の相互作用（§II-D）: 貯蔵槽を増やすと充電時間が延び、充電の限界時間の SMC が上がる（充電容量の限界価値は上がるが、貯蔵の限界価値は下がる）。
- 不確実性下（§V）: 完全予見を前提とする限界価値を、予測・ディスパッチアルゴリズムの下での期待限界価値に置き換える枠組みを提示。
- 均衡概念: 費用最小化の一階条件（限界価値＝限界費用）。競争均衡と同値であることは明示しないが、Schmalensee (2020) と同じ Boiteux 型の論理。

## 4. 主要結果（数値を必ず。表番号を付す）
- **Fig.7（限界価値の等高線）**: 貯蔵槽限界価値（$/kWh-yr）と充放電限界価値（$/kW-yr）を貯蔵容量×充放電容量の平面に描く。両方とも**収穫逓減**。小容量では相互作用が強く（一方を増やすと他方の限界価値が上がる）等高線がほぼ平行。
- 例示の最適構成（§III-C）: 充放電費 2.0 $/kW-yr、貯蔵費 1.5 $/kWh-yr（「optimistically」）で最適は **1.25 GW／6.3 GWh**（約5h）。貯蔵費が 1.0 $/kWh-yr に下がると **2.2 GW／12.5 GWh**（約5.7h）。（費用水準は非現実的に低く、限界価値の絶対水準が小さいことを示唆）
- **Fig.8（価格持続曲線、10 GW／30 GWh）**: 蓄電はオンピーク価格を大きく下げるが、オフピーク価格はほとんど上げない（オフピークでは価格が需要に非感応、Fig.6）。
- **§IV の含意**: (1) 風力（オフピークに発電）を蓄電が支援するためにはオフピーク価格を上げる必要があるが、その効果は小さい → 蓄電と風力の補完性は限定的。(2) 夏ピーク系統では太陽光がピーク時間に収入の大半を得るため、蓄電によるピーク価格低下は**太陽光投資を阻害**する。

## 5. 著者が挙げる限界・今後の課題
- 例示はカリフォルニアのモデルではない（2001年データ、スケール調整）。価格–負荷は日次の双線形フィット。
- 完全予見に基づく限界価値（§V で不確実性下の拡張を概念的に示すのみ）。
- 充放電を同一装置とする場合の扱い（§II-C-6）。部分サイクルの収入は限界価値に寄与しない。
- 発電投資の内生化と蓄電の相互作用は枠組みの提示にとどまる。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 蓄電容量の限界価値＝「サイクルごとの充放電価格差の年間和」という解析表現は、本研究の π_spot(K)（TB4h 型の日内スプレッドの年間集計）の理論的定義に対応。限界価値＝限界資本費の条件は自由参入条件の投資側の表現。
  - 第3章／第5章（風力 vs 太陽光）: 「蓄電はオンピーク価格を下げるがオフピーク価格はほとんど上げない」「したがって風力（オフピーク発電）との補完性は小さく、太陽光（ピーク発電）の収入を減らす」（§IV）は、本研究の「風力主導ゾーンでは日内スプレッドが広がらず蓄電価値が小さい」と「BTM 併設は抑制回避価値で成り立つ」の両方に理論的裏付けを与える。特に**オフピーク側の価格非感応性**は、北海道で風力が夜間に価格をフロア（0.01円）まで下げる状況で、蓄電の充電がフロア価格を押し上げられない（充電側にレントがない）ことの説明に使える。
  - 第7章: 収穫逓減と構成要素間の相互作用（Fig.7）は、本研究が 4h 固定で K（出力）だけを動かす簡略化の限界を述べる際に参照。
- 支持する点: 蓄電容量の収穫逓減、蓄電が太陽光収入を減らす（Butters/Karaduman と一致）、風力との補完性の限定性。
- 対立・留意点: 貯蔵費 1.0–1.5 $/kWh-yr という仮定は現実の Li-ion（数十 $/kWh-yr）より2桁低く、最適容量（GW 級）は本研究の K* と直接比較できない。Lamont の風力支援論は「オフピークの価格を上げる」経路だけで、抑制回避（BTM）経路は扱わない。
- 手法の源流: Sioshansi (2009) と同様の価格–負荷関係（双線形）による価格影響モデル、限界価値の解析表現。
- 新規性チェック: 既に行われていること＝蓄電の限界価値の解析枠組みと、風力・太陽光への価格効果の非対称性の指摘（2013年）。本研究が新たに行うこと＝実データ（JEPX 北海道）で電源別の日内スプレッド効果を推定し、π(K) と政策収入を含む自由参入均衡へ接続。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract (p.911): "If storage is to penetrate the system, the marginal value of storage capacity must be high enough to enable investments in storage. To have a significant impact on investments in intermittent technologies, it must be large enough to affect the prices on the system."
2. §I (p.911): "As an example, wind often generates overnight when demand is low. Large wind capacity tends to drive down the prices during those hours that it generates the most power discouraging further investment in wind. If large-scale storage is added to the system, it can charge during periods of low prices, raising the load on the system and increasing prices."
3. §II-C (p.917): "To optimize system, capacity is added to each type of technology up to the point that the marginal value of capacity is equal to the marginal cost of capacity."
4. §IV (p.920): "The results of this example indicate that storage would have a relatively small effect on off-peak prices since the off-peak prices are not particularly responsive to demands ... This could often be the case since off-peak naturally implies that there are substantial generation resources available."
5. §IV (p.920): "Fig. 8 also indicates that storage substantially reduces the on-peak prices. ... In a summer peaking system such as California's, solar generators earn a substantial portion of their revenues during the peak hours of the day. Reducing the prices in peak hours would tend to discourage investment in solar technologies."
