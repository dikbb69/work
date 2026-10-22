# 付録E　再現のための資料

本付録は、本論文の数値と図表を再現するための資料をまとめる。付録E.1 はデータ台帳、付録E.2 は解析スクリプトの一覧と実行の順序、付録E.3 は図表と出力ファイルの対応、付録E.4 はデータの処理上の注意である。パスは筆者のリポジトリの最上位からの相対パスで示し、原データは `data/raw/`、処理後のデータは `data/processed/`、解析スクリプトは `analysis/`、図は `figures/hokkaido/` に置く。表の中では、スクリプトをファイル名の先頭の2桁の番号（例：`41` は `analysis/41_equilibrium_v3.py`）で示す。原データは各提供機関の利用条件に従って取得したものであり、再配布しない。処理後のデータとスクリプトを電子付録として配布できるかは【要確認】である。

## E.1　データ台帳

データの提供機関・期間・取得日は表A.1 に示した。表E.1 は、原データの格納場所、処理後のファイル、それを作るスクリプトの対応である。

: 表E.1　データ台帳（原データと処理後のファイル）

| 区分 | 原データ（`data/raw/`） | 処理後のファイル（`data/processed/`） | スクリプト・記録 |
|---|---|---|---|
| スポット市場の約定結果 | `jepx/spot_summary_2016.csv`〜`spot_summary_2026.csv`（年度別の11本） | `jepx_kyushu_30min.csv`、各エリアの時間パネルの価格の列 | `01`、`11`。市場分断の分類（`46`）、30分値で下限のコマを含むかの判定（`50`）、東京エリアプライス（`40`）は `data/raw/jepx/` の30分コマを直接読む |
| 九州の需給実績 | `kyushu/`（旧様式の四半期ファイル32本、新様式の月次ファイル29本） | `kyushu_hourly_panel.csv`、`kyushu_daily_metrics.csv`、`kyushu_battery_backtest_daily.csv` | `01`、`03` |
| 北海道・東北の需給実績 | `hokkaido/`（59本）、`tohoku/`（61本） | `hokkaido_hourly_panel.csv`、`tohoku_hourly_panel.csv` | `11` |
| 太陽光・風力の導入容量（表B） | `fit_b/`（市町村別の四半期ファイル44本と、都道府県別の `B_pref202103.xlsx`） | `fit_capacity_pref_quarterly.csv`、`area_capacity_series.csv`、`hokkaido_cf_series.csv`、`hokkaido_cf_series_corrected.csv`（計上時期を補正した系列。感応度にだけ用いる） | `12`、`51` |
| 長期脱炭素電源オークション | `ltda/`（第1〜3回の約定結果の本文と別紙） | `ltda_battery_projects.csv`、`ltda_area_reconciliation.csv`、`ltda_hokkaido_summary.csv` | `49` |
| 容量市場の需要曲線・調整係数 | `capacity_demand_curve/`、`capacity_chouseikeisu/` | `capacity_adjustment_coefficients.csv` | `42`（2030年度向けの4点の折れ線はコードに置く。数量の軸は2029年度向けで代用） |
| 蓄電池の資本費・再エネの費用の想定 | `storage_system/`、`santeii/` | `battery_capex_series.csv`、`santeii_cost_assumptions.csv` | 公表資料の値を転記 |
| 風力の導入実績（突合用） | `jwpa/` | — | 付録A.5 の突合に用いる |
| 系統用蓄電池の接続・補助・案件 | 公表資料（北海道電力ネットワーク、環境共創イニシアチブの交付決定一覧、事業者の発表と報道） | `gap_ledger_projects.csv`、`gap_ledger_summary.csv` | `49` |
| ローカル系統の出力制御 | 電力広域的運営推進機関の検証結果の本体と別紙1〜3（2025年11月分、2026年5月分、2026年6月分） | `local_congestion_control_occto.csv` | 値は `50` のコードに転記 |
| 資本コスト・契約・ヘッジの諸元 | 公表資料（財務省、長期脱炭素電源オークションの募集要綱、電力先物の商品概要、系統連系保証金の資料） | `irr_cost_of_capital.csv`、`apv_decomposition.csv`、`hedge_tenor_share.csv`、`real_option_waiting_value.csv` | `38`、`39`、`40` |

注）原データの取得の記録と検証の結果は `data/README.md` にある。

出所）筆者作成。

## E.2　解析スクリプトの一覧

表E.2 は `analysis/` のスクリプトの内容と、本論文での用途である。`01`〜`10` は九州の比較対象の分析で、本論文の数値には `01`・`03`・`10` の出力だけを用いる。「用いない」としたスクリプトは、分析の設計の段階の予備的な計算か、本論文の現行の計算に置き換えた計算である。

: 表E.2　解析スクリプトの一覧（`analysis/`）

| スクリプト | 内容 | 本論文での用途 |
|---|---|---|
| `01_build_panel.py` | 九州の需給実績と JEPX の価格から時間パネルを構築する（旧様式と新様式の統合、連系線の符号の統一、見出しの名前による列の対応） | 第3章、付録A.2 |
| `02_descriptive_figures.py` | 九州の記述統計の図表 | 用いない |
| `03_battery_backtest.py` | 九州の4時間蓄電池の日次の裁定価値の計算 | 表D.1 の九州の完全予見粗利 |
| `04_spread_montecarlo.py` | 日次スプレッドの確率モデルと年間価値の分布 | 用いない |
| `05_normalized_metrics.py` | 価格水準で規格化した指標 | 用いない |
| `06_factor_decomposition.py` | 九州の FY2023〜25 の下限張り付きとスプレッドの変化の要因分解 | 用いない |
| `07_counterfactual.py` | 九州の需要増と原子力の稼働変動の反実仮想 | 用いない |
| `08_wind_timescale.py` | 九州のフリート集約の風力出力の時間スケール構造 | 用いない |
| `09_export_figures_xlsx.py` | 図表データの Excel への書き出し | — |
| `10_hokkaido_quick_xlsx.py` | 北海道のエリアプライスによる簡易集計 | 表D.1 の下限張り付きコマ数 |
| `11_build_area_panels.py` | 北海道・東北の時間パネルの構築（`01` のエリアへの一般化） | 第3章、付録A.2 |
| `12_fit_capacity_series.py` | 表B から都道府県別・エリア別の太陽光・風力の導入容量の四半期系列を構築する | 第3章、付録A.4 |
| `13_price_process_v1.py` | 価格過程の基本仕様（仕様A と分断混合仕様、水準固定） | 表C.21、表C.23。`18`・`23`・`33`・`41`・`48`・`51` が部品として読み込む |
| `14_export_progress_figures.py` | 図表データの Excel への書き出し | 表C.23 に関する3年平均の値 |
| `15_price_curve_shapes.py` | 太陽光の多寡別の時刻別価格カーブ | 図5.1 |
| `16_strategy_decomposition.py` | 戦略 b の改善の分解（予測か、平均化によるノイズの除去か） | 用いない |
| `17_wind_battery_deepdive.py` | 風力の多寡別の時刻別価格カーブ | 図5.2 |
| `18_kwind_sweep.py` | 風力導入量を0.5〜3倍に振ったときの蓄電池の価値（基本仕様の価格過程） | 図7.1 |
| `19_hokkaido_extra_figs.py` | 北海道の帯域分解と年間粗利の図 | 図5.3、図6.2 |
| `20_btm_case.py` | 併設蓄電池を対象に加える根拠のデータ整理 | 用いない（補助図） |
| `21_band_comparison.py` | 北海道の風力と九州の太陽光の帯域分解の比較（発電量の系列） | 付録C.1.1 の発電量の系列による帯域分解 |
| `22_wind_vs_price_shape.py` | 発電量と価格の水準・日内形状の関係（季節別、区間なし） | 用いない（`46` に置き換え） |
| `23_pi_k_curve.py` | フリートを内生化した $\pi(K)$ の初期の計算 | 用いない（`41` に置き換え） |
| `24_vol_verification.py` | 日次回帰（式(5.2)）の推定（北海道・九州、風力を加えた Fuke and Ohashi 型の拡張） | 表5.2、表C.14 |
| `25_fo_replication.py` | Fuke and Ohashi（2025）の仕様の再現と、TB4h との対比 | 表5.5、表C.11〜表C.13 |
| `26_price_process_v2.py` | 年度別の水準係数を入れた価格過程 | 表7.1。`27`・`28`・`29`・`38`・`41`・`47`・`48`・`51` が部品として読み込む |
| `27_pi_k_curve_v2.py` | 水準係数付きの価格過程の上の $\pi(K)$ の計算 | 用いない（`41` に置き換え） |
| `28_equilibrium_surface.py` | 2次元の感応度面・損益分岐面と需給調整市場のレントの上限（ΔkW 価格の単位を 円/ΔkW·h とみなした旧い計算） | 用いない（レントの上限は `52`）。他は `42` に置き換え |
| `52_eprx_rent_cap_v2.py` | 需給調整市場のレントの上限（ΔkW 価格を 円/ΔkW・30分 として年額に換算） | 表7.3 の需給調整市場のレントの行、表C.28 |
| `29_spatial_dispersion.py` | 集中立地の反実仮想の初期の計算（加法による増幅） | 用いない（`47` に置き換え） |
| `30_btm_avoidable.py` | 併設蓄電池の容量制約の下での抑制回避可能率 | 表C.36 |
| `31_export_new_sheets.py` | 図表データの Excel への追記 | — |
| `32_negative_price.py` | 下限価格のシナリオの初期の計算 | 表C.50。シナリオの定義を `43`・`50` が読む。他は `43` に置き換え |
| `33_price_curve_sensitivity.py` | 供給曲線とベースロードの一律減の分解、下限価格の機構の検証 | 図7.4、図7.5、表7.4、表C.29 |
| `34_price_curve_pca.py` | 24時間の価格カーブの主成分分解と、完全予見粗利の因子エクスポージャー | 5.7節の寄与率・負荷、6.4.2項、付録C.2.3 |
| `35_option_layers.py` | 完全予見粗利の3層分解 | 表6.2、図6.4、表D.1、表D.3 |
| `36_strategy_tests.py` | 実行可能戦略の予測評価と取引ルールの検定（DM 検定、SPA 検定、実現率の区間） | 表6.3、図6.3、表C.18〜表C.20 |
| `37_robust_inference.py` | 日次回帰の系列相関に頑健な推論、同月内の識別、冬の TB4h の上位・下位4時間への分解 | 表5.2 の推論、表5.6、図5.8、表C.1、表C.14、表C.15 |
| `38_real_option_threshold.py` | 静学の損益分岐と待機を考慮した参入閾値、参入が開く確率、接続枠の待機価値 | 図7.6、表C.17 の競争均衡の閾値の比、表C.31〜表C.35、付録C.4.4 |
| `39_irr_cost_of_capital.py` | 事業 IRR、資産の資本コストと $\theta^*$、APV による分解、確実性等価 | 表8.2、図8.4、表C.41〜表C.45 |
| `40_cfar_hedging.py` | 多因子 CFaR と、上場先物によるヘッジ有効性 | 表8.3、図8.5、表C.46〜表C.48 |
| `41_equilibrium_v3.py` | 戦略 c の粗利を直接計算した $\pi(K)$、損益分岐の $\theta^*$、価格過程の条件付き応答の検証 | 表7.2、表7.3、図7.2、表C.22〜表C.25 |
| `42_breakeven_surface_v3.py` | 損益分岐面と均衡容量の格子、容量市場価格の $K$ 依存 | 表7.3、図7.3、図8.3、表C.25〜表C.27、表C.39、表C.40 |
| `43_negative_price_v3.py` | 段差モデルの $\pi(K)$ と $\theta^*$ の直接解、下限張り付き時間の感応度、実績価格での直接計算、線形外挿との比較 | 7.7節の負の価格の深さ、表9.1〜表9.3、図9.1、表C.49 |
| `44_regression_robustness_v3.py` | 日次回帰の頑健化（区間と上限、暦月の4季節、比の集合と検出力、Fuke and Ohashi 型の推論、九州の原子力、相対価格、主成分分解の EWC と2021年1月の除外） | 表5.2 の区間、表5.5、図5.7、表C.1、表C.9、表C.10、表C.12〜表C.14、表C.16、表C.30 |
| `45_quantile_moe_v3.py` | 分位点回帰による風力のメリットオーダー効果の期間比較（`--subperiods` で感応度の期間） | 図5.5、表C.2、表C.3 |
| `46_market_split_v3.py` | 市場分断の分類と記述統計 | 表3.1、表5.1、表5.3、図5.4、表6.2 の分断の列、表D.2 |
| `47_spatial_dispersion_v3.py` | 集中立地の反実仮想（校正、実現分散比による増幅、日周の位相、価格過程の感応度の検証と補正） | 表5.4、図5.6、表C.4〜表C.8 |
| `48_duration_legs.py` | 北海道と九州の脚の比較と、duration 別の参入閾値 | 表6.1、図6.1、6.5節、表C.17 |
| `49_gap_ledger.py` | LTDA の落札蓄電池の所在エリアの照合と乖離の勘定 | 表8.1、図8.1、付録A.6 |
| `50_colocation_v3.py` | 併設蓄電池の価値、5円超の抑制の分類、併設の参入条件、負の価格の移転、$\pi(K)$ の傾き | 図8.2、表9.2、表C.37、表C.38、表C.50、表D.4、表D.5、9.5節の脚注 |
| `51_cf_correction.py` | 風力の設備利用率の計上時期の補正と、その感応度 | 図A.1、付録A.4 と各章の計上時期の感応度 |

注）`analysis/pilots/finance_20261020/` は、`33`〜`40` の前に行ったファイナンスの手法の予備計算と、その点検の記録である。入出力のパスは作業時の一時ディレクトリを指しており、本論文の数値には用いない。

出所）筆者作成。

**実行の順序**　`01`・`11`・`12` でパネルと容量系列を作り、`13`（基本仕様の価格過程）と `26`（水準係数付きの価格過程）を実行する。`13` は `18`・`23`・`33`・`41`・`48`・`51` が、`26` は `27`・`28`・`29`・`38`・`41`・`47`・`48`・`51` が部品として読み込む。`15`・`17`・`22` は同じ Excel ファイルに書くので直列に実行する。`33`〜`40` は既存の出力を読むので、その後に実行する。`34`・`35` は時間パネルだけから計算する。現行の計算は次の順に実行する。

1. `36` → `41`（`41` は `36` の `strategy_daily_margins.csv`・`strategy_tests.csv` を読み、`pi_k_curve_v3.csv`・`price_model_level_ratios.csv`・`k0_variants_direct_c_v3.csv` などを書く）。
2. `41` → `38`・`39`・`40`・`49`・`50`（いずれも `pi_k_curve_v3.csv` を読む。`38` は `price_model_level_ratios.csv` も読む）と `42`（`41` の定義部分を読み込む）。
3. `42` → `43`（`breakeven_surface_v3_pik.csv` を読み、`41` の定義部分と `k0_variants_direct_c_v3.csv`、`32` の `negative_price_scenarios.csv` を読む）。
4. `38` → `48`（`real_option_short_duration.csv`・`real_option_price_level.csv`。`36` の `strategy_daily_margins.csv` も読む）、`39` → `49`（`apv_decomposition.csv`）。
5. `44`・`45` は `37` の推論の実装を読み込む。`44` はさらに `25`・`34`・`45` を読み込み、`25` の `fo_replication_results.csv`、`33` の `kyushu_nuclear_coef.csv`、`34` の `price_curve_pca_*.csv` と照合する。`45` の `--subperiods` は主の実行の後に走らせる。
6. `46` は `35` の `table73_refresh.csv` と照合する。`47` は `26` だけを読み込む。`50` は `30` の `btm_avoidable_share.csv` と `32` の `negative_price_scenarios.csv` を読む。`51` は `12`（関数だけ）・`13`・`26` を読み込み、`18`・`28`・`29`・`32`・`33` の出力と照合する。`49` は `ltda_battery_projects.csv` に所在エリアの列を加えて書き出す（付録E.4）。

`37` は `24` の `vol_regression_results.csv`・`vol_regression_results_ex21-22.csv` と係数が一致することを確かめ、`33` は `18` の `kwind_sweep.csv` と照合する。`36` は `26` の `price_level_theta.csv` と `28` の `equilibrium_surface.csv` を読む。`40` は照合のために `23`・`27`・`28` の出力も読む。

## E.3　図表と出力ファイルの対応

表E.3 は本文と付録の図、表E.4 は本文の表、表E.5 は付録の表について、出力ファイルと作成するスクリプトを示す。ファイルは、図が `figures/hokkaido/`、表のデータが `data/processed/` にある。

: 表E.3　図と出力ファイルの対応

| 図 | ファイル（`figures/hokkaido/`） | スクリプト |
|---|---|---|
| 図5.1　太陽光の多寡別の時刻別価格 | `price_curve_shapes_fy2023-25.png` | `15` |
| 図5.2　風力の多寡別の時刻別価格 | `wind_price_curves_fy2023-25.png` | `17` |
| 図5.3　北海道の風力の帯域分解の年度別推移 | `wind_bands_timeseries.png` | `19` |
| 図5.4　日次発電量の五分位別の日平均価格と TB4h | `gen_vs_price_shape_ci.png`（区間は `gen_quintile_ci_v3.csv`） | `46` |
| 図5.5　分位点回帰による北海道の風力の係数 | `quantile_moe_v3.png` | `45` |
| 図5.6　集中立地と日周位相の反実仮想 | `spatial_dispersion_v3.png` | `47` |
| 図5.7　24時間価格カーブの主成分負荷と時刻別係数 | `price_curve_pca_v3.png`（上段の負荷は `34` の全標本と FY2023〜25 の値） | `44` |
| 図5.8　推論法と仕様による TB4h の係数の95%区間 | `robust_inference_ci.png` | `37` |
| 図6.1　北海道と九州の脚の比較と、duration 別の損益分岐の価格水準係数 | `duration_legs.png` | `48` |
| 図6.2　完全予見粗利と実行可能戦略の年間粗利の推移 | `annual_backtest_series.png` | `19` |
| 図6.3　実行可能戦略の実現率と戦略 c との差 | `strategy_capture_ci.png` | `36` |
| 図6.4　完全予見粗利の層分解 | `option_layers.png` | `35` |
| 図7.1　風力導入量と完全予見粗利・下限張り付き時間 | `kwind_sweep.png` | `18` |
| 図7.2　限界参入者の実現可能収益と価格水準 | `pi_k_curve_v3.png` | `41` |
| 図7.3　風力導入量別の限界参入者の実現可能収益 | `equilibrium_surface_v3.png` | `42` |
| 図7.4　仕様A の供給曲線と純需要の分布 | `supply_curve_net_dist.png` | `33` |
| 図7.5　ベースロードの一律減への完全予見粗利の応答と分解 | `baseload_shift_response.png` | `33` |
| 図7.6　不確実性の下での参入閾値 | `real_option_threshold.png` | `38` |
| 図8.1　乖離の勘定と属性別の調整現在価値 | `gap_ledger.png` | `49` |
| 図8.2　併設4時間蓄電池の参入条件と抑制率 | `btm_entry_threshold.png` | `50` |
| 図8.3　損益分岐の価格水準係数 θ* の等高線 | `breakeven_frontier_v3.png` | `42` |
| 図8.4　調整現在価値による乖離の分解 | `apv_decomposition.png` | `39` |
| 図8.5　年間市場収入の5%下振れと因子別の寄与 | `cfar_decomposition.png` | `40` |
| 図9.1　下限価格のシナリオ別の限界参入者の収益曲線 | `negative_price_pi_k_v3.png`（パネル (b) を含め段差・仕様A による） | `43` |
| 図A.1　北海道の風力の容量の計上時期と補正 | `cf_correction.png` | `51` |

注）`band_comparison.png`・`band_comparison_hokkaido.png`（`21`）と `btm_case.png`（`20`）は、本論文に掲載しない補助図である。`figures/hokkaido/` のうち、ここに挙げない図（`pi_k_curve.png`、`pi_k_curve_v2.png`、`equilibrium_surface.png`、`breakeven_frontier.png`、`spatial_dispersion.png`、`negative_price_pi_k.png`、`gen_vs_price_shape.png`、`price_curve_pca.png`）は、本論文では用いない。

出所）筆者作成。

: 表E.4　本文の表と出力ファイルの対応

| 表 | ファイル（`data/processed/`） | スクリプト |
|---|---|---|
| 表2.1・表2.2（先行研究の整理）、表3.2（制度の要点）、表4.1・表4.2（分析の構成と手法） | —（本文の整理） | — |
| 表3.1　日次の記述統計 | `descriptive_stats_v3.csv`（導入量と年度平均の設備利用率は `descriptive_capacity_v3.csv`。2018年9月6日を除いた回帰は `regv3_ex20180906.csv`／`44`） | `46` |
| 表5.1　制御前出力の帯域分解 | `band_shares_cf_v3.csv` | `46` |
| 表5.2　日次回帰の係数 | `vol_regression_results.csv`（係数）、`robust_inference_table62.csv`（EWC の標準誤差・星・補正 p 値）、`regv3_wind_tb4_ci.csv`（区間と効果の上限） | `24`、`37`、`44` |
| 表5.3　北海道エリアプライスの分断の構成 | `market_split_v3_pooled.csv`、`market_split_v3_by_fy.csv`、`market_split_v3_route.csv` | `46` |
| 表5.4　集中立地の反実仮想の主な結果 | `spatial_dispersion_v3_table64.csv`、`spatial_dispersion_v3_calibration.csv`、`spatial_dispersion_v3_phase.csv` | `47` |
| 表5.5　先行研究の仕様による日間 IQR 係数と TB4h への係数 | `regv3_fo_tables.csv`（係数は `fo_replication_results.csv`） | `44`、`25` |
| 表5.6　主要な係数の頑健性 | `robust_inference_table62.csv`、`robust_inference_specs.csv`（実効的な棄却率は `robust_inference_size_mc.csv`） | `37` |
| 表6.1　完全予見粗利の脚の分解 | `legs_hokkaido_kyushu.csv`（充放電の窓の時刻別の分布は `legs_window_hours.csv`） | `48` |
| 表6.2　風力の三分位別の裁定指標 | `table73_refresh.csv`（北本連系線の拘束と東日本側の列は `market_split_v3_wind_tercile.csv`、北本連系線の潮流は `market_split_v3_export.csv`） | `35`、`46` |
| 表6.3　実行可能戦略の検定と頑健性の要約 | `strategy_tests.csv` | `36` |
| 表7.1　年度別の水準係数と価格過程の再現 | `price_level_theta.csv` | `26` |
| 表7.2　限界参入者の実現可能スポット収益 | `pi_k_curve_v3.csv`（$\pi=0$ と半減の $K$ は `pi_k_curve_v3_zero.csv`） | `41` |
| 表7.3　均衡の判定の感応度 | `theta_star_v3.csv`、`equilibrium_v3_irr.csv`、`capacity_price_of_k_v3.csv`、`eprx_rent_cap_v2.csv` | `41`、`42`、`52` |
| 表7.4　下限価格の機構の検証 | `floor_mechanism_check.csv` | `33` |
| 表8.1　乖離の勘定 | `gap_ledger_summary.csv`、`gap_ledger_projects.csv`、`ltda_hokkaido_summary.csv`（APV の収益の基準と APV が0となる割引率は `gap_ledger_apv_basis.csv`、LTDA のエリアの照合は `ltda_area_reconciliation.csv`） | `49` |
| 表8.2　マーチャント4時間蓄電池の事業 IRR | `irr_cost_of_capital.csv`（ブロックA） | `39` |
| 表8.3　年間市場収入の5% CFaR と因子別の寄与 | `cfar_multifactor.csv` | `40` |
| 表8.4　主な結論の頑健性 | —（本文の表8.1〜表8.3 と付録C.4 の結果の要約） | — |
| 表9.1・表9.3　下限価格のシナリオ別の収益と θ*、段差モデルの仕様と余剰の量の置き方への感応度 | `negative_price_v3_table101.csv`（$\theta^*$ の格子と比例の式との比較は `negative_price_breakeven_v3.csv`、全曲線は `negative_price_v3_pik.csv`、実績価格の行は `negative_price_actual_v3.csv`） | `43` |
| 表9.2　下限張り付き時間の再エネ発電と出力制御の影の価格 | `negative_price_transfer_v2.csv`（比の列は発電実績による `比_発電実績_c5`・`比_発電実績_c10`、抑制前の出力による比は `比_抑制前_c5`・`比_抑制前_c10`。年度の行は `negative_price_transfer_ratio_v3.csv`／`43` と一致し、4〜6月どうしの比はそのファイルの4〜6月の行） | `50`、`43` |
| 表10.1　主要な前提・捨象と結論への影響 | —（本文の各章の結果） | — |

出所）筆者作成。

: 表E.5　付録の表と出力ファイルの対応

| 表 | ファイル（`data/processed/`） | スクリプト |
|---|---|---|
| 表A.1〜表A.9（データの出所、変数と区分の定義） | — | — |
| 表C.1　冬の TB4h の上位・下位4時間への分解 | `robust_inference_winter_legs.csv`、`robust_inference_winter_proportional.csv`、`regv3_winter_ratio.csv`（比の集合、平行と比例の p） | `37`、`44` |
| 表C.2　分位点回帰による北海道の風力の係数 | `quantile_moe_v3_coef.csv`、`quantile_moe_v3_diff.csv`（年度別と下限張り付きを除く推定は `quantile_moe_v3_yearly.csv`・`quantile_moe_v3_floor_excl.csv`） | `45` |
| 表C.3　分位点回帰の感応度 | `quantile_moe_v3_subperiod.csv` | `45`（`--subperiods`） |
| 表C.4〜表C.8　集中立地の反実仮想の校正・全結果・日周の位相・検証・補正 | `spatial_dispersion_v3_calibration.csv`、`spatial_dispersion_v3_table64.csv`、`spatial_dispersion_v3_phase.csv`、`spatial_dispersion_v3_validation.csv`、`spatial_dispersion_v3_correction.csv` | `47` |
| 表C.9・表C.10　風力・太陽光の時刻別係数ベクトルの形（全標本、2021年1月を除く） | `regv3_pca_shape_ewc.csv`、`regv3_pca_contrasts_ewc.csv`（5.7節の本文は `regv3_pca_variance.csv`・`regv3_pca_factor_ewc.csv`・`regv3_pca_hourly_ewc.csv`・`regv3_pca_tb4_channels.csv` と、`34` の `price_curve_pca_variance.csv`・`price_curve_pca_loadings.csv`・`price_curve_pca_metrics_corr.csv`） | `44`、`34` |
| 表C.11　Fuke and Ohashi（2025）の仕様の再現 | `fo_replication_results.csv` | `25` |
| 表C.12・表C.13　日間の変動性と日内スプレッド（太陽光・風力） | `regv3_fo_tables.csv`（係数は `fo_replication_results.csv`） | `44`、`25` |
| 表C.14　燃料危機期を除いた日次回帰 | `vol_regression_results_ex21-22.csv`（係数）、`robust_inference_specs.csv` の除外標本の行（星）、相対価格の比較は `regv3_relative_price.csv` | `24`（`EXCLUDE_FY=2021,2022`）、`37`、`44` |
| 表C.15　推論法・仕様・標本による違い | `robust_inference_table62.csv`、`robust_inference_specs.csv` | `37` |
| 表C.16　暦月の4季節の区分による係数 | `regv3_cal4_panelC.csv`（春の純需要の三分位は `regv3_spring_netdemand.csv`） | `44` |
| 表C.17　duration 別の参入閾値 | `duration_theta_star_v3.csv`、`duration_value_v3.csv`（競争均衡の閾値の比は `real_option_short_duration.csv`／`38`） | `48` |
| 表C.18　実行可能戦略の実現率と検定 | `strategy_tests.csv`、`strategy_capture_annual.csv` | `36` |
| 表C.19・表C.20　SPA 検定と Reality Check、動的因子予測 | `strategy_tests.csv` | `36` |
| 表C.21　基本仕様の価格過程の標本内の再現 | —（`13` の標準出力） | `13` |
| 表C.22　価格過程の風力への条件付き応答の検証 | `price_model_validation.csv`（$\lambda$ と期間別の実績/モデルの比は `price_model_level_ratios.csv`） | `41` |
| 表C.23　構造イベントの部分均衡効果 | —（`13` の標準出力の構造イベントの実験。3年平均の値は `14` の Excel の記録）。上端の扱いの感応度は `dc_upper_end_sensitivity.csv`、ベースロードの一律減の戦略 c の直接計算は `k0_variants_direct_c_v3.csv`（いずれも `41`）。マルコフ型の抽出（20本の平均）は検算の値で、リポジトリの出力にはない | `13`、`14`、`41` |
| 表C.24　風力導入量のスイープ | `wind_sweep_v3.csv`（計上時期の補正は `cf_correction_kwind_specB.csv`／`51`） | `41` |
| 表C.25　価格水準シナリオ別の実現可能スポット収益 | `pi_k_theta_v3.csv`（FY2026上期の水準＋泊3号の列は `pi_k_curve_v3.csv`） | `42`、`41` |
| 表C.26　2次元の感応度面 | `breakeven_surface_v3_table86.csv`（全曲線は `breakeven_surface_v3_pik.csv`、計上時期の補正は `cf_correction_pik.csv`・`cf_correction_pik_summary.csv`／`51`） | `42` |
| 表C.27　容量市場価格の蓄電池容量への依存 | `capacity_price_of_k_v3.csv` | `42` |
| 表C.28　需給調整市場のレントの上限 | `eprx_rent_cap_v2.csv`（ΔkW 価格を 円/ΔkW・30分 として1時間あたり2倍に換算し、1kW あたりの物理上限 $2p_{\Delta}\times8{,}760$ で抑えた値） | `52` |
| 表C.29　泊の再稼働による完全予見粗利の変化の分解 | `baseload_shift_response.csv`（下端の傾きは `supply_curve_bin_slopes.csv`、計上時期の補正は `cf_correction_decomp.csv`／`51`） | `33` |
| 表C.30　九州の原子力発電量と日次の価格指標 | `regv3_kyushu_nuclear.csv`（欠測の20日を除く。付録E.4） | `44` |
| 表C.31　価格水準の2因子分解 | `real_option_price_level.csv` | `38` |
| 表C.32　参入に必要な価格水準係数 | `real_option_threshold.csv` | `38` |
| 表C.33　マーチャント参入が開く確率と2040年度の期待容量 | `real_option_entry_prob.csv`（フリートを戦略 c の窓で配分した期待容量は `real_option_fleet_alloc_v3.csv`） | `38` |
| 表C.34　容量収入の上振れ・補助・既設容量の感応度 | `real_option_sensitivity_v3.csv` | `38` |
| 表C.35　期待成長を見込む場合の参入閾値と確率 | `real_option_drift_sensitivity.csv` | `38` |
| 表C.36　併設蓄電池の抑制回避可能率 | `btm_avoidable_share.csv` | `30` |
| 表C.37　併設蓄電池の抑制回避の増分価値 | `btm_local_value.csv` | `50` |
| 表C.38　併設4時間蓄電池の参入が開く抑制率 | `btm_entry_threshold.csv`、`btm_entry_breakeven_capex.csv` | `50` |
| 表C.39　損益分岐の価格水準係数 θ* | `breakeven_frontier_v3.csv` | `42` |
| 表C.40　参入が開く組合せの均衡容量 | `kstar_table93_v3.csv`（全格子は `kstar_grid_v3.csv`） | `42` |
| 表C.41〜表C.43　事業 IRR の全ケース、LTDA 6時間の事業 IRR、資産の資本コスト別の θ* | `irr_cost_of_capital.csv`（ブロックA・B・C） | `39` |
| 表C.44　調整現在価値による乖離の分解 | `apv_decomposition.csv`（節税効果と資本構成は `irr_cost_of_capital.csv` のブロックD・G） | `39` |
| 表C.45　確実性等価によるリスク調整 | `certainty_equivalent.csv` | `39` |
| 表C.46・表C.47　多因子 CFaR の感応度と Shapley 配分 | `cfar_multifactor.csv`（年度別の形状と $\theta$ の代理は `cfar_annual_exposure.csv`） | `40` |
| 表C.48　ヘッジ有効性 | `hedge_effectiveness.csv`（期間の不一致は `hedge_tenor_share.csv`、北海道と東京の TB4h の相関は `hedge_basis_corr.csv`） | `40` |
| 表C.49　下限価格のシナリオ別の実現可能収益と θ*（全体） | `negative_price_v3_table101.csv`、`negative_price_breakeven_v3.csv`、`negative_price_actual_v3.csv`（計上時期の補正は `cf_correction_negprice.csv`／`51`） | `43` |
| 表C.50　太陽光・風力の抑制時間と下限張り付きの時間 | `negative_price_transfer.csv`、`negative_price_transfer_v2.csv` | `32`、`50` |
| 表C.51　主要な前提・捨象と結論への影響（詳細） | —（本文の各章と付録C の結果） | — |
| 表D.1　年度別の完全予見粗利と下限張り付きコマ数 | 北海道は `option_layers_by_fy.csv`、九州は `kyushu_battery_backtest_daily.csv` の年度合計÷1,000。下限張り付きコマ数は `jepx_kyushu_30min.csv` の30分値で約定価格が0.011円以下のコマの年度計 | `35`、`03`、`10` |
| 表D.2　季節別の日次の記述統計 | `descriptive_stats_v3_season.csv`（FY2016〜25 の版と最小・中央値・最大を含む） | `46` |
| 表D.3　完全予見粗利の3層分解（全年度・季節×風力の三分位） | `option_layers_by_fy.csv`、`option_layers_by_season.csv` | `35` |
| 表D.4　5円超の風力の抑制の分類 | `curtailment_above5_classification.csv`、`curtailment_price_bands.csv` | `50` |
| 表D.5　ローカル系統の混雑による出力制御の一覧 | `local_congestion_control_occto.csv` | `50` |

注）本文の数値のうち図表にないものの出典は次のとおりである。損益分岐の $\theta^*$・損益分岐の資本費・事業 IRR（7.5節、8.6節）は `theta_star_v3.csv`・`equilibrium_v3_irr.csv`（`41`）、duration 別の価値（6.5節）は `duration_value_v3.csv`・`duration_theta_star_v3.csv`（`48`）、完全予見粗利の因子エクスポージャー（6.4.2項）は `price_curve_pca_pf_exposure.csv`・`price_curve_pca_pf_channels.csv`・`price_curve_pca_pf_exposure_by_period.csv`・`price_curve_pca_sensitivity.csv`（`34`）、下限を外した場合の負の価格の深さ（7.7節、付録C.3.7）は `negative_price_extrap_depth_v3.csv`（`43`）、接続枠の待機価値（8.4.2項）は `real_option_waiting_value.csv`（`38`）、抑制の価格帯（8.5.1項）は `curtailment_price_bands.csv`（`50`）、$\pi(K)$ の傾き（9.5節の脚注）は `weitzman_slopes.csv`（`50`）、設備利用率の計上時期の補正（付録A.4 と各章の感応度）は `hokkaido_cf_series_corrected.csv`・`cf_correction_fy.csv`・`cf_correction_monthly.csv`・`cf_correction_btable_quarters.csv` ほか（`51`）による。表C.5 の注の、計上時期を補正した設備容量を使った場合の完全予見粗利の変化（0.2ポイント以下）は作業時の確認の値で、リポジトリの出力にはない。

出所）筆者作成。

## E.4　データの処理上の注意

原データ（`data/raw/`）は取得したときのまま残し、次の処理はすべて処理の段階で行う。記録は `data/README.md` と各スクリプトの docstring にもある。

**九州の新様式の連系線の符号**　九州の需給実績の新様式（2024年3月以降）の連系線の列は、旧様式と符号の向きが逆である（旧様式は負が域外への送電、新様式は正が域外への送電）。様式の境界で昼間の平均が −2,197MW から +2,203MW に不連続になることで確かめられる。`01` は新様式の符号を反転し、パネルでは受電を正（域外への送電を負）に統一する。北海道と東北の連系線は新旧の様式とも受電が正で、反転しない。

**九州の2026年4・5月のファイルの列構成**　九州の2026年4月・5月のファイルは、火力とバイオマスの出力制御量の2列が挿入された22列の構成である（6月以降は20列に戻る）。列の位置で読むと太陽光・揚水・連系線などが誤って対応するので、`01` は見出しの名前で列を対応させる（未知の列名があれば停止する）。

**北海道の価格の欠測**　北海道エリアプライスの2018年9月7日〜26日の480時間の欠測は、北海道胆振東部地震の後の取引停止によるもので、データの不具合ではない（付録A.3）。

**九州の需要などの欠測日**　`kyushu_hourly_panel.csv` は2019年3月12日〜31日（20日、480時間）の需要と原子力・火力の発電量を欠く（揚水と連系線の潮流も一部が欠測し、太陽光・風力の発電量と価格はある）。日次の集計は、24時間がそろわない日を欠測として除く（`sum(min_count=24)`）。このため九州の日次標本は3,632日であり、`24`、`33`、`37` の九州の日次回帰と表C.30 の九州の原子力の回帰はこの20日を含まない。北海道の数値はこの処理の影響を受けない。欠測日を需要0・発電0の日として含めると、九州の風力・不需要期の TB4h の係数は+0.275（除くと+0.173）になる。

**LTDA の落札蓄電池の所在エリア**　`ltda_battery_projects.csv` の都道府県の列は、各回の約定結果の別紙の地名で確定した値である。第1回の森町睦実２蓄電所（56,351kW）の所在は静岡県周智郡森町（中部エリア）で、北海道ではない。第1回の美唄（39,004kW）・長沼（37,515kW）は北海道、第1回の松阪は三重県、由利本荘は秋田県、第2回の BS浪江は福島県、津山杉宮は岡山県、石巻は宮城県である。第1回の FUKO-B1（36,814kW）は県名が特定できず、エリアを九州と推定した。案件名は `project` 列に置き、`area_est`（エリア）、`area_basis`（根拠）、`area_conf`（確定〔別紙の地名〕・名称〔案件名のエリア名・県名〕・高〔本文との照合のすべての解で一意〕・参考〔複数の候補〕）、`area_candidates`（残る候補と解の数）、`duration_class` の列を設ける。kW の合計は76件、3,713,239kW である。推定の方法は付録A.6 に示した。この表は `49` が原データから再現する。

**導入容量の計上時期**　設備利用率の分母とする表B の導入量の計上時期のずれと、その補正（`51`）は付録A.4 に示した。補正した系列は `hokkaido_cf_series_corrected.csv`、年度別の値は `cf_correction_fy.csv` にあり、本文の主の分析は補正前の系列（`hokkaido_cf_series.csv`）による。市町村別の表を欠く2021年3月末の照合に用いた都道府県別の表（`B_pref202103.xlsx`）は、`12` の集計には読み込まない。`data/README.md` の追記4 と `12` の docstring も同じ内容である。
