# 付録

## 付録A データ台帳

| 区分 | 出所・取得 | 期間・粒度 | 処理後ファイル |
|---|---|---|---|
| JEPXスポット約定結果 | JEPX 市場情報（手動DL、2026-07-26） | FY2016〜FY2026（2026/7/27受渡分まで）、30分48コマ、システム／9エリアプライス | `data/processed/jepx_kyushu_30min.csv`、各エリアの時間値パネル |
| 九州エリア需給実績 | 九州電力送配電（手動DL） | 2016/4〜2026/7。2024/2まで60分値（MWh）、2024/3から30分値（MW平均） | `kyushu_hourly_panel.csv`、`kyushu_daily_metrics.csv`、`kyushu_battery_backtest_daily.csv` |
| 北海道・東北エリア需給実績 | 北海道電力NW・東北電力NW（手動DL、2026-07-27） | 2016/4〜2026/6、60分値に統一。出力制御量列を含む | `hokkaido_hourly_panel.csv`、`tohoku_hourly_panel.csv` |
| FIT/FIP 導入容量（B表） | 再エネ FIT/FIP 公表サイト B_city 四半期（手動DL） | 2014/6〜2025/12、都道府県別。月次補間 | `fit_capacity_pref_quarterly.csv`、`area_capacity_series.csv`、`hokkaido_cf_series.csv` |
| 長期脱炭素電源オークション約定結果 | OCCTO 本文・別紙（第1〜3回、2025年度応札分） | 蓄電池案件のエリア・容量 | `ltda_battery_projects.csv`、`notes/16`・`notes/28` |
| 容量市場 需要曲線・調整係数 | OCCTO（2027〜2029年度向け需要曲線、2024〜2029年度向け調整係数） | 全国アンカーとエリア別 κ | `capacity_adjustment_coefficients.csv`、`notes/17` |
| 蓄電池資本費・費用諸元 | 定置用蓄電システム普及拡大検討会、調達価格等算定委員会 | FY2022〜24 実績・規模別、風力・太陽光の資本費・IRR | `battery_capex_series.csv`、`santeii_cost_assumptions.csv`、`notes/19`・`notes/20` |
| 風力導入実績（第三者検証） | JWPA 導入実績（2019〜2025年末版） | 年末累計 | `notes/16` |

データ修正の記録（`data/README.md`）: 九州新形式の連系線列の符号反転（パネル上は「負＝域外送電」に統一）、2026年4〜5月ファイルの列構成変更（ヘッダー名ベースのマッピングに変更）、北海道の2018/9/7〜26 の価格欠損480時間（胆振東部地震後の取引停止）。

## 付録B 変数と区分の定義

| 項目 | 定義 |
|---|---|
| 年度（FY） | 4月〜翌3月 |
| 報告用の季節区分 | 夏＝7〜8月、冬＝12〜2月、不需要期＝3〜6月・10〜11月、端境期＝9月（推定に含め、係数は非報告） |
| 価格過程の季節 | 気象学的4区分（12〜2月、3〜5月、6〜8月、9〜11月）。報告用区分とは別 |
| 制御前出力 | 発電実績＋出力制御量 |
| 純需要 $net$ | 需要 − 制御前太陽光 − 制御前風力 − 原子力 |
| TB4h スプレッド | 日内の上位4時間平均価格 − 下位4時間平均価格 |
| PF価値 | 完全予見4時間蓄電池（往復効率0.85、1日1サイクル）の年間裁定粗利（円/kW-年） |
| 床 | 0.01円/kWh（30分コマまたは60分時間で ≤0.011円） |
| 市場分断の3レジーム | 安値分断（道内＜システム−0.01）、連系（±0.01円以内）、高値分断（道内＞システム+0.01） |
| 帯域分解 | 移動平均カスケード: <6h＝x−MA6h、6〜24h＝MA6h−MA24h、1〜7日＝MA24h−MA168h、>7日＝MA168h−平均（非直交） |
| 価格水準係数 $\theta_{FY}$ | 水準係数付き価格過程の年度別スケール（FY2023〜25の時間加重平均＝1） |

## 付録C 図表と出力ファイルの対応

| 原稿の図 | ファイル（`figures/hokkaido/`） | 生成スクリプト |
|---|---|---|
| 図6.1 太陽光大小×3季節の価格カーブ | `price_curve_shapes_fy2023-25.png` | `15_price_curve_shapes.py` |
| 図6.2 風力大小×3季節の価格カーブ | `wind_price_curves_fy2023-25.png` | `17_wind_battery_deepdive.py` |
| 図6.3 帯域分解の年度別推移 | `wind_bands_timeseries.png` | `19_hokkaido_extra_figs.py` |
| 図6.4 発電量五分位×水準・TB4h | `gen_vs_price_shape.png` | `22_wind_vs_price_shape.py` |
| 図6.5 空間分散シミュレーション | `spatial_dispersion.png` | `29_spatial_dispersion.py` |
| 図7.1 年間裁定粗利の時系列（PF・a・b・c） | `annual_backtest_series.png` | `19_hokkaido_extra_figs.py` |
| 図8.1 風力導入量スイープ | `kwind_sweep.png` | `18_kwind_sweep.py` |
| 図8.2 π(K)曲線（基本仕様） | `pi_k_curve.png` | `23_pi_k_curve.py` |
| 図8.3 π(K; K_wind) | `equilibrium_surface.png` | `28_equilibrium_surface.py` |
| 図8.4 π(K)の価格水準感応度（水準係数付き） | `pi_k_curve_v2.png` | `27_pi_k_curve_v2.py` |
| 図9.1 損益分岐面 | `breakeven_frontier.png` | `28_equilibrium_surface.py` |
| 図10.1 下限価格シナリオ別の π(K) | `negative_price_pi_k.png` | `32_negative_price.py` |
| 補助図 帯域分解の比較（北海道風力 vs 九州太陽光） | `band_comparison.png`、`band_comparison_hokkaido.png` | `21_band_comparison.py` |
| 補助図 併設の根拠 | `btm_case.png` | `20_btm_case.py` |

表の出典: 表6.2・6.8 `vol_regression_results{,_ex21-22}.csv`、表6.5〜6.7 `fo_replication_results.csv`、表7.3 図表データ.xlsx「風力×裁定指標」、表8.2 `price_level_theta.csv`、表8.4 `pi_k_curve.csv`、表8.5 `pi_k_curve_v2.csv`、表8.6 `equilibrium_surface.csv`、表8.7 `capacity_price_of_k.csv`、表8.8 `eprx_rent_cap.csv`、表9.1 `btm_avoidable_share.csv`、表9.2 `breakeven_frontier.csv`、表9.3 `kstar_grid.csv`、表10.1 `negative_price_scenarios.csv`・`negative_price_breakeven.csv`、表10.2 `negative_price_transfer.csv`。編集可能なグラフ付きデータは `slides/進捗報告_20260817_図表データ.xlsx`。

## 付録D 解析スクリプト一覧（`analysis/`）

| スクリプト | 内容（docstring 先頭行） |
|---|---|
| `01_build_panel.py` | 九州パイロット: 生データから分析用パネルを構築する |
| `02_descriptive_figures.py` | 九州パイロット: 記述統計図表の生成(ゼミ発表用) |
| `03_battery_backtest.py` | 案1: 九州エリアにおける4時間蓄電池の日次裁定価値バックテスト |
| `04_spread_montecarlo.py` | 案2: 日次スプレッド(完全予見粗利)の確率モデル + モンテカルロによる年間価値分布 |
| `05_normalized_metrics.py` | 価格水準で規格化した指標 |
| `06_factor_decomposition.py` | FY2023→25 の「張り付き減・スプレッド縮小」の要因分解 |
| `07_counterfactual.py` | 反実仮想分析: 「半導体需要増・原子力稼働変動がなかりせば」のFY2024-25価格と裁定価値 |
| `08_wind_timescale.py` | 風力変動の時間スケール構造の実測（九州フリート集約出力、FY2022-25） |
| `09_export_figures_xlsx.py` | 発表資料の図表データをExcel化（1図=1シート、数値データ＋ネイティブグラフ） |
| `10_hokkaido_quick_xlsx.py` | 北海道の簡易分析（JEPXエリアプライスのみで可能な範囲） |
| `11_build_area_panels.py` | 北海道・東北の需給実績パネル構築（01_build_panel.py のエリア一般化） |
| `12_fit_capacity_series.py` | FIT/FIP 情報公表用ウェブサイト B表（市町村別導入容量）から都道府県・エリア別の |
| `13_price_process_v1.py` | フェーズB: 北海道の価格過程モデル v1 |
| `14_export_progress_figures.py` | 進捗報告（2026-08-17）デッキの図表データをExcel化（編集可能なネイティブグラフ付き） |
| `15_price_curve_shapes.py` | 北海道の時間帯別価格カーブの形状: 3季節 × 太陽光の大小（FY2023-25） |
| `16_strategy_decomposition.py` | 戦略bの改善の分解: 「予測」か「平均化によるノイズ除去」か（北海道） |
| `17_wind_battery_deepdive.py` | 風力×蓄電池の初期分析（北海道、FY2023-25） |
| `18_kwind_sweep.py` | K_windスイープ: 風力導入量を0.5×〜3×に振ったときの蓄電池スポット価値（基本仕様の価格過程） |
| `19_hokkaido_extra_figs.py` | 北海道の追加図2点（進捗報告用） |
| `20_btm_case.py` | 併設蓄電池を研究対象に加える根拠のデータ整理（北海道・風力） |
| `21_band_comparison.py` | 帯域分解の比較: 北海道風力 vs 九州太陽光（いずれも制御前出力） |
| `22_wind_vs_price_shape.py` | 風力は水準を下げるがスプレッドを広げない — 発電量×価格の関係（季節別、太陽光と対比） |
| `23_pi_k_curve.py` | フェーズC v1: 蓄電池フリートの内生化 → π(K)曲線 → 均衡容量K*の初回判定 |
| `24_vol_verification.py` | ①「再エネ→価格ボラ上昇」の北海道検証（Fuke & Ohashi 型の回帰・風力拡張） |
| `25_fo_replication.py` | Fuke & Ohashi (2025) 仕様の再現と、日内スプレッド（TB4h）との対比（第6章6.5） |
| `26_price_process_v2.py` | 供給曲線 v2: 上側水準を年度別スケール係数 θ_FY で非定常化した価格過程（北海道） |
| `27_pi_k_curve_v2.py` | フェーズC v2: 供給曲線 v2（26、年度別水準係数 θ）の上で π(K) と均衡容量 K* を再計算 |
| `28_equilibrium_surface.py` | 8.5 2次元の感応度面と 9.4 損益分岐面（供給曲線 v2 の上で） |
| `29_spatial_dispersion.py` | 6.4 空間分散シミュレーション: 集中立地の反実仮想（日内帯域を λ 倍に増幅）を価格過程 v2 に通す |
| `30_btm_avoidable.py` | 9.3.2 併設蓄電池の容量制約下での抑制回避可能率（北海道風力、2025/4〜2026/6 の時間値） |

実行順序の依存: `01`/`11`/`12` → パネル・容量系列、`13` → 基本仕様の価格過程（`18`・`23` が exec）、`26` → 水準係数付き価格過程（`27`・`28`・`29` が exec）。`15`・`17`・`22` は同じ xlsx に書くため直列に実行する。

| `32_negative_price.py` | 下限価格（床）シナリオ: 負価格の導入が蓄電池の裁定価値・均衡容量・再エネ収入に与える影響 |
