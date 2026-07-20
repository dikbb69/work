# methods

## summary
電力市場分析の金融工学手法を7領域で整理した。確率モデルではLucia-Schwartz(2002)の平均回帰+季節性、Cartea-Figueroa(2005)のジャンプ拡散、Janczura-Weron(2012)のレジームスイッチングが標準であり、Weron(2014)のレビューが全体地図を与える。ボラティリティはKnittel-Roberts(2005)らのGARCH/EGARCH系とCorsi(2009)由来のHAR-RV系が電力に適用済み。構造モデルはBarlow(2002)の供給曲線モデルとWagner(2014)の残余需要モデル、均衡モデルはSFE・Cournot・EPEC・スクリーニングカーブ、蓄電池運用はSDP/強化学習（価格テイカー/メーカーの区別が重要、Karaduman 2021が均衡分析の到達点）、投資評価はリアルオプション（Bakke et al. 2016）が代表。JEPXの30分コマ別エリアプライスは無料公開されており、データ面の障壁は低い。

## key_findings
### 1. 確率モデル: Lucia-Schwartz（平均回帰＋季節性）
Lucia & Schwartz (2002)「Electricity Prices and Power Derivatives: Evidence from the Nordic Power Exchange」Review of Derivatives Research, Vol.5(1), pp.5-50。決定論的季節性成分＋平均回帰（OU/Vasicek型）確率成分の1ファクター・2ファクターモデルをNord Poolに適用した電力価格モデルの基礎文献。スポット価格系列のみで推定可能（MLE）で計算負荷は低く、修論の出発点として実現可能性は高い。
src: https://www.researchgate.net/publication/2617769_Electricity_prices_and_power_derivatives_-_Evidence_from_the_Nordic_Power_Exchange

### 1. 確率モデル: Cartea-Figueroa（ジャンプ拡散）
Cartea & Figueroa (2005)「Pricing in Electricity Markets: A Mean Reverting Jump Diffusion Model with Seasonality」Applied Mathematical Finance, Vol.12(4), pp.313-335。季節性付き平均回帰ジャンプ拡散モデルで、フォワード価格の閉形式解を導出し、英国England & Walesのデータでカリブレーション。価格スパイクの表現にジャンプ項を導入した代表文献。JEPXの上限999円/kWh・下限0.01円/kWh制度下のスパイク表現に応用可能。
src: https://www.tandfonline.com/doi/abs/10.1080/13504860500117503

### 1. 確率モデル: レジームスイッチングとWeronのレビュー
Janczura & Weron (2012)「Efficient estimation of Markov regime-switching models: An application to electricity spot prices」AStA Advances in Statistical Analysis。独立レジーム型MRSモデルのEM推定を100〜1000倍高速化し、独EEXと豪NSWで検証。Weron (2014)「Electricity price forecasting: A review of the state-of-the-art」International Journal of Forecasting, Vol.30(4), pp.1030-1081は、マルチエージェント・ファンダメンタル・誘導形・統計・AIの5クラスに手法を分類した必読レビュー。レジームスイッチングはスパイク処理に有効だが予測性能の評価は文献間で結果が分かれている。
src: https://link.springer.com/article/10.1007/s10182-011-0181-2

### 2. ボラティリティモデル: GARCH/EGARCH
Knittel & Roberts (2005) が時間別電力価格にGARCH系を適用、Escribano, Peña & Villaplana らが欧州市場で GARCH/TARCH/EGARCH を比較。電力価格には逆レバレッジ効果（正のショックでボラティリティがより増大）があり、EGARCHが持続性と逆レバレッジの双方を捉えるのに優位との報告。日次・コマ別価格データのみで推定でき計算負荷は最小、修論での実現可能性は最も高い。48コマの日中構造には periodic GARCH（条件付き歪度・尖度成分付き、Energy Economics 2021掲載例）や Engle & Sokalska (2012) 型の日次×日中周期×確率的日中成分の分解が使われる。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988314000486

### 2. ボラティリティモデル: 実現ボラティリティ・HAR
Corsi (2009) のHAR-RVモデル（日・週・月の異なるホライズンのRVの線形結合で長期記憶を再現）が電力に応用されている。独墺EPEX連続時間前市場の実現ボラティリティのモデル化・予測（ResearchGate 2017掲載研究）、ロジスティック平滑遷移HAR（Energy Economics 2016, ScienceDirect S0140988315003497）、RVのボラティリティのモデル化（Energy Economics 2018, S014098831830286X）、スペイン市場の2021-2025年エネルギー危機期のRV予測（Mathematics 2026, MDPI）など。JEPXは30分コマの離散価格のため、コマ間リターンからのRV構築という設計上の工夫が論点になる。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988315003497

### 3. 構造モデル: Barlowモデル
Barlow (2002)「A diffusion model for electricity prices」Mathematical Finance, Vol.12(4), pp.287-298。非線形供給関数（Box-Cox変換の逆関数、指数関数を特殊ケースに含む）にOU過程の需要を通すことで価格を生成する、実際のオークションデータに動機づけられた最初期の構造モデル。欠点として価格スパイクの明示的表現と需要季節性の欠如が指摘されている。供給曲線の傾き（merit order の急峻さ）が価格ボラティリティを決めるという本テーマの核心メカニズムを最も単純に定式化した文献。
src: https://personal.math.ubc.ca/~barlow/preprints/dme.pdf

### 3. 構造モデル: 残余需要アプローチ
Wagner (2014)「Residual Demand Modeling and Application to Electricity Pricing」The Energy Journal, Vol.35(2)。風力・太陽光の出力を明示的にモデル化して総需要から差し引く残余需要モデルを独前日市場に適用し、再エネが低需要時にはフォワードボラティリティを増大させ、ピーク時には低減しうることを示した。Carmona, Coulon & Schwarz (2013) の multi-fuel bid stack モデル（arXiv:1205.2299）、Howison & Coulon (2009) も代表的。必要データは需要・再エネ出力・燃料価格・電源構成で、日本ではOCCTO・北海道電力ネットワーク・JEPX入札曲線から入手可能。計算負荷は中程度で、本テーマとの整合性が最も高い。
src: https://journals.sagepub.com/doi/abs/10.5547/01956574.35.2.3

### 4. 均衡モデル: SFE vs Cournot
SFEはKlemperer & Meyer (1989) が創始し、Green & Newbery (1992) が英国England & Wales市場に適用。Willems, Rumiantseva & Weigt (2009, Energy Economics)「Cournot versus Supply Functions: What does the data tell us?」は独市場に両者を同一の需要・供給仕様でカリブレーションし、価格変動の説明力はほぼ同等、ネットワーク制約等を扱える Cournot は短期分析向き、カリブレーションに頑健な SFE は長期分析向きと結論。SFEは関数微分方程式系の求解が必要で計算上の困難があり、線形SFEに限定しないと修論2年間では負荷が大きい。Cournot系は相補性問題（GAMS/PATH等）で解け実現可能性は中程度。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988308001151

### 4. 均衡モデル: MPEC/EPEC・capacity expansion・スクリーニングカーブ
戦略的入札のMPEC（Hobbs et al. の Strategic gaming analysis for electric power systems）、各社のMPECを束ねたEPEC（Ralph & Smeers, Cambridge EPRG WP0602）、容量拡張均衡のEPEC定式化（Capacity Expansion Equilibria in Liberalized Electricity Markets: An EPEC Approach）が代表。EPECは非凸・複数均衡で対角化法による検証が必要なため修論での実現可能性は低〜中。一方、スクリーニングカーブ法は負荷持続曲線ベースで従来は再エネ・蓄電池を扱えなかったが、Pratama & Mac Dowell (SSRN 3821841) が蓄電池・再エネへ拡張し、Energy Systems誌 (2024, DOI 10.1007/s12667-024-00654-y) には再エネ＋蓄電池のみの長期均衡（各技術がコストをちょうど回収するゼロ利潤参入条件）の解析研究がある。この「参入ゼロ利潤条件」は本テーマの『均衡普及量』の自然な定義を与え、計算負荷も低い。
src: https://link.springer.com/article/10.1007/s12667-024-00654-y

### 5. 蓄電池運用最適化: DP/SDP/強化学習
価格テイカー前提では、SoC（充電状態）を状態変数とする動的計画法・確率的動的計画法が標準（例: Energy誌 2018「Maximum income resulting from energy arbitrage by battery systems subject to cycle aging and price uncertainty from a dynamic programming perspective」、劣化コストとMarkov価格過程を統合）。周波数調整との複数市場同時最適化にはmulti-scale DP（IEEE Trans. 2016）。強化学習ではWang & Zhang (2018) のQ学習によるリアルタイム市場入札、DRLによるアービトラージ（arXiv:1904.12232）、エネルギー・予備力市場入札のTemporal-aware DRL（arXiv:2402.19110）など。小容量なら価格テイカー仮定が妥当だが、普及量の均衡分析には価格インパクト（プライスメーカー）の内生化が不可欠で、そこが単純DPとの本質的な違い。単体のDPは計算負荷が低く実現可能性は高い。DRLは実装・再現性の負荷が高く中程度。
src: https://www.sciencedirect.com/science/article/abs/pii/S0360544218309563

### 5.-4. 蓄電池の市場均衡効果（本テーマの直接先行研究）
Karaduman (2021)「Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets」MIT CEEPR Working Paper 2021-005。再エネ比率約5割の南オーストラリア市場（2017年データ）に動学的構造均衡モデルを適用し、蓄電池の価格インパクトと既存火力の応答を内生化。蓄電池が火力の残余需要と市場支配力を変化させ、既存事業者はより積極的に入札する（市場支配力の緩和）ことを示した。また蓄電池台数の増加とともに各蓄電池の市場支配力が減少し均衡が社会的最適に収束するという理論結果（arXiv 2024-2026の複数論文）や、蓄電池普及がスプレッドを自食（cannibalize）するという定型事実も確認され、「再エネ増→ボラティリティ増、蓄電池増→ボラティリティ減」の均衡点分析の理論的土台となる。
src: https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf

### 6. 投資評価: リアルオプション
Bakke, Fleten et al. (2016)「Investment in electric energy storage under uncertainty: a real options approach」Computational Management Science, Vol.13(3)。収益と投資コスト双方が不確実な下での蓄電池投資のオプション価値を評価し、スポット市場のみの収益では初期投資を回収できないが、需給調整（バランシング）市場収益を加えるとNPV・オプション価値とも正になり、オプション価値がNPVを上回ることを示した。住宅用PV+蓄電池の多段階複合リアルオプション（ResearchGate 2019）、風力併設蓄電池のオプション評価（2024）、幾何ブラウン運動で長期需要不確実性を表す配電網投資評価（IET Renewable Power Generation 2022）など応用が多い。カリブレーション済み価格モデル＋Longstaff-Schwartz法で実装でき、修論の補論・応用章として実現可能性は高い。
src: https://rd.springer.com/article/10.1007/s10287-016-0256-3

### 7. 日本(JEPX)対象の先行研究
確認できた学術研究: (1) Energy Policy 2023「Electricity price spike formation and LNG prices effect under gross bidding scheme in JEPX」(ScienceDirect S0301421523001374)、(2) Frontiers in Sustainability 2021のFY2016-2019メリットオーダー効果分析（OLS・分位点回帰で時間帯・価格帯・エリア別に推定、風力のMOEは増加・太陽光のMOEは減少と結論）、(3) RIETIディスカッションペーパー17-J-072「スポット価格予測に基づくJEPX先渡価格付けモデルの構築」（一般化加法モデルで季節性・曜日・トレンドを推定し残差に時系列モデル）、(4) Energies 2019のJEPX投機的取引モデル (DOI 10.3390/en12152946)。ジャンプ拡散や本格的な構造均衡モデルをJEPX北海道エリアに適用した研究は今回の検索では確認できず、研究の空白（ギャップ）である可能性が高い。
src: https://www.frontiersin.org/journals/sustainability/articles/10.3389/frsus.2021.770045/full

### 7. データ入手可能性（北海道エリア）
JEPX公式サイト（jepx.jp「市場情報＞スポット市場」）から30分48コマのエリアプライス（北海道含む9エリア）・システムプライス・約定量のCSVが無料でダウンロード可能。Japanese Electricity Market Data Hub (japanesepower.org) は2011年以降の過去データCSVを無料提供。北海道の再エネ状況: 太陽光接続量は2024年9月末時点で231万kW（2012年度末比約23倍、日経BP報道）、北海道エリア初の再エネ出力制御は2022年5月8日に実施され対象1,916カ所（太陽光1,177・風力739）・制御量18.8万kW。北海道電力ネットワークが出力制御見通し・実績を公表、2025年度出力制御見通しはMETI審議会資料（2025年1月23日）にも掲載。需要・再エネ出力はでんき予報・OCCTOから入手可能で、データ面の実現可能性は高い。
src: https://www.jepx.jp/electricpower/market-data/spot/

### 7. 手法別の修論実現可能性の総合評価（本調査に基づく評価）
【高】OU/ジャンプ拡散/レジームスイッチング（データ=価格系列のみ、MLE/EMで数分〜数時間、Pythonで実装容易）、GARCH/EGARCH・HAR-RV（同上、arch等の既存パッケージ利用可）、価格テイカーの蓄電池DP（状態空間小）、リアルオプション（LSMモンテカルロ）。【中】残余需要・merit order構造モデル（需要・再エネ・燃料価格データの整備に数カ月、ただし本テーマとの整合性最高）、Cournot均衡（相補性問題ソルバー要）、DRL（実装・チューニング負荷大、再現性の担保が課題）。【低〜中】SFE（関数微分方程式、線形SFEに限定すれば可）、MPEC/EPEC（非凸・複数均衡・対角化検証で修論2年間ではリスク大）。推奨構成は「誘導形カリブレーション→残余需要構造モデル→ゼロ利潤参入条件による均衡普及量の算定」の3段構え。

## thesis_implications
第一に、手法の組合せとして「3段構え」が現実的である。(1)北海道エリアプライス（30分48コマ、JEPX無料公開）に季節性付き平均回帰ジャンプ拡散またはレジームスイッチングモデルとEGARCH/HAR-RVをカリブレーションし、現状のボラティリティの定型事実を定量化する（金融工学専攻としての基礎技術の証明、半年程度で完了可能）。(2)Barlow-Wagner系の残余需要・merit order構造モデルで「再エネ増→残余需要の変動増と供給曲線急峻部での約定→ボラティリティ増」「蓄電池→残余需要の平準化→ボラティリティ減」のメカニズムを北海道の需要・再エネ・電源構成データで実装する。(3)「均衡点」の定義には、フルのSFE/EPECではなく、スクリーニングカーブ系の長期均衡研究(Energy Systems 2024)が用いるゼロ利潤参入条件（蓄電池のアービトラージ収益がスプレッド自食により固定費と一致する点で参入が止まる）を採用すれば、修士論文の計算負荷で「均衡普及量の推定」という目標に到達できる。第二に、Karaduman (2021)の南豪州分析が本テーマの最も近い先行研究であり、その簡略版をJEPX北海道エリアに適用する形が「新規性の主張」として明確である。今回の調査ではジャンプ拡散や構造均衡モデルをJEPX北海道エリアに適用した研究は確認できず、研究ギャップとなっている可能性が高い（ただし国内学会誌・CiNii・J-STAGEの体系的検索で再確認すべき）。第三に、リスクとして、MPEC/EPECやフルSFEは非凸性・複数均衡・計算負荷の点で2年間では危険であり、主要な貢献をそこに置くべきではない。DRLも同様に補助的位置づけが安全。第四に、北海道は太陽光231万kW（2024年9月末、2012年度末比23倍）で出力制御も始まっており、市場分断によるエリアプライスの独自変動があるため対象として適切だが、蓄電池・再エネの限界的増加が価格分布に与える影響の識別（内生性処理）と、需給調整市場・容量市場収益を無視した場合の均衡普及量の過小推定バイアスは、研究計画段階で明示的に扱うべき論点である。

## sources
- Lucia & Schwartz (2002) Electricity Prices and Power Derivatives (Review of Derivatives Research 5(1)) | https://www.researchgate.net/publication/2617769_Electricity_prices_and_power_derivatives_-_Evidence_from_the_Nordic_Power_Exchange | 平均回帰＋季節性の基礎文献
- Cartea & Figueroa (2005) A Mean Reverting Jump Diffusion Model with Seasonality (Applied Mathematical Finance 12(4)) | https://www.tandfonline.com/doi/abs/10.1080/13504860500117503 | ジャンプ拡散の代表文献
- Janczura & Weron (2012) Efficient estimation of Markov regime-switching models (AStA) | https://link.springer.com/article/10.1007/s10182-011-0181-2 | レジームスイッチングの高速推定
- Weron (2014) Electricity price forecasting: A review (IJF 30(4), 1030-1081) | https://ideas.repec.org/a/eee/intfor/v30y2014i4p1030-1081.html | 手法5分類の必読レビュー
- Energy markets volatility modelling using GARCH (Energy Economics 2014) | https://www.sciencedirect.com/science/article/abs/pii/S0140988314000486 | GARCH系電力適用のサーベイ的文献。Knittel-Roberts(2005)等を整理
- Forecasting realized volatility in electricity markets using logistic smooth transition HAR (Energy Economics 2016) | https://www.sciencedirect.com/science/article/abs/pii/S0140988315003497 | HAR-RVの電力適用
- Modeling and forecasting realized volatility in German-Austrian continuous intraday electricity prices | https://www.researchgate.net/publication/315328238_Modeling_and_forecasting_realized_volatility_in_German-Austrian_continuous_intraday_electricity_prices | 日中連続市場のRV
- Barlow (2002) A diffusion model for electricity prices (Mathematical Finance 12(4), 287-298) | https://personal.math.ubc.ca/~barlow/preprints/dme.pdf | 供給曲線ベース構造モデルの原典（著者公開PDF）
- Wagner (2014) Residual Demand Modeling and Application to Electricity Pricing (The Energy Journal 35(2)) | https://journals.sagepub.com/doi/abs/10.5547/01956574.35.2.3 | 再エネを明示した残余需要モデル
- Carmona, Coulon & Schwarz (2013) Electricity price modeling and asset valuation: a multi-fuel structural approach | https://ideas.repec.org/p/arx/papers/1205.2299.html | bid stack構造モデル
- Willems, Rumiantseva & Weigt (2009) Cournot versus Supply Functions (Energy Economics) | https://www.sciencedirect.com/science/article/abs/pii/S0140988308001151 | 独市場でのCournotとSFEの実証比較
- Holmberg & Newbery (2010) The supply function equilibrium and its policy implications (Utilities Policy) | https://www.sciencedirect.com/science/article/abs/pii/S095717871000038X | SFEのサーベイ
- Ralph & Smeers, Using EPECs to Model Bilevel Games in Restructured Electricity Markets (Cambridge EPRG WP0602) | https://www.jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp0602.pdf | EPECの定式化
- Capacity Expansion Equilibria in Liberalized Electricity Markets: An EPEC Approach | https://www.researchgate.net/publication/260508557_Capacity_Expansion_Equilibria_in_Liberalized_Electricity_Markets_An_EPEC_Approach | 容量拡張均衡のEPEC
- Pratama & Mac Dowell, Screening Curve for Valuing Power Generation and Storage Technologies (SSRN 3821841) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3821841 | スクリーニングカーブの蓄電池拡張
- Long-term equilibrium in electricity markets with renewables and energy storage only (Energy Systems, 2024) | https://link.springer.com/article/10.1007/s12667-024-00654-y | 再エネ＋蓄電池のみの長期均衡（ゼロ利潤条件）
- Karaduman (2021) Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets (MIT CEEPR WP 2021-005) | https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf | 蓄電池の動学的構造均衡分析（南豪州）。本テーマの最重要先行研究
- Maximum income from energy arbitrage by battery systems ... a dynamic programming perspective (Energy, 2018) | https://www.sciencedirect.com/science/article/abs/pii/S0360544218309563 | 劣化・価格不確実性込みのDP
- Arbitrage of Energy Storage in Electricity Markets with Deep Reinforcement Learning (arXiv:1904.12232) | https://arxiv.org/pdf/1904.12232 | DRLによる蓄電池アービトラージ
- Bakke, Fleten et al. (2016) Investment in electric energy storage under uncertainty: a real options approach (Computational Management Science 13(3)) | https://rd.springer.com/article/10.1007/s10287-016-0256-3 | 蓄電池リアルオプション評価。ROV>NPV
- The Impact of Variable Renewable Energy Penetration on Wholesale Electricity Prices in Japan FY2016-2019 (Frontiers in Sustainability, 2021) | https://www.frontiersin.org/journals/sustainability/articles/10.3389/frsus.2021.770045/full | JEPXのメリットオーダー効果実証
- Electricity price spike formation and LNG prices effect under gross bidding scheme in JEPX (Energy Policy, 2023) | https://www.sciencedirect.com/science/article/abs/pii/S0301421523001374 | JEPXスパイク形成の実証
- RIETI 17-J-072 スポット価格予測に基づくJEPX先渡価格付けモデルの構築 | https://www.rieti.go.jp/jp/publications/nts/17j072.html | 日本語のJEPX価格モデル研究
- JEPX スポット市場データ（公式） | https://www.jepx.jp/electricpower/market-data/spot/ | 30分48コマ・9エリアプライスのCSV無料公開
- Japanese Electricity Market Data Hub | https://japanesepower.org/ | 2011年以降のJEPXデータCSV無料配布
- 日経BP: 北海道エリアで初の出力制御、5月8日に実施 | https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02523/?ST=msb | 2022年5月8日実施。対象1,916カ所・18.8万kW
- 北海道電力ネットワーク 再エネ出力制御（需給バランス制約） | https://www.hepco.co.jp/network/renewable_energy/output_control/constraints/index.html | 北海道の出力制御の制度・実績情報