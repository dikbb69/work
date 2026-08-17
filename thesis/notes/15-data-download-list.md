# 手動ダウンロード依頼リスト（優先度順）

- 作成日: 2026年7月27日
- 背景: この作業環境からはOCCTO・METI・JEPX等へのアクセスがプロキシで遮断されるため、以下はユーザーの手動取得が必要。取得後はzipでチャットに添付（ファイル名はそのまま）
- 対応フェーズ: equilibrium-quantification-plan.md §7.5（A=基盤データ）

## 優先度A — フェーズB（価格過程モデル）着手のブロッカー

| # | データ | 用途 | 取得先 |
|---|---|---|---|
| A1 | **北海道の太陽光・風力導入量の時系列**（月次または四半期、2016〜現在） | cf（設備利用率）過程の正規化＝価格過程モデルの前提。K_pv・K_windの実績経路 | 経産省 FIT/FIP情報公表用ウェブサイト [B表: 都道府県別導入量](https://www.fit-portal.go.jp/PublicInfoSummary)（月次Excel、北海道行）。補完: [JWPA導入実績プレスリリース](https://jwpa.jp/information/)（年末値）、系統WG資料の接続量（下記C4） |

## 優先度B — K\*求解（フェーズD）に必須

| # | データ | 用途 | 取得先 |
|---|---|---|---|
| B1 | **長期脱炭素電源オークション 約定結果（第1〜3回）＋別紙「落札電源一覧」** | AFC（年間固定費）の市場実測値／政策ストックK_policyのエリア別集計 | OCCTO。第3回: [約定結果](https://www.occto.or.jp/assets/various/capacity-market/jitsujukyukanren/2025_boshuyoukou_long/260513_longauction_youryouyakujokekka_kouhyou_ousatsu2025.pdf)・[別紙](https://www.occto.or.jp/assets/various/capacity-market/jitsujukyukanren/2025_boshuyoukou_long/260513_longauction_youryouyakujokekka_kouhyou_besshi_ousatsu2025.pdf)。第1回（2024/4/26公表）・第2回（2025/4/28公表）はOCCTOサイト内検索「長期脱炭素電源オークション 約定結果」 |
| B2 | **容量市場の需要曲線（北海道エリア、直近2〜3オークション分）** | P_cap(K)の閉形式計算（二重カニバリの容量市場側） | OCCTO 各年度「メインオークション需要曲線の公表」資料（サイト内検索「容量市場 需要曲線 公表」。2029年度向け=2025年度実施分から） |
| B3 | **調整係数の公表資料（蓄電池・揚水の発電可能時間別）** | κ（期待容量ディレーティング）の確定＝容量収入の実効値 | OCCTO（毎年7〜8月公表。例: 2028年度向けは2024/8/7）。サイト内検索「容量市場 調整係数」 |
| B4 | ~~調達価格等算定委員会の蓄電池コスト関連資料~~ **取得済み（2026/7/28）**: 第67・75・84・93・102・114回の意見案＋別紙 → 系統用蓄電池の資本費想定は算定委に存在しないことを確認（notes/19）。AFCはLTDA実測バンドで確定。副産物の風力・太陽光コスト想定は `santeii_cost_assumptions.csv` に整理 | AFCの公式想定側（LTDAと三角測量） | [調達価格等算定委員会](https://www.meti.go.jp/shingikai/santeii/index.html) |

## B5（2026/7/28追加）— 蓄電池資本費のMETI審議会資料（B4の後継・調査済み）

算定委に蓄電池資本費想定がないことを受けた再調査の結果（notes/19参照）。優先度順。

| # | データ | 期待できる数値 | 取得先 |
|---|---|---|---|
| B5-1 | ~~定置用蓄電システム普及拡大検討会~~ **取得済み（2026/7/28）**: 2024年度とりまとめ＋2025年度第1回資料6-1/6-2 → 系統用実勢価格 FY2022 6.1／FY2023 7.6／FY2024 6.8万円/kWh（総額）を確定、AFC(4h)=2.5〜3.0万円/kW-年に精緻化（notes/20、`battery_capex_series.csv`） | 系統用蓄電池の実勢価格（補助事業ベース）＝AFCの一次資料 | [検討会トップ](https://www.meti.go.jp/shingikai/energy_environment/storage_system/index.html) |
| B5-2 | **発電コスト検証WG（2024年度）とりまとめ**（2025/2/6）＋第4回資料3「統合コスト」（2024/11/29） | 併設蓄電池の建設費想定（太陽光併設9.5万円/kWh・陸上風力併設6.0万円/kWh）、統合コストの中での系統用蓄電池の扱い＝**均衡モデルの社会的費用側の公式参照点** | [とりまとめ](https://www.enecho.meti.go.jp/committee/council/basic_policy_subcommittee/mitoshi/cost_wg/pdf/cost_wg_20250206_01.pdf)・[第4回資料](https://www.enecho.meti.go.jp/committee/council/basic_policy_subcommittee/mitoshi/cost_wg/2024/data/04_06.pdf) |
| B5-3 | **制度検討作業部会→次世代電力基盤（system_review）→安定供給電源WG（stable_power_supply_wg）のLTDA関連資料**: 第92回資料3-3（2024/5/10）・第102回資料4（2025/4/23）・第103回資料3-3・第104回資料3・第113回資料3（2026/4/3）・安定供給WG第1回資料7-3（2026/5/13）・第4回資料4-1（2026/7/14） | 応札上限10万円/kW/年の閾値設定の経緯、蓄電池・揚水の募集上限と応札倍率、**第4回オークション（2026年度）に向けた上限・区分見直し**＝AFC上限側の制度アンカー | [92回](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/seido_kento/pdf/092_03_03.pdf)・[102回](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/seido_kento/pdf/102_04_00.pdf)・[113回](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/jisedai_kiban/system_review/pdf/113_03_00.pdf)・[安定供給WG第1回](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/jisedai_kiban/stable_power_supply_wg/pdf/001_07_03.pdf)・[同第4回](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/jisedai_kiban/stable_power_supply_wg/pdf/004_04_01.pdf) |
| B5-4 | **SII 系統用蓄電池等導入支援事業の公募要領**（令和5・6・7年度＋令和7年度補正） | 目標価格の年度推移（例: 2025年度 11.9万円/kWh=設備＋工事・税抜、大規模業務産業用）、補助上限単価＝**投資家が直面する実効資本費の下限側** | [令和5年度](https://sii.or.jp/chikudenchi05/)・[令和6年度](https://sii.or.jp/chikudenchi06/)・[令和7年度](https://sii.or.jp/chikudenchi07/public.html)・[令和7補正 公募要領PDF](https://sii.or.jp/daikibogyousan07r/uploads/R7r_less_kouboyouryou_02.pdf) |
| B5-5 | **蓄電池産業戦略**（官民協議会 2022/8/31）＋**蓄電池産業戦略推進会議 資料6「定置用蓄電システムの現状と課題」**（2025/3/12） | 価格目標: 2030年 業務・産業用6万円/kWh（工事費込み）、長期は揚水並み2.3万円/kWh＝**シナリオの終端値** | [戦略本文](https://www.meti.go.jp/policy/mono_info_service/joho/conference/battery_strategy/battery_saisyu_torimatome.pdf)・[推進会議資料6](https://www.meti.go.jp/policy/mono_info_service/joho/conference/battery_strategy2/shiryo06.pdf) |

- 換算メモ: FY2024実勢6.8万円/kWh × 4h = 27.2万円/kW → CRF(6%・20年)8.7%で**資本費年額約2.4万円/kW-年**＋運維
  → LTDA三角測量の作業バンド2〜3万円/kW-年と整合。B5-1の年次系列が取れれば、均衡モデルのAFC(h)を
  「実勢価格×低下率シナリオ」で内生的に動かせる

## 優先度C — シナリオ・精緻化（フェーズB後半〜E）

| # | データ | 用途 | 取得先 |
|---|---|---|---|
| C1 | **OCCTO供給計画取りまとめ（2026年度）**＋北海道電力の供給計画届出概要 | 供給スタック構築（泊・石狩湾新港・石炭退役のシナリオ部品） | OCCTO「供給計画の取りまとめ」ページ（2026/3/30公表分）＋北海道電力プレス |
| C2 | **連系線の運用容量（北本、月別・2016年度〜）** | 分断レジーム判定（フロー張り付きの閾値）と増強シナリオ | OCCTOサイト内検索「連系線の運用容量」（年度別の別紙Excel/PDF） |
| C3 | **OCCTO需要想定（2026年度、エリア別最大需要・年間電力量）** | fig1の確定・需要比指標の分母統一 | OCCTOサイト内検索「需要想定」（2026/1公表分） |
| C4 | **次世代電力系統WG 第7回 資料1-1**（蓄電池のエリア別契約申込表の原本）＋**第6回・第1回の接続量資料**（風力136万kWの時点確定用 [001_s01_01.pdf](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/001_s01_01.pdf)） | notes/14の数表の一次確認／RECHECK A2の残タスク | [次世代電力系統WG](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/)（第7回=2026/2/9、[007_01_01.pdf](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/007_01_01.pdf)） |
| C5 | **北海道のローカル系統混雑による出力抑制の実績資料**（2026/8/17追加・取得先特定済み）: ①OCCTO月次検証「北海道エリアにおける流通設備混雑による再エネ出力抑制に関する検証結果」（2025年11月分〜最新2026年5月分、[例: 2026年5月分](https://www.occto.or.jp/news/oshirase_shutsuryokuyokusei_2026_260729_shutsuryokuyokusei2_hokkaido_1.html)）②系統WG第6回資料2-2（2025/12/24、[初回=2025年11月分の検証](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/006_02_02.pdf)）③[ほくでんNW実施通知（66kV岩松線）](https://www.hepco.co.jp/network/info/info2025/1252921_2061.html)・[系統情報の公表](https://www.hepco.co.jp/network/con_service/public_document/bid_info.html)・[ノンファーム接続・申込状況](https://www.hepco.co.jp/network/renewable_energy/fixedprice_purchase/nonfirm_connect_app_status.html)④[OCCTO広域系統整備委: 2030年度に系統混雑が見通される変電所一覧（北海道）](https://www.occto.or.jp/assets/iinkai/kouikikeitouseibi/2025/files/seibi_92_04_01.pdf)⑤[暫定措置の説明（系統WG第3回資料2-2）](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/003_02_02.pdf) | BTM狭域価値の一次資料: 「エリア余剰型 vs ローカル型」抑制の分解（notes/21 B-1）を公式データで検証。④は将来のローカル制約マップ＝BTM立地価値の予測材料 | 北海道初のローカル混雑制御=2025年11月・66kV岩松線。混雑管理システム運開（2026年度末予定）後はルール変更に注意 |

## 優先度D — 任意・拡張（あれば嬉しい）

| # | データ | 用途 | 取得先 |
|---|---|---|---|
| D1 | 需給調整市場の約定結果CSV（一次・二次①のΔkW価格、2024年度〜） | EPRXレント感応度の実測（移行期プレミアム） | [EPRX 取引結果](https://www.eprx.or.jp/)（市場情報→取引結果のCSV） |
| D2 | JEPXスポット入札カーブ（買い・売り曲線） | 供給曲線推定の精緻化（Rassi & Kanamura型）。当面は不要 | JEPX 取引情報（会員公開範囲に注意） |
| D3 | 電力調査統計（エリア別・燃種別発電実績） | 供給スタックのクロスチェック | 経産省 電力調査統計 |

## 取得のコツ・注意

- OCCTOのPDFはURL直リンクが変わることがある → 見つからない場合は「容量市場・発電設備等の情報掲示板」または各ページのサイト内検索で表題検索
- A1のfit-portal B表は月次ファイルが積み上がっているため、**2016年4月〜最新まで一括**でお願いしたい（北海道行だけ使うので全国版で可）
- B1の別紙（落札電源一覧）は3回分すべて必要（エリア別集計はこちらで行う）
- 既に取得済み: JEPXスポット（〜2026/7）、九州・北海道・東北の需給実績（〜2026/6）、容量市場メインオークション約定結果4期分
