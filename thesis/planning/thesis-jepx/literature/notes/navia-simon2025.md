# Navia Simon & Diaz Anadon (2025) Power price stability and the insurance value of renewable technologies
- 書誌: *Nature Energy* 10, 329–341 (March 2025). DOI 10.1038/s41560-025-01704-0（published online 28 Jan 2025）
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 再エネは電力価格を安定化させるのか不安定化させるのか。マクロ経済的に重要な**年次**価格の変動性と化石燃料価格への感応度に対して、2030年の欧州 NECP 目標容量はどう効くか。
- 著者の主張する貢献: (1) ENTSO-E ERAA 2022 の NECP 2030 容量を GenX でディスパッチし、需要・燃料価格・気象の歴史的変動を Monte Carlo（300反復）で再現。(2) **β-感応度**（ガス価格 €1 上昇に対する年平均電力価格の上昇額）という新指標を提案し、「ガスが限界電源となる時間数」より適切と主張。(3) 燃料・気象・需要のショックを同時に扱う。(4) 価格安定化の厚生利得＝再エネの**保険価値**を定式化し、市場が内部化しないため政策で考慮すべきと主張。

## 2. データ・市場・期間
- 対象: 欧州各国（EU＋英国・スイス）、国単位ゾーン（小国は地域集約）、2024年と2030年（NECP）の容量構成。
- 需要・燃料: 1990–2021 年の年次系列を HP フィルタ（λ=100）で除トレンドし、残差の分散共分散を再現する多変量正規乱数（300反復）。CO2 価格は政策変数として固定。
- 気象: ERAA の1987–2016 年の気象年から一様乱数で選択（風力・太陽光の設備利用率、水力流入、時間別需要プロファイル）。
- ディスパッチ: GenX v0.3.0（ETS 費用を化石燃料の変動費に追加）、8,760時間、水力・揚水・蓄電池も最適運用。1反復約0.5時間、11容量構成×300反復。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 被説明変数: 各反復の**年平均**電力価格（国別）。
- 変動性の指標: 年平均価格の標準偏差、p85・p95 分位点、および β-感応度＝$\partial E[\bar P_{elec}]/\partial \bar P_{gas}$（€/MWh per €/MWh）。
- シナリオ: 2024、2030 NECP、および 2030 の風力・太陽光容量を −20%〜+60%（10%刻み）に変えた構成（Table 3）。
- 保険価値: 社会厚生関数の下で、消費の安定化から生じる厚生利得として定義（Lucas 流）。

## 4. 主要結果（数値を必ず。表番号を付す）
- Table 1: 2030 NECP で欧州平均価格は **26%低下**。ドイツ 134→89 €/MWh（−34%）、標準偏差 22→21（−4%）。オランダ −41%、ベルギー −36%。
- Table 2: β-感応度は欧州平均 **1.4→1.0**。ドイツ 1.3→0.9、デンマーク 1.4→0.9、スウェーデン・ノルウェー 0.9→−0.1、イタリア 2.1→2.0（ほぼ不変）。p95 ドイツ 175→128 €/MWh（−27%）。
- Table 3（2030 の VRE 容量を目標比で変化）: 欧州で β<0.5 には **+30%**、β<0.25 には **+50〜60%** の追加導入が必要。ドイツ: −20%で1.42、目標で0.91、+30%で0.44、+60%で0.26。イタリアは+60%でも1.61。
- 鍵: 低い β を実現する主因は「VRE がほぼゼロの変動費で価格を決める時間数の増加」。
- 結論での留保: 追加導入は**カニバリゼーション**を招き、日前市場収入だけでは民間投資の採算性が疑わしい → 市場改革（PPA/CfD）と保険価値の政策的考慮。

## 5. 著者が挙げる限界・今後の課題
- 国単位ゾーンで国内送電制約を無視。
- CO2 価格固定。
- 年次頻度の変動性のみ（時間別価格の特性は「蓄電池運用等に重要」と述べるに留まる）。
- 保険価値の定量化は割引率・リスク回避度の較正に依存。貯蔵・連系線の追加が β を下げる代替手段になりうることは Methods で試算するに留まる。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1（再エネと価格変動の時間スケール：年次帯域では再エネは**安定化**要因）、第5章（政策ウェッジの理論的根拠：市場が内部化しない価値）、第6章（政策含意）。
- 何を言うために引用するか: (i) 再エネの変動性効果は時間スケールに依存し、**7日超・年次帯域**では燃料価格リスクの遮断を通じて変動性を下げる。本研究の帯域分解（日内／1–7日／7日超）の「7日超」帯域の解釈を補強。(ii) 「市場が内部化しない価値（保険価値）」という枠組みは、本研究の**政策ウェッジ**（容量市場・長期脱炭素オークション・補助金・BTM 抑制回避価値・期待）の理論的な相似形。(iii) 「再エネ追加はカニバリゼーションで市場収入を毀損し、純市場では必要容量に届かない」という結論は、本研究の蓄電池 π(K) の急速なカニバリゼーションと K*=0 の結果と同型。
- 支持する点: 純市場均衡では社会的に望ましい容量に到達しない、という帰結。
- 対立する点: 直接の対立なし。ただし対象は年次の燃料リスクであり、本研究の日内スプレッドとは別帯域であることを明記。
- 手法の源流: GenX ディスパッチ＋Monte Carlo は本研究の価格過程シミュレーションとは異なる（本研究は縮約的な価格過程）。
- 新規性チェック: Navia Simon らは再エネ側の保険価値を扱い、蓄電池の参入均衡やスプレッドのカニバリゼーションは扱わない。本研究は蓄電池を主体として、市場価値と政策ウェッジを分解する点で異なる。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "We propose a β-sensitivity metric, defined as the projected increase in the average annual price of electricity when the price of natural gas increases by 1 euro. We show that annual power prices spikes would be more moderate because the β-sensitivity would fall from 1.4 euros to 1 euro." (Abstract, p.329)
2. "Because market mechanisms do not internalize this value, we argue that it should be explicitly considered in energy policy decisions." (Abstract, p.329)
3. "further increasing the capacity of renewable technologies, while lowering the sensitivity and improving the stability of electricity prices, results in cannibalization conditions that would be associated with low market revenue for renewable producers in day-ahead markets. Hence, the financial viability of private investments based strictly on this market for reaching the capacity levels required to stabilize electricity prices is doubtful." (Conclusions and discussion)
4. "one key factor to achieve a low β-sensitivity stands out: a higher number of hours where variable renewables set the price of electricity at their own, almost zero, variable costs." (Results, Table 3 discussion)
5. "Reducing the β-sensitivity to less than 0.5 euros would require deploying 30% more renewables by 2030, and going below 0.25 euros would require 60% additional deployment versus the currently envisioned target." (Conclusions and discussion)
