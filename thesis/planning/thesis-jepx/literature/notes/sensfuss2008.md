# Sensfuß, F., Ragwitz, M., & Genoese, M. (2008) The merit-order effect: A detailed analysis of the price effect of renewable electricity generation on spot market prices in Germany
- 書誌: *Energy Policy* 36(8), 3086–3094. DOI 10.1016/j.enpol.2008.03.035（Received 2008-01-18／Accepted 2008-03-25／Online 2008-06-06）。所属: Fraunhofer ISI（Sensfuß, Ragwitz）、Univ. Karlsruhe (TH) IIP（Genoese）。
- 書誌の照合状況: DOI・誌名・巻・年・頁は PDF 本文（p.3086 のヘッダ・脚注）で確認済み。**issue 番号 (8) は PDF に印字なし**（library-check-list.md E9 の 36(8) を踏襲）。Würzburg et al. (2013) の参考文献欄も「Energy Policy 36, 3086–3094」で一致（issue は不記載）。Crossref での外部照合は api.crossref.org が組織のエグレス制限で 403 となり未実施。
- 出所: Drive 格納PDF（`1-s2.0-S0301421508001717-main.pdf`、fileId 1483NF79uvV9qZjlljsdBFQg-52kBvZwo）を Drive 経由でテキスト抽出して 2026-09-29 精読。**抽出テキストでは「€」が「h」に化ける**ため、本ノートは € に復元して記す。式・表の数値を引用するときは原PDFで最終確認（CLAUDE.md ルール5）。頁は雑誌頁（3086–3094）。

## 1. 問いと貢献（著者の主張する新規性）
- 要旨: ドイツの固定価格買取（EEG）で優先買取される再エネ発電が卸スポット価格を下げる効果を、エージェントベースの市場シミュレーション（PowerACE）で定量化。短期には発電事業者の利潤を減らして需要側へ移す**分配効果**で、2006年は「MOE の総額が、消費者が負担する再エネの純支援額を上回る」（Abstract）。
- 用語の定義: 再エネ電力は供給会社が事前に買い取るため、市場で調達すべき残余需要が減る（前日市場の視点では需要は非弾力）。よって再エネの優先買取は「需要の減少」として働き、価格が供給曲線（メリットオーダー）に沿って下がる。「この効果を本論文では merit-order effect と呼ぶ」（§1, p.3087, Fig.1）。供給曲線が右上がりである限り価格は下がる。
- 貢献: 単純な供給曲線モデル（Bode & Groscurth 2006）や単変量の統計分析（Neubarth et al. 2006）に対し、時間別・発電所単位の詳細シミュレーションで、年別（2001, 2004–06）の**総額**と、燃料・CO2・再エネ量・発電所構成への感応度を示した点（§1, §4）。

## 2. データ・市場・期間
- ドイツ（単一市場。越境取引は扱わない閉鎖系）。シミュレーション対象は 2001・2004・2005・2006 年、各年 8,760 時間のスポット価格（§2）。
- PowerACE を較正して使用（Sensfuß 2007 博論、Genoese et al. 2007）。火力・揚水は可変費＋起動費で入札、需要と再エネは価格非弾力で入札。**全需要がスポットで取引されると仮定**（実際に 2006 年にスポットで取引されたのは約 89 TWh＝需要の 16.5%、EEX）。基礎条件から価格を作るため実際より変動が小さく、この点で「保守的」と主張（§2, p.3087）。
- 対象の再エネは EEG 支援分。大型水力は支援の影響外として両ケースに含める。年末の設備容量が年間稼働すると仮定するため、シミュレーション発電量は公表値とずれる（2006年 52.2 TWh, Table 1 注）。支援額・平均買取価格は VDN (2007)。
- 燃料価格（Table 2, €/MWh, 2001→2006）: ガス 14.25→21.69、石炭 6.93→7.98、褐炭 3.8 で一定、石油 16.02→32.15。

## 3. 手法
- 各年について「EEG 再エネあり」と「なし」を各 50 回シミュレーション（発電所の故障に使う乱数の影響を平均化）し、平均時系列同士を比較（§2）。
- 式(3.1): v = Σ_{h=1}^{8760} (x_h − p_h)·d_h（d: 総需要 MWh、p: 再エネ込み価格、x: 再エネなし価格、v: MOE 総額 €）。式(3.2): s = v / r（r: 再エネ発電量 MWh、s: 再エネ1MWh当たりの MOE）（§3, p.3088）。
- 感応度: 2006年について 42 シナリオ×50 回＝2,100 回（データ約 20 GB）。燃料価格±20%、再エネ容量 60〜140%、希少性マークアップ、CO2 価格 0〜40 €/t、発電所構成（廃止・休止容量を再エネ起因とみなすシナリオ）（§4）。
- 年ごとに較正が異なる（Table 12 注）: 2004 は CO2 価格なし、2005 は織り込み率 ガス100%/石炭85%/褐炭70%、2006 は 100%/100%/20%。マークアップは全年で不採用。

## 4. 主要結果
- **Table 1（p.3089）**
  | 年 | 再エネ発電量 TWh | 平均価格低下 €/MWh | MOE 総額 bn € | 再エネ1MWh当たり €/MWh | 平均買取価格 €/MWh |
  |---|---|---|---|---|---|
  | 2001 | 24.3 | 1.7 | 1.07 | 44 | 86.9 |
  | 2004 | 41.5 | 2.5 | 1.65 | 40 | 92.9 |
  | 2005 | 45.5 | 4.25 | 2.78 | 61 | 99.5 |
  | 2006 | 52.2 | 7.83 | 4.98 | 95 | 109 |
- **2006年**: 平均価格低下 **7.83 €/MWh**（結論では「unweighted average」7.8）、MOE 総額 **約 4.98 bn €**（結論では「約 5 bn €」）、再エネ1MWh当たり 95.4 €/MWh（平均買取価格 109 €/MWh に対し約 87%、筆者計算）。同比は 2001年 51%、2004年 43%、2005年 61%（筆者計算）。総額は 2001→2006 で約 1 → 約 5 bn €（§6）。
- **賦課金（純支援額）との比較**（p.3086, p.3093）: 2006年の支援額 5.6 bn €（2001年 1.6、VDN）。再エネの市場価値は約 2.5 bn €（支援額の約 45%; Wenzel & Diekmann 2006 では 44 €/MWh＝2.3 bn €）。系統増強・系統サービスの追加費用は 1〜10 €/MWh（約 52〜520 百万€、Auer et al. 2006; Klobasa & Ragwitz 2006）で別扱い。§6: 支援額から市場価値と MOE（最大 5 bn €）を差し引くと消費者に純利得が生じる。
- **該当箇所**（「MOE が賦課金負担を上回る」）: Abstract 末文（p.3086）と §6 最終段落（p.3093）。§1 に算式の材料（支援額と市場価値）がある。
- **時間帯別の大きさ**（Fig. 2–3, p.3087–3088）: 2006年10月の1日で再エネ出力 4.4〜14.7 GW、価格低下は低負荷時 0 €/MWh、ピーク需要時に最大 36 €/MWh。理由はメリットオーダー曲線の傾きが高需要域ほど急なため。
- **感応度**（Table 3–7, p.3088–3090）:
  - 燃料（±20%）: ガス −20% で MOE −30%、+20% で +26%（最大）。石炭は逆向きで −20% で +11%、+20% で −9%（符号は本文の記述による。Table 3 は符号なし）。褐炭・石油は 2% 以内、原子力は 0。効果を決めるのは石炭とガスの価格比（供給曲線の傾き）。
  - 再エネ量（Table 4）: 発電量 60/80/100/120/140%（31.3〜73.1 TWh）に対し MOE は 66/86/100/118/131%。+40% で +31% とほぼ比例だが、低負荷域で曲線が平坦なため増分は逓減。
  - 希少性マークアップ（Table 6）: 加えると 2005年 2.78→3.41、2006年 4.98→5.69 bn €（+0.63／+0.71）。実証的検証がなく本分析では不採用。
  - CO2 価格（Table 7）: 0→40 €/t で MOE は約 −16%。石炭が上位へ移って肩・ピークの傾きが緩む燃料転換効果が、技術内の効率差による傾き増を上回る。
  - 発電所構成（Table 11, p.3092）: 火力の廃止・休止が再エネ起因だと仮定した場合の 2006年 MOE は 5.01（廃止のうち運転30年未満 2.7 GW）→ 3.6（40年まで 5.4 GW）→ 2.84（廃止全部 6.4 GW）→ 2.1 bn €（廃止＋休止 9.0 GW）。
  - 結論（§6）: 「2006年の MOE が 3〜5 bn €のオーダーである」ことは頑健。
- **既存推定との比較**（§5, Table 12, p.3092–3093）: 本論文 2004年 2.5、2005年 4.25、2006年 7.83 €/MWh に対し、Bode & Groscurth (2006) は 3.17（2005年相当へ換算、元は 36.7 TWh・CO2 0 €/t で 2.4）、Neubarth et al. (2006) は 6.08（1.89 €/MWh per GW の風力を 18.4 GW に換算）。Morthorst (2007, デンマーク) と Neubarth (2006, 独) の風力による価格低下 12〜15% と「同程度」と評価。

## 5. 著者が挙げる限界・今後の課題
- 全需要がスポット価格で取引される仮定（実際は 16.5%）。相対契約は変動が小さいと想定（§2）。
- 閉鎖系: 再エネが輸出入を変え、MOE の一部が国外へ波及しうる。欧州規模の時間別シミュレーションが必要（§6）。EU-ETS との相互作用も今後の課題（§1）。
- 発電所構成は基準ケースで固定。2006年までは過剰設備と低価格で再エネが新規投資を抑えたとは言えないと議論（§4.5.1）し、廃止・休止は感応度で確認（§4.5.2–4.5.3）。
- 希少性マークアップの検証不足。将来年の MOE の推定方法（§6）。
- 卸の節約が小売に転嫁されるかは競争度、とくに需要家市場に依存（§6）。

## 6. 本研究との関係
- 引用予定箇所: 第2章の MOE 節（定義と水準効果の起点）。節番号は既存ノートで 2.1〜2.3 に揺れがある（Ketterer/Woo は 2.1、Hirth は 2.2、日本の MOE の系譜は 2.3）ため要確定。research-plan.md §1.1 の「メリットオーダー効果; Sensfuß et al. 2008」の出典にあたり、v1-research-full.json の「Sensfuß 2008 が原点」もこの論文。
- 支持: (i) 価格低下は「その時間の残余需要位置での供給曲線の傾き」で決まり、低負荷 0、ピーク 36 €/MWh と時間帯で不均一（Fig. 3）。(ii) 傾きは石炭・ガス価格比と CO2 価格で変わる＝供給スタックと燃料費に依存（v2 計画のユニット単位メリットオーダーと同じ発想）。(iii) 短期は生産者→消費者への移転で、廃止・休止など容量調整が起きると効果は 5.0→2.1 bn €まで縮む（Table 11）＝容量の内生調整を扱う本研究の動機づけ。Würzburg et al. (2013) の「移転であり投資シグナルを弱める」という整理とも一致。
- **対比・注意**:
  - 本論文の MOE は価格の**平均水準**への効果。日内形状（TB4h）や変動性は被説明変数ではない（Fig. 3 は1日の例示のみ）。
  - 蓄電池は明示しない（揚水は入札に含む）。発電所構成は外生シナリオで、参入・退出を均衡として解くものではない。
  - 説明の書き分け: Sensfuß は「優先買取＝残余需要の減少（メリットオーダー上の移動）」、research-plan の「供給曲線を右にシフト」は Würzburg らの説明に近い。同値だが、引用時はどちらの言い方かを区別する。
- **引用時の注意**:
  1. 「原点」と書くときは、本論文が「この論文では merit-order effect と呼ぶ」と定義しドイツで定量化した代表研究という意味に限る。Würzburg et al. (2013, p.S159) は理論的着想を Jensen & Skytte (2002) に帰している。
  2. 総額 4.98 bn €は「全需要がシミュレーション価格で取引されたと仮定した場合の仮想の移転額」で、実現額ではない。平均低下 7.83 €/MWh は**単純平均**で、総額から逆算した需要加重の低下幅とは別物（4.98 bn €÷約 539 TWh≒9.2 €/MWh。539 TWh は 89 TWh÷16.5% の筆者逆算）。
  3. 「MOE＞賦課金」は基準ケースで成立。純支援額は 5.6−2.5≒3.1 bn €（筆者計算）で、頑健範囲 3〜5 bn €の下端ではほぼ同額、Table 11 の Step III/IV（2.84／2.1）では下回る。論文は Step III/IV を「very unlikely」とする。引用は「2006年・短期・卸の節約が転嫁される場合」の条件付きで。
  4. 2006年はガス価格が高い年で MOE が最大化（2001→2006 で 1.07→4.98 bn €）。年次依存が大きく一般化しない。再エネは需要の約1割（52.2 TWh÷539 TWh、筆者計算）の水準の推定で、風力主導・高浸透の市場への直接の外挿は不可。年ごとに較正条件も異なる（本ノート §3 末）。
  5. Würzburg et al. (2013) の Table 2 は本論文の値を €/MWh per GWh に換算して収録（2006年 −1.34）。換算値を引く場合は wurzburg2013.md の注意（表内の不整合）を参照。
- 新規性チェック: 独の MOE を時間別シミュレーションで示した先行例。本研究は（a）風力主導・単一価格ゾーンの北海道、（b）日内形状（TB4h）と帯域分解、（c）蓄電池の内生化と自由参入均衡へ進む点で異なる。

## 7. 引用に使える原文（€ は抽出時の文字化けを復元）
- "In the case of the year 2006, the volume of the merit-order effect exceeds the volume of the net support payments for renewable electricity generation which have to be paid by consumers."（Abstract, p.3086）
- "As this effect shifts market prices along the German merit-order of power plants this effect is called merit-order-effect in this paper."（§1, p.3087）
- "It is assumed that the entire electricity demand is traded at the simulated spot market."（§2, p.3087）
- "The results indicate a considerable reduction of the average market price by 7.83 €/MWh in the year 2006. In total the volume of the merit-order effect reaches its highest value in the year 2006 with about 4.98 billion €."（§3, p.3088）
- "the claim that the merit-order effect for the year 2006 reaches a considerable volume in the order of magnitude of 3–5 billion € is robust."（§6, p.3093）
- "If the market value of renewable electricity and the potential savings for consumers created by the merit-order effect are taken into account the feed-in support can lead to a net profit for consumers in the short run. Whether the savings created on the wholesale market are passed on to consumers heavily depends on the competitiveness of the electricity supply system, especially the consumer market."（§6, p.3093）
