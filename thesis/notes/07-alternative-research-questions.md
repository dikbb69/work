# angles

## summary
北海道エリアは、太陽光接続量231万kW（2024年9月末、2012年度末比約23倍）、風力79万kW（2023年3月末）、系統用蓄電池の接続申込160万kW（2022年7月末、61件）、北本連系線90万kW（新々北本増強・日本海ルートHVDC 200万kWを2030年度目途に計画中）、京極純揚水40万kW稼働という、再エネ・蓄電池・連系線制約が同時進行する「自然実験場」であり、金融工学的な均衡・オプション・ヘッジ分析の題材として極めて適合的である。JEPXスポット価格（2005年4月以降、30分48コマ、エリア別CSV無料）、ほくでんネットワークのエリア需給実績・ユニット別発電実績、EPRX需給調整市場約定結果、間接送電権約定価格など実証に必要な公開データは概ね揃う。先行研究ではKaraduman（スタンフォード、豪州データ）やAndrés-Cerezo & Fabra（RAND 2023）が蓄電池の均衡・市場構造分析を確立し、豪州では大型蓄電池がコマ間スプレッドを縮小させた実証があるが、日本・北海道を対象とした均衡分析はほぼ空白であり、元テーマの洗練版（蓄電池の自由参入均衡によるボラティリティ均衡点推定）を軸にRQ候補8件を提案する。

## key_findings
### 【RQ候補1・本命】蓄電池自由参入均衡によるボラティリティ均衡点の推定（元テーマの洗練版）
(a) RQ:「北海道エリアのJEPXスポット市場において、再エネ（太陽光・風力）導入量の増加関数として価格ボラティリティ（コマ間スプレッド・実現ボラ・スパイク頻度）はどう増大し、蓄電池の裁定収益が資本コストと一致するゼロ利潤・自由参入均衡では、再エネ導入量ごとに何MW/MWhの蓄電池が普及しボラティリティはどの水準に収束するか」。(b) 理論・手法: ビッドスタック（供給関数）に基づく構造価格モデル＋蓄電池の動的計画法（DP）による充放電最適化＋自由参入（zero-profit）条件で不動点を解く。Karaduman（Stanford GSB, 豪州NEMデータ）の均衡蓄電池モデル、Andrés-Cerezo & Fabra（RAND Journal 2023「Storing Power: Market Structure Matters」、市場支配力下では単独蓄電池は過小投資・垂直統合は過大投資）を理論的支柱とする。感度分析として競争的均衡と支配力ありの両ケースを比較。(c) データ: JEPX北海道エリアプライス（2005年4月2日以降、48コマ、CSV無料）、ほくでんNWエリア需給実績（太陽光・風力発電実績CSV）、出力制御実績、蓄電池コスト（METI定置用蓄電システム普及拡大検討会資料）。(d) 新規性: 蓄電池均衡分析は豪州・欧米が中心で、市場分断が頻発し蓄電池申込1.6GWが集中する北海道での実証は空白。「再エネ量→ボラ→蓄電池参入→ボラ低下」のフィードバックを均衡として閉じる点が単純収益シミュレーション（業界に多数存在）との差分。(e) リスク: 構造推定＋均衡計算は計算負荷が大きい→価格テイカー近似・代表日サンプリングで軽減可能。将来の再エネシナリオ（洋上風力等）の前提依存性は感度分析で対処。実現可能性は高い。(f) 貢献: 北海道の蓄電池導入目標・接続許容量の政策議論（充電制御装置による接続拡大等）へ定量的根拠を提供。
src: https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf

### 【RQ候補2】再エネ電源別（太陽光vs風力）のボラティリティ寄与の計量分解
(a) RQ:「北海道エリアプライスの日次実現ボラ・コマ間スプレッド・スパイク頻度・価格デュレーションカーブに対し、太陽光と風力の出力変動はそれぞれ異なる符号・大きさで寄与しているか」。(b) 手法: GARCH-X（再エネ出力を外生変数）、分位点回帰、レジームスイッチングモデル、スパイクにはHawkes過程（Energies 2023, 16(4):1570でJEPX価格スパイクへの適用実績あり）。金融工学のボラティリティ・ジャンプモデリングそのもの。(c) データ: JEPXエリアプライス、ほくでんNW需給実績（30分値の太陽光・風力実績・想定誤差）、気象庁アメダス。全て無料公開。(d) 新規性: 既存のJEPX研究はシステムプライスや2021年1月スパイク（平均7〜8円に対し高値220円/kWh、Rassi & Kanamura 2023 Energy Policy）が中心で、風力主導の北海道単体エリアでの電源別分解は薄い。(e) リスク: 最も低リスク（データ完備・手法標準的）だが、単体では新規性を問われうる→RQ1のボラティリティ生成関数の推定パートとして組み込むのが得策。(f) 貢献: 洋上風力5.7GW（2030年度政府目標）時代の北海道の価格リスク定量化の基礎。
src: https://www.mdpi.com/1996-1073/16/4/1570

### 【RQ候補3】蓄電池のマルチマーケット価値評価（JEPX裁定＋需給調整＋容量市場のスタッキング）
(a) RQ:「北海道エリアの系統用蓄電池のリアルオプション価値は、JEPX裁定単独と比べ、需給調整市場（EPRX 5商品）・容量市場収益を加えたマルチマーケット運用で何倍になり、2026年3月の需給調整市場制度改定（上限価格引下げ等と業界解説で報じられる）でどれだけ毀損されるか」。(b) 手法: 確率的動的計画法またはLeast-Squares Monte Carlo による切替オプション（市場間コミットの機会費用）評価、制度改定のイベントスタディ。(c) データ: JEPXエリアプライス、EPRX取引情報（エリア別・商品別約定結果を公開、2025年度の調達不足率等も公表）、OCCTO容量市場約定価格（第3回オークションでは市場分断により北海道・九州が高値）。(d) 新規性: 業界の収益シミュレーションは多いが、査読水準のオプション理論的評価＋北海道エリア実データ（一次調整力は応動の速い蓄電池が有利）での実証は新しい。(e) リスク: EPRXデータの粒度・複合約定の扱いが煩雑。制度改定詳細（上限15円・必要量1σ化）は業界ブログ由来で一次資料（EPRX取引規程）での確認が必須。(f) 貢献: 蓄電池投資のIRRと制度リスクの定量化、規制設計（価格上限）の副作用評価。
src: https://www.eprx.or.jp/information/

### 【RQ候補4】北本連系線増強の実物オプション評価と蓄電池との代替性
(a) RQ:「北海道-東北エリア間スプレッドのスプレッドオプションの束として北本連系線増強（現行90万kW→新々北本増強、さらに日本海ルートHVDC 200万kW・2030年度目途・2陣営が意思表明済み・2025年度末に広域系統整備計画決定予定）の実物オプション価値を評価すると、市場分断解消価値は投資額に見合うか、また連系線増強は域内蓄電池の裁定価値をどれだけ食うか（代替性）」。(b) 手法: 2エリア価格のOU過程・共和分モデル＋Margrabe型スプレッドオプション/モンテカルロ、実物オプション（欧州で確立した手法: 'How much should we pay for interconnecting electricity markets? A real options approach', Energy Economics）。理論値をJEPX間接送電権約定価格（北海道→東北順方向は2023年4月-2024年3月の期待値差が0.01円/kWh超で商品化対象）と突合し、'Valuation anomalies for interconnector transmission rights'（Energy Policy）の日本版検証も可能。(c) データ: JEPX北海道・東北エリアプライス、間接送電権市場データ（JEPX公表）、OCCTO広域系統整備委員会資料。(d) 新規性: 日本の連系線への実物オプション適用＋間接送電権価格との比較はほぼ空白。(e) リスク: 増強シナリオ・費用便益の前提が政策依存で変動中（2025-26年に計画確定プロセス進行中）。市場分断頻度の将来推計に予測モデルが必要。(f) 貢献: 国内最大規模のHVDC投資の意思決定と、連系線vs蓄電池という柔軟性資源選択の理論的整理。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988311001241

### 【RQ候補5】出力制御の経済損失と蓄電池による回収価値（curtailment insurance）
(a) RQ:「北海道エリアで2024年度から本格化した再エネ出力制御（OCCTOが2025年7月30日に公平性検証結果を公表、2024年度実施分は検証対象2日間）の経済損失はいくらで、FIP併設・系統用蓄電池はそのうち何%を回収でき、出力制御リスクは蓄電池投資の『保険価値』としていくらに評価されるか」。(b) 手法: 出力制御制約を組み込んだ蓄電池最適運用モデル、'Microeconomic models of electricity storage: Price forecasting, arbitrage limits, curtailment insurance'（Energy Economics 2021）の枠組み、将来シナリオはほくでんNW『2026年度出力制御見通し』（2025年12月24日METI WG資料）に準拠。(c) データ: ほくでんNW出力制御実績・見通し、需給実績、JEPX価格、FIP制度資料（エネ庁）。(d) 新規性: 九州対象の出力制御研究は多いが、風力比率が高く冬ピークの北海道での蓄電池回収価値の実証は新しい。(e) リスク: 北海道の出力制御実績はまだ日数が少なく（2024年度2日）、実績ベース分析が困難→将来見通しシナリオ・シミュレーション依存になる点が最大の弱点。(f) 貢献: FIT/FIP転換・併設蓄電池の投資判断と出力制御ルール設計への示唆。
src: https://www.occto.or.jp/assets/oshirase/shutsuryokuyokusei/2025/files/250730_kenshokekka_hokaido_kouhei.pdf

### 【RQ候補6】北海道エリアの価格スパイクリスクのヘッジ設計（先物・オプション・間接送電権のクロスヘッジ）
(a) RQ:「先物が上場されていない北海道エリアの小売・需要家は、TOCOM東エリア先物（JPX上場: 東・西・中部エリアのベース/日中ロード）＋EEX商品（日本の電力先物の約9割を扱い、2025年2月に東京・関西対象の月間平均アジアンオプションを上場）＋間接送電権を組み合わせたクロスヘッジで、スパイクリスク（2021年1月級）をどこまで削減できるか、残るベーシスリスクの価格はいくらか」。(b) 手法: ジャンプ拡散・レジームスイッチ・Hawkesによるスパイクモデル＋アジアンオプション評価、最小分散ヘッジ比率とヘッジ有効性（variance reduction）の計測。金融工学の中核領域。(c) データ: JEPX北海道・東北・東京エリアプライス、JPX/TOCOM先物価格（公表）、間接送電権約定価格（JEPX）、EEX価格（入手性要確認・有料の可能性）。(d) 新規性: 北海道のベーシスリスクを明示した電力クロスヘッジ研究は国内でほぼ皆無。北海道エリア先物上場の是非という商品設計提言につながる。(e) リスク: EEXデータが有料の場合はTOCOM＋間接送電権に限定する設計に縮小可能。先物流動性の低さが推定を歪める点に注意。(f) 貢献: 新電力の破綻リスク（2021年1月に顕在化）低減とヘッジ市場育成策。
src: https://www.jpx.co.jp/derivatives/products/energy/electricity-futures/index.html

### 【RQ候補7】柔軟性資源の比較: 蓄電池 vs 揚水（京極）vs 連系線のボラティリティ低減費用対効果
(a) RQ:「北海道エリアのボラティリティ低減1単位あたりの社会的費用は、系統用蓄電池・京極純揚水（20万kW×2基=40万kW稼働、1号機2014年10月・2号機2015年11月運開、3号機2032年度以降で計60万kW計画）・北本連系線増強のどれが最も低く、社会厚生（生産者+消費者余剰）を最大化する柔軟性ポートフォリオは何か」。(b) 手法: 需給・市場シミュレーション＋厚生分析。ほくでんNW公開の『ユニット別発電実績』から京極の実運用（充放電パターン）を復元し、蓄電池DPモデルと同一土俵で比較。(c) データ: ユニット別発電実績（ほくでんNW公開）、エリア需給実績、JEPX、各資源のコスト公表値。(d) 新規性: 公開ユニット別実績から揚水の実運用を復元して蓄電池と厚生比較する実証は国内で新しい。(e) リスク: スコープが広く修士2年では全資源は困難→『蓄電池vs揚水』の2資源比較に絞るのが現実的。DRはデータ入手が難しく外すべき。(f) 貢献: 均衡点分析（RQ1）を social planner 版に拡張した政策評価。
src: http://denkiyoho.hepco.co.jp/bghatsu.html

### 【RQ候補8】大型蓄電池稼働のイベントスタディ: スパイク自己励起性は減衰したか
(a) RQ:「北豊富変電所の国内最大級蓄電池240MW/720MWh（2023年3月稼働、豊田通商・GSユアサ、風力変動緩和用）や2023年以降相次ぐ系統用蓄電池の市場参入は、北海道エリアプライスのスパイク強度・自己励起性（Hawkesのbranching ratio）・コマ間スプレッドを統計的に有意に低下させたか」。(b) 手法: 時変Hawkes過程・構造変化検定＋DiD/合成コントロール（対照: 東北・九州エリア）。豪州の実証 'Large-scale battery storage, short-term market outcomes, and arbitrage'（Energy Economics 2021、大型蓄電池が日中価格スプレッドを縮小させたと報告）の日本版。(c) データ: JEPX全エリアプライス、蓄電池の運開時期（プレスリリース）、需給実績。(d) 新規性: 日本での蓄電池の市場価格因果効果の実証は空白。RQ1の均衡モデルの妥当性検証（validation）にも使える。(e) リスク: 識別が最大の難所—北豊富は風力併設でJEPX裁定運用ではない可能性が高く、JEPX参加蓄電池の特定（例: 2025年11月運用開始の札幌50MW/100MWh等）と処置時点の定義に精緻さが要る。交絡（燃料価格・需要変動）の統制も必要。(f) 貢献: 『蓄電池はボラを下げる』という政策前提の日本初級の因果証拠。
src: https://www.sciencedirect.com/science/article/abs/pii/S0140988321006241

### 事実確認: 北海道の再エネ・蓄電池・系統の主要数値
太陽光接続量は2024年9月末時点231万kW（2012年度末比約23倍、OCCTO/METI資料）、2023年3月末時点で太陽光221万kW・風力79万kW。系統用蓄電池の接続申込は2022年7月末時点で61件・160万kW（北海道の平均需要約350万kWの5割近く、日経BP）。ほくでんNWは充電制御装置活用による蓄電池接続拡大策を実施（2025年4月1日対象系統追加、2026年4月10日資料あり）。札幌市で50MW/100MWhの系統用蓄電池が2025年11月1日運用開始（大和エナジー・インフラ）。北豊富変電所240MW/720MWh（2023年3月稼働）、南早来変電所レドックスフロー15MW/60MWh実証（住友電工）。京極純揚水は40万kW稼働（60万kW計画）。洋上風力は2025年7月30日に松前沖・檜山沖が北海道初の促進区域指定、政府目標は2030年10GW案件形成・第6次エネ基2030年度5.7GW稼働、エクイノールが道西方4海域で計400万kWの浮体式を計画。
src: https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02823/?ST=msb

### 事実確認: データ入手可能性（実証可能性の根拠）
JEPXスポット市場: 2005年4月2日以降の約定価格（システムプライス＋9エリアプライス、30分48コマ）と約定量をCSVで無料公開。ほくでんネットワーク: エリア需給実績（太陽光・風力・水力等の30分実績、当年度+過去5カ年）、ユニット別発電実績、出力制御実績・見通しをCSV公開。EPRX（電力需給調整力取引所）: 需給調整市場5商品のエリア別約定結果・上限価格・必要量・調達不足率を公表（2025年度の不足率例: 一次調整力オンライン40.8%等）。JEPX間接送電権市場: 約定価格を公表、2018年10月間接オークション導入、2025年3月にJEPX・エネ庁が制度見直しとりまとめ公表、年間商品新設へ。容量市場: OCCTOが約定結果公表（第3回は市場分断で北海道・九州が高値、前年比1.7倍）。電力先物: JPX/TOCOMが東・西・中部エリアのベース/日中ロードを上場し価格公表、EEXが日本電力先物の約9割を取扱い2025年2月に月間平均オプション上場（EEXデータは入手性要確認）。
src: http://denkiyoho.hepco.co.jp/area_jukyu_download.html

### 事実確認: 理論・実証の先行研究アンカー
(1) Karaduman 'Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets'（Stanford GSB）: 豪州市場データで蓄電池の裁定と均衡効果を分析、蓄電池増加が価格変動を平準化し裁定収益が自己減衰する構造を定式化。(2) Andrés-Cerezo & Fabra 'Storing Power: Market Structure Matters'（RAND Journal of Economics 2023）: 市場構造別の蓄電池運用・投資均衡を理論化、垂直統合下で過大投資・独立支配力下で過小投資。(3) 'Large-scale battery storage, short-term market outcomes, and arbitrage'（Energy Economics 2021）: 大型蓄電池導入が日中卸価格スプレッドを縮小させた実証。(4) 'Microeconomic models of electricity storage'（Energy Economics 2021）: 裁定限界・curtailment insurance・送電線利用の微視的モデル。(5) Rassi & Kanamura（Energy Policy 2023）: JEPXの2021年1月スパイク（平均7-8円/kWhに対し高値220円/kWh）を入札カーブの構造モデルで分析。(6) Hawkes過程によるJEPXスパイクモデル（Energies 2023, 16(4):1570）。(7) 実物オプションによる連系線評価（Energy Economics 2012ほか）。これらの交点＝『日本・北海道・エリア単位の蓄電池均衡実証』が空白領域。
src: https://onlinelibrary.wiley.com/doi/abs/10.1111/1756-2171.12429

### 事実確認: 北本連系線・市場分断
北本連系線は連系容量が小さく市場分断が頻発し、北海道エリアは全国価格より高値傾向（夜間で数円、昼間は10円程度高いことも珍しくない、日経エネルギーNext）。2019年5月OCCTO資料以降増強が議論され、日経（2021年5月）は送電容量3割増強を報道。さらに2022年7月に経産省が日本海ルート200万kW海底HVDC（北海道-秋田-新潟、約800km、国内最大規模）の計画策定に着手し2030年度運用開始目標、2つのコンソーシアムが事業実施を意思表明、2025年度末を目途に広域系統整備計画決定予定。間接送電権では北海道→東北順方向の期待値差（2023年4月-2024年3月）が0.01円/kWh超と算定され商品化対象になった。
src: https://enehub.jp/news/%E5%8C%97%E6%B5%B7%E9%81%93%E6%9C%AC%E5%B7%9E%E9%96%93%E3%81%AE%E6%B5%B7%E5%BA%95hvdc%E8%A8%AD%E5%82%992%E9%99%A3%E5%96%B6%E3%81%8C%E6%95%B4%E5%82%99%E3%81%AE%E6%84%8F%E6%80%9D%E8%A1%A8%E6%98%8E/

## thesis_implications
第一に、軸に据えるべきはRQ1（蓄電池の自由参入均衡によるボラティリティ均衡点推定）であり、RQ2（ボラ生成関数の計量推定）を第1章の実証、RQ8（イベントスタディ）をモデル検証に組み込む「1+2構成」が修士2年で最も現実的かつ金融工学として一貫する。理論はKaraduman・Andrés-Cerezo & Fabraという確立された枠組みに接ぎ木でき、指導教員への説明可能性も高い。第二に、実証可能性は高い: JEPXエリアプライス（2005年〜無料CSV）、ほくでんNWの再エネ実績・ユニット別発電実績、EPRX約定結果、間接送電権価格まで公開データで完結する。ただしJEPXサイトは自動取得を拒否するため手動DLが必要で、EEX先物データのみ入手性に不確実性がある。第三に、均衡の定義は「蓄電池裁定収益＝資本コストの自由参入均衡」を主定義、「社会厚生最大化」（RQ7）を比較ベンチマークとする二層構成にすると、私的均衡と社会最適の乖離（＝政策介入の根拠）が論文の結論として立つ。第四に、北海道固有の交絡に注意が必要: 北本連系線増強（新々北本・日本海HVDC 2GW、2025年度末に整備計画決定見込み）と洋上風力促進区域指定（2025年7月に松前沖・檜山沖）が分析期間中に前提を変えるため、連系線容量を外生シナリオ変数としてモデルに明示すべきで、これはRQ4（実物オプション）を発展章として取り込む余地にもなる。第五に、落とし穴として (1) 北豊富240MW/720MWhは風力変動緩和用でJEPX裁定運用ではない可能性が高く「蓄電池=裁定プレイヤー」と一括りにできない、(2) 北海道の出力制御実績はまだ2日程度でRQ5は実績ベースでは成立しにくい、(3) 2026年需給調整市場改定の詳細は業界ブログ情報でありEPRX一次資料での確認が必須、の3点を研究計画書に明記しておくと審査での指摘を先回りできる。

## sources
- JEPX スポット市場 市場情報（約定価格・約定量CSV公開） | https://www.jepx.jp/electricpower/market-data/spot/ | 2005年4月2日以降のエリアプライス48コマをCSV無料公開。サイトは自動取得を403で拒否するためブラウザでの手動DLが必要
- ほくでんネットワーク 過去の系統の需給に関する情報ダウンロード | http://denkiyoho.hepco.co.jp/area_jukyu_download.html | 北海道エリアの太陽光・風力等30分実績CSV
- ほくでんネットワーク ユニット別発電実績データ | http://denkiyoho.hepco.co.jp/bghatsu.html | 京極揚水等の実運用復元に利用可能
- 日経BP: 北海道で「系統用蓄電池」の申込が1.6GW、接続に負担金も | https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02823/?ST=msb | 2022年7月末61件・160万kW
- 資源エネルギー庁: 系統用蓄電池の迅速な系統連系に向けて（2025年3月17日） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/002_02_00.pdf | 
- ほくでんネットワーク: 充電制御装置を活用した系統用蓄電池の接続（2025年対象系統追加） | https://www.hepco.co.jp/network/info/info2025/1252764_2061.html | 
- OCCTO: 北海道エリア出力抑制の公平性検証結果（2024年度実施分、2025年7月30日） | https://www.occto.or.jp/assets/oshirase/shutsuryokuyokusei/2025/files/250730_kenshokekka_hokaido_kouhei.pdf | 
- 北海道電力ネットワーク: 2026年度出力制御見通し（2025年12月24日 METI WG資料） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/006_s01_01.pdf | 
- 豊田通商: 北海道道北 北豊富変電所 240MW/720MWh蓄電池竣工（2023年5月） | https://www.toyota-tsusho.com/press/detail/230516_006236.html | 
- 北海道電力 京極発電所（純揚水20万kW×3計画） | https://www.hepco.co.jp/energy/water_power/kyogoku_ps.html | 
- エネハブ: 北海道〜本州間（日本海ルート）海底HVDC 2GW、2陣営が意思表明 | https://enehub.jp/news/%E5%8C%97%E6%B5%B7%E9%81%93%E6%9C%AC%E5%B7%9E%E9%96%93%E3%81%AE%E6%B5%B7%E5%BA%95hvdc%E8%A8%AD%E5%82%992%E9%99%A3%E5%96%B6%E3%81%8C%E6%95%B4%E5%82%99%E3%81%AE%E6%84%8F%E6%80%9D%E8%A1%A8%E6%98%8E/ | 
- JEPX・資源エネルギー庁: 間接送電権の制度・在り方等に関する検討会とりまとめ（2025年3月） | https://www.jepx.jp/company/conference/pdf/TRCF20250326.pdf | 北海道→東北順方向の商品化根拠を含む
- EPRX 電力需給調整力取引所 取引情報 | https://www.eprx.or.jp/information/ | 需給調整市場5商品のエリア別約定結果・不足率を公表
- JPX 電力先物 商品概要 | https://www.jpx.co.jp/derivatives/products/energy/electricity-futures/index.html | 東・西・中部エリアのベース/日中ロード上場。北海道エリアは非上場
- EEX Japanese Power Market | https://www.eex.com/en/markets/power/japanese-power-market | 日本電力先物の約9割を取扱。2025年2月に月間平均オプション上場
- Karaduman: Economics of Grid-Scale Energy Storage in Wholesale Electricity Markets（Stanford GSB） | https://gsb-faculty.stanford.edu/omer-karaduman/files/2022/09/Economics-of-Grid-Scale-Energy-Storage.pdf | 蓄電池均衡モデルの中核先行研究（PDF直接取得は403、検索経由で要旨確認）
- Andrés-Cerezo & Fabra: Storing Power: Market Structure Matters（RAND Journal of Economics 2023） | https://onlinelibrary.wiley.com/doi/abs/10.1111/1756-2171.12429 | 
- Large-scale battery storage, short-term market outcomes, and arbitrage（Energy Economics 2021） | https://www.sciencedirect.com/science/article/abs/pii/S0140988321006241 | 大型蓄電池が日中スプレッドを縮小させた実証
- Microeconomic models of electricity storage: Price forecasting, arbitrage limits, curtailment insurance（Energy Economics 2021） | https://www.sciencedirect.com/science/article/abs/pii/S0140988321002899 | 
- Rassi & Kanamura: Electricity price spike formation and LNG prices effect under gross bidding scheme in JEPX（Energy Policy 2023） | https://www.sciencedirect.com/science/article/abs/pii/S0301421523001374 | 2021年1月スパイク（高値220円/kWh）の構造モデル分析
- A Hawkes Model Approach to Modeling Price Spikes in the Japanese Electricity Market（Energies 2023, 16(4):1570） | https://www.mdpi.com/1996-1073/16/4/1570 | 
- How much should we pay for interconnecting electricity markets? A real options approach（Energy Economics） | https://www.sciencedirect.com/science/article/abs/pii/S0140988311001241 | 
- 北海道 松前町: 松前沖洋上風力の促進区域指定（2025年7月30日） | https://www.town.matsumae.hokkaido.jp/hotnews/detail/00002775.html | 
- 日経エネルギーNext: 北海道の電力市場価格がおかしい | https://project.nikkeibp.co.jp/energy/atcl/feature/15/031400070/042700054/ | 北海道エリアの恒常的高値・市場分断の解説
- ScienceX: 蓄電池の3つの収益源 — JEPX・需給調整市場・容量市場のスタッキング | https://www.scix.co.jp/column-revenue | 業界コラム（2024年JEPX日次高低差平均約20円/kWh等は一次資料未確認）