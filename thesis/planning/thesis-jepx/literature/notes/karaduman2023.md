# Karaduman (2023) Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets
- 書誌: Ömer Karaduman, Working Paper (Stanford University), March 26, 2023 版（MIT博士論文由来。Butters et al. は "Karaduman (2021)" として引用）。DOIなし。引用時は "Karaduman (2023, working paper)" とし、公刊されていれば差し替える。
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 卸電力市場における系統用蓄電の**投資・運用の私的誘因と社会的誘因は一致するか**、再エネ投資を補完する政策は必要か。
- 新規性（§1 "Related Literature"）: "The main novelty of my approach relative to previous research on electricity markets is modeling storage-induced price effects explicitly and allowing incumbent generators to respond to resulting price changes due to entry." 先行研究の多くは蓄電を価格テイカーと仮定しており、大規模になるほど収益性を過大評価する。Butters et al. (2020) は動学最適化を扱うが「discards the price impact of utility-scale batteries」（※2024年改訂版のButtersは均衡効果を扱うので、この批判は旧版向け）。
- 技術的貢献: 供給関数均衡（SFE）は一般に計算不能・非一意（Klemperer & Meyer 1989）だが、蓄電の生産を「公的シグナル条件付きの残余需要分布への特定のショック」として扱い、蓄電なし市場で観測された需要変動への既存事業者の最適応答を反復して新均衡を求めるアルゴリズムを提案（§4.4）。

## 2. データ・市場・期間
- 豪州NEM（エネルギー・オンリー市場、容量市場なし、価格上限 AU$14,500/MWh、下限 −AU$1,000/MWh）、**南オーストラリア**（VRE約50%・ガス火力約50%、Victoria とのみ連系・700 MW）。2016年7月〜2017年12月（この期間に参入・退出なし、2018年1月にHornsdale Power Reserve (HPR) 稼働）。
- AEMO公開データ: 日次入札（48コマ×10ステップ、価格ステップは1日共通→490次元戦略）、5分発電量、需要・再エネ予測。
- 仮想蓄電: HPRの裁定用部分に合わせ **120 MWh / 30 MW（E/P=4）、往復効率85%**（HPR 2018年データから γ=0.85 と推定）。投資費用は Fu et al. (2018): E/P=8,4,2,1,0.5 で US$320, 380, 454, 601, 895/kWh、20年寿命・劣化なし（付録Bで使用コストを追加）。
- 市場規模の位置づけ: この蓄電は平均発電容量の約5%。"This result holds even for a unit that is only 5% of the average electricity production capacity."

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 市場: 多単位一様価格オークション。各日、火力は公的シグナル X（需要・再エネ予測）と私的シグナル（燃料費）を観察し前日に入札。蓄電は充電水準 Ch を状態とする無限期間の動学最適化（価値関数反復）。
- **均衡定義（Definition 4.1, §4.3）**: Markov Perfect Equilibrium。(4.4) 火力 j は σ* の下で期待日次利潤を最大化、(4.5) 蓄電の価値関数 V(X,Ch,σ*) ≥ V(X,Ch,σ′_i,σ*_{−i})、(4.6) 市場清算 D_dh = Σ_j S_jdh(p*) + a_idh（蓄電）+ a_rdh（再エネ）、(4.7) X は f_X に従う。
- 最適応答写像（§4.4）: 蓄電なし均衡 σ_{−is} から出発し、蓄電の生産分布 σ̄_i(a|X) を「更新された純需要」のシグナルとして火力の最適応答を推定し、蓄電が再最適化…と反復。
- 所有形態: 独占（利潤最大化）、負荷所有（消費者余剰最大化）、競争的（価格＝限界価値）を比較（§6.3）。再エネ倍増シナリオでは D+700 を超える分を出力抑制として扱い、蓄電が抑制電力を購入できる（§5.5）。
- **参入の扱い**: 自由参入条件は明示せず。単一の仮想ユニットの年間利潤 vs 年換算投資費用で採算を判定し、「不採算だが消費者余剰増加が費用を上回る → 過少投資」と結論。**アンシラリー・容量市場の収入は除外**。

## 4. 主要結果（数値を必ず。表番号を付す）
- **Table 2（年間・1 MWhあたり、1000 AU$）**: (1) 完全予見・価格テイカー: 収入46.66、費用25.27、利潤+21.39、994サイクル。(2) 不確実性あり・価格影響なし: 収入23.31、利潤−1.96、842サイクル（ほぼ損益分岐）。(3) +価格影響: 収入12.38、利潤−12.89、601サイクル。(4) +既存事業者の応答: 収入11.18、利潤−14.09、529サイクル。→ 完全予見の除去で収入半減、価格影響でさらに半減（"Previous methods that ignore the price effect channel overestimate the profitability of operating a storage unit by two-fold"）。既存火力はより攻撃的に入札し、蓄電利潤 −10%、消費者厚生 +10%。
- **Table 3（所有形態、年間・百万AU$）**: 独占: 収入1.34、費用3.03、利潤−1.69、市場費用Δ −1.54、消費者余剰Δ +3.25（利潤の約2倍）、CO2 −3.12千t、529サイクル。負荷所有: 収入0.59、利潤−2.44、消費者余剰 +5.45、CO2 +1.61千t、1,120サイクル。競争的: 収入1.06、利潤−1.97、消費者余剰 +3.56、820サイクル。→ 競争的蓄電市場でも負荷所有ほどの社会的成果は得られず、「価格シグナルは（蓄電に市場支配力がなくても）他社が価格を歪めるため正しい誘因ではない」。
- **Table 5（再エネ倍増）**: ベースラインでは蓄電は風力収入 −1.70、太陽光収入 −0.44百万AU$（平均価格低下が支配）。風力を35%→70%に倍増すると年間約50 GWh の抑制が発生し、蓄電の収入2.75・利潤−0.28（ほぼ採算）、消費者余剰 +6.12、風力収入 **+1.63**、抑制 −18.6 GWh。太陽光倍増（10→20%）では抑制ほぼなし（0.5 GWh）、蓄電利潤−1.38、太陽光収入 −0.78。→ **再エネと蓄電の関係は非単調**（抑制が生じるまでは代替、抑制後は補完）。
- **Table 8（容量感応度、独占）**: 120 MWh で出力 15/30/60/120 MW: 利潤 −1.37/−1.69/−1.98/−2.81。30 MW で 30/60/120/240 MWh: 利潤 −0.25/−0.69/−1.69/−3.43。小さいほど損失が小さい（収入の逓減が費用の線形性に負ける）。
- 排出: 南豪州ではディーゼルをガスで置換するため蓄電はCO2を減らす（Carson & Novan 2013 のERCOT結果と逆）。
- 政策含意: "These results argue for a capacity market to compensate a private firm for investing in storage."（§1）/ "In a capacity market, the storage operator is paid the difference between the change in consumer surplus and its revenue."（§6.3）

## 5. 著者が挙げる限界・今後の課題
- §7（原文）: "This paper suggests several future lines of research. First, the revenue of storage capacity in ancillary services and capacity markets could be considered in addition to the wholesale energy market. Second, regulations in electricity markets can be updated to allow for fair and efficient energy storage entry and participation. ... Finally, extending the model to nodal pricing would enable the determination of location-specific returns for energy storage investments in US electricity grids."
- 脚注19: 再エネ拡張で火力が退出しうるため「My results for VRE generation expansion might not be a long-run equilibrium.」
- Table 2の注釈: 不確実性の結果は情報構造のモデル化に依存しうる（付録Bで頑健性）。HPRの極端価格期間を含めると推定収入は AU$1.96M（実績 AU$2.43M）。
- 単一ユニット分析であり、フリート規模 K の関数としての利潤曲線 π(K) や自由参入均衡は導出していない。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 「価格テイカー仮定は大規模蓄電の収益を2倍過大評価する」（Table 2）を、本研究が π(K) を K の関数として推計する動機として引用。**風力主導ゾーン**（南豪州＝風力35%・太陽光10%）での蓄電経済性を扱う数少ない研究として、北海道との類似性（風力主導、単一価格ゾーン、連系線1本＝北本連系線）を強調。
  - 第7章: 完全予見→実行可能戦略で収入が半減（46.66→23.31）という結果を、本研究の capture ratio 81–83%（DA 30分値、前日確定価格のため不確実性が小さい）と対比し、なぜ日本の DA スポットでは捕捉率が高いかを説明。
  - 第8章8.3〜8.4: 「不採算だが社会的に望ましい → 過少投資 → 容量市場か一括補助で消費者余剰増分と収入の差を補償」という論理は、本研究の政策ウェッジ（容量市場 κ·P_cap、LTDA）の正当化根拠として直接引用。BTM併設の抑制回避価値は Table 5 の「風力倍増で抑制が発生すると蓄電が風力収入を増やす」と同じチャネル。
  - 第9章: 「アンシラリー・容量市場の収入を追加すべき」「ノーダル化」という今後の課題を、本研究が（容量市場を明示的に組み込む形で）部分的に埋めると位置づける。
- 支持する点: 蓄電の価格影響は市場規模の5%程度でも無視できない（北海道の1 GWは需要約3–5 GWの20–30%に相当し、影響はさらに大きい）。競争的蓄電市場でも社会最適に届かない。再エネ収入への効果は抑制の有無で符号が変わる。
- 対立・留意点: 南豪州は価格上限 AU$14,500 の energy-only 市場で価格スパイクが収入源。JEPX は価格上限（インバランス連動）・フロア0.01円で分布が圧縮されており、スパイク依存の収入構造は移植できない。Karaduman は劣化なし・20年寿命、E/P=4 を仮定。
- 手法の源流: 本研究の「価格影響を明示した裁定利潤」と「balancing 市場ゼロレント」の扱いは Karaduman の「エネルギー市場のみ」の設定に近い。ただし本研究は SFE を解かず、観測された供給曲線の傾き（価格–純負荷関係）に基づく簡略化した π(K) を使う点で Sioshansi et al. (2009) 型。
- 新規性チェック: Karaduman が既に行っていること＝風力主導・単一ゾーンで、価格影響と既存事業者の応答を含む単一蓄電ユニットの私的/社会的リターン、所有形態比較、再エネ倍増との非単調性。本研究が新たに行うこと＝フリート容量 K に対する π(K) 曲線と自由参入均衡 K* の導出、容量市場・LTDA・補助金・BTM・期待への政策ウェッジ分解、日内形状指標（TB4h）と電源別（太陽光 vs 風力）の価格形状への効果の実証。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "Results indicate ignoring storage's price impact leads to biased estimates; although privately operated storage entry is not profitable, it increases consumer surplus and reduces emissions, ownership has a significant effect on storage's impact, and storage substitutes or complements renewables under different generation mixes."
2. §1 p.4: "Previous methods that ignore the price effect channel overestimate the profitability of operating a storage unit by two-fold. ... Accounting for generators' best responses decreases the storage operator's profit by 10% and increases consumer welfare by 10%."
3. §1 p.4: "The storage-induced consumer surplus change is two times as large as the storage operator's profit, and the combined benefits are higher than the investment cost. This difference in private and social returns makes investing in storage unprofitable but socially desirable, which presents an under-investment problem. ... These results argue for a capacity market to compensate a private firm for investing in storage."
4. §6.2 p.38: "In column 2, without the price effect, storage almost breaks even, while in column 3, substantial improvements on the cost side are necessary. Failing to account for this price effect channel in energy storage profitability calculations can lead to incorrect conclusions."
5. §6.5 p.44–45: "at moderate levels of renewable power, where there is almost no curtailment for VREs as currently seen in South Australia, introducing grid-scale storage to the system reduces renewable generators' revenue. ... Storage prevents a notable portion of the curtailment, increasing the return to wind production. Additionally, higher wind generation capacity leads to higher revenue for energy storage, making entering the electricity market almost profitable for privately operated storage."
6. §7 p.46: "First, the revenue of storage capacity in ancillary services and capacity markets could be considered in addition to the wholesale energy market."
