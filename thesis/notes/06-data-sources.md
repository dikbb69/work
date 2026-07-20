# data

## summary
修論に必要な9種のデータはほぼすべて公的機関から無料入手可能と確認した。JEPXスポット市場は年度別CSV（30分値48コマ、システム/9エリアプライス・約定総量・売買入札量）を公式サイトから無料取得できる。入札カーブは2021年2月27日以降「画像」のみ公開で、数値データは取引会員限定。OCCTO系統情報サービスで連系線潮流・空容量、北海道電力NWサイトで太陽光・風力実績を含む需給実績CSV（2016年4月以降、ただし掲載は当年度＋過去5カ年との情報あり）が取得できる。出力制御は2022年5月8日に北海道初実施で実績が月次検証・公表される。EPRX約定結果は無料公開、TOCOM/EEX先物は日次データ無料・ヒストリカルは有料。気象はアメダス・全天日射量CSVが気象庁から、MSM-GPVは京大RISHアーカイブから研究目的無償で入手可能。

## key_findings
### 1. JEPXスポット市場データ（価格・約定量・入札量）
JEPX公式サイト「電力取引＞市場情報＞スポット市場」から年度別CSV（ファイル名: spot_summary_[年度].csv）を無料・登録不要でダウンロード可能。列構成は受渡日・時刻コード（1〜48、30分単位48コマ）・売り入札量(kWh)・買い入札量(kWh)・約定総量(kWh)・システムプライス(円/kWh)・エリアプライス9エリア（北海道含む）・ブロック入札関連。JEPXの取引開始は2005年4月で2005年4月2日以降のデータが公表対象とされるが、現行サイトのダウンロードUIで確実に確認できたのは2012年度〜2024年度＋直近年度（それ以前の年度の現行サイト掲載は要確認）。時間前市場（当日市場）のCSVも同様に公開されている。なお本調査環境ではjepx.jpへの直接アクセスがブロックされたため、列構成等は複数の技術記事（Qiita・DevelopersIO）とKaggleミラーで裏付けた。
src: https://www.jepx.jp/electricpower/market-data/spot/

### 2. JEPX入札カーブ（需給曲線）
2020年12月末〜2021年1月のスポット価格高騰を受け、2021年2月27日以降、全48コマの需給曲線（システムプライスベース）を約定当日中にJEPXサイトで無料公開。ただし公開形式は「画像（グラフ）」であり、数値データ（入札カーブの価格・量の組）は約定処理後に取引会員へ通知されるのみで一般公開されていない。研究利用には(a)画像の数値化（Qiitaに Python による変換事例あり）、(b)第三者による数値化データ（japanpowerportal.jp/bidcurve、Kaggle「JEPX Day Ahead Market」データセット等）の利用、(c)JEPXへの直接依頼、のいずれかが必要。エリア別の入札カーブや個別入札データは非公開。
src: https://www.jepx.jp/electricpower/market-data/spot/bid_curves.html

### 3. OCCTO系統情報サービス（連系線潮流・空容量）
電力広域的運営推進機関（OCCTO）の「系統情報サービス」（occtonet3.occto.or.jp、一般公開画面はログイン・登録不要・無料）で、地域間連系線（北海道本州間連系設備＝北本連系を含む）の潮流実績・運用容量・空容量（長期/年間・月間/週間/翌日）をCSVダウンロード可能。潮流実績は5分平均値ベースで公表され30分値への集計利用が可能（正確な粒度は操作マニュアル 251107_keitoujouhou.pdf で要確認）。web-kohyo.occto.or.jp/kks-web-public/download に日付範囲パラメータを付けたCSV直接取得URLも存在。加えてOCCTOは業務規程第168条に基づく「供給区域別需給実績（電源種別・1時間値）」を月次公表し、年報「電力需給及び電力系統に関する概況」（例: 2024年度実績版、2025年9月10日公表）も無料PDFで入手できる。
src: https://www.occto.or.jp/institution/keitoujouhou/

### 4. 北海道電力ネットワーク「でんき予報」・エリア需給実績
北海道電力ネットワークは(a)でんき予報（denkiyoho.hepco.co.jp/area_forecast.html、当日実績CSV）、(b)過去の電力使用状況データ（area_download.html）、(c)過去の系統需給情報（area_jukyu_download.html、月別CSVのZIP）、(d)エリア需給実績・燃料種別需給実績（hepco.co.jp配下）を無料公開。需給実績データの公表は資源エネルギー庁「系統情報の公表の考え方」に基づき2016年4月1日開始で、需要・火力・水力・原子力・地熱・バイオマス・太陽光実績・風力実績・揚水・連系線潮流等を送電端で収録（太陽光・風力は出力制御後の値）。重要な注意点として、掲載は「当年度および過去5カ年」の年度別データとの記載があり、2016年度以降の全期間が常時入手できるとは限らないため早期のアーカイブ取得を推奨（掲載期間・30分値/1時間値の別は本人確認要）。
src: https://www.hepco.co.jp/network/con_service/public_document/supply_demand_results/index.html

### 5. 再エネ出力制御の実績データ（北海道）
北海道エリア初の再エネ出力制御は2022年5月8日実施（12:30〜14:00、最大18.8万kW、対象1,916件＝太陽光1,177件・風力739件）で、詳細は北海道電力NWのMETI系統WG報告資料（2022年5月24日、資料3）に記載。以後の実績は(a)でんき予報「再生可能エネルギー出力制御見通し」ページ（前日・当日の見通しと実績、過去の制御指示内容のExcel）、(b)OCCTOによる月次の出力抑制妥当性検証結果（例: 2026年5月分）と年度別の公平性検証結果（2024年度実施分は2025年7月30日公表PDF）、(c)METI系統WGの年度別出力制御見通し資料（2025年度見通し: 2025年1月23日、2026年度見通し: 2025年12月24日公表。北海道の連系量は太陽光231万kW・風力136万kW＝2024年9月時点等の数値を収録）から取得可能。すべて無料。
src: https://www.occto.or.jp/assets/oshirase/shutsuryokuyokusei/2025/files/250730_kenshokekka_hokaido_kouhei.pdf

### 6. 系統用蓄電池の接続量・申込量の統計
全国統計は資源エネルギー庁・系統WG資料（2025年9月24日、資料4「系統用蓄電池の迅速な系統連系に向けて」）に接続検討約14,300万kW・契約申込約1,800万kW（2025年6月末時点）等を収録。OCCTO「発電設備等系統アクセス業務に係る情報の取りまとめ（2024年度受付・回答分、2025年6月20日公表）」に電源種別・エリア別の接続検討/契約申込統計あり。北海道固有では、北海道電力NWのMETI系統WG資料（2022年9月14日）に接続検討61件・160万kW（2022年7月末時点、エリア平均需要約350万kWの約5割）、広域系統整備委員会第95回資料（2025年11月28日）に新規連系の課題整理あり。個別大型案件として北豊富変電所の風力併設蓄電池240MW/720MWh（2023年3月稼働、GSユアサ納入）、札幌市の系統用蓄電池50MW/100MWh（2025年11月1日運転開始、大和エナジー・インフラ）を確認。北海道電力NWは「発電等設備の受付状況・出力制御区分の内訳」ページで受付状況を継続公表。
src: https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/004_04_00.pdf

### 7. 気象データ（アメダス・全天日射量・MSM）
観測値は気象庁「過去の気象データ・ダウンロード」（data.jma.go.jp/risk/obsdl/）から地点・項目・期間を指定しCSVで無料取得可能（風向・風速・気温・日照時間等の10分値/時別値/日別値）。全天日射量の時別値は全国49地点の気象官署のみで観測され、北海道では札幌（block_no:47412）・網走等が対象（アメダス一般地点では日射量は観測されない点に注意）。予報値・格子データはメソ数値予報モデルMSM-GPV（5km格子、1日8回更新、GRIB2形式）が基本で、公式には気象業務支援センター（JMBSC）から有償提供だが、研究・教育目的なら京都大学生存圏研究所（RISH）の気象庁GPVアーカイブ（database.rish.kyoto-u.ac.jp/arch/jmadata/）で無償取得可能。RISHの記載ではMSMオリジナルデータへの日射量要素追加は2018年1月9日以降。DIASのGPVアーカイブは2002年7月以降を収録（要アカウント）。太陽光関連ではNEDO日射量データベース（METPV-20等）も無料で利用可能。
src: https://database.rish.kyoto-u.ac.jp/arch/jmadata/

### 8. 需給調整市場（EPRX）約定結果
一般社団法人電力需給調整力取引所（EPRX）の「取引情報」ページ（eprx.or.jp/information/）で、取引実績（約定結果: agree_results.php）、取引実績の取りまとめ結果（summary.php）、三次調整力②の使用率、上限価格、調整力必要量を無料公開。エリア別（北海道含む9エリア）・商品別（一次・二次①②・三次①②の5商品）の約定量・約定価格が取得できる。市場開始は2021年4月（三次調整力②）、2022年度に三次①、2024年度から一次・二次①②を追加し全商品が市場取引化。2021年度以降の実績取りまとめが遡って掲載されている。ブロック単位等の詳細粒度・CSV形式の詳細は本調査環境からサイト直接確認ができなかったため要確認。
src: https://www.eprx.or.jp/information/

### 9. 電力先物（TOCOM/EEX）価格データ
TOCOM電力先物（東エリア・西エリアのベースロード/日中ロード。北海道エリア価格を対象とする上場商品は無い）のデータは、JPX「電力先物・LNG先物各種データ」ページ（毎営業日18時頃更新の日次取引データ、月次限月別帳入値段の推移等）で無料公開。長期ヒストリカルはJPXデータポータル/JPXデータクラウド経由の有料提供が基本。EEXのJapanese Power Futures（2020年5月上場、東京・関西エリア、JEPXスポット月間平均価格で最終清算）は、Market Data Hubで一部無料閲覧でき、EoD約定データ（XLSX）はEEX Group Webshop/DataSourceの有料サービス（問い合わせ: datasource@eex-group.com）。第三者サイトjapanesepower.org（Japanese Electricity Market Data Hub）ではJEPXスポット・時間前の過去CSVが無料配布されている。
src: https://www.jpx.co.jp/markets/derivatives/reference/electricity/index.html

### 調査上の制約（重要な注記）
本調査環境ではjepx.jp・occto.or.jp・hepco.co.jp・meti.go.jp・eprx.or.jp・jpx.co.jp等への直接アクセスがプロキシ制限で不可だったため、詳細（CSV列構成・掲載開始年度・粒度）は検索結果要約と二次資料（Qiita、DevelopersIO、日経BP、ENERGY ADVISOR等）に基づく。特に(a)JEPXスポットCSVの最古年度、(b)北海道電力NW需給実績の掲載保持期間（過去5カ年ローリングの可能性）、(c)OCCTO連系線潮流CSVの正確な時間粒度、(d)EPRX約定結果CSVの詳細仕様、の4点は執筆前に公式サイトで直接確認することを推奨する。

## thesis_implications
（1）分析の中核となるJEPX北海道エリアプライス（30分値）、北海道の需給実績（太陽光・風力実績含む）、連系線潮流はすべて無料で入手でき、金融工学的なボラティリティ分析（GARCH系、実現ボラティリティ等）に必要な時系列は構築可能である。ただし北海道電力NWの需給実績は「当年度＋過去5カ年」のローリング掲載の可能性があるため、直ちに全期間をアーカイブすべきである。（2）市場均衡理論に基づき供給曲線の傾き（価格感応度）から均衡点を推定するアプローチを取る場合、最大の制約はJEPX入札カーブが画像でしか公開されていない点である。画像の数値化処理を研究の一部として組み込むか、公開されている約定量・売買入札量・価格から誘導的に供給曲線の傾きを推定する設計に切り替えるか、早期に方針を決める必要がある。JEPXへの研究目的でのデータ提供依頼も検討に値する。（3）北海道は2022年5月8日に初の出力制御が実施され、系統用蓄電池の接続申込が需要規模比で全国最大級（2022年7月末時点で1.6GW、平均需要の約5割）という特異なエリアであり、「再エネ増→ボラティリティ増」と「蓄電池増→ボラティリティ減」の両効果が観測データで同定しやすい理想的な対象である。北豊富240MW/720MWh（2023年3月）や札幌50MW/100MWh（2025年11月）など大型蓄電池の運開時点をイベントとした前後比較（構造変化検定）も設計できる。（4）蓄電池の「普及量」データは接続検討・契約申込・連系済の3段階で統計の性格が大きく異なるため、審議会資料の時点別数値を丁寧に整理する必要がある。（5）北海道エリアを対象とする先物商品は存在しないため、先物データ（TOCOM東西エリア、EEX東京・関西）はリスクプレミアム推定の補助的利用にとどめ、ボラティリティ分析はスポット・時間前・需給調整市場（EPRX、2021年4月以降）データを主軸に据えるのが現実的である。（6）検証できなかった細部（JEPX CSVの最古年度、OCCTO CSVの粒度、EPRX CSV仕様）は研究計画確定前に公式サイトで直接確認すること。

## sources
- JEPX スポット市場（市場情報・データダウンロード） | https://www.jepx.jp/electricpower/market-data/spot/ | spot_summary_[年度].csv の無料ダウンロード。30分値48コマ、システム/エリアプライス・約定総量・売買入札量
- JEPX スポット市場における入札カーブ | https://www.jepx.jp/electricpower/market-data/spot/bid_curves.html | 2021年2月27日以降、需給曲線を画像形式で当日中に無料公開（数値データは取引会員限定）
- JEPX 取引ガイド | https://www.jepx.jp/electricpower/outline/pdf/Guide_2.00.pdf | スポット市場の商品仕様（1日48商品・30分単位）の一次資料
- JEPXスポット市場価格データをcURLでダウンロードする（Qiita） | https://qiita.com/InvestorX/items/f1649d046a8405bdca8e | CSVのURLパターン・列構成を確認した二次資料
- JEPXが公開する電力市場価格のCSVをLambdaで整形してみた（DevelopersIO） | https://dev.classmethod.jp/articles/jepx-spot-csv-etl-lambda/ | spot_summary CSVの構造の二次確認
- JEPX | Day Ahead Market（Kaggle） | https://www.kaggle.com/datasets/mitsuyasuhoshino/jepx-dayaheadmarket | スポット市場データのミラー。入札カーブ数値化の代替入手経路
- JEPXのスポット需給曲線画像を数値データに変換（Qiita） | https://qiita.com/LANcat/items/fcfd23ced98c39b1cc6f | 入札カーブが画像公開であることの傍証と数値化手法
- OCCTO 系統情報サービス等 | https://www.occto.or.jp/institution/keitoujouhou/ | 連系線潮流実績・運用容量・空容量のCSVダウンロード入口（登録不要・無料）
- OCCTO 広域機関システム 操作マニュアル 系統情報公表（一般用） | https://www.occto.or.jp/assets/various/occtosystem/manual/251107_keitoujouhou.pdf | CSVダウンロード手順・データ粒度の一次資料
- OCCTO 電力需給及び電力系統に関する概況（2024年度実績、2025年9月） | https://www.occto.or.jp/assets/houkokusho/2025/files/denryokujukyuu_2024_250910.pdf | エリア別需給・連系線運用の年次統計
- 北海道エリアのでんき予報（ほくでんネットワーク） | https://denkiyoho.hepco.co.jp/area_forecast.html | 当日の電力使用状況CSV
- 過去の系統の需給に関する情報 ダウンロード（ほくでんネットワーク） | http://denkiyoho.hepco.co.jp/area_jukyu_download.html | 月別CSV（ZIP）で過去の需給データを提供
- 北海道エリアの需給実績（ほくでんネットワーク） | https://www.hepco.co.jp/network/con_service/public_document/supply_demand_results/index.html | 2016年4月開始、当年度＋過去5カ年掲載との情報。太陽光・風力実績（出力制御後・送電端）を含むCSV
- 再生可能エネルギー出力制御見通し（でんき予報） | https://denkiyoho.hepco.co.jp/renewable_energy_output_control_forecast.html | 出力制御の見通し・実績の公表ページ
- 5月8日における再エネ出力制御の実施状況について（北海道電力NW、2022年5月24日、METI系統WG資料3） | https://www.meti.go.jp/shingikai/enecho/shoene_shinene/shin_energy/keito_wg/pdf/039_03_00.pdf | 北海道初の出力制御（2022年5月8日、最大18.8万kW）の詳細
- 北海道エリア出力抑制の公平性検証結果 2024年度実施分（OCCTO、2025年7月30日） | https://www.occto.or.jp/assets/oshirase/shutsuryokuyokusei/2025/files/250730_kenshokekka_hokaido_kouhei.pdf | 年度別の出力制御実績の検証資料
- 2025年度出力制御見通しについて（北海道電力NW、2025年1月23日） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/001_s01_01.pdf | 北海道の太陽光231万kW・風力136万kW（2024年9月時点）等の連系量データ
- 系統用蓄電池の迅速な系統連系に向けて（資源エネルギー庁、2025年9月24日、系統WG資料4） | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/004_04_00.pdf | 全国の接続検討約14,300万kW・契約申込約1,800万kW（2025年6月末）
- 系統用蓄電池の接続に係る課題と対策について（北海道電力NW、2022年9月14日） | https://www.meti.go.jp/shingikai/enecho/shoene_shinene/shin_energy/keito_wg/pdf/041_02_00.pdf | 北海道の接続検討61件・1.6GW（2022年7月末）
- OCCTO 発電設備等系統アクセス業務に係る情報の取りまとめ（2024年度受付・回答分、2025年6月） | https://www.occto.or.jp/assets/houkokusho/2025/files/250620_access_toukei_2024.pdf | 電源種別・エリア別の接続検討/契約申込の年次統計
- OCCTO 第95回広域系統整備委員会 資料1「系統用蓄電池の新規連系における課題と対応」（2025年11月28日） | https://www.occto.or.jp/assets/iinkai/kouikikeitouseibi/95/seibi_95_01_01.pdf | 系統用蓄電池の連系状況・課題の最新審議資料
- GSユアサ 北豊富蓄電池設備（240MW/720MWh）稼働 | https://newsroom.gs-yuasa.com/news-release/121 | 2023年3月稼働、北海道北部風力送電網向け
- 大和エナジー・インフラ 札幌市系統用蓄電池（50MW/100MWh） | https://daiwa-ei.jp/portfolio/energy/sub/p164/ | 2025年11月1日運転開始
- 気象庁 過去の気象データ・ダウンロード | https://www.data.jma.go.jp/risk/obsdl/ | アメダス・気象官署の観測値をCSVで無料取得（時別値・10分値等）
- 京都大学生存圏研究所 気象庁GPVアーカイブ | https://database.rish.kyoto-u.ac.jp/arch/jmadata/ | MSM-GPV等を研究・教育目的で無償提供。日射量要素は2018年1月9日以降
- 気象業務支援センター メソ数値予報モデルGPV（MSM） | https://www.jmbsc.or.jp/jp/online/file/f-online10200.html | MSM-GPV（5km格子）の公式有償提供窓口
- NEDO 日射量データベース閲覧システム | https://appww2.infoc.nedo.go.jp/appww/metpv.html | METPV等の日射量データを無料提供
- EPRX 取引情報 | https://www.eprx.or.jp/information/ | 需給調整市場の約定結果・取りまとめ結果の無料公開ページ（2021年4月市場開始）
- EPRX 需給調整市場かいせつ資料（2026年3月13日 第2版） | https://www.eprx.or.jp/outline/docs/kaisetsu.pdf | 商品区分（一次〜三次②）と市場導入年度の一次資料
- JPX 電力先物・LNG先物各種データ | https://www.jpx.co.jp/markets/derivatives/reference/electricity/index.html | 毎営業日18時頃更新の日次取引データ（無料）
- EEX Japanese Power Market | https://www.eex.com/en/markets/power/japanese-power-market | 2020年5月上場。東京・関西エリア先物、JEPXスポット月間平均で清算
- EEX Japanese Power Futures EoD（EEX Group Webshop） | https://webshop.eex-group.com/data-type/eex-japanese-power-futures-eod | EoDヒストリカルデータの有料提供（XLSX、sFTP）
- Japanese Electricity Market Data Hub | https://japanesepower.org/ | JEPXスポット・時間前の過去CSVを無料配布する第三者サイト
- 北海道エリアで初の出力制御、5月8日に実施（日経BP メガソーラービジネス） | https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02523/?ST=msb | 2022年5月8日の初制御の報道（最大18.8万kW、1,916件）
- 北海道で「系統用蓄電池」の申込が1.6GW、接続に負担金も（日経BP） | https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/02823/?ST=msb | 北海道の蓄電池申込急増の報道