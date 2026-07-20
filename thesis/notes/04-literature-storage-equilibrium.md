# lit_storage

## summary
蓄電池と電力市場均衡の先行研究を調査し、理論的支柱となる13本を特定した。系譜は(1)価格受容者の裁定価値推定（Sioshansi et al. 2009）と最適運用の確率的動的計画法（Jiang & Powell 2015）、(2)蓄電池自身の価格平準化が裁定収益を侵食するカニバリゼーションの理論・実証（Lamp & Samano 2022、Karaduman 2021、CAISO・豪州NEMの収益急減データ）、(3)社会的最適容量＝長期競争均衡を示す理論（Schmalensee 2022、Junge et al. 2022、Korpås & Botterud 2020）、(4)再エネ＋蓄電池の共進化均衡（Butters et al. 2025 Econometrica）、(5)Cournot型市場支配力分析（Andrés-Cerezo & Fabra 2023、Huang et al. 2021）に整理できる。修論の「再エネ増→ボラティリティ増、蓄電池増→ボラティリティ減の均衡点」という着想は、自由参入ゼロ利潤条件で貯蔵量を内生化するこれら文献の枠組みで定式化可能である。

## key_findings
### ①裁定価値の古典: Sioshansi, Denholm, Jenkin & Weiss (2009) Energy Economics 31(2)「Estimating the value of electricity storage in PJM: Arbitrage and some welfare effects」
プレイヤー: 価格受容者(price-taker)の独立貯蔵事業者。意思決定: PJMの2002〜2007年の時間別価格に対する充放電最適化（完全予見）。均衡概念: 部分均衡・価格外生。主要結果: 裁定価値は往復効率・立地・燃料構成に依存。大規模貯蔵は昼夜価格差を平準化して自らの裁定価値を減少させる一方、消費者コスト低減など外部的な厚生利得を生む——カニバリゼーション研究の出発点。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988308001631

### ②所有構造と厚生: Sioshansi (2010) The Energy Journal 31(2)「Welfare Impacts of Electricity Storage and the Implications of Ownership Structure」
貯蔵の所有者が独立事業者・発電事業者・需要家（小売）のいずれかで運用インセンティブと厚生効果が変わることを理論的に分析。貯蔵導入は消費者余剰と生産者余剰を再分配し、所有構造によっては社会厚生を最大化しない運用が選ばれることを示した。市場支配力下では貯蔵が厚生を悪化させ得る点は同著者の後続研究（When energy storage reduces social welfare, Energy Economics 2014）でも展開。
src: https://journals.sagepub.com/doi/10.5547/ISSN0195-6574-EJ-Vol31-No2-7

### ③確率的動的計画法による最適運用: Jiang & Powell (2015) INFORMS Journal on Computing 27(3), pp.525-543「Optimal Hour-Ahead Bidding in the Real-Time Electricity Market with Battery Storage Using Approximate Dynamic Programming」
プレイヤー: NYISOリアルタイム市場に入札する単一蓄電池事業者。意思決定: 価格不確実性下の1時間前入札＋充放電を動的計画法(DP)で定式化し、価値関数の単調性を利用した収束保証付き近似動的計画法(ADP)で解く。価格分布の知識を要しない分布フリー版も提案し、NYISO実価格データで有効性を実証。最適運用系（SDP/ADP/モデル予測制御）の代表論文。
src: https://pubsonline.informs.org/doi/10.1287/ijoc.2015.0640

### ④カニバリゼーションの実証(CAISO): Lamp & Samano (2022) Energy Economics 107「Large-scale battery storage, short-term market outcomes, and arbitrage」
カリフォルニアCAISOの2018〜2019年の系統用蓄電池の充放電パターンを実証分析。蓄電池の挙動は裁定最大化の最適解と部分的にしか整合せず（特定時間帯のみ価格に反応）、2013〜2017年の蓄電池導入が日中の卸価格スプレッド平均を既に低下させ、現行市場条件が蓄電池の収益性を制約していることを示した。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988321006241

### ⑤動学的構造均衡モデル(豪州): Karaduman (2021) MIT CEEPR WP 2021-03 / Stanford GSB WP「Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets」
プレイヤー: 蓄電池事業者＋既存発電事業者。南オーストラリア市場2017年データで、蓄電池の価格インパクトと発電側の最適応答を組み込んだ動学的構造均衡モデルを構築。主要結果: 平均日次容量のわずか5%の蓄電池でも均衡効果が重要で、価格効果を無視する従来手法は貯蔵の収益性を約2倍過大評価。発電側の応答を考慮すると貯蔵の利潤は10%減、消費者厚生は10%増。蓄電池は既存事業者の市場支配力を緩和。
src: https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf

### ⑥再エネ＋蓄電池の共進化・長期均衡の最重要論文: Butters, Dorsey & Gowrisankaran (2025) Econometrica 93(3), pp.891-927「Soaking Up the Sun: Battery Investment, Renewable Energy, and Market Equilibrium」(NBER WP 29133)
プレイヤー: 自由参入する蓄電池投資家＋再エネ・既存電源。意思決定: 動学的な充放電運用と参入投資。均衡概念: 蓄電池の価格インパクトを内生化した市場均衡（自由参入ゼロ利潤）。主要結果(カリフォルニア): 再エネ比率50%到達で最初の貯蔵ユニットは2024年までに無補助で損益分岐。均衡効果が決定的で、最初の5,000MWhの貯蔵は卸価格を5.6%下げるが、25,000→50,000MWhへの増設は2.6%しか下げない（収益逓減）。均衡効果ゆえ補助・義務化なしでは2030年まで蓄電池普及はほぼ進まない。修論の「均衡点の普及量推定」に最も近い枠組み。
src: https://onlinelibrary.wiley.com/doi/abs/10.3982/ECTA20411

### ⑦長期競争均衡＝費用最小化の理論: Schmalensee (2022) The Energy Journal 43(2), pp.1-16「Competitive Energy Storage and the Duck Curve」
モデル: Boiteux-Turvey型の平和的(peak-load pricing)電力システムに太陽光のある昼と無い夜が交互に訪れる設定で、発電と貯蔵への投資を期待費用最小化。均衡概念: 長期競争均衡。主要結果: エネルギー価格に上限が無ければ、全ての期待費用最小点は長期競争均衡であり、長期均衡での貯蔵容量は発電容量所与のもとで期待システム費用を最小化する——「厚生最適な貯蔵容量＝競争均衡の貯蔵容量」を示す理論的支柱。
src: https://journals.sagepub.com/doi/abs/10.5547/01956574.43.2.rsch

### ⑧効率的システムでの貯蔵投資: Junge, Mallapragada & Schmalensee (2022) The Energy Journal 43(6)「Energy Storage Investment and Operation in Efficient Electric Power Systems」(MIT CEEPR)
費用効率的（社会最適）な電力システムにおいて裁定を行う貯蔵の投資・運用条件を導出。主要結果: 社会最適において採用される全ての貯蔵技術はちょうど損益分岐（ゼロ超過利潤）となり、社会最適と競争均衡が一致するため、市場メカニズムに貯蔵投資を委ねることの理論的正当化を与える。自由参入均衡での貯蔵投資量導出の直接の参照点。
src: https://ceepr.mit.edu/energy-storage-investment-and-operation-in-efficient-electric-power-systems/

### ⑨VRE＋貯蔵のみの市場の最適性条件: Korpås & Botterud (2020) MIT CEEPR WP 2020-05「Optimality Conditions and Cost Recovery in Electricity Markets with VRE and Energy Storage」および Tarel, Korpås & Botterud (2024) Energy Systems (DOI: 10.1007/s12667-024-00654-y)「Long-term equilibrium in electricity markets with renewables and energy storage only」
モデル: VREと貯蔵のみの系統をネット負荷持続曲線で解析的に最小費用最適化し、最適容量を導く均衡条件を導出。主要結果: 貯蔵の充放電・出力抑制・負荷遮断の各期間に応じた価格構造（貯蔵エネルギーの価値と固定投資費用に基づく価格帯）がVREと貯蔵双方の費用回収と整合。限界費用ゼロ電源主体の市場でも固定費ベースの均衡価格形成が成立するという、従来の火力中心理論と対照的な結果。北海道のような再エネ主導系統の長期均衡分析に直接適用可能。
src: https://link.springer.com/article/10.1007/s12667-024-00654-y

### ⑩市場構造と貯蔵(理論の決定版): Andrés-Cerezo & Fabra (2023) The RAND Journal of Economics 54(1), pp.3-53「Storing power: market structure matters」
プレイヤー: 貯蔵事業者と発電事業者（それぞれ競争的か独占的か、垂直統合かの複数市場構造）。意思決定: 貯蔵の運用と投資。均衡概念: 各市場構造下の均衡を解析的に特徴付け。主要結果: 市場支配力は(i)貯蔵設備の非効率な運用（動学的生産非効率）と(ii)投資インセンティブの歪みの2経路で効率を低下させ、消費者・総厚生にとって最悪の帰結は貯蔵と発電の垂直統合の場合。貯蔵の市場支配力分析の理論的基盤。
src: https://onlinelibrary.wiley.com/doi/10.1111/1756-2171.12429

### ⑪Cournot貯蔵ゲーム: Huang, Xu & Courcoubetis (2021) IEEE Transactions on Network Science and Engineering 8, pp.1789-1801「Strategic Storage Operation in Wholesale Electricity Markets: A Networked Cournot Game Analysis」
プレイヤー: 利潤最大化する複数の商業貯蔵事業者（Cournot競争）＋経済負荷配分を行う社会計画者。均衡概念: ネットワーク上のCournot均衡（存在と一意性を証明、均衡を導く凸最適化問題を構成）。主要結果: 均衡での社会厚生は貯蔵なしの場合を常に下回らず、対称な貯蔵事業者数が無限大に近づくと最大社会厚生に収束——貯蔵の市場支配力は参入増で解消されることを示す。
src: https://ieeexplore.ieee.org/document/9406390

### ⑫不完全競争下の貯蔵投資(二層モデル): Virasjoki, Siddiqui, Oliveira & Salo (2020) Energy Economics 88 (DOI: 10.1016/j.eneco.2020.104716)「Utility-scale energy storage in an imperfectly competitive power sector」
モデル: 二層(bi-level)最適化。下位層は完全競争またはCournot寡占の市場運用、上位層は厚生最大化者または利潤最大化の独立商業事業者による貯蔵投資。主要結果: 貯蔵の投資規模・立地・収益性には投資家の目的関数よりも市場の競争度が大きく影響し、完全競争下の厚生最大化者が最大容量を投資。いずれのケースでも消費者の利得が投資家の利得を上回る。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988320300554

### ⑬豪州NEMの実証: Rangarajan, Foley & Trück (2023) Energy Economics 120 (DOI: 10.1016/j.eneco.2023.106601)「Assessing the impact of battery storage on Australian electricity markets」
豪州2州への系統用蓄電池（Hornsdale Power Reserve 150MW等）の段階的導入を利用した差の差(DiD)分析。蓄電池導入がFCAS（周波数制御補助サービス）費用を有意に低下させ、効果は蓄電容量に比例し、短周期市場（レギュレーション・6秒）で最も顕著（高コストな火力の代替）と実証。豪州の価格・サービス市場への蓄電池効果の査読付き実証として引用価値が高い。
src: https://www.sciencedirect.com/science/article/pii/S0140988323000993

### 補足: カニバリゼーションの最新市場実績（CAISO・NEM・JEPX）
CAISO: 蓄電池の年間純収益は2023年約78 USD/kW→2024年約53 USD/kW（約32%減）、2025年9月末時点で2023年比約50%減。4時間Top-Bottomスプレッドは2025年11月に前年比約30%減の約3 USD/kW（Modo Energy, 2025年11月・2026年1月レポート）。豪州NEM: スプレッドは2024年後半のピーク200〜280 AUD/MWhから2026年初に90〜105 AUD/MWhへ低下し、全本土4地域で同方向（WattClarity 2026年7月「Is the NEM's battery fleet starting to compete with itself?」）。JEPX: 日次平均スプレッドは2020年頃の約4円/kWhから2024年に約20円/kWhへ拡大しており、日本は「スプレッド拡大局面＝カニバリゼーション前夜」にある点が研究の新規性となる。
src: https://wattclarity.com.au/articles/2026/07/is-the-nems-battery-fleet-starting-to-compete-with-itself/

## thesis_implications
修士論文の理論枠組みとして、(1)短期均衡＝価格インパクトを内生化した蓄電池の充放電最適化（Karaduman 2021の動学的構造均衡、またはHuang et al. 2021のCournot均衡）、(2)長期均衡＝自由参入ゼロ利潤条件で蓄電池容量を内生決定（Butters et al. 2025、Junge et al. 2022、Schmalensee 2022）という二層構造が標準であり、修論もこの構成を踏襲するのが安全である。特にButters et al. (2025, Econometrica)は「再エネ比率上昇→スプレッド拡大→蓄電池参入→スプレッド縮小→参入停止」というまさに研究テーマの均衡メカニズムをカリフォルニアで定量化しており、最重要のベンチマークとなる。理論面では「社会最適容量＝競争均衡容量で貯蔵はちょうど損益分岐」（Junge et al. 2022）が均衡点の定義を与えるため、北海道エリアプライスのスプレッド・ボラティリティを再エネ導入量と蓄電池容量の関数として推定し、蓄電池の年間裁定収益＝年換算固定費となる容量を「自由参入均衡量」として解けばよい。実証面では、CAISO（2023→2025年に収益約50%減）と豪州NEM（2024→2026年にスプレッド半減以下）でカニバリゼーションが既に顕在化している一方、JEPXはスプレッド拡大局面（2020年約4円→2024年約20円/kWh）にあり北海道の系統用蓄電池は導入初期であるため、「日本・北海道での均衡普及量の事前推定」は明確な研究ギャップである。留意点として、豪州の実証（Rangarajan et al. 2023）は裁定よりも調整力（FCAS）市場への効果が先行して大きいことを示しており、日本でも需給調整市場・容量市場収益を無視すると均衡容量を過小推定する恐れがある点、および市場支配力の有無（Andrés-Cerezo & Fabra 2023）で均衡が大きく変わる点を、モデルの仮定（完全競争を仮定するか）として明示的に議論すべきである。

## sources
- Sioshansi, Denholm, Jenkin & Weiss (2009) Estimating the value of electricity storage in PJM, Energy Economics 31(2) | https://www.sciencedirect.com/science/article/abs/pii/S0140988308001631 | 裁定価値推定とカニバリゼーション（価格平準化による自己収益侵食）の古典
- Sioshansi (2010) Welfare Impacts of Electricity Storage and the Implications of Ownership Structure, The Energy Journal 31(2) | https://journals.sagepub.com/doi/10.5547/ISSN0195-6574-EJ-Vol31-No2-7 | 貯蔵の所有構造別の厚生分析
- Jiang & Powell (2015) Optimal Hour-Ahead Bidding in the Real-Time Electricity Market with Battery Storage Using ADP, INFORMS Journal on Computing 27(3) | https://pubsonline.informs.org/doi/10.1287/ijoc.2015.0640 | 確率的動的計画法による最適運用・入札の代表論文（arXiv:1402.3575）
- Lamp & Samano (2022) Large-scale battery storage, short-term market outcomes, and arbitrage, Energy Economics 107 | https://www.sciencedirect.com/science/article/abs/pii/S0140988321006241 | CAISOでのスプレッド縮小の実証
- Karaduman (2021) Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets (MIT CEEPR / Stanford GSB WP) | https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf | 南豪州の動学的構造均衡モデル。CEEPR紹介: https://ceepr.mit.edu/the-economics-of-grid-scale-energy-storage/
- Butters, Dorsey & Gowrisankaran (2025) Soaking Up the Sun, Econometrica 93(3), pp.891-927 | https://onlinelibrary.wiley.com/doi/abs/10.3982/ECTA20411 | 再エネ×蓄電池の市場均衡・自由参入投資。NBER WP 29133: https://www.nber.org/papers/w29133
- Schmalensee (2022) Competitive Energy Storage and the Duck Curve, The Energy Journal 43(2) | https://journals.sagepub.com/doi/abs/10.5547/01956574.43.2.rsch | 長期競争均衡＝期待費用最小の理論。WP版: https://ceepr.mit.edu/wp-content/uploads/2021/09/2020-012.pdf
- Junge, Mallapragada & Schmalensee (2022) Energy Storage Investment and Operation in Efficient Electric Power Systems, The Energy Journal 43(6) | https://doi.org/10.5547/01956574.43.6.cjun | 社会最適で貯蔵はゼロ超過利潤（損益分岐）。CEEPR: https://ceepr.mit.edu/energy-storage-investment-and-operation-in-efficient-electric-power-systems/
- Tarel, Korpås & Botterud (2024) Long-term equilibrium in electricity markets with renewables and energy storage only, Energy Systems | https://link.springer.com/article/10.1007/s12667-024-00654-y | VRE＋貯蔵のみの長期均衡と費用回収。先行WP(Korpås & Botterud 2020): https://ceepr.mit.edu/optimality-conditions-and-cost-recovery-in-electricity-markets-with-vre-and-energy-storage/
- Andrés-Cerezo & Fabra (2023) Storing power: market structure matters, RAND Journal of Economics 54(1), pp.3-53 | https://onlinelibrary.wiley.com/doi/10.1111/1756-2171.12429 | 貯蔵・発電の市場支配力と垂直統合の均衡分析
- Huang, Xu & Courcoubetis (2021) Strategic Storage Operation in Wholesale Electricity Markets: A Networked Cournot Game Analysis, IEEE TNSE 8 | https://ieeexplore.ieee.org/document/9406390 | Cournot貯蔵均衡の存在・一意性と厚生収束
- Virasjoki, Siddiqui, Oliveira & Salo (2020) Utility-scale energy storage in an imperfectly competitive power sector, Energy Economics 88 | https://www.sciencedirect.com/science/article/abs/pii/S0140988320300554 | 二層モデル（完全競争/Cournot×厚生最大化/商業投資家）。arXiv:1908.03167
- Rangarajan, Foley & Trück (2023) Assessing the impact of battery storage on Australian electricity markets, Energy Economics 120 | https://www.sciencedirect.com/science/article/pii/S0140988323000993 | 豪州NEMのDiD実証（Hornsdale等）。SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4291677
- Modo Energy (2025-2026) CAISO Battery Benchmark レポート群 | https://modoenergy.com/research/en/caiso-battery-benchmark-november-2025-energy-arbitrage-weather-la-nina-el-nino | CAISO蓄電池収益の実績データ（2023年78→2024年53 USD/kW等）。2025Q3総括: https://modoenergy.com/research/en/battery-caiso-bess-resource-adequacy-capacity-energy-arbitrage-2025-q3
- WattClarity (2026年7月) Is the NEM's battery fleet starting to compete with itself? | https://wattclarity.com.au/articles/2026/07/is-the-nems-battery-fleet-starting-to-compete-with-itself/ | 豪州NEMのスプレッド縮小（2024年後半200-280→2026年初90-105 AUD/MWh）
- CAISO (2025年5月29日) 2024 Special Report on Battery Storage | https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf | 系統運用者による公式の蓄電池市場レポート
- Borderless法律事務所 (2025) Battery Energy Storage System Business in Japan — Investment & Legal Guide | https://www.borderless.law/en/topics/battery_investment_guide_2025/ | JEPXスプレッド（2020年約4円→2024年約20円/kWh）等の日本市場データ