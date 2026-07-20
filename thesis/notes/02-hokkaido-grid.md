# hokkaido

## summary
北海道エリアは冬季ピーク型（厳寒想定567万kW、夏は約400万kW）の小規模系統で、2025年3月末の接続量は太陽光236万kW・風力136万kW。需給制約による出力制御は2022年5月8日に初実施され、洋上風力は2025年7月に松前沖・檜山沖が道内初の促進区域に指定された。本州との連系は北本90万kWのみで、2027年度末に120万kWへ増強予定。蓄電池は南早来レドックスフロー電池（17MW/51MWh）や北豊富240MW/720MWhが稼働し、系統用蓄電池の接続申込が急増中。2018年に日本初のブラックアウト（約295万戸停電）を経験し、JEPXでは北本連系設備の市場分断率が2023年度8.5%と高く、北海道は他エリアと異なる独自の価格動態を持つことが学術研究でも確認されている。

## key_findings
## thesis_implications
（1）研究対象としての妥当性: 北海道は「再エネ急増（太陽光236万kW・風力136万kW、洋上風力で今後数百万kW級の追加見通し）」「出力制御の開始（2022年5月～）」「系統用蓄電池の大量導入（南早来51MWh、北豊富720MWh、接続申込160万kW超）」「連系線制約（北本90万kW、分断率8.5%）」が同時進行する日本で唯一のエリアであり、再エネ由来ボラティリティと蓄電池によるボラティリティ低減の均衡点を分析する対象として最適である。先行研究（Frontiers 2021等）でも北海道のみ他エリアと独立した価格動態を持つことが示されており、北海道エリアプライスを単一市場として扱うモデル化が正当化できる。（2）モデル設計への示唆: 冬季ピーク型需要（厳寒H1想定567万kW）と春秋の軽負荷期（平均需要約350万kW）の季節性、北本連系線120万kW化（2027年度末）による分断緩和、泊3号機再稼働（2027年目標、207万kW級のベースロード復帰）、ラピダス・DCによる需要急増（2030年代半ば693万kW試算）は、いずれも均衡点を大きく動かす構造変化であり、シナリオ分析の軸として組み込むべきである。（3）データ入手可能性: JEPXエリアプライス30分値、北海道電力NWの需給実績（太陽光・風力実績含む30分値）、OCCTO需要想定・出力制御検証資料が公開されており、ボラティリティ推定（GARCH等）とメリットオーダー効果の実証、蓄電池アービトラージの収益関数の構築に必要なデータは揃う。（4）留意点: 年間需要量の正確な値、出力制御率%の見通し値、北海道の0.01円コマ数統計は今回のWeb検索では数値を直接確認できなかったため、HEPCO需給実績CSV・METI次世代電力系統WG資料PDF・JEPX約定データから直接取得する必要がある。また蓄電池のボラティリティ低減効果は、北海道では系統用蓄電池が「調整力・出力変動緩和」目的（北豊富等）と「市場アービトラージ」目的（近年の接続申込急増分）で性格が異なる点をモデル上区別することが望ましい。

## sources
- 北海道電力ネットワーク「2025年度出力制御見通しについて」（2025年1月23日、経産省 次世代電力系統WG参考資料1-1） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/001_s01_01.pdf | 太陽光236万kW・風力136万kW（2025年3月末接続量）、30日等出力制御枠（太陽光117万kW・風力36万kW）
- 北海道電力ネットワーク「2026年度出力制御見通しについて」（2025年12月24日） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/006_s01_01.pdf | 最新の出力制御見通し。制御率%の具体値はPDF本体の直接参照が必要（プロキシ制限で本文未取得）
- 北海道電力ネットワーク「2023年度冬季の電力需給見通しについて」 | https://www.hepco.co.jp/network/info/2023/1252263_1968.html | 1月最大電力562万kW・供給力591万kW・予備率5.2%、厳寒H1想定567万kW
- 北海道エリアの需給実績（ほくでんネットワーク） | https://www.hepco.co.jp/network/con_service/public_document/supply_demand_results/index.html | エリア需要・太陽光/風力発電実績の30分値データ（論文の実証分析用データソース）
- 日経BPメガソーラービジネス「北海道エリアで初の出力制御、5月8日に実施」 | https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02523/?ST=msb | 2022年5月8日初実施、制御量18.8万kW、対象1,916カ所
- OCCTO「北海道エリアの出力抑制における公平性の検証結果（2024年度実施分）」（2025年7月30日） | https://www.occto.or.jp/assets/oshirase/shutsuryokuyokusei/2025/files/250730_kenshokekka_hokaido_kouhei.pdf | 2024年度の需給制約による出力抑制は計2日間
- 北海道新聞「送電容量不足で初の出力制御 十勝の太陽光発電対象 北電ネット、11月に」 | https://www.hokkaido-np.co.jp/article/1227003/ | ローカル系統送電容量不足による初のノンファーム出力制御
- ウインドジャーナル「洋上風力第4ラウンド 北海道松前沖と檜山沖の2海域を促進区域に指定」 | https://windjournal.jp/124361/ | 2025年7月30日、道内初の促進区域指定
- ウインドジャーナル「風の宝庫が本格始動！北海道沖5海域」 | https://windjournal.jp/117610/ | 有望区域5海域の想定出力規模（石狩市沖114万kW等）
- 北海道庁「一般海域での洋上風力発電の有望区域選定について」 | https://www.pref.hokkaido.lg.jp/kz/gxs/152605.html | 石狩市沖・岩宇南後志沖・島牧沖・檜山沖・松前沖（いずれも着床式）
- DeepWind「北海道石狩市沖洋上風力発電プロジェクト概要」 | https://deepwind.jp/en/projects-en/hokkaido-ishikari-offshore-wind/ | 石狩湾新港洋上風力（8MW×14基＝11.2万kW、2024年1月1日運転開始）
- OCCTO「北海道本州間連系設備に係る広域系統整備計画」（2024年2月21日変更） | https://www.occto.or.jp/assets/kouikikeitou/seibikeikaku/kitahon/files/hokkaidohonsyu_20240221.pdf | 新々北本30万kW増強（計120万kW）、2027年度末運転開始
- ほくでんネットワーク「新北本連系設備」 | https://www.hepco.co.jp/network/stable_supply/efforts/north_reinforcement/index.html | 既設60万kW＋新北本30万kW＝90万kW（2019年3月～）
- EnergyShift「新々北本連系線とは その増強による便益と費用負担」 | https://energy-shift.com/news/95df02b3-9c52-4832-8e12-89ab0d1d4f95 | 総額約480億円・工期5年程度
- 住友電工プレスリリース「北斗今別直流幹線増強（新々北本連系線）向けHVDCケーブル受注」（2024年4月） | https://sumitomoelectric.com/jp/press/2024/04/prs043 | 新々北本の工事進捗の裏付け
- OCCTO 第90回広域系統整備委員会「北海道本州間連系設備の第1極更新について」（2025年6月25日） | https://www.occto.or.jp/assets/iinkai/kouikikeitouseibi/2025/files/seibi_90_02_01.pdf | 既設北本第1極の更新検討
- 住友電工プレスリリース「北海道電力ネットワーク向けレドックスフロー電池設備が竣工」（2022年4月） | https://sumitomoelectric.com/jp/press/2022/04/prs036 | 南早来変電所 1.7万kW×3時間＝5.1万kWh
- 豊田通商プレスリリース「北海道道北地域における送電・蓄電事業の設備が竣工」（2023年5月16日） | https://www.toyota-tsusho.com/press/detail/230516_006236.html | 北豊富変電所240MW/720MWh（国内最大）、送電線78km、総事業費約1,050億円、2023年4月12日商業運転開始
- 北海道電力ネットワーク「系統用蓄電池の接続に係る課題と対策について」（2022年9月14日、系統WG資料2） | https://www.meti.go.jp/shingikai/enecho/shoene_shinene/shin_energy/keito_wg/pdf/041_02_00.pdf | 蓄電池接続申込61件・160万kW（2022年7月末）、平均需要約350万kW
- 北海道電力ネットワーク「系統用蓄電池導入拡大について～北海道系統の特徴および再エネ導入状況・課題～」（2024年1月） | https://www.hepco.co.jp/network/renewable_energy/efforts/opinion_inquiry/pdf/govt_battery_expansion.pdf | 北海道系統の特徴と蓄電池導入課題の包括資料（論文の背景整理に有用）
- 北海道電力ネットワーク「出力変動緩和対策に関する技術要件の撤廃について」 | https://www.hepco.co.jp/network/info/info2023/1252089_1969.html | 風力の蓄電池併設要件を2023年7月1日撤廃
- ITmedia スマートジャパン「北海道の風力発電、蓄電池の併設が不要に――2023年7月」 | https://www.itmedia.co.jp/smartjapan/articles/2207/12/news062.html | 北海道ルール撤廃の経緯
- OCCTO「平成30年北海道胆振東部地震に伴う大規模停電に関する検証委員会 最終報告（概要）」（2018年12月19日） | https://www.occto.or.jp/assets/soukaihoka/hyougiinkai/2018/files/hyougiinkai_2018_2_houkoku_1.pdf | ブラックアウトの原因分析と再発防止策
- 北海道電力「北海道胆振東部地震対応検証委員会 最終報告」（2018年12月21日） | https://www.hepco.co.jp/info/info2018/__icsFiles/afieldfile/2019/11/26/181221.pdf | 約295万戸停電、苫東厚真N-3＋送電線事故の複合要因
- 電気新聞「北海道電力、泊3に設置変更許可／27年再稼働へ前進」 | https://www.denkishimbun.com/sp/390798 | 2025年7月30日設置変更許可、2027年早期再稼働目標
- 日本経済新聞「ラピダス新工場など、原発なしでは電力ギリギリの北海道」 | https://www.nikkei.com/article/DGXZQOUC080Z80Y5A400C2000000/ | 2030年代半ば需要693万kW・供給力694万kW試算
- JEPX・資源エネルギー庁「間接送電権の制度・在り方等に関する検討会とりまとめ」（2025年3月） | https://www.jepx.jp/company/conference/pdf/TRCF20250326.pdf | 北本の分断・エリア間値差（北海道→東北の期待値差＞0.01円/kWh）
- JEPX スポット市場データ | https://www.jepx.jp/electricpower/market-data/spot/ | エリアプライス30分値の一次データ（実証分析用）
- JEPX Information（State of Market Split / Yearly Average等の非公式集計サイト） | https://www.jepx.info/en/spot_splitted | 市場分断状況・年度平均価格の集計（プロキシ制限で本文未取得）
- JPX先物・オプションレポート2021年7月号「2020年度冬季におけるJEPXスポット市場価格高騰の要因分析」（草薙真一） | https://www.jpx.co.jp/derivatives/market-report/futures-options-report/archives/nlsgeu00000595vz-att/rerk2107.pdf | 2021年1月13日の1日平均154.57円/kWh等の高騰分析
- Frontiers in Sustainability "The Impact of Variable Renewable Energy Penetration on Wholesale Electricity Prices in Japan Between FY 2016 and 2019" | https://www.frontiersin.org/journals/sustainability/articles/10.3389/frsus.2021.770045/full | 風力のメリットオーダー効果が高価格分位で大きいのは北海道のみ、北海道は独自の価格動態との分析
- 日経xTECH「北海道の電力市場価格がおかしい」 | https://xtech.nikkei.com/dm/atcl/feature/15/031400070/042700054/ | 北海道エリアプライスの特異性を扱った記事
- OCCTO「全国及び供給区域ごとの需要想定（2025年度）」（2025年1月22日） | https://www.occto.or.jp/assets/juyousoutei/2024/files/250122_juyousoutei.pdf | 北海道エリアの年間需要量・将来需要想定の一次資料