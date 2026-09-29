# Kyritsis, Andersson & Serletis (2017) Electricity prices, large-scale renewable integration, and policy implications
- 書誌: *Energy Policy* 101, 550–560. DOI 10.1016/j.enpol.2016.11.014
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: ドイツにおける太陽光と風力の発電量が、日次スポット価格の**水準**と**ボラティリティ**に、それぞれどう異なる影響を与えるか。
- 著者の主張する貢献: (1) 太陽光と風力を**分離**して効果を推定（2015年6月までの最新データ）。(2) GARCH-in-Mean で水準と分散を統合推定し、Granger 因果も検証。(3) 再エネ浸透率の水準別に価格分布の高次モーメント（歪度・尖度）を記述。(4) 負の価格を除去せず分析に含める。
- 結論の要旨: 太陽光はピーク電源の稼働を抑えてボラティリティを**低下**、風力は系統の柔軟性を試してボラティリティを**上昇**させる。

## 2. データ・市場・期間
- 市場: ドイツ EPEX 日前（Phelix Day Base＝24時間平均、Day Peak＝9–20時平均、Off-peak＝1–8時・21–24時平均）。
- 期間・頻度: 2010年1月1日〜2015年6月30日、日次2,007観測。
- 変数: 太陽光実績 $s_t$（平均67,091 MWh/日）、風力実績 $w_t$（平均131,069 MWh/日）、総負荷 $l_t$（平均1,326,660 MWh/日）。価格平均40.7 €/MWh、歪度 −0.64、尖度6.6（Table 2）。
- 前処理: 負の価格は保持。原系列の標準偏差の10倍を超える値のみ置換。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 被説明変数: 日次価格（all/peak/off-peak）の水準。
- 変動性の定義: GARCH(1,1) の条件付き分散 $h_t$（日次価格の日間ボラティリティ）。
- 推定式: AR(p)-GARCH(1,1)-in-Mean。平均式に $h_t$（GARCH-M項）、$s_t, w_t, l_t$ を、分散式にも $s_t, w_t, l_t$ を外生変数として投入。AR次数は情報量規準で選択（Table 6）。
- 補助分析: 浸透率（発電量／負荷）区間別の価格分布特性（Table 5）、Granger 因果（Table 10）。

## 4. 主要結果（数値を必ず。表番号を付す）
- Table 5（浸透率別の価格分布）: 太陽光 0–7%/7–14%/14–21% で平均 43.3/36.0/28.0 €/MWh、標準偏差 12.1/9.7/9.7（浸透率上昇で平均も分散も低下）。風力 0–5%…25–55% で平均 46.1→22.9（25%超で約50%低下）、標準偏差 10.2, 10.6, 9.5, 9.5, 10.9, **14.3**、25%超で歪度 −2.17・尖度 9.0（極端な低価格の確率が上昇）。
- Tables 7–9（GARCH-M）: 平均式では太陽光・風力とも負（all hours: $s$ −3.47E−05、$w$ −4.48E−05；peak: $s$ −6.84E−05、$w$ −5.04E−05、いずれも p<0.0001）。off-peak では太陽光は非有意（−1.50E−06, p=0.64）、風力 −3.86E−05。
- 分散式: 太陽光 **−1.48E−05**（all）/ −1.48E−05（peak）/ −1.72E−05（off-peak）、風力 **+1.39E−05**（all）/ +1.95E−05（peak）/ +3.31E−05（off-peak）、負荷は負（−1.44E−05 など）。GARCH持続 $h_{t-1}$ 係数 0.552（peak）、0.278（off-peak）。GARCH-M 項はピーク時のみ5%有意。
- Table 10（Granger）: 太陽光・風力・負荷はいずれも価格を Granger cause（p=0.0000、all/peak/off-peak）。
- 解釈: 風力の分散上昇はオフピークで最も顕著（「system flexibility is even lower」）。

## 5. 著者が挙げる限界・今後の課題
- 日次集計（Phelix Day Base 等）に基づくため、時間別の相互作用は扱えない。
- Ljung-Box 検定は一部ラグで残差自己相関を棄却できず（ただしパターンは無いと主張）。
- 柔軟性（貯蔵、DR、連系、経済的出力抑制）の政策効果は議論に留まり、推定していない。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1（電源別の価格変動効果の先行研究）、第2章で「時間スケール」の論点を導入する箇所。
- 何を言うために引用するか: 「太陽光＝安定化、風力＝不安定化」という日次 GARCH の標準的結論を示し、その**変動性の定義が日次平均価格の日間条件付き分散**であることを明示する。本研究の主張（太陽光は日内スプレッド TB4h を拡大、風力は水準のみ低下し日内スプレッドを拡げない）は、この論文と**対象とする時間スケールが異なる**ため矛盾しない。むしろ「日次平均で見ると太陽光は安定化、日内形状で見るとダックカーブで不安定化」という対比を作る材料。
- 支持する点: 風力の分散効果がオフピークに集中する（Table 9）＝風力は日内の底値側に作用する。負荷が分散を下げるという「反直観的」結果は、ピーク電源が価格を安定させる Mwampashi (2021) の説明と共通。
- 対立する点: 風力は分散を上げるという結論（ただし日間分散）。
- 手法の源流: GARCH-X 系（Ketterer 2014 の拡張）。本研究の分位点回帰とは異なるが、浸透率区間別の分布記述（Table 5）は本研究の記述統計の設計に流用可能。
- 新規性チェック: Kyritsis らは日次3系列（all/peak/off-peak）の分散を別々に推定するが、**peak と off-peak の差＝日内形状**そのものは分析していない。本研究の TB4h と帯域分解がその空白を埋める。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "we show that both solar and wind power Granger cause electricity prices, that solar power generation reduces the volatility of electricity prices by scaling down the use of peak-load power plants, and that wind power generation increases the volatility of electricity prices by challenging electricity market flexibility." (Abstract, p.550)
2. "the probability of very low electricity prices increases when wind power serves more than 25% of the electricity demand. This rapid change of distributional properties during the large interval might be an indication of non-linear effects of wind power generation on electricity prices." (Sec. 3, Table 5 discussion)
3. "It is important to state that for wind power penetration higher than 25%, the mean of electricity price declines by around 50%." (Sec. 3)
4. "This effect becomes more prominent during off-peak hours, when system flexibility is even lower" (Sec. 5, discussion of Tables 7–9)
5. "It is worth mentioning that peak hours cover hours 9–20, while off-peak hours cover hours 1–8 and hours 21–24" (Sec. 3, data)
