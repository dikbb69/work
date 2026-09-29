# Paraschiv, Erni & Pietsch (2014) The impact of renewable energies on EEX day-ahead electricity prices
- 書誌: *Energy Policy* 73, 196–210. DOI 10.1016/j.enpol.2014.05.004
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: ドイツの再エネ（風力・太陽光）は EEX 日前価格の形成にどう影響するか。特に (a) 極端価格（正スパイク・負価格）との関係、(b) 価格とファンダメンタルズの関係が**時間とともに、また時刻によって**どう変わるか。
- 著者の主張する貢献: (1) 再エネ政策（EEG, AusglMechV 等）の歴史的整理。(2) 再エネ促進が日前価格を下げメリットオーダー曲線をシフトさせたことを、**時刻別・時変係数**の基本モデルで示す。著者は「ドイツの再エネ投入が日前価格に与える影響を示した初の包括的研究」と位置づける。
- 副次的結論: 卸価格は下がったが、最終消費者価格は FIT 賦課金で上昇。

## 2. データ・市場・期間
- 市場: EEX/EPEX ドイツ Phelix 時間別日前価格。
- 期間: 2010年1月1日〜2013年2月28日（AusglMechV 発効後、TSO が太陽光データを公表し始めた時期以降）。週末・祝日は除外。
- 説明変数（Table 4）: 石炭・ガス・石油・CO2 価格、負荷（需要）、発電所利用可能量（PPA）、風力・太陽光**実績**投入量、前日同時刻価格、前日平均価格、過去の価格ボラティリティ。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 第4節（極端事象）: 3σ 超（約70 EUR/MWh 超）を正スパイク、0未満を負価格と定義し、発生時の風力投入量・曜日・時刻を集計。
- 第6節（動学的基本モデル）: 時間別価格を被説明変数とする**時変係数回帰**。係数はランダムウォークに従う潜在状態、状態空間表現＋カルマンフィルタで推定（Karakatsani & Bunn 2010 に倣う）。**時刻ごとに別モデル**を推定し、代表として3時（夜間）、12時（正午ピーク）、18時（夕方ピーク）を報告。
- 変動性はボラティリティの代理変数（過去の時間別価格の標準偏差）として説明変数側に入るのみで、被説明変数ではない。

## 4. 主要結果（数値を必ず。表番号を付す）
- 極端事象（第4節）: 正スパイク108件、負価格88件（全観測の0.71%）。正スパイクはほぼ全て平日・昼間。負価格は平日31件・週末祝日57件、**約65%が夜間**。スパイク時の平均風力投入 3,137 MWh に対し、負価格時は **15,689 MWh**（風力分布の90%分位点超）。最小値 −222 EUR/MWh。
- 時変係数（Figs. 5–6、第7節）: 風力・太陽光係数は負。風力係数は**夜間（3時）で変動が大きく**、負価格の主因。太陽光係数は時間的に安定だが**正午（12時）で大きい**。ガス係数は2011年半ば以降低下（正午の PV 投入増による代替）。石炭係数は高需要時（12・18時）で大きく安定。前日同時刻価格の係数は負（平均回帰）、前日平均価格の係数は正（学習・シグナリング）。
- 再エネ変数を加えると説明力が大幅に改善（Appendix B, Table B1–B2）。

## 5. 著者が挙げる限界・今後の課題
- 風力・PV は実績値（事後の気象データ）を用いており、アウトオブサンプルは厳密ではない（脚注3）。
- 週末・祝日を除外している（脚注4）。
- 3時刻のみ詳細報告。変動性そのものはモデル化していない。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1（電源ごとに効く時刻が異なる、という「日内形状」機構の実証）、第4章の結果解釈（風力は夜間の底値、太陽光は昼ピークに作用）。
- 何を言うために引用するか: 太陽光は正午に、風力は夜間・夕方に価格を下げる。すなわち**太陽光は日内形状（昼の谷）を作り、風力は昼夜を問わず（やや夜間寄りに）水準を下げる**。本研究の TB4h スプレッドはこの時刻別効果の要約統計量であり、蓄電池の裁定価値の源泉が「太陽光の形状効果」にある理由を説明する材料。
- 支持する点: PV の効果が正午に集中（日内形状形成）。負価格が高風力・低需要の夜間に集中（風力は底値側の水準を下げる）。
- 注意点（対立になりうる点）: ドイツでは風力が夜間に偏るため、風力が底値を下げて日内スプレッドを拡げる可能性がある。本研究は北海道の風力の日内プロファイルが平坦（空間分散）であること、および JEPX の価格下限（0.01円）で底が張り付くことを示して、この経路が北海道では弱いことを論じる必要がある。
- 手法の源流: 時刻別モデルと時変係数という発想は、本研究のローリング推定・時刻別（top-4h/bottom-4h）分析に通じる。
- 新規性チェック: Paraschiv らは時刻別の**水準**効果を示すのみで、日内スプレッドを被説明変数にせず、蓄電池価値にも結びつけない。本研究はスプレッドを直接測り、裁定価値と参入均衡に接続する。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "An analysis of electricity spot prices reveals that the introduction of renewable energies enhances extreme price changes." (Abstract, p.196)
2. "Our analysis shows that during hours with upward spikes, an hourly average of 3137 MWh wind infeed is observed, while for hours with negative prices, 15,689 MWh. We observe that the average wind infeed in hours with negative prices lies above the 90% quantile." (Sec. 4)
3. "We show that the increase in the infeed from renewable energies, wind and PV, led to a partial decrease in electricity day-ahead prices in Germany. This effect is noticeable for afternoon, evening and night hours in case of wind, and for noon peak hours, in case of PV." (Sec. 8 Conclusion)
4. "We observe a decrease of coefficient for gas after the middle of 2011. This can be explained by the increase in the PV infeed (see Fig. 6) especially at noon, when the sun is very intense." (Sec. 7)
5. "In the above state-space formulation, the regression coefficients are not unknown constants, but latent, stochastic variables that follow random walks, estimated by Kalman Filter" (Sec. 6.1)
