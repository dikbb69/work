# Mwampashi, Nikitopoulos, Konstandatos & Rai (2021) Wind generation and the dynamics of electricity prices in Australia
- 書誌: *Energy Economics* 103, 105547. DOI 10.1016/j.eneco.2021.105547
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 世界で最も速く VRE が拡大した豪州 NEM で、風力発電は電力価格の**水準**と**ボラティリティ**にどう影響したか。水力・連系線・炭素価格（CPM）・COVID-19 の役割は。
- 著者の主張する貢献: (1) NEM で価格変動性を長期（2011–2020）に検証した初の研究。(2) 連系線と水力を統制変数として明示的に扱う初の試み。(3) 風力浸透率（風力／消費）の水準別・時変的な効果をローリング推定。
- 主結論: 風力1 GWh/日増で日次価格は最大1.3 AUD/MWh 低下、ボラティリティは最大2%上昇（SA）。ただし高浸透州（TAS）では低下。連系線が水準・変動性を左右。

## 2. データ・市場・期間
- 市場: 豪州 NEM の4州 NSW, SA, VIC, TAS（QLD は風力が少なく除外）。
- 期間・頻度: 2011年1月1日〜2020年12月31日、5分/30分値から集計した**日次**データ。
- 変数: 卸価格、電力消費（グリッド需要＝屋根置き PV 控除後）、風力発電量、水力発電量、連系線潮流（輸出入）、ガス価格（STTM アデレード・シドニー、DWGM ビクトリア）。
- 背景: SA の風力浸透率は約53%（2018年に SA 電力需要の約40%を風力が供給）、NSW・VIC は15%以下。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- ARX-eGARCHX: 平均式は AR(p)＋外生変数、分散式は $\log\sigma_t^2=\omega+\sum\beta_j\log\sigma_{t-j}^2+\sum\alpha_i|z_{t-i}|+\gamma_i z_{t-i}+\delta' X_{t-1}$（非対称性を許容、分散の正値制約が不要）。
- 変動性の定義: 日次価格の条件付き分散（eGARCH の潜在ボラティリティ）。頑健性として実現分散（RV）・日中レンジ（IR）を用いた realGARCH（Hansen et al. 2012）。
- 風力浸透率 $wp_t$＝風力／消費で再推定（Model J）、3年ローリング窓（4.5節）、CPM 期間ダミー（2012/7〜2014/7）、COVID ダミー。
- 外れ値処理: 3×MAD で上限約150 AUD/MWh を除く頑健性（Appendix C）。

## 4. 主要結果（数値を必ず。表番号を付す）
- Tables 2–5（平均式）: 風力1 GWh/日増の価格効果 **SA −1.3、TAS −0.6、VIC −0.5、NSW −0.4 AUD/MWh**（全て有意）。消費・ガス価格・水力は正。
- Tables 2–5（分散式）: 風力1 GWh 増でボラティリティ **SA +2%、VIC +1%、TAS −3%**、NSW は非有意。消費1 GWh 増で SA +6%（VIC の約3倍、NSW の約6倍）。ガス1 AUD/GJ 増で SA +11〜14%。
- 浸透率（Model J、4.4節）: 浸透率1%増で価格 NSW −0.9、VIC −0.7、SA −0.5、TAS −0.3 AUD/MWh。TAS はボラティリティ −1%。
- Table 8（浸透率別分布）: SA では平均価格 110.7（<5%）→43.6 AUD/MWh（≥50%）、標準偏差 118.5→29.5。「明確なパターンは無いが高浸透で標準偏差は相対的に低い」。
- Fig. 5（3年ローリング）: 2017年半ば以降、NSW・VIC では浸透率上昇がボラティリティを**低下**。SA では浸透率約50%まで低下しその後反転（火力が系統に残る間は価格を平滑化するため）。
- Table 6（CPM 期間）: SA では風力1 GWh 増でボラティリティ −2%、浸透率1%増で −1%。石炭州（NSW, VIC）で価格上昇が大きく、再エネ州（SA, TAS）で小さい。
- Table 7（COVID）: 需要減で価格低下、ボラティリティへの影響は限定的。

## 5. 著者が挙げる限界・今後の課題
- 揚水と流れ込み式を合算した水力（脚注3）。屋根置き PV は市場外のため分析対象外（脚注7）。
- 日次集計のため日内ダイナミクスは扱わない（realGARCH は補助）。
- 石炭火力の早期退出が将来の価格ショックを増幅しうると指摘するが、モデル化はしていない。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1（風力主導市場の実証、北海道の最近接事例として）、第2章2.3（連系線・柔軟性資源の役割）、第4章の結果解釈（風力浸透率と変動性の非単調性）。
- 何を言うために引用するか: (i) 風力主導市場（SA 浸透率約53%）でも、風力のボラティリティ効果は小さく（+2%）、高浸透州では負に転じる。(ii) 浸透率別の分布（Table 8）で標準偏差が高浸透ほど低い。(iii) 連系線が価格水準・変動性を規定する＝北海道の北本連系（0.9 GW、増強後 1.2 GW）の議論の参照点。
- 支持する点: 風力の変動性効果は小さく非単調（Wozabal／Schöniger-Morawetz の U 字と整合）。「火力が系統に残る間は平滑化する」という機構は、北海道で石炭・LNG 火力が限界電源である現状と対応。
- 対立する点: SA・VIC で風力がボラティリティを上げる（ただし日間の条件付き分散）。
- 手法の源流: eGARCH-X は本研究の手法ではないが、ローリング推定・浸透率区分別記述統計は本研究の設計と共通。
- 新規性チェック: Mwampashi らは日次ボラティリティを扱い、日内形状（NEM の5分値から集計しているにもかかわらず）や蓄電池の裁定価値は扱わない。本研究は日内スプレッドと蓄電池参入均衡を対象とする点で異なる。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "We find that a 1 GWh increase in wind generation decreases daily prices up to 1.3 AUD/MWh and typically increases price volatility up to 2%." (Abstract)
2. "Nevertheless, we see no clear pattern in the standard deviation. Its magnitude, however, is relatively lower with higher levels of wind penetration." (Sec. 4.4, Table 8)
3. "the increase in wind penetration lowers price volatility to a specific level (in this case, around annual wind penetration of 50%) and then regresses to the previous phenomena. One explanation is that incumbent thermal plants remain online up to a certain penetration rate (50% to 60%), thus smoothing out the price volatility from the higher wind output" (Sec. 4.5)
4. "We find that increasing wind penetration in states with an annual wind share of around or less than 15%, i.e., NSW and VIC, tends to result in price swings, which are currently biased below zero. States with high wind penetration, i.e., SA and TAS, tend to exhibit a marginal reduction in price volatility." (Sec. 4.5)
5. "The cross-border interconnectors play a significant role in determining price levels and volatility dynamics. This underscores the important role of strategic provisions and investment in the connectivity within the NEM" (Abstract)
