# 風力はいつから・本当にスポット価格に効くのか — 欧米の実証と北海道への適用

- 目的: 発表後半（P11-12）への想定反論「北海道で風力が本当にスポット価格を動かすのか。発電所間で変動が打ち消し合ってボラが出ないのではないか」への、文献と市場データに基づく回答
- 作成日: 2026年7月26日

---

## 1. Q1: 風力が価格に「効き始める」のはどの水準からか

### 1.1 欧米の実証アンカー（分析対象期間の風力シェアと検出された効果）

| 市場 | 期間 | 風力シェア（発電量比） | 検出された効果 | 文献 |
|---|---|---|---|---|
| ERCOT（テキサス） | 2007-10 | **約5〜8%** | 価格水準の低下＋**価格分散の有意な拡大** | Woo et al. (2011, Energy Policy) |
| ドイツ | 2006-12 | **約6〜8%** | 水準低下＋**ボラティリティ増**（ARX-GARCH） | Ketterer (2014, Energy Econ) |
| スペイン | 2005-09 | 再エネ計 約11% | メリットオーダー効果 | Gelabert et al. (2011) |
| 西デンマーク | 2000年代 | 20%超 | **風力予測が日中の価格分布そのものを規定** | Jónsson et al. (2010, Energy Econ) |
| デンマーク／独 | 2010年代 | 30-40%／10-20% | 風力は日次ボラを増加（独）・市場構造次第で符号が変わる | Rintamäki et al. (2017) |
| 豪州NEM | 2010年代 | SA州 30-40% | 価格ダイナミクスへの有意な影響 | [Csereklyei et al. (2021, Energy Econ)](https://www.sciencedirect.com/science/article/abs/pii/S0140988321004230) |
| デンマーク現在 | 2024 | **54%**（[国内供給比](https://ourworldindata.org/data-insights/denmarks-electricity-has-a-larger-share-of-wind-power-than-any-other-country)、[再エネ計88%](https://investindk.com/insights/denmark-1-in-share-of-renewables-in-net-electricity-generation-for-2024-in-the-eu)） | 風力が価格形成の支配要因 | IEA/OWID |
| 南豪州現在 | 2025-26 | 風力+太陽光で7割前後 | **負値価格が四半期の46%**（[Q4 2025、NEM記録](https://www.energycouncil.com.au/analysis/increases-in-negative-prices-is-it-a-positive/)）、[2026年6月も19%](https://leadingedgeenergy.com.au/blog/electricity-market-review-latest/) | AEMO QED等 |

**定型化された事実**: 風力の価格効果（水準・ボラとも）は**エネルギーシェア5〜10%の段階で既に統計的に検出されている**。閾値的な「スイッチ」ではなく、「低需要時に風力が残余需要を供給曲線の急峻部・平坦部に押し込む頻度」が浸透率とともに連続的に増える構造。

### 1.2 北海道の現在地と将来位置

- **現在**: 風力接続量136万kW（2024年9月末）。エネルギーシェア概算 = 1.36GW × 設備利用率22-25% × 8760h ≈ 2.6〜3.0TWh ÷ エリア需要約30TWh ≈ **7〜10%**（概算。HEPCO需給実績の取得後に実測値へ置換） → **ERCOT・ドイツで効果が検出された水準に既に到達**
- **将来**: 洋上風力5海域・最大380万kW（CF35%）で+11.6TWh → シェア**約45〜50%** → **現在のデンマーク・南豪州の領域**に入る
- **夜間最低需要との比較**: 北海道の夜間最低需要は約2.8GW。現在の風力フル出力（1.36GW）で既にその約半分、洋上追加後（5.2GW）は**最低需要を超える** — 「風力が残余需要をゼロ以下に押し込む夜」が構造的に発生する

### 1.3 北海道で「既に」観測されている直接証拠（将来の話ではない）

1. **Sakaguchi & Fujii (2021, Frontiers in Sustainability)**: JEPXのFY2016-19データの分位点回帰で、**北海道エリアでは風力のメリットオーダー効果が高価格分位で最大**と報告 — 風力シェアが今より低い時期に、既にエリアプライスへの影響が統計的に検出されている
2. **出力制御に風力が含まれる**: 2022年以降の北海道の出力制御は太陽光だけでなく**風力（初回で739件）**が対象 — 風力は既に余剰マージンに到達している
3. **間接送電権の商品化**: 2023-24年度実績で北海道→東北順方向の値差期待値が正となり2026年度から商品化 — **余剰の輸出制約（閉じ込め）が価格に表れている**

## 2. Q2: 発電所間の「打ち消し合い」でボラが消えることはないか

### 2.1 空間平滑化の物理 — 消えるのは高周波だけ

風力出力の発電所間相関は距離とともに指数的に減衰するが、**時間スケールに強く依存する**：

- **秒〜分〜1時間未満の変動**: 発電所間でほぼ無相関 → 集約で打ち消し合う（平滑化が効く）
- **数時間〜数日の変動（総観規模: 低気圧・前線・冬型気圧配置。空間スケール100〜1000km）**: **数百km離れても高相関のまま残り、集約しても消えない**。欧州の実証では、デンマークとドイツの国全体の風力出力ですら相関0.65（[Malvaldi et al. 2017, *Wind Energy*](https://onlinelibrary.wiley.com/doi/full/10.1002/we.2095)）。単一発電所の自己相関は約40時間まで持続し、**平滑化の効果は「地域の広さ」だけで決まり、発電所の数を増やしても頭打ち**になる

**スポット市場（前日・30分コマ）の価格を動かすのは、まさにこの「集約後も残る数時間〜数日スケール」の変動**である。したがって「各発電所の誤差が打ち消し合ってボラが消える」ことは、スポット価格に関連する時間スケールでは起こらない。平滑化が実際に効くのは分単位変動と（相対的な）予測誤差であり、これはインバランス・時間前市場の論点。

### 2.2 反例による実証 — 小さくて風力だらけの市場ほど雄弁

- **デンマーク**（東西あわせて約300km四方、風力54%）: 打ち消し合いで消えるなら風力は価格に現れないはずだが、実際には風力が価格形成の支配要因であり、風況によって輸出入・負値価格が大きく振れる
- **南豪州**: 州単位（風力発電所は数百kmに分布）でも、[2025年Q4に全コマの46%が負値価格](https://www.energycouncil.com.au/analysis/increases-in-negative-prices-is-it-a-positive/)。逆方向には、**フリート全体が数日止まる"wind drought"（風の干ばつ）で価格が急騰し蓄電池が空になる**事例が現実に発生（[RenewEconomy, 2026](https://reneweconomy.com.au/big-batteries-caught-short-as-worst-wind-drought-in-two-years-sends-prices-through-the-roof/)） — 集約はフリート同時の無風・強風を消せない
- **北海道の地理はむしろ相関を高める側**: 陸上風力は道北（宗谷・留萌）日本海側に集中し、洋上5海域（石狩・岩宇・島牧・檜山・松前）も**すべて日本海側の約300km帯**に並ぶ。冬型の季節風・日本海低気圧という同一の気象システムに同時に晒される立地であり、Malvaldiらの距離減衰スケール（数百km）に照らして**打ち消し合いは限定的**

### 2.3 結論

「風力の変動が打ち消し合ってボラが出ない」は、(i) 理論的に総観規模変動には適用できず、(ii) 北海道より広いか同等の市場（デンマーク・南豪州）で実証的に棄却されており、(iii) 北海道の風力立地は一方の海岸に集中していて平滑化の前提すら弱い。むしろ研究上の含意は逆で、**風力ボラの主周期が「数日」であること（日内サイクルの太陽光と異なる）こそが、蓄電池のduration選択・価値構造を変える本研究の核心**になる。

## 3. 発表への反映（P12に追加する2行）

- 「風力シェア概算7〜10%は、独・テキサスで価格効果が検出された水準に既に到達。洋上でデンマーク・南豪州の領域へ」
- 「空間平滑化が消すのは分単位の変動のみ。スポットを動かす数時間〜数日の総観規模変動は数百kmでは消えない（デンマーク・南豪州が実証）」

## 4. データ到着後の第一弾分析（Next Action）

北海道電力NWの需給実績（風力実績出力30分値）入手後、直ちに:
1. **風力出力×北海道エリアプライスの相関・分位点回帰**（Sakaguchi & Fujii 2021 の最新データでの再現・拡張。彼らの発見が直近データで強まっているかが最初の実証結果になる）
2. 風力出力の**自己相関・周期構造**（数日周期の確認）と、太陽光（日内周期）との対比 — duration論点の実証的裏付け
3. 風力集約出力の変動係数 vs 個別地点（アメダス風速の地点間相関で代理可能）— 平滑化の実測

## 主な出典

- [Malvaldi et al. (2017) "A spatial and temporal correlation analysis of aggregate wind power in an ideally interconnected Europe", *Wind Energy*](https://onlinelibrary.wiley.com/doi/full/10.1002/we.2095)
- Woo et al. (2011), Ketterer (2014), Rintamäki et al. (2017), Gelabert et al. (2011), Sakaguchi & Fujii (2021) — 書誌は `notes/03-literature-renewables-volatility.md`
- Jónsson, Pinson & Madsen (2010) "On the market impact of wind energy forecasts", *Energy Economics* 32(2)
- [Csereklyei et al. (2021) "Wind generation and the dynamics of electricity prices in Australia", *Energy Economics*](https://www.sciencedirect.com/science/article/abs/pii/S0140988321004230)
- [Our World in Data: デンマークの風力シェア（2024年 国内供給の54%）](https://ourworldindata.org/data-insights/denmarks-electricity-has-a-larger-share-of-wind-power-than-any-other-country)・[Invest in Denmark（再エネ88.4%）](https://investindk.com/insights/denmark-1-in-share-of-renewables-in-net-electricity-generation-for-2024-in-the-eu)・[IEA Denmark 2023](https://www.iea.org/reports/denmark-2023/executive-summary)
- [Australian Energy Council: 負値価格の増加（SA Q4 2025で46%）](https://www.energycouncil.com.au/analysis/increases-in-negative-prices-is-it-a-positive/)・[Leading Edge Energy（2026年6月）](https://leadingedgeenergy.com.au/blog/electricity-market-review-latest/)
- [RenewEconomy: wind droughtによる価格急騰（2026年）](https://reneweconomy.com.au/big-batteries-caught-short-as-worst-wind-drought-in-two-years-sends-prices-through-the-roof/)
