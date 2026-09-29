# Butters, Dorsey & Gowrisankaran (2021/2024) Soaking Up the Sun: Battery Investment, Renewable Energy, and Market Equilibrium
- 書誌: NBER Working Paper No. 29133, August 2021, Revised September 2024. http://www.nber.org/papers/w29133 （JEL L94, Q40, Q48, Q55）。フォルダ内表記は「2025」だが本文の版は2024年9月改訂版。引用時は "Butters, Dorsey and Gowrisankaran (2024, NBER WP 29133, rev.)" とし、公刊版が出ていれば差し替える。
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 三つの目的（Introduction, p.1–2）: (1) 大規模蓄電池の**均衡効果**（価格の山谷の平準化）と再エネ浸透との補完性を、火力のランプ費用・市場支配力を組み込んだモデルで推定する枠組みを構築、(2) 蓄電池大量導入で誰が得をし誰が損をするかを計算、(3) **動学的競争均衡の参入（採用）モデル**で、補助金・義務化なしに蓄電池がどれだけ入るかを評価。
- 先行研究との差別化（p.5）: Sioshansi et al. (2009) 等の完全予見・有限期間の工学的枠組みを「競争的蓄電市場における大規模蓄電の均衡効果」へ拡張。Zhao et al. (2022) の完全情報Cournot投資モデルとは、需給の確率性・供給関係の凸性・ランプ費用・動学的採用モデルの点で異なる。Karaduman (2021) との整合を脚注6で明記: "Our results that there are large equilibrium effects of storage entry, that storage entry was not profitable during our sample period but would nonetheless raise consumer surplus, and that storage entry lowers solar and wind revenue are all consistent with Karaduman (2021)."
- 三つの識別仮定（p.4–5）: (i) 推定した純負荷・供給関係は構造的で、反実仮想の大規模蓄電下でも不変（火力の退出・入札変化を排除）、(ii) DAM–RTM価格差は火力の利用不能（蓄電が緩和できる）を反映し共通コストショックではない、(iii) 採用モデルはサンプル内の再エネ比率が高い週を将来の高浸透の代理とする。

## 2. データ・市場・期間
- CAISO、SP-15ハブのRTM価格（5分値）と DAM価格、2016–19年（2015年は訓練サンプル）。総負荷、太陽光・風力発電、火力供給（CEMS）等。RTMに焦点を当てる理由: "We focus on storage operators' final bids in the RTM, where the greatest arbitrage value lies" (§2.3)。
- 蓄電池パラメータ: 4時間・往復効率85%（Cole & Frazier 2019 に従う。"Four hours is the average duration of batteries operating in California in 2019"）、Xu et al. (2016) の劣化モデル。資本費予測は NREL（Cole & Frazier 2019）の25文献の集計。
- 市場構造: 2018年の蓄電池市場HHI=1,347.9（非集中）。アンシラリー市場は無視し「追加的に入る蓄電池はエネルギー裁定で稼ぐ」と位置づけ（2021年CAISO新設容量の80%超が裁定用途、EIA 2022a）。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- **運用モデル（§3）**: 5分刻みの確率的動学計画。純負荷の日内周期・系列相関、火力の非線形供給関係（市場支配力・ランプ費用＝過去の発電が現在の限界費用を下げる）、往復ロス、サイクル劣化を含む。価格テイカーの蓄電池群の均衡は「単一エージェントのBellman方程式」に書き換えて解く（競争的フリートの誘因は積分形の流列利得に対応）。火力が限界費用入札なら社会計画者問題と一致。
- **採用モデル（§5.1）**: 無限個の事前同質な潜在参入者、各々 k=1 の小容量（価格テイカー）。毎年、資本費 c_y（Markov 過程・期待的に低下）を観察して「今投資するか待つか」の**最適停止問題**（Bellman (9)）。年次営業利益 π(y, K*) は運用モデルから (10) 式でマイクロファウンド: π(y,K*) = Σ_t E[p_t(1{q*>0} q* υ + 1{q*<0} q*/υ)]。**均衡条件**（p.32）: "In an equilibrium with price-taking potential battery operators, the marginal operator sets per-unit adoption cost equal to the marginal operating revenue net of the opportunity cost of adopting." 対応する単一エージェント問題 (11): W(c,y,K)=max_{K*≥K} −E[Σ_t ∫_0^{Z_t} P_{d(t)}(ζ,·)dζ] − c(K*−K) + β∫W(c′,y+1,δ(y,K*)K*)dG(c′|c,y)。
- 利益関数の推定（Table 2）: 週次の流列リターンを ln(K*)、再エネ比率、交差項、統制変数（夕方ピーク負荷、ガス価格、水年指数、週固定効果）に回帰。ln(K*) の主効果は負（非有意）、再エネ比率は正で有意、交差項は負で有意。劣化率は再エネ比率30%・1ユニットで年2.8%。
- 市場構造（§6）: 独占・複占（Stackelberg交互手番、K=10,000 MWh のみ）を比較。

## 4. 主要結果（数値を必ず。表番号を付す）
- **損益分岐（§4.2, Fig.3）**: 劣化はストレージ価値を平均27%減らす。劣化考慮後、最初の1ユニットが黒字になるのは再エネ比率>50.2%かつ資本費<$264/kWh（2024年に実現見込み）。2019年に黒字化するには資本費が40%低い必要。不確実性下の実行可能戦略は完全予見価値の**70%**を達成（Fig.3b）。
- **均衡価格効果（§4.3, Table A.4）**: 最初の5,000 MWh で夕方価格 −10.3%（$54.25→$48.67/MWh）、平均価格 −5.6%（$35.92→$33.90）。25,000→50,000 MWh では夕方 −7.3%（$39.76→$36.84）、平均 −2.6%（$31.02→$30.20）。火力のピーク時刻が19時→20時へ、谷が11時→12時へ移動（ランプ費用の重要性）。
- **収益の偏り（Table A.5）**: 1,000 MWh フリートで、収益の大半は上位1%の5分区間から（$38,400/MWh vs 残り99%で $17,293/MWh）。100→10,000 MWh で上位区間の単位収益が約28%減。
- **共食い（Fig.5, 再エネ比率50%時）**: 単位価値 $280/kWh（10 MWh）→ $230/kWh（10,000 MWh）→ $140/kWh（50,000 MWh）。「10,000 MWh でさえ2024年時点で補助なしでは裁定業者として採算が取れない」。
- **分配効果（Table 1, 年平均, 百万ドル）**: K=1,000 MWh: 蓄電利益 14.46（$14.46M/GWh-yr）、LSE支出 −123.98、火力収入 −125.55、**太陽光・風力収入 −12.88**、粗社会余剰 +13.96。K=50,000 MWh: 単位利益 4.48/GWh-yr、火力収入 −1,379、太陽光・風力 −84.39、粗社会余剰 +351.09。再エネ収入減の理由: 15–17時の価格低下が9–13時の上昇を上回る（CAISO固有で普遍的ではないと明記）。
- **採用経路（§5.3, Fig.6）**: 補助・義務なしのベースラインでは最初の設置が2026年、2030年で288 MWh、2035年で7,098 MWh。ピーク負荷+25%で2035年容量4倍、−25%で80%超減少（蓄電はピーク削減投資の代替）。RPS 60%で1,430 MWh、80%で3,650 MWh（2030年）。
- **補助金（Fig.7）**: 25%未満の補助ではほぼ採用なし。IRA相当30%で2024年に5,000 MWh超、40%で25,000 MWh。カリフォルニアの義務（5,200 MWh=1,300 MW）は30.4%の前払い補助と等価。
- **市場構造（Table 3）**: K=10,000 MWh のピーク価格: 無蓄電 $54.25、競争 $45.04、複占 $46.71、独占 $46.09。K=5,000 では競争 $33.90 vs 独占 $34.04 とほぼ同じ、K=25,000 で $31.02 vs $33.87。市場支配力の歪みは10,000 MWh を超えるまで軽微。

## 5. 著者が挙げる限界・今後の課題
結論（§7, p.45–46）で明示的に列挙されている限界は以下の**6点**（原文）:
1. "First, we hold fixed the existing dispatchable generation capacity and the associated electricity supply relationship, even though our results imply that utility-scale batteries would lower dispatchable generator revenues and hence would likely lead to retirements. Relatedly, our analysis of the impact of battery market power assumes separate ownership among dispatchable generators and the battery operator(s). We believe that modeling endogenous dispatchable generator retirement and alternative ownership structures—including the potential for load serving entities to own batteries—are useful areas for further research."
2. "Second, while we model generator ramping costs, our supply relationship for generators in the presence of ramping costs and large-scale batteries is an approximation to a complex dynamic oligopoly problem."
3. "Third, we do not model the impact of storage on grid reliability, an abstraction that interacts with the potential exit of dispatchable generators' capacity and one worthy of future research."
4. "Fourth, we assume that battery costs evolve exogenously, not allowing for battery mandates to lead to declines in production costs through learning-by-doing."
5. "Fifth, we use weekly variation in renewable energy over our 4-year sample period and extrapolate to predict the value of storage investment in a world where more renewable generation exists than we can observe within our sample."
6. "Finally, we do not attempt to solve for the optimal storage subsidy to mitigate environmental externalities, given the complex interplay between a combination of mechanisms that incentivize both renewable energy and storage."

これに加えて本文中で「モデル化していない」と述べられている事項:
- 出力抑制（脚注33）: "Our measure of generation from renewables is net of any curtailments, which we do not model explicitly. In the California market over our sample period, curtailment of solar and wind generation was relatively small. However, to the extent that batteries eliminate the need for renewable sources to curtail (by storing their energy when they would have curtailed) that is a channel that may add to the value of a battery fleet with a large presence of renewables, beyond what we find."
- §5冒頭: "our modeling framework is limited in that it does not consider dispatchable generator retirement, learning-by-doing causing battery capital cost reductions, or energy storage technologies other than lithium-ion batteries."
- 脚注48: 卸価格をコストとマークアップに分解しないため「競争的蓄電市場の参入が過剰か過少かは判定できない」。
- 継続時間は4時間に**固定**（§2.2, §3.3）で、限界として挙げてはいない。アンシラリー市場・容量市場は「追加的な蓄電池は裁定で稼ぐ」として分析対象外（§2.2）だが、これも限界としては列挙されていない。連系線・送電制約、価格下限（フロア）についての限界言及はない。

**要注意（新規性主張の検証）**: 本研究の草稿が「Butters et al. の stated limitations = curtailment, duration, interconnection, price floor, multiple markets」と書いているなら**不正確**。著者が結論で明示する限界は上の6点（火力退出の内生化、動学寡占の近似、信頼度、学習効果、外挿、最適補助金）。出力抑制は脚注33で「明示的にモデル化しない」と述べているのみ、継続時間・複数市場は仮定（限界ではない）、連系線・価格フロアは言及なし。本研究は「著者が挙げる限界を埋める」ではなく「著者の**仮定・分析対象外**（4h固定、単一市場、抑制なし、カリフォルニアの太陽光主導）を、風力主導・複数市場・価格フロア(0.01円)・連系線制約のある北海道に置き換えたときに均衡がどう変わるか」という形で差別化を書き直すべき。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2（先行研究）: 蓄電池の均衡効果・共食い（"each additional storage unit acts as an arbitrageur, smoothing price differentials across time and lowering the value of existing units"）と、自由参入（最適停止）による K* 決定の枠組みの源流として。
  - 第7章（π(K) の共食い曲線）: Fig.5 の $280→$230→$140/kWh（10 MWh→10 GWh→50 GWh）と Table 1 の単位利益 14.46→4.48 $M/GWh-yr を、本研究の「≈1 GW(4h) で spot rent 枯渇」と並べて比較。CAISO は 50 GWh でも単位利益が正で残るのに対し、北海道は市場規模（需要 ~3–5 GW）が小さく 1 GW で枯渇する、というスケールの違いを強調。
  - 第8章8.3〜8.4（政策ウェッジ）: 「補助・義務なしでは2030年まで採用がほぼゼロ」「IRA 30%補助で義務水準に到達」という結果は、本研究の「純市場均衡 K*=0、しかし契約済み ≈2.3 GW → 政策ウェッジ」と同型。Fig.7 の補助金–採用量曲線は本研究の κ·P_cap と LTDA の役割に対応。
  - 第9章（限界・拡張）: 上記6点の限界に対し、本研究が何を追加するかを正確に対応づける。
- 支持する点: (a) 均衡効果は大きく逓減的、(b) サンプル期間中は参入不採算だが消費者余剰は増加、(c) 蓄電池は再エネ収入を減らす（本研究のBTM併設価値の議論では、これと逆に「抑制回避」が併設側の私的価値になる点が北海道固有）、(d) 実行可能戦略は完全予見の70%（本研究の capture ratio 81–83% は DA 30分値ベースで、CAISO の RTM 5分値より予測しやすいので整合的）。
- 対立・相違点: 収益の大半が上位1%の5分区間（RTMスパイク）から来る構造は、北海道の JEPX スポット（DA）には当てはまらない。本研究の価値は「日内形状（TB4h）」で決まる点を対比。また蓄電池が太陽光収入を減らすのは CAISO の相関構造に依存すると著者自身が留保している。
- 手法の源流: 二層参入（政策層外生・merchant層ゼロレント）の merchant 層は、Butters の「限界的参入者が単位採用費 = 限界営業収入 − 待機オプション価値」に対応。本研究は待機オプション（Leahy/Grenadier）を期待項として扱い、静学的な自由参入条件 π_spot(K)·c + κ·P_cap − c_req = 0 に落とす（Butters のオプション価値を捨象する簡略化であることを明記する）。
- 新規性チェック: Butters が既に行っていること＝CAISO・太陽光主導・単一市場（RTM）・4h固定・価格テイカー参入の動学均衡、補助金と義務の同値化。本研究が新たに行うこと＝風力主導ゾーンでの日内形状の違い（TB4hが広がらない）に起因する π(K) の急速な枯渇、容量市場・LTDA・補助・BTM抑制回避・期待の**分解**、価格フロア（0.01円）下の裁定、連系線制約。「Butters の限界を埋める」という表現は使わず「Butters の設定（太陽光・単一市場・4h）を北海道の制度環境へ置換して均衡を再導出」と書く。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "Equilibrium effects are important: the first 5,000 MWh of storage capacity would reduce wholesale electricity prices by 5.6%, but an increase from 25,000 to 50,000 MWh would only reduce these prices by 2.6%."
2. Introduction p.1: "the equilibrium value of large-scale storage investment is limited because each additional storage unit acts as an arbitrageur, smoothing price differentials across time and lowering the value of existing units. Finally, even after capital costs reach a break-even point, companies may defer battery investments to exploit the option value of waiting for additional capital cost declines."
3. §4.3 p.27: "with a 50% renewable energy share, average battery value falls from $280/kWh to $230/kWh when aggregate capacity increases from 10 MWh to 10,000 MWh. These values fall further to $140/kWh when there is 50,000 MWh of battery storage in the market. Because of equilibrium effects, storage fleets of even 10,000 MWh would not be profitable as arbitrageurs by 2024 without subsidies or unless capital costs were to fall far below current expectations."
4. §5.1 p.32: "In an equilibrium with price-taking potential battery operators, the marginal operator sets per-unit adoption cost equal to the marginal operating revenue net of the opportunity cost of adopting."
5. §7 p.45: "utility-scale battery adoption would be limited in the absence of subsidies or mandates, due to the equilibrium effects and because of the option value of waiting for future capital cost declines. We estimate that the 2022 U.S. Inflation Reduction Act storage subsidy of 30% is roughly sufficient to implement California's 2024 battery mandate of 5,200 MWh (1,300 MW)."
6. §4.4 p.29 (Table 1 の解釈): "Surprisingly, the presence of batteries reduces solar and wind generators' revenues by $13 million annually. ... These impacts are likely to occur in markets similar to CAISO, though they may not hold universally. The impact of batteries on renewables' profits will depend on the correlation between load and renewable generation across the day, among other factors."
