# Landy, M., Schmidt, O., Johnson, N., & Staffell, I. (2026) Maximising the economic value of renewable and battery storage hybrids with revenue stacking
- 書誌: *Energy & Environmental Science* 19, 4469–4494（号数は PDF に記載なし）。DOI 10.1039/d6ee00776g（OA, CC BY 4.0）。受付 2026-02-04・受理 2026-06-17・公開 2026-06-19。Centre for Environmental Policy, Imperial College London（責任著者 I. Staffell）。付録1–14 は SI（DOI 先）
- 書誌の訂正: 依頼時の暫定題名（"…renewable and storage co-location"）は誤り。巻号は 19(13) と聞いていたが、PDF には巻（19）と頁（4469–4494）のみで号数の記載なし。library-check-list.md の E16 行は未更新（本ノート作成では他ファイルを変更していない）
- 出所: Drive fileId 1R5_MwLZz8dXrEfR81sijQzmsK1VjnVWF（d6ee00776g.pdf, 16MB）を read_file_content でテキスト抽出して精読（2026-09-29）。本文（PDF 26頁）を参考文献末尾まで通読。付録1–14（SI）は PDF に含まれず未読。図（Fig. 2–21）の数値はテキストに出ない。不確実点は §8 に集約

## 1. 問いと貢献（要旨）
- 問い: 再エネ（風力・太陽光）に蓄電池を併設すれば、出力を高価格時間へ移し、抑制を減らし、系統接続を共有できる、という通説的期待（Abstract 冒頭で "widely proposed"）が、どの市場・制度条件で経済的に成り立つか。ハイブリッドが単独再エネ・単独蓄電池より優位になる条件と、設計・運用を特定する。
- 用語（§2.3）: **co-located** = 系統接続を共有するが独立運用（本モデルでは RES が輸出優先、蓄電池は残りの接続容量で運用）。**full hybrid** = 一体運用（共同最適化、単一インバータ）。
- 結論（Abstract）: (a) 英国では、蓄電池が大きく黒字化するのは「グリッドから充電でき、かつ複数市場で収益をスタックできる」ときのみ。(b) 放電時間は4時間が最もコスト効率的。(c) 単独蓄電池は併設・ハイブリッドより収益が高くなりやすい。(d) 30か国の比較では、単独が有利なのは豪州・北欧・米国の大半、ハイブリッドが優位なのは欧州・Texas・日本の一部。収益性は立地（資源の質）より市場アクセスと運用制約に依存する。
- 貢献の主張（§2.5）: 既存研究の7つの空白（系統規模の評価、収益最大化、市場価格の考慮、多技術・多市場の比較、長期契約を含む複数市場、地域差、自己放電・劣化）を同時に埋める。運用最適化（LP）と容量探索の2段階モデルを、英国の収益スタッキング詳細ケースと30か国の卸裁定比較に適用。

## 2. データ・設定
- 英国詳細ケース: Lyneham Solar Farm（イングランド南部、英国の MW 級太陽光から無作為抽出）。南・北の2地点で感応度（年間利益は RES 設備利用率＝立地に依存するが、蓄電池等の最適規模は立地で変わらず。付録12）。卸（WS）・需給調整メカニズム（BM）・Dynamic Containment（DCH/DCL）の価格・約定量（系統運用者の公開データ）、30分値。基本設定は 100 MW の風力または太陽光＋100 MW の系統接続。風力の詳細は「概ね同様」として付録8–11。
- 国際比較: 30か国・45市場（米5・豪5・日本8・欧州は国単位で27）・252サブ地域。**卸裁定のみ**（他市場のデータが不揃いのため）。2023年の卸価格（CAISO, ERCOT, MISO, PJM, NYISO, ENTSO-E, NESO, **JEPX**, AEMO）。各サブ地域は実在の風力・太陽光発電所1件で代表（平均規模: 米198 MW・豪194 MW・欧118 MW・**日本32 MW**）、出力は Renewables.ninja の2023年気象による時間値の設備利用率（実績出力ではない）。**日本は市場が小さいためサブ地域に分けず1市場1サイト**。RES 資本費のみ GNESTE データベースの地域値、他の入力は全地域共通。国は高頻度の価格データがあるものから選択。
- 共通前提: 2023年の価格・出力をプロジェクト全期間に反復。割引率 8% 固定。蓄電池は暦年寿命13年・サイクル寿命4,500回・交換費＝初期 CAPEX の50%（式23）・日次サイクル上限あり。プロジェクト期間 N・費用・効率の数値は付録5【SI未読】。

## 3. 手法
- 2段階（Python、Google OR-Tools の GLOP による線形計画）: (1) 運用最適化＝規模を固定して収益最大化（WS・BM の売買、DC の予約、RES から蓄電池／系統への配分）、(2) 蓄電池容量の探索（目的関数が容量について凸として二分法）。
- 制約: 系統接続容量（全取引の双方向合計 ≤ Cap_g、式12）、蓄電池出力・SOC、暦年＋サイクル劣化（Hesse et al. 2017 型、SOH 80% 基準）、日次サイクル上限（保証条件の代理）。RES は卸価格が負なら出力ゼロ、接続容量超過分は抑制（式1–2）。
- 設定の軸: (i) 資産構成（単独蓄電池／RES 単独／PV＋蓄電池／風力＋蓄電池／PV＋風力＋蓄電池）、(ii) 運用形態（**co-located** = RES 輸出優先で、蓄電池事業者の利益を最大化。RES の基準収益を控除し、接続費 CAPEX_g は容量比で按分（式28）／**full hybrid** = 共同最適化。全資産の費用を計上（式29））、(iii) 接続形態（一方向＝RES からのみ充電／双方向＝グリッド充電・輸出可）と収益源（WS のみ／＋BM／＋DC）、(iv) RES の売り方（市場価格／固定価格 PPA・CfD／24/7ハイブリッド PPA）。
- 指標: NPV, IRR, 回収期間（PBP）、capture rate（RES の受取平均価格 ÷ 市場平均価格、式31–32）、grid usage（接続容量の利用率、式33–34）。価格・約定量は外生（価格受容者）。式は抽出で崩れているため引用時は原PDF（CLAUDE.md ルール5）。

## 4. 主要結果
（金額の通貨記号は抽出で「d」に化けている。英国ケースは £ と推定して転記、国際比較の金額は「d」のまま。§8-4）

- **英国・併設（co-located; 100 MW の RES＋100 MW 接続。図は太陽光 Lyneham 中心）**
  - 1h・100 MW 蓄電池の収益は、全市場参加＋グリッド充電で最大。co-located で黒字になるのは「グリッド充電あり かつ BM＋WS 参加」の2シナリオのみで、DC 参加は利益を僅かに増やす。全市場＋グリッド充電の最適容量は **252 MW**（RES の約2.5倍）、年間利益 **£4m**（大半が BM）。風力併設は全ケースで利益がやや低い（Fig. 4）。
  - 放電時間別: **4h・106 MW が最高利益 £8.5m/年**（424 MWh 相当、筆者換算）。長時間ほど黒字になる容量の範囲は狭まる（Fig. 5）。
  - 接続容量＝RES 容量（100 MW）の設定では余剰接続容量も抑制も乏しく、蓄電池は過少利用。**自前の接続を持つ単独設置のほうが高収益**（§4.1.1）。
  - RES/接続比を 0（＝単独蓄電池）〜2（太陽光）・〜4（風力）で動かした 1h の分析（Fig. 6）: 風力・太陽光とも**単独蓄電池の NPV が最大**。太陽光併設は比が低い・高いときに NPV が大きく、最適容量は 100–115 MW（夜間に接続が空き、昼の余剰を夜に売れる）。**風力併設は比が上がるほど NPV・最適容量とも低下**し、著者は比4でも "will never be profitable" と記す（§4.1.1 は風力併設も「同様の結果でやや低利益」としており、粒度が揃わない【要確認】）。正の NPV となる単独 RES 容量の上限は太陽光 <170 MW・風力 <440 MW。
  - Table 3（太陽光→蓄電池の年間移送量。co-located は負価格時のみ充電）: 1h 74.9 vs 完全ハイブリッド 18,001.5 MWh／2h 532.0 vs 30,008.1／4h 30,603.8 vs 37,496.2 MWh。
  - 運用: 収益スタック時の平均 1.21 サイクル/日、SOH 80% 割れは約10.2年（§3.4.2）。参考値として実運用は豪州平均 0.85、GB（2h）1.1 サイクル/日（Modo Energy 引用）。
- **英国・完全ハイブリッド（既設 RES 100 MW; Table 4）**
  - 全ての蓄電池容量で利益は完全ハイブリッド > co-located（Fig. 8a）。最適蓄電池も完全ハイブリッドが大（例: 太陽光 200 MW に 288 MW、Fig. 9）。co-located のように RES に優先されず、RES 出力を蓄電池経由で高価格時間へ移せるため。
  - Table 4（100 MW RES＋100 MW 接続、全市場＋グリッド充電、蓄電池 4h）。**単独 RES 2列（*印）は見出しと値の対応に疑義があり、印刷の見出し順のまま転記**【§8-3】。

| 指標 | 単独風力* | 単独太陽光* | 単独蓄電池 | 完全ハイブリッド太陽光 | 完全ハイブリッド風力 |
|---|---|---|---|---|---|
| 蓄電池容量 | — | — | 114 MW | 115 MW | 111 MW |
| IRR | 8.88% | 17.95% | 24.31% | 16.31% | 19.50% |
| NPV | £5.8m | £107.6m | £99.6m | £103.1m | £185.1m |
| 回収期間（年） | 15 | 7 | 5 | 8 | 6 |
| Capture rate | 93.7% | 96.4% | — | 97.2% | 100.5% |
| Grid usage | 14.9% | 35.3% | 53.8% | 61.7% | 71.1% |

  - 著者の読み: 蓄電池を足すと RES の capture rate と接続利用率が上がり、全指標が改善する（"Incorporating storage improves all economic indicators"）。ただし蓄電池開発者から見れば「接続が取れるなら単独設置が最高収益」（単独蓄電池 IRR 24.31%・回収5年）。
- **英国・新設（RES と蓄電池の同時最適化; 100 MW 接続; Fig. 10–12）**
  - 両者が市場に売る場合の最適は **太陽光 95 MW＋蓄電池 115 MW（NPV £103m）**、**風力 195 MW＋蓄電池 95 MW（NPV £217m）**。
  - RES が固定価格（PPA/CfD）・蓄電池は市場売り: 固定価格が高いほど RES 容量と利益が増える。蓄電池の最適容量は太陽光でほぼ不変、風力では減る（風力は日周パターンが弱く裁定機会が乏しいので、固定価格が上がると蓄電池より風力の増設が有利になる）。
  - 24/7ハイブリッド PPA（Table 5）: 黒字化の最低固定価格は太陽光 £120/MWh・風力 £100/MWh。蓄電池 100 MW、RES 98 MW（太陽光）／85 MW（風力）、一定出力 33／36 MW。PPA 出力のうちグリッド充電由来 34.9%／18.5%、RES から直接充電 2.2%／6.5%。
- **国際・完全ハイブリッド（卸裁定のみ、RES・蓄電池・接続とも 100 MW; Fig. 13–19）**
  - RES 開発者から見て蓄電池の追加が有利なのは一部地域のみ（単独 RES が最適な地域が大半）。有利な地域の最適蓄電池は太陽光で 80–120 MW（RES 容量の80–120%）、風力で 60–140 MW。IRR は Texas が最高、Victoria（豪州）が最低。卸のみだと豪州5州中 IRR>8% は2州のみ（負価格時間と低い RES 価格を裁定収益が部分的にしか補えない）。エストニア・ラトビア・リトアニアの太陽光も同様。多くの地域で 4h が最適。
  - 蓄電池開発者から見て（100 MW/4h に RES を足すか; Fig. 14・18）: **単独蓄電池が最適 = 豪州全域、米国（Texas 以外: PJM/MISO/CAISO/NYISO）、日本の大半、北欧**。ハイブリッド優位 = 欧州の多く・Texas。太陽光ハイブリッド優位 = Texas の大半・Chubu・南欧など日照が強く風が弱い地域。風力ハイブリッド優位 = オランダ・ベルギー・デンマーク・スコットランド・バルト・**北日本**など風が強く日照が弱い地域。単独が有利になるのは、価格変動が大きい地域か、RES の受取価格が低い地域（§4.4）。
  - ハイブリッド優位地域の最適 RES 容量（接続 100 MW あたり）: 太陽光 **215±5 MW**、風力 **160±15 MW**、太陽光＋風力の合計 **175±25 MW**。ほぼ全域で RES が接続容量を超え、蓄電池がピーク時の抑制を減らす。
  - 蓄電池資本費の上限（4h、太陽光ハイブリッドが卸裁定で黒字になる最大値、Fig. 15–16。通貨未確認 d）: 南豪 1,560/kWh、ノルウェー 60/kWh（水力との競合）、欧州 約250（イタリア・スイス）〜680（ルーマニア・バルト）、**日本 250（東京）〜520（九州）**。卸価格の標準偏差の対数とほぼ線形に相関（RES の設備利用率には依存しない）。
  - 必要な固定 PPA 価格（Fig. 17。通貨未確認 d）: 米欧日の大半で太陽光 60–80/MWh・風力 50–75/MWh、豪州は 25–45／35–55。NY 80–90、北欧>85、ノルウェー>120（太陽光）。日本・豪州・Texas・California では風力の必要価格は太陽光と同程度。
  - 卸のみで売る（merchant）資産は、ハイブリッドでも単独でも年間利益は小さいか負（§4.4, §5）。サイクルは 252地点の中央値 0.96 回/日（風力併設 0.91、太陽光併設 0.98）。
- **国際・併設（co-located; Fig. 20–21）**
  - 最適蓄電池容量が正（併設が成立）となるのは豪州・Texas・東欧。それでも単独蓄電池のほうが高収益な場合がある。太陽光は成立地域で概ね単独より高収益（例外: ラトビア・リトアニア・NSW・南豪）。風力は成立する地域が少なく、最適風力容量も太陽光より小さい。
  - 条件: **RES の初期接続利用率が約25–30%を超える地域では、併設は単独より不利**（蓄電池の運用余地が無い）。太陽光は夜間に接続が空くが、風力は接続が数日間混雑し続ける。
- **日本（JEPX）に関する記述の全量**（本文に Hokkaido の名指しはない）
  - 8市場・2023年 JEPX 価格・1市場1サイト（平均32 MW）・出力は Renewables.ninja の模擬値。Abstract は、ハイブリッドが優位なのは「日本の一部」。日本の大半は単独蓄電池が最適で、例外は Chubu（太陽光ハイブリッド）と北日本（風力ハイブリッド）。資本費の上限は東京 250〜九州 520/kWh（日本の最小〜最大と読める）。PPA 必要価格は、日本では風力が太陽光と同程度。
  - 【要確認】北日本が北海道を含むか、そこでの風力ハイブリッド優位が完全ハイブリッド（共同最適化）の結果か併設（輸出優先）の結果か。Fig. 14/18/20/21 の日本部分と付録13で確認。
- **著者の政策含意（§5–6）**
  - 蓄電池を再エネ収益の安定化装置とするなら、裁定・需給調整・補助サービスを分断された参加枠組みに閉じ込めず、収益スタックとグリッド充電を認める。認めなければハイブリッドは成立しにくい。
  - 一律のハイブリッド推進は不適切。"negative pricing, curtailment, and multi-market access coexist" する市場に絞る。トルコの2022年義務化（新設の風力・太陽光に定格容量と同量の蓄電池）は、全国一律の比率が出力特性次第で過小・過大となり、再エネの資本費を押し上げて参入を妨げうる。
  - 系統接続: 単独蓄電池が有利でも、併設は既存接続の利用で接続待ち・接続費用を避けられる。運用制約の機会費用と、接続までの時間短縮・待ち行列脱落リスク・接続費を比べる **connection-adjusted NPV** で評価すべき。
  - 契約設計（PPA）が採算性を左右する。24/7型は大きなグリッド充電に依存し、「24/7」の信頼性・炭素会計に含意がある。今後は、接続規則・network charges・規制上の「ハイブリッド定義」が収益スタックに与える影響の比較研究が要る。

## 5. 限界（著者の自認）
- （§3.8）2023年の価格・出力を全期間に反復（2022年の高価格なら最適容量は同程度でも NPV は大幅に増え、2020年の低価格なら容量・NPV とも大幅に減る。Fig. 3）／割引率 8% 固定（上げると最適容量・利益は低下）／効率・劣化の簡略化（交換間隔は暦年寿命のみ）／約定価格・量が確実に得られると仮定（入札の成否なし）／技術費用は現状固定／**抑制は接続容量超過だけを想定し、混雑・保守による追加制約は無し**。
- （§5）国際結果は卸のみで、需給調整・容量市場の収益が大きい地域では保守的。価格・量を外生とし、"at scale, storage and hybrids can compress spreads ... the private optimum may diverge from the system optimum once equilibrium feedbacks are included"。今後の課題として、複数年・将来シナリオ、**ネットワーク混雑起因の抑制**、内生的な価格効果、容量市場・ロケーショナル信号を含む多サービス最適化、劣化モデル、入札受諾確率を挙げる。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.2.3（併設研究の位置づけ。Atherton 2023 と対）、第9章9.3（併設蓄電池のローカル価値。9.3.2 の回避価値の上限、9.3.3 の BTM 参入条件）、価格受容者評価の限界を述べる箇所（第1章・第2章のギャップ提示）。E16 は Atherton 2023・Loukatou 2021・Maji 2025 を引用していない（参考文献に出現せず）ので、併設研究の独立した系統として並置できる。
- **【要修正】現行原稿 2.2.3 の E16 引用**（manuscript/02_literature.md 49行、thesis_draft_v0.1.md 162行）: 原稿は E16（"Energy & Environmental Science, 2026"）を「併設によるインバータと系統接続の共有が抑制と資本費を同時に削減する効果」の報告として引いている。しかしこれは E16 序論の背景記述（引用文献17–18 = Gorman et al. 2022, Canbulat et al. 2021 に帰属）で、E16 自身の結果ではない。E16 は抑制削減量も、接続・インバータの共有による資本費削減額も本文で定量しておらず（資本費の項目は蓄電池・太陽光・風力・系統接続のみで、共有インバータ費の項は見当たらない。付録は未読）、むしろ**英国では単独設置が併設を上回る**（接続を共有する節約 < 輸出優先による運用制約の収益損失）と結論する。修正案（原稿は未変更、提案のみ）: 「Landy et al. (2026) は英国と30か国45市場で、併設（RES 輸出優先）・完全ハイブリッド・単独設置を収益スタッキング付きの運用最適化で比較し、接続共有の節約は運用制約による収益損失を上回らないことが多く、単独蓄電池が最も高収益になりやすいこと、RES の初期接続利用率が25–30%を超える地域では併設は単独より不利になることを示した。併設が成り立つのはグリッド充電と複数市場での収益スタックが可能な場合に限られる」。
- 位置づけ: Atherton 2023 が英国47サイトの事後的なサイト別評価（裁定が回収の主因、抑制回避は上乗せ）であるのに対し、E16 は多市場・多国の運用最適化で「併設・一体・単独のどれが有利か」を制度条件ごとに示す。共通点は、併設の価値の主因が裁定・市場アクセスにあり、抑制回避や接続の共有は条件付きの上乗せにとどまること。
- **9.3 の3類型との対応**
  - ① 抑制回避: E16 の抑制は「卸価格が負のときの出力ゼロ」と「接続容量超過」だけ。指令・混雑による出力制御は対象外（§3.8。将来課題として "curtailment driven by network congestion"）。co-located は RES 輸出優先のため、RES から蓄電池へ充電できるのは負価格時間のみ（Table 3: 1h 74.9 MWh → 4h 30,603.8 MWh/年、太陽光・英国）。抑制削減が効くのは RES を接続容量より大きく置く場合（最適 RES 容量は接続 100 MW あたり太陽光 215 MW・風力 160 MW）。抑制削減量（%・MWh）の直接値は本文にない。→ 9.3.1 の「価格に映らない抑制（ローカル混雑）」は E16 の枠外で、著者自身が課題に挙げる論点。新規性の裏付けとして使える。9.3.2 の回避価値の上限は E16 では検証できない。
  - ② 接続費: 接続費 CAPEX_g は co-located では容量比で按分（式28）。除外資産の容量を0とする規定から、単独では蓄電池が接続費を全額負担、併設では容量比（RES 100 MW＋蓄電池 100 MW なら半分）と読める（推定）。C_g の値は付録5【未読】。結果は「新規接続を避けて節約できる費用より、接続容量をフルに使える運用の追加収益のほうが大きい」ため単独蓄電池の NPV が最大（Fig. 6）。併設の残る価値は接続待ち・接続費用の回避で、connection-adjusted NPV での評価を著者が推奨。→ 接続費の節約を「併設の上限価値」に置き、輸出優先による機会費用（風力は接続が数日間混雑）との差引で評価する整理の根拠になる。£/MW・% の数値は付録5を取得して補う。
  - ③ 系統利用料: 未モデル化。言及は §5 の "network costs" と、末尾の今後の課題 "network charges" のみ。→ E16 は根拠を与えない。先行研究に定量が乏しいことの傍証（著者が比較研究の必要性を明記）としてのみ使える。
- BTM 参入条件への含意（9.3.3）: 英国の co-located 蓄電池は、グリッド充電なしでは黒字にならない（§4.1.1）。BTM の π'_spot はグリッド充電の可否で大きく変わる。BTM を政策層（FIP 併設・併設要件）として外生に置く判断を支持する。風力は接続混雑で併設が成立しにくい（Fig. 6）が、これは英国・接続＝RES 容量・輸出優先の設定なので、北海道の風力併設へそのまま外挿しない。
- 規模の比較（筆者換算）: E16 の風力ハイブリッド最適規模は風力 1 kW あたり蓄電池 0.5〜1.4 kW（新設 95/195＝0.49、既設 111/100＝1.11、国際 60–140 MW/100 MW）。4h と読めば 2〜5.6 kWh/kW で、9.3.2 が用いた系統WGの併設前提（0.64 kWh/kW）の約3〜9倍。ただし E16 は卸裁定＋接続制約下の経済的最適で、抑制吸収のみの規模ではない。
- 均衡との接続: 著者が「均衡フィードバックを含めると私的最適は社会的最適から乖離しうる」と明記（§5）。併設研究が価格受容者評価であることの自認として、第2章のギャップ（蓄電池の内生化・均衡容量）の提示に使える。"fully merchant storage usually marginal or loss-making when restricted to wholesale markets"（§5）は、純市場の K*=0（第8章）と同方向。
- 政策ウェッジの事例: トルコ2022の同容量併設義務、分断された市場参加枠組み、グリッド充電の制限（§5）。
- 日本の先行結果: JEPX 8市場・2023年・卸裁定のみで、日本の大半は単独蓄電池が最適、北日本のみ風力ハイブリッド優位（§4 日本の項）。単独蓄電池が有利という結果は、本研究が FTM 単独を主軸（第8章）に置くことと整合する。資本費の上限（東京 250〜九州 520/kWh）は、通貨を確定して円換算すれば表9.1（資本費 2.3–6.8万円/kWh）と比較できるが、E16 は割引率 8%・暦年寿命13年（＋交換費50%）で、本研究の WACC 6%・20年 CRF と前提が違い直接には比べられない。
- 追跡候補（E16 が併設の便益の根拠として引用）: Gorman et al. (2022, *Energy Econ.* 107, 105832)、Canbulat et al. (2021, *Energies* 14, 1691)（参考文献17・18）。
- 新規性チェック: E16 は価格受容者の運用最適化で、風力主導市場の均衡容量・政策ウェッジ・ローカル抑制の価格への不可視性は扱わない。日本は45市場の一部（1市場1サイト）として登場するのみ。本研究（風力主導・北海道・均衡容量・ゾーン価格で価格に映らない抑制）との差別化は維持できる。

## 7. 引用に使える原文
- "storage only becomes strongly profitable when it can both charge from the grid and stack revenues across markets. Four-hour discharge duration was most cost-effective, and stand-alone storage tends to be more profitable than co-located or hybridised systems."（Abstract）
- "For both solar and wind in the UK, a stand-alone storage system achieves the highest NPV, as full use of the grid connection capacity allows BESS dispatch to be prioritised and operations to be optimised, generating greater additional revenues than the costs saved by avoiding the installation of a new grid connection."（§4.1.3）
- "For BESS co-located with wind, the BESS will never be profitable, even at an RES-to-grid ratio of 4, because higher wind capacity leads to more congestion in the grid connection, further limiting BESS dispatch."（§4.1.3。§4.1.1 との粒度差に注意、§8-9）
- "The greatest opportunities for co-location exist where grid connections are under- or over-built, benefitting from either spare grid connection capacity to optimise operations without paying for the grid connection or free electricity from the co-located generator that would otherwise be curtailed."（§4.1.1）
- "Co-location is economically attractive only when the savings from sharing a grid connection outweigh any revenue losses arising from operational constraints. In regions where initial grid utilisation exceeds 25–30%, co-located configurations are generally less favourable than stand-alone systems."（§4.5）
- "co-location can still bring value where using an existing grid connection avoids lengthy connection queues and network costs. Project appraisers should evaluate the connection-adjusted NPV of projects, balancing the opportunity cost of restricted dispatch against the reduced time to connect, queue attrition risk, and cost of connection."（§5）
- "Storage tends to be underutilised if the co-located renewable asset has export priority or if storage is limited to a single revenue stream. The general intuition that hybridisation stabilises renewable revenues is true, but we find it is conditional."（§5）
- "the model assumed curtailment only when renewable output exceeded grid connection capacity. In reality, grid operators may impose additional constraints due to congestion or maintenance, which would reduce revenues and profits."（§3.8）
- "at scale, storage and hybrids can compress spreads and reshape balancing needs, so the private optimum may diverge from the system optimum once equilibrium feedbacks are included."（§5）
- "the use of a nationwide fixed ratio will lead to under- and over-sized batteries depending on the output profile of the renewable asset they co-locate with. More broadly, mandating co-located storage increases the capital cost of renewables projects which could in turn deter developers."（§5、トルコの義務化）
- "In windy but low-sun regions, such as the Netherlands, Belgium, Denmark, Scotland, the Baltics, and northern Japan, the reverse is true."（§4.4。"the reverse" = 風力ハイブリッドが単独蓄電池より優位）

## 8. 引用時の注意（確認範囲・未確認点）
1. 確認範囲: 本文はテキスト抽出（約10.5万字）で参考文献末尾まで通読。付録1–14（SI: 全パラメータ・サイト一覧・風力の詳細・追加2地点・地域ケース）は PDF に無く未読。図の値（Fig. 2–21）はテキストに出ないので、地域別の IRR・容量・閾値は原PDFの図を目視で確認する。
2. Hokkaido: 本文は名指ししない（出現するのは Chubu・Tokyo・Kyushu・northern Japan のみ）。日本8市場の内訳は付録13【未読】。
3. **Table 4 の列見出し**: 抽出テキストの見出し順は「単独風力・単独太陽光・単独蓄電池・完全ハイブリッド太陽光・完全ハイブリッド風力」。しかし (i) Grid usage 14.9%／35.3% は太陽光／風力の設備利用率の水準に見え、見出し順だと逆になる。(ii) 見出し順のままだと完全ハイブリッド太陽光（IRR 16.31%・NPV £103.1m・回収8年）が単独太陽光（17.95%・£107.6m・7年）より悪化し、本文 §4.2 の "improves all economic indicators" と矛盾する。(iii) 正の NPV となる単独 RES の容量上限（太陽光 <170 MW・風力 <440 MW、§4.1.3）は、100 MW で NPV £5.8m の風力とは整合しにくい。→ 単独 RES 2列は技術ラベルが逆（左＝太陽光・右＝風力）の可能性が高い（推定）。ハイブリッド2列と単独蓄電池列は本文（§4.3: 太陽光 £103m／風力 £217m）と整合する。原PDFの表で確認するまで、単独 RES の数値は風力・太陽光を特定して引用しない。
4. 通貨記号: 抽出では £・$・€ がすべて「d」に化け、本文中に £・$ の出現がゼロ。英国ケース（Table 1 の "d per MWh"、BM・DC など英国市場）は £ と推定。国際比較の資本費閾値・PPA 価格は £ か US$ か不明。引用前に原PDFで確認。
5. その他の化け文字: 「B」＝「~」（"B30%"＝約30%、"Bd250"＝約250）、「o」＝「<」（"o170 MW"＝<170 MW、"o0.95 cycles"＝<0.95）、"215±5 MW" の「±」も化けた記号を読み替えたもの。式・係数は崩れているので、引用は原PDFで（CLAUDE.md ルール5）。
6. 書誌: 号数は PDF に無い（RSC 表記は "Energy Environ. Sci., 2026, 19, 4469"）。依頼時の「19(13)」は未確認。
7. 適用範囲: 2023年1年の反復、価格受容者、国際比較は卸のみ（著者も保守的と自認）、割引率 8%・暦年寿命13年（本研究の WACC 6%・20年 CRF と前提が異なり、資本費の上限は直接比較不可）、日本は1市場1サイト（平均32 MW）で Renewables.ninja の模擬出力。
8. 用語: E16 の "co-located" は「RES 輸出優先＋接続共有＋独立運用」で、日本の BTM 併設（FIP 併設・併設要件）とは制度が異なる。"curtailment" は負価格時の出力ゼロと接続容量超過であり、指令・混雑による出力制御ではない。英国は単一価格帯で、抑制の補償制度も日本と異なる（Atherton ノート参照）。
9. 風力の数値: 英国詳細ケースの本文の図表は太陽光（Lyneham）が中心で、風力は「概ね同様」として付録8–11に回されている。風力併設の数値は §4.1.3（比4でも赤字）・Table 4 の風力列・§4.3 に限られる。§4.1.1（Fig. 4d: 風力併設も黒字でやや低利益）と §4.1.3（"never be profitable"）の記述の粒度が揃わないため、"never" を強い主張として写さない（「単独より有利にならない」の意と読むのが自然、推定）。
