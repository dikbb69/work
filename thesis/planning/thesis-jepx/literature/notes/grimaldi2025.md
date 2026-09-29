# Grimaldi, A., Minuto, F. D., Perol, A., Casagrande, S., & Lanzini, A. (2025) Techno-economic optimization of utility-scale battery storage integration with a wind farm for wholesale energy arbitrage considering wind curtailment and battery degradation
- 書誌: *Journal of Energy Storage* 112, 論文番号 115500（全24頁）. DOI 10.1016/j.est.2025.115500（OA, CC BY）。PII S2352152X25002130。受理 2025-01-20、オンライン公開 2025-01-26。所属: トリノ工科大学（DENERG／Energy Center Lab）、Edison S.p.A.。責任著者 A. Grimaldi
- 出所: Drive の PDF（1-s2.0-S2352152X25002130-main.pdf、fileId 1wWEfdYgUIyE5n_S-4rC2BoiHZB1CQQd_）を MCP で全文テキスト化して精読（2026-09-29）→ セットE E15。データは機密（Data availability）で再現不可。式は引用前に原PDFで確認
- 表記: 「当方換算」＝論文の値から本ノート作成時に計算した値（論文自身の数値ではない）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 既設の陸上風力（イタリア、実稼働）に AC 連系のリチウムイオン蓄電池を後付けし、卸市場（日前）での裁定と TSO 給電指令による出力抑制の緩和を狙うとき、最適容量と採算はどうなるか。
- 貢献の主張（§1.2）: (i) 実風力発電所の SCADA（風速・TSO 給電指令）を入力に使う、(ii) 15年のフルライフを MILP で連続シミュレーション（先行研究の多くは1年）、(iii) サイクル計数型の劣化（9次多項式）を最適化に内蔵、(iv) 抑制緩和を含める（「文献ではまれ」と主張）。
- 手法の性格: 完全予見の決定論的 MILP（価格テイカー）。確率的・ロバスト最適化は今後の課題。

## 2. データ・市場・期間
- 市場: イタリア日前市場（DAM）の PUN（GME）、2023年（論文は「BAU の代表年」とする。年平均 127 €/MWh）。
- 風力: 実風力発電所（所在地・定格は非開示）の SCADA から風速と TSO 給電指令（0〜100%）を時間値で。Table 2: 年間発電量 ≈90,000 MWh、CF ≈26.2%、抑制電力量 ≈2,000 MWh/年（≈2.2%）。当方逆算: 定格 ≈39MW（90,000÷(8,760×0.262)）。
- 給電指令 0% は系統混雑による全面抑制（風車停止）、中間値は部分負荷（保守由来も含み得る、§4.2）。
- BESS: NMC リチウムイオン、AC 連系、充放電効率各 90%（往復≈81%）、SOC 20–100%（劣化後容量基準）、EOL＝容量70%＝6,147サイクル、自己放電 99.99%/h。CAPEX 353 €/kWh（Table 3、NREL Storage Futures Study 由来。内訳: セル 173.7、インバータ 13.9、BOS 22.2＋48.1、設置 25.9、EPC 27.7、開発費 40.7）、O&M 10.6 €/kWh/年（3%）、割引率 5%、15年（設置は0年目）。
- 15年分の入力の作り方は明記されない。Table 10 の年利益が単調減少（劣化のみで変動）であることから、2023年プロファイルの反復と読める（推定）。

## 3. 手法
- MILP（Pyomo＋Gurobi）、Δt=1h、48時間窓・24時間ローリング、完全予見。変数: 風力→系統、風力→BESS、系統→BESS（**系統充電可**）、BESS→系統、風力損失（抑制）、SOC、充放電の排他二値（BigM）。
- 目的関数（式1–8）: 風力売電収入＋BESS売電収入−系統充電コスト−抑制コスト（＝卸価格×失われた風力電力量）−劣化ペナルティ。ペナルティ単価 C_pen＝CAPEX/寿命＝23,533 €/MWh に、直近エピソードの線形化した劣化係数を乗じて更新。
- 制約: 式(11)「風力→系統＋BESS 放電 ≤ TSO 給電指令」（放電も指令上限に含まれる）、式(15)–(16) SOC。劣化: 経験式 E_rem(cyc)（式9）で容量を更新し、15年連続で再最適化。
- 経済指標（式30–33）: NPV は **BESS のキャッシュフローのみ**（BESS 放電収入−系統充電費−CAPEX−O&M）。LCOS、IRR、回収期間も同様。

## 4. 主要結果
- (a) 最適容量（Table 4、NPV k€、1〜10MW）:
  - 1h: 79.25/122.26/146.92/**151.72**/136.07/103.62/61.36/8.90/−57.47/−136.74
  - 2h（MWh は MW の2倍）: 108.23/**141.54**/126.97/68.01/−21.53/−134.96/−275.29/−441.60/−630.86/−825.70
  - 最適は 1h 4MW/4MWh（NPV 151.7、IRR 6.6%、LCOS 75.4 €/MWh、回収 12.7年）と 2h 2MW/4MWh（141.5、6.5%、75.0、12.8年）（Abstract、Table 9）。NPV>0 は 1h で 8MW/8MWh、2h で 4MW/8MWh まで。
  - 当方換算（定格≈39MW）: 最適 0.10 kWh/kW（出力比10%）、NPV>0 の上限 0.20 kWh/kW、探索範囲の上端（2h 10MW/20MWh）0.51 kWh/kW で NPV −826 k€。
- (b) 運用（Table 9、4MW/4MWh）: 年サイクル 397（本文は 380、5,694サイクル/15年と不一致）、BESS CF 55.5%、抑制 2.2%、風力→BESS 1.4%、風力→系統 96.4%。容量は15年で 100%→72.5%。BESS 純利益は初年度 214.6→15年目 169.6 k€/年（−20.9%）、15年平均 190.4 k€/年（Table 10）。
- (c) **収益（Table 5、k€/年）**: 風力売電収入 10,999（BESSなし）→10,880（あり）、BESS 純利益 190.353、総純利益 10,999→**11,071**（+72、+0.65%）。本文は「約190 k€の増加」と記述（§4.1）。
- (d) 抑制の感度（Table 13）: 抑制率 0.1/0.5/1.4/2.2/8.1% → NPV 58.44/75.00/104.60/151.72/227.12 k€、IRR 5.64/5.82/6.14/6.64/7.43%（8.1%では 440サイクル/年・寿命14年）。
  - 本文: 抑制は稀（2.2%）なので卸裁定を加えて稼働率を上げた。充電は「抑制風力＋低価格時の風力（＋系統）」（§4.2）。
  - **抑制回避量そのものは報告されない**。Table 9 の抑制率 2.2% は BESS あり（結果）だが Table 2 の入力値と同値で、風力→BESS 1.4% は風力→系統（97.8→96.4%）から出ている → 抑制回避は表の丸め精度以下（0.1pp 未満≈90 MWh/年、抑制量の約4.5%以下）と読める（当方の読み）。
  - 当方換算: 抑制 0.1%→2.2% で NPV +93 k€（基準 NPV の61%）。ただし全て BESS 単体勘定。
- (e) 費用・効率の感度: CAPEX（Table 11）は 25 €/kWh 毎に NPV 約131 k€。IRR は 325 €/kWh で 7.94%（NPV 271 k€）、300 で 9.62%、125 で 34.67%（回収約3年）。ハードル 8–9%（Judge et al. 2019、洋上風力の財務モデル由来）には <325 €/kWh が必要（基準 IRR 6.6%）。効率（Table 12）NPV(70/75/80/85/90/95/100%)＝−1,365/−1,129/−813/−287/152/373/329 k€（88–89% 未満で負）。100% では 696サイクル/年で8年で EOL となり、95% より低い。
- (f) LCOS 70.2〜85.3 €/MWh（全構成）は 2023年 DAM 平均 127 €/MWh を下回るが、ボラティリティを反映せず最適容量の判断には不適と著者も認める（§4.1）。
- (g) **劣化を無視した場合の過大評価は定量化されていない**。定性的に「劣化を考慮しないと収益性評価は楽観的になり得る」（§5）。当方概算: 初年度利益 214.6 k€ が15年続くと置くと NPV ≈375 k€（劣化考慮の 152 k€ の約2.5倍、+223 k€）。論文の「劣化なし」シナリオではない。

## 5. 著者が挙げる限界・今後の課題
- 完全予見（確率的・ロバスト最適化へ）、劣化は線形近似で温度・DOD の影響を単純化、収益源は裁定＋抑制緩和のみ（周波数調整・予備力・需要応答なし）、イタリア以外への一般化、ハイブリッド蓄電・新技術は対象外、実証検証。データは機密。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.2.3（併設研究：伊・実データ・MILP・抑制＋劣化）、第9章9.3.2（併設容量と抑制回避の対比）、研究計画v2 §4.2（劣化コストの限界費用への内生化、完全予見は上界）。
- 支持: (1) 併設蓄電池のマーチャント最適容量は小さい（≈0.10 kWh/kW）。容量を増やすと NPV は急落（2h 10MW/20MWh＝0.51 kWh/kW で −826 k€）。本研究の 0.64 kWh/kW（系統WG前提の FIP 併設）は探索範囲の外で、「補助で採算と無関係に入る競合ストック」という扱いと方向が整合。(2) 抑制率が高いほど併設 NPV・IRR は上がる（0.1→8.1% で NPV 58→227 k€）→ 抑制が頻発する北海道で抑制回避の寄与が大きくなる方向の外部根拠。(3) 劣化を内生化しないとサイクル過多で寿命が縮む（効率100%で8年EOL）。研究計画の「サイクル制約・劣化コストの限界費用への内生化」と同型。
- 容量比の並置（当方換算、風力 kW あたり）: Atherton（1MWh/≥50MW＝≤0.02、固定）、Grimaldi（最適 0.10）、Loukatou（0.24–0.95、最良は最小）、本研究の前提 0.64 kWh/kW。
- **注意（引用時）**:
  1. **NPV は BESS 単体勘定**（式30）。Table 5 の総純利益の差は +72 k€/年（+0.65%）で、BESS 純利益 190 k€/年との差 119 k€/年は充電に回した風力の売電収入減（機会費用）。Table 10 から NPV を再計算すると 151.3 k€（論文 151.72）と再現でき、機会費用は控除されていない。増分 +72 k€/年で計算すると NPV は約 −1.1 百万€（当方概算）。→ 「併設で NPV +152 k€」は「併設しない場合との差」ではない。引用は「BESS 単体キャッシュフロー基準」と限定する。
  2. **抑制回避率は報告されない**ので、9.3.2 の抑制回避可能率とは直接比較できない。比較は (i) 条件差（抑制率 2.2%、容量比 0.10）、(ii) 抑制率→NPV の感度、に限る。
  3. 抑制コストは「卸価格×失われた電力量」の機会損失として扱い、TSO 補償の有無を論じない。イタリアの抑制補償規則は別途一次資料で確認が必要（9.3 の制度3類型への当てはめに必須。未確認）。給電指令には保守由来の部分負荷も含み得る。
  4. 価格は PUN（需要側の全国単一価格）。発電側はゾーン価格で精算されるのが通例で、風力の多い南部・島嶼では PUN より低い可能性（論文外の一般知識、要確認。風力の所在地は非開示）。
  5. 単年（2023、年平均 127 €/MWh）の反復（推定）＋完全予見（上界）＋価格テイカー → 楽観方向の偏り。将来のスプレッド低下は考慮されない。
  6. マーチャント単一事業者の NPV 最大化であり、自由参入均衡容量 K* ではない。
  7. 本文と表の不整合: サイクル数（Table 9/12: 397、本文: 380）、CAPEX（Table 3: 353、§4.3.1: 350）、Table 11 の見出し（抽出テキストで欠落。本文の記述から対応付け）。
  8. 二次情報（論文が引く。原典未確認）: Rayit et al. (2021, J Energy Storage 39, 102641; 英国、抑制風力の活用) は抑制を5〜25%で動かし、15%超では抑制+1%で NPV +£4m・IRR +0.1%。Lobato et al. (2022, Sustain. Energy Grids Netw. 32, 100854; スペイン30MW風力) は併設の利益 15.74 k€/年（2週間観測）、最終年の利益は初年度比 −30.5%。Li et al. (2023, IEEE PES GM; 豪州、DRL) は抑制緩和＋裁定。
- 新規性チェック: 実風力データ＋15年 MILP＋サイクル劣化＋抑制緩和を含む併設の技術経済評価は既出。本研究は併設価値（裁定＋抑制回避）を、蓄電池の内生化・均衡容量・政策ウェッジ（F&O との差別化点）に接続する点が異なる。

## 7. 引用に使える原文
- "the highest net present value (NPV) of 152 k€ is achieved with a 1-h BESS of 4 MW / 4 MWh, while a 2-h BESS configuration with a size of 2 MW/4 MWh yields an NPV of 142 k€"（Abstract）
- "only the BESS cash flows are considered in the NPV definition, as the objective of the conducted techno-economic analysis is to determine the profitability of integrating a BESS into an existing wind farm"（§3.3.3）
- "Given that wind curtailment is a rare phenomenon (as indicated in Table 2, this case study considers a wind curtailment of approximately 2.2 % of the annual wind farm production), it was deemed reasonable to broaden the utilization of the BESS by incorporating wholesale energy arbitrage"（§4.2）
- "the NPV increases steadily from approximately 58 k€ at 0.1 % annual curtailed wind energy to around 227 k€ at 8.1 %"（§4.3.3）
- "Without considering battery degradation, profitability evaluations could be overly optimistic, potentially leading to misguided investment decisions"（§5）
- "A further aspect that distinguishes this work is its focus on wind curtailment mitigation, a factor rarely addressed in the literature"（§1.2）
- "the proposed method assumes perfect foresight of wholesale energy prices and dispatching orders"（§5）
