# 図書館アクセスで確認する文献リスト（2026-09-29）

**状況（2026-09-29 夕）**: ユーザーが Drive フォルダ `1dPuGAp7oyQaN6gbSyrl_4rCgK4iOdmFv` に B 欄11件（E5〜E7, E9〜E16）と D 欄2件（自然エネルギー財団コラム、OCCTO 2025年度約定結果）を格納。**E8・E17 と D 欄の残り（METI 検討会資料、Modo/CAISO）は未取得**。格納分は精読ノート作成中（`notes/`）。

用途: 本セッションの環境から本文を取得できなかった文献（Web検索の抄録・スニペットのみで把握）と、原典を精読したが最終確認が必要な箇所。確認後は `doi-list.md` に編入し、PDF は Drive `参考研究_20260728` に **SetE（追加）** フォルダを作って保存してください（ファイル名は `著者年_短い題名.pdf`）。

## A. 原稿で既に引用中・本文未確認（最優先）【E1〜E4 は 2026-09-29 に原典確認済み → notes/ に精読ノート、doi-list セットE】

| # | 検索用 | 誌名・巻・DOI | 確認したい点 |
|---|---|---|---|
| E1 | Tselika, K. (2022). The impact of variable renewables on the distribution of hourly electricity prices and their variability: A panel approach | *Energy Economics* 113, 106194. doi:10.1016/j.eneco.2022.106194 | 対象（DK/DE 2015–20）、MMQR の仕様、「日次時系列は MOE を過小評価」「太陽光は高需要時に不確実性を減らす」の該当箇所と数値 |
| E2 | Emmanuel, M., & Denholm, P. (2022). A market feedback framework for improved estimates of the arbitrage value of energy storage using price-taker models | *Applied Energy* 310, 118250. doi:10.1016/j.apenergy.2021.118250 | 100 MW 刻み・1,000 MW まで、PJM/CAISO、過大評価の大きさ（%）、4h・η80% |
| E3 | Atherton, J., Akroyd, J., Farazi, F., Mosbach, S., Lim, M. Q., & Kraft, M. (2023). British wind farm ESS attachments: curtailment reduction vs. price arbitrage | *Energy & Environmental Science* 16. doi:10.1039/D3EE01355C（Cambridge C4E preprint 305 も可） | 47サイト、回収の主因が裁定、スコットランドで抑制削減大、回収年数の数値、巻・頁 |
| E4 | Maji, D., Irwin, D., Shenoy, P., & Sitaraman, R. K. (2025). A first look at node-level curtailment of renewable energy and its implications | *Proc. ACM e-Energy '25*. doi:10.1145/3679240.3734627 | 「20%のノードが抑制の77%」「74.3%が混雑起因」の該当箇所、LMP による要因識別法 |

## B. 補助的に引用予定・本文未確認【E5〜E7, E9〜E16 は Drive 格納済み（2026-09-29）→ 精読ノート作成済み。E8・E17 は未取得】

| # | 検索用 | 誌名・巻・DOI | 確認したい点 |
|---|---|---|---|
| E5 | Loukatou, A., Johnson, P., Howell, S., & Duck, P. (2021). Optimal valuation of wind energy projects co-located with battery storage | *Applied Energy* 283, 116247（要確認）. doi:10.1016/j.apenergy.2020.116247（要確認） | 巻・番号、「補助なしでは不採算」の結論、手法（動的計画） ｜状況: 精読済み → `notes/loukatou2021.md` |
| E6 | Shen, D., Ilic, M., & Parsons, J. (2026). Peak-load pricing and investment cost recovery with duration-limited storage | arXiv:2603.13678（OA） | 命題（ピークイベント単位の費用回収、最適規模なら回収保証）の番号と条件 ｜状況: 精読済み → `notes/shen-ilic-parsons2026.md` |
| E7 | Oeltz, D., & Pfingsten, T. (2025). Rolling intrinsic for battery valuation in day-ahead and intraday markets | arXiv:2510.01956（OA） | 「マルチマーケット＞単一市場」「サイクル制約」の数値 ｜状況: 精読済み → `notes/oeltz-pfingsten2025.md` |
| E8 | 蓄電池事業者が参加する同時市場における市場参加者の損益評価手法 | *電気学会論文誌B* 146(2), 125–（2026）. doi:10.1541/ieejpes.146.125（J-STAGE） | 著者名、要旨、プライスメーカーとしての扱い ｜状況: 未取得 |
| E9 | Sensfuß, F., Ragwitz, M., & Genoese, M. (2008). The merit-order effect: A detailed analysis of the price effect of renewable electricity generation on spot market prices in Germany | *Energy Policy* 36(8), 3086–3094. doi:10.1016/j.enpol.2008.03.035 | MOE の原典として書誌確認のみ ｜状況: 精読済み → `notes/sensfuss2008.md` |
| E10 | Würzburg, K., Labandeira, X., & Linares, P. (2013). Renewable generation and electricity prices: Taking stock and new evidence for Germany and Austria | *Energy Economics* 40, S159–S171. doi:10.1016/j.eneco.2013.09.011 | レビューとしての書誌確認のみ ｜状況: 精読済み → `notes/wurzburg2013.md` |
| E11 | St. Martin, C. M., Lundquist, J. K., & Handschy, M. A. (2015). Variability of interconnected wind plants: correlation length and its dependence on variability time scale | *Environmental Research Letters* 10, 044004（OA） | 相関距離の時間スケール依存の数値（第6章6.4 の λ 校正に使用） ｜状況: 精読済み → `notes/st-martin2015.md` |
| E12 | Handschy, M. A., Rose, S., & Apt, J. (2017). Is it always windy somewhere? Occurrence of low-wind-power events over large areas | *Renewable Energy* 101, 1124–1130. doi:10.1016/j.renene.2016.10.004 | 低風力イベントの同時発生の数値 ｜状況: 精読済み → `notes/handschy2017.md` |
| E13 | Malvaldi, A., Weiss, S., Infield, D., Browell, J., Leahy, P., & Foley, A. M. (2017). A spatial and temporal correlation analysis of aggregate wind power in an ideally interconnected Europe | *Wind Energy* 20(8), 1315–1329. doi:10.1002/we.2095 | 集約後に残る相関の数値 ｜状況: 精読済み → `notes/malvaldi2017.md` |
| E14 | Ohlendorf, N., & Schill, W.-P. (2020). Frequency and duration of low-wind-power events in Germany | *Environmental Research Letters* 15, 084045（OA） | 数日規模イベントの頻度・持続 ｜状況: 精読済み → `notes/ohlendorf-schill2020.md` |
| E15 | Grimaldi, A., Minuto, F. D., Perol, A., Casagrande, S., & Lanzini, A. (2025). Techno-economic optimization of utility-scale battery storage integration with a wind farm for wholesale energy arbitrage considering wind curtailment and battery degradation | *Journal of Energy Storage* 112, 115500. doi:10.1016/j.est.2025.115500（確定） | 著者・巻・DOI、抑制・劣化を含む最適化の結論 ｜状況: 精読済み → `notes/grimaldi2025.md` |
| E16 | Landy, M., Schmidt, O., Johnson, N., & Staffell, I. (2026). Maximising the economic value of renewable and battery storage hybrids with revenue stacking（題名確定） | *Energy & Environmental Science* 19, 4469–4494. doi:10.1039/d6ee00776g（号数は PDF に記載なし） | 著者・DOI、併設による抑制・資本費削減の数値 ｜状況: 精読済み → `notes/landy2026.md` |
| E17 | 風力の太陽光・貯蔵併設ハイブリッド化（題名要確認） | *Renewable Energy* (2024), PII S0960148124021256 | 著者・題名・DOI ｜状況: 未取得 |

| E18 | De Vos, K. (2015). Negative wholesale electricity prices in the German, French and Belgian day-ahead, intra-day and real-time markets | *The Electricity Journal* 28(4), 36–50. doi:10.1016/j.tej.2015.04.001 | 負価格の頻度・深さ・発生条件（第10章10.2 の c の目安） ｜状況: 未取得 |
| E19 | Weitzman, M. L. (1974). Prices vs. quantities | *Review of Economic Studies* 41(4), 477–491. doi:10.2307/2296698 | 価格規制が数量規制に勝る条件（限界費用の不確実性・限界便益の傾き）の命題（10.5） ｜状況: 未取得 |
| E20 | 資源エネルギー庁 (2026-08-06) 再生可能エネルギー出力制御の長期見通し等について（次世代電力系統WG 資料1-1） | Web（METI） | 2035年度の出力制御率（北海道37%・太陽光43%）、優先給電ルール見直し＋FIP併設3kWh/kW で 53%→3% の試算、最小需要日の需給（10.3・10.5・9.3） ｜状況: 未取得（参考資料 20260930.md 経由の二次情報） |

## C. 原典精読済みだが最終確認が必要な箇所

| # | 文献 | 確認したい点 |
|---|---|---|
| C-1 | Butters, Dorsey & Gowrisankaran (2025) *Econometrica* 93(3), 891–927. doi:10.3982/ECTA20411 | 読んだのは NBER w29133（2024年9月改訂）。掲載版で結論の限界6点・Fig.5/Table 1 の数値・頁番号が変わっていないか |
| C-2 | Schmalensee (2022) *The Energy Journal* 43(2). doi:10.5547/01956574.43.2.rsch | 読んだのは CEEPR WP 2020-012。掲載版の条件式(4.6)と §5 の「容量メカニズムの類」の記述 |
| C-3 | Karaduman (2023 WP) | 最新版（2023 以降の改訂）の有無。Table 2/5 の数値 |
| C-4 | Sakaguchi & Fujii (2021) Fig. 6 | 北海道の分位点係数（図のみ）。可能なら図から τ 別の値を読み取り、本研究の再推定（τ=0.9 −11.2）と並べる |
| C-5 | Li et al. (2024) *Energy* 307, 132607, Table 5–6 / Fig. 8–9 | 利益表の単位（"million JPY" では桁が合わない。千円と解釈すると九州 2022 年電池 ≒ 2.3万円/kW-年） |
| C-6 | Fuke & Ohashi (2025) Table 9 | 再現結果（表6.5）との突合済み。掲載版の頁番号 |

## D. 図書館ではなく Web で取得（この環境からは遮断）

- 経済産業省 定置用蓄電システム普及拡大検討会 2024年度 第3回 資料3「系統用・再エネ併設蓄電システムのコスト面・収益面での課題整理」（2024-08-29）、第4回 資料3-1「系統用蓄電システムの需給調整市場における収益性分析」（三菱総研、2024-11-11）、第5回 資料3「結果とりまとめ（案）」（2025-01-30）
- 自然エネルギー財団 連載コラム「総論：長期脱炭素電源オークションの有効性を問う」（2025-07-16）— **Drive 格納済み（2026-09-29）→ `notes/28-ltda-2025-results-and-ref-column.md`**
- OCCTO 長期脱炭素電源オークション 約定結果（2025年度応札分、2026-05-13）と落札電源一覧 — **別紙を Drive 格納済み（2026-09-29）→ 同上ノート**
- Modo Energy（2025）ERCOT 蓄電池収益の記事、CAISO (2025) 2024 Special Report on Battery Storage
