# Oeltz, D., & Pfingsten, T. (2025) Rolling intrinsic for battery valuation in day-ahead and intraday markets
- 書誌: Daniel Oeltz（Fraunhofer SCAI, Computational Finance）, Tobias Pfingsten（RIVACON GmbH）. arXiv:2510.01956v2 [q-fin.PR], 2025-10-29（プレプリント、全22頁、表紙は "October 2025"）。誌名・巻号・頁・DOI は PDF に記載なし（査読状況は PDF から不明）。
- 出所: Google Drive の PDF（fileId 1qVc0YBiC3Yp1C2y97FyLfebzWiiPzGa2、2510.01956v2.pdf）。2026-09-29 に Drive のテキスト抽出（read_file_content）で精読。各表の数値は本文中の記述（+9%、−14%、5/12/18%、約130・93 €/日 等）および表同士（Table 2 = Table 4 基準行 = Table 6 の1サイクル行 など）と突き合わせて整合を確認。PDF ページ画像での照合は、Drive のダウンロードが繰り返しセッション切れとなり未実施 → 式(10)の和の添字と Table 1 の単位は要目視。
- 以下、「本ノート算出」は本ノート作成者による検算・換算（論文は €/日と一部の % のみを報告）。「著者」は論文の著者。

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 中欧（ドイツ、EPEX Spot）の卸電力市場で、系統用蓄電池（in-front-of-the-meter）にとって、前日市場（DA）・当日オークション（IDA1）・連続当日市場（IDC）のどの入札戦略が収益的か。特に連続当日市場で実行可能な戦略を bid–ask スプレッド込みで評価するとどうなるか。
- 貢献（§1）: (i) 連続当日市場の現実的な取引戦略として rolling intrinsic を用い、取引データから bid/ask を構成して流動性制約を織り込む。(ii) DA・IDA1・IDC を組み合わせたマルチマーケット戦略を体系比較。(iii) bid-ask の作り方・取引頻度・商品粒度（15分/1時間）・C レート・サイクル制約への感応度を評価。rolling intrinsic 自体は Semmelmann et al. (2024)、Miskiw et al. (2025) に先行（著者も §1 で引用）。
- 主張（Abstract）: "multi-market bidding strategies consistently outperform single-market participation"。"maximum cycle limits significantly affect profitability ... more flexible strategies which relax daily cycling constraints while respecting annual limits can unlock additional value"。

## 2. データ・市場・期間
- 市場: EPEX Spot ドイツ。DA オークション（12:00 CET、1時間商品。15分化は2025年10月予定）、当日オークション IDA1（15:00 CET）、連続当日 IDC（15分商品を使用。納入5分前まで取引可、60分前まで国境を越えて板を結合、30分前以降はドイツ4TSO エリアに分離）。
- 期間: 2024-06-14〜2025-07-01（383日）の EPEX 取引データ（Fig. 2 の期間だけで当日取引30万件超）。
- 市場統計（§2.1、2024年、ドイツ）: 取引量は DA 291 TWh、IDC 91 TWh、当日オークション 11 TWh。ドイツ純消費 465 TWh（ENTSO-E）。IDC の流動性は納入直前の数時間に集中（Fig. 5）。ID AEP は各15分商品の直近 500 MW 取引の平均で、TSO が不均衡料金の構成要素に使う指標。
- 対象電池（Table 1）: エネルギー容量 SoC = 2、出力 P̄ = 2 / 1 / 0.5 の 1h / 2h / 4h 電池、SoC0 = SoC_T = 0.5、1日あたり最大サイクル数 1、充電効率 η+ = 97%、放電効率 η− = 98%（往復 ≈ 95.1%、本ノート算出）。Table 1 に単位はなく、§3 の定義から MWh/MW と解釈。**利益（€/日）は容量 2 MWh の電池1台あたり**で、2h 電池は 1 MW なので €/MW·日と同値（1h は 2 MW、4h は 0.5 MW）。

## 3. 手法（最適化問題、rolling intrinsic の再最適化頻度、bid-ask の作り方）
- 最適化問題（§3、式(1)–(6)）: SoC 遷移（充電 η+、放電 1/η−）、出力上限、同時充放電禁止（二値）、**スループット型サイクル制約 Σ c_i·Δt ≤ N_max^cycles·SoC（式(4)）**、日次で期末 SoC = 期首 SoC（式(5)）。目的は Δt·Σ(p^b_i·d_i − p^a_i·c_i)（式(6)）。価格×数量のみで、劣化費用・手数料・価格インパクトの項はない。年間サイクル保証は日次の等価制約に置き換える（脚注3）。
- **rolling intrinsic**（Semmelmann et al. 2024 に準拠）: 取引時点の格子 {t^T_j} で、その時点の bid/ask を観測して式(10)を解き直し、既存ポジション (c̄, d̄) との差分（residual c^r, d^r; 式(7)(8)）だけを約定。納入が始まった区間はポジションを確定して SoC0 を更新。実現済み充電量を織り込むようサイクル制約を式(9)に修正（Algorithm 1）。
  - **再最適化の頻度**: 基準は**5分ごと**（5分バケット）。比較として30分ごと。使う商品は15分商品が基準（流動性が高い）、比較で1時間商品。
- **bid/ask の構成**（式(11)(12)）: 直前バケット (t^T_{j−1}, t^T_j] の取引が N = 10 件以上なら bid = 取引価格の 20% 分位、ask = 80% 分位。10件未満なら bid = −4000、ask = +4000 €/MWh（取引不可）。50% 分位（bid = ask）は「スプレッドなし」の比較ケース。
- 戦略（§4）: DA（12:00 の DA オークション価格で最適化）、ID AUCT（IDA1）、ID ROLL（連続当日の rolling intrinsic）、X|Y（X で初期ディスパッチ、Y で再ディスパッチ）。ID AEP / ID1 / ID3 / IDFULL は事後定義の指標で**取引不可**、比較用ベンチマークのみ。DA と IDA1 は予測価格が必要と本文にある（p.14）が、バックテストは実現オークション価格で最適化しているように読める（予測誤差の扱いは明記なし）。
- 求解: EAO パッケージ（RIVACON 公開、github.com/RIVACON/EAO）。

## 4. 主要結果（数値を必ず。表番号を付す）
特記なき限り 2h 電池（1 MW/2 MWh）・1日1サイクル・2024-06-14〜2025-07-01 の日次平均利益（€/日）。DA 比 % と年換算（×365、k€/MW·年）は本ノート算出。

**Table 2（平均利益）と、単一市場 vs マルチマーケット**
- 単一市場: DA 228.75（年換算 83.5 k€/MW·年）、ID AUCT 287.09（DA 比 +25.5%）、ID ROLL 296.60（+29.7%、108.3 k€/MW·年）。
- マルチマーケット: DA|ID AUCT 285.30（+24.7%）、DA|ID ROLL 315.83（+38.1%、115.3）、ID AUCT|ID ROLL 340.93（+49.0%、124.4）、DA|ID AUCT|ID ROLL 339.15（+48.3%、123.8）。
- **DA 単独 → 最良マルチマーケットの差**: +112 / +110 €/日（ID AUCT|ID ROLL / DA|ID AUCT|ID ROLL）＝ +40.9 / +40.3 k€/MW·年（本ノート算出）。最良の単一市場（ID ROLL 296.60）比でも +14.9% / +14.3%。
- **「一貫して上回る」には例外がある**（本文 p.14 も認める）: DA|ID AUCT (285.30) は ID AUCT 単独 (287.09) と同水準（−0.6%）。DA を含む3段（339.15）は含まない2段（340.93）よりわずかに低い（−0.5%）。ただし DA を含む3段は中央値が高く（312.17 vs 306.04）、標準偏差が小さい（215 vs 310 €/日）、最大値も小さい（2,298 vs 4,958）。著者は「DA でも入札すれば約定リスクが減る」と述べるが定量化はしない。DA 単独の標準偏差が小さいのは「リスク調整後に良い」のではなく上側の利益幅が狭いため（p.16）。
- 事後指標（取引不可）: ID1 337.75、ID3 293.48、IDFULL 301.84、ID AEP 453.10。ID ROLL（実行可能）は ID1 の 87.8%、ID AEP の 65.5%、ID3 の 101%、IDFULL の 98%（本ノート算出）。著者: 「納入直前だけを含む指標ほど価格変動が大きく近似収益が高い。bid/offer スプレッドも反映されない」（§2.1）。

**Table 3（商品粒度、ID ROLL 5分）**: 15分商品 296.60、1時間商品 240.43。15分商品は +23.4%（逆に1時間商品は −18.9%。本文の "nearly 20% higher" は後者に近い丸め）。

**Table 4（bid-ask・頻度、ID ROLL）**: 基準（5分・20/80%分位）296.60。50%分位（スプレッドなし）323.37（基準比 +9.0%、つまり bid-ask の摩擦で −8.3%）。30分バケット 255.67（基準比 −13.8%、50%分位比 −20.9%）。

**Table 5（C レート＝継続時間）**: エネルギー容量 2 MWh 固定、出力 2/1/0.5 MW（DA / DA|ID AUCT / DA|ID AUCT|ID ROLL の €/日）。
- 1h: 241.25 / 318.88 / 401.44。2h: 228.75 / 285.30 / 339.15。4h: 198.31 / 234.07 / 274.54。
- 1h vs 2h（出力2倍）: +5%（DA）、+12%（DA|ID AUCT）、+18%（＋ID ROLL）（本文 p.17。本ノート検算 +5.5 / +11.8 / +18.4%）。理論上限（200%）を大きく下回る。2h→4h（出力半減）でも利益は −13 / −18 / −19% にとどまる（本ノート算出）。
- 出力1 MW 当たりの利益は継続時間が長いほど大きい（DA: 1h 120.6、2h 228.8、4h 396.6 €/MW·日）が、容量1 MWh 当たりでは短いほど大きい（DA: 120.6 / 114.4 / 99.2 €/MWh·日）（本ノート算出）。
- 当日市場を加える効果は短時間（高出力）ほど大きい: DA → フル3段で 1h +66.4%、2h +48.3%、**4h +38.4%**。DA 単独の価値はフル3段の 60%（1h）/ 67%（2h）/ **72%（4h）**（本ノート算出）。

**Table 6（サイクル制約、ID AUCT|ID ROLL、2h）**: 1サイクル/日 340.93、2サイクル 466.16（+36.7%）、3サイクル 530.13（+55.5%）、4サイクル 559.13（+64.0%）€/日。限界価値は 2回目 +125.2、3回目 +64.0、4回目 +29.0 €/日（本文: 1→2 で約130、2→4 で追加約93 €/日）。1サイクル制約は4サイクル時の価値の 61%（本ノート算出）。

**Table 7（年間サイクルの柔軟配分、事後の最適配分）**: 下位日の稼働を止め、増分の大きい日に2サイクルを充てる。停止可能日数 0% 340.93 → 5% 351.36 → 10% 352.15（最大）→ 15% 351.47 → 20% 349.50 → 25% 346.17 €/日。改善は最大 +3.3%（本文は「at most 3.2%」）。著者の結論: 年間サイクル総数を増やせば追加収益は無視できないが、総数を固定した柔軟配分の余地は小さい。追加サイクルは劣化・保証違反・後半年の柔軟性低下とのトレードオフ。

**季節性（Fig. 7–8）**: 冬季（10〜3月）は充電が昼から早朝へ、放電が夕方から午後〜午前遅くへ移る。rolling intrinsic はやや変動が大きいが基本形は同じ。

## 5. 著者が挙げる限界・今後の課題
- 確率的な予測を rolling intrinsic に組み込む（高次元のため deep hedging も候補）。
- 予備力・調整力市場との結合（本論文はエネルギー市場の裁定のみ。FCR/FRR に売った容量は裁定に使えない、§2.1）。
- 日次と年次のサイクル制約を統一的に扱う長期運用制約の研究。
- 本文で認めている前提: 保証は年間サイクルだが日次制約は「モデル簡略化」（p.19）。DA・IDA1 戦略には価格予測が必要（p.14）。指標ベースの結果はベンチマークで取引不可（p.13）。
- 明示されていない限界（本ノート所見）: 約1年（383日）・1市場・小規模電池（価格インパクト・出来高制約なし）。劣化費用・手数料・不稼働を含まない粗利。DA/IDA1 は実現価格最適化の可能性（予測誤差の扱い不明）。§4 冒頭の研究課題にある初期/最終 SoC への感応度は結果が示されていない。

## 6. 本研究との関係
- 引用予定箇所:
  - **第7章7.2（実行可能戦略の capture 率）**: 計画書v2 §4.2 の「完全予見LPに capture ratio のヘアカット（文献値で1〜3割）」の文献値として。本論文は完全予見LPとの比（capture 率そのもの）は報告していない。代わりに実行可能性の摩擦を分解して数値化している: bid-ask で −8.3%（50%分位比）、5分→30分で −13.8%（50%分位比では −20.9%）、15分→1時間商品で −18.9%、事後指標との比は ID1 88%、ID AEP 65%（取引不可指標が過大）。摩擦単独で1〜2割で、1〜3割の校正レンジの下側〜中央を支持（本ノート算出の比率）。
  - **第10章（スポット単独評価の保守性）**: DA のみの評価は、実行可能なマルチマーケット戦略（DA|ID AUCT|ID ROLL）の 60%（1h）/ 67%（2h）/ 72%（4h）。ドイツ 2024-25 年では、スポット単独評価はマルチマーケットより 28〜40% 低い（本ノート算出）。DA 完全予見的な評価に対して、実行可能な ID ROLL 単独でも +29.7% 上回る。
  - サイクル制約の感度（計画書 §4.2 の「1日1〜2サイクル」）: 2サイクルで +36.7% だが、サイクル総数を固定した柔軟配分は最大 +3.3%。1日1サイクル制約は、日次で縛る限り価値を大きく抑える（4サイクル比 61%）が、年間総数を動かさない再配分の効果は小さい。
- **示唆: スポット完全予見のLPは「実現可能収益の上界」ではない**。本論文では DA 完全予見的な最適化（228.75 €/日）を、実行可能な ID ROLL 単独（296.60）が上回る。市場を跨げば「スポット完全予見＝上界」は成り立たない。計画書の「完全予見は実現可能収益の上界」は「同一市場・同一価格系列内で」と限定して書く必要がある（DA が実現価格最適化かは要確認）。
- 支持: 日次サイクル制約・期末 SoC の置き方は本研究の LP 設定（サイクル制約 1〜2/日）と同型。mercier2023.md（DA 完全予見 MILP の正当化）に対し、DA 単独評価が当日市場を含む戦略より低いことを示す補完的な証拠。
- **引用時の注意**:
  - ドイツ（太陽光主導、流動性の高い IDC: IDC 取引量 91 TWh は DA 291 TWh の約31%、純消費の約20%）・2024-25 年の1サンプル。JEPX の時間前市場の流動性は本ノートでは未確認（一次資料で確認が必要）。+25〜49% などの比率をそのまま北海道に移植せず、方向と機構の根拠として使う。
  - 利益は粗利（劣化・手数料・不稼働・予備力収益なし）。€/日は 2 MWh 電池1台あたりで、1h/2h/4h は出力が異なる（2/1/0.5 MW）。€/MW·年への換算（×365）は本ノートの概算。
  - 「マルチマーケット＞単一市場」は平均で成り立つが、DA を含むか否かの差はほぼゼロ（−0.5%）。価値の大部分は当日市場（ID AUCT、ID ROLL）に由来し、DA の役割は主にリスク低減。要旨の "consistently" は文字通りには成り立たない（p.14 が例外を認める）。
  - 数値の細かな不整合: "nearly 20% higher"（15分 vs 1時間、実際は +23.4%／逆算 −18.9%）、"at most 3.2%"（Table 7 から +3.3%）。1h と 2h の比較は「出力2倍」の比較（本文の「1時間と2時間の間の増加」は 1h が 2h より高い意味）。式(10)の和の添字が抽出テキストで t_i < t^T_j と読める（将来の納入区間 t_i > t^T_j の誤記と思われるが未確認）。
  - プレプリント（v2）。第2著者の所属 RIVACON GmbH は企業で、参考文献 [10] は同社の実務ガイド。査読済み版が出たら書誌・数値を確認する。
- 新規性チェック: 連続当日市場の rolling intrinsic 評価やマルチマーケット入札は先行あり（Semmelmann et al. 2024、Miskiw et al. 2025、Löhndorf & Wozabal 2023）。本研究は JEPX スポット評価を基本にし、これらの文献値でヘアカットと上振れ幅を校正する位置づけ。
- 引用チェーン（未取得、要否を判断）: Löhndorf & Wozabal (2023, *Operations Research* 71(1), 1–22)、Semmelmann et al. (2024, *ACM SIGEnergy Energy Informatics Review* 4(4), 163–174)、Miskiw et al. (2025)、Hornek et al. (2025, arXiv:2501.07121)、Schaurecker et al. (2025)。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract (p.1): "Our analysis shows that multi-market bidding strategies consistently outperform single-market participation."
2. §4 (p.14): "An exception is observed in the case of the day-ahead bidding strategy followed by redispatching in the intraday auction, which achieves profit levels comparable to those obtained by directly dispatching based solely on the intraday auction prices."
3. §2.1 (p.6): "The choice of the index, however, constitutes a strong assumption for revenues, as shown in figure 2. The less time before delivery is included, the higher volatility generally is and the higher approximated revenues. In addition, bid/offer spreads are not reflected when using indices."
4. §4 (p.17): "A decrease of intraday trading frequency from 5 to 30 min intervals, which by construction also leads to an increase in bid-ask spreads, leads to a decrease of approximately 14% to a mean profit of 256 €/day compared to the base scenario with 297 €/day."
5. §4 (p.19): "A single cycle generates on average 340 €/day, whereas the incremental profit from a second cycle is only 130 €/day."
