# Rassi, Samin & Kanamura, Takashi (2023) Electricity price spike formation and LNG prices effect under gross bidding scheme in JEPX
- 書誌: Energy Policy, 177, 113552, doi:10.1016/j.enpol.2023.113552（受理 2023-03-18、公開 2023-04-06、京都大学 GSAIS）
- 出所: Google Drive 参考研究_20260728/SetC（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 2021年1月の JEPX 価格スパイク（最高 250 円/kWh、日平均 100 円）はどう形成されたか。LNG スポット価格は「限界費用経由で数か月遅れて」ではなく「入札行動経由で即時に」電力価格に伝播するようになったのか。
- 著者の3つの貢献（Abstract）: (1) JEPX 板（買い・売り入札曲線）に基づく新しい構造モデルを提案し LNG スポット価格の効果を組み込む、(2) 同モデルが 2021年1月のスパイクを適切に捕捉、(3) パラメータ推定から「natural gas spot price immediately shifts the price curve upward」。
- 政策含意: スパイクリスク管理には限界費用ではなく LNG が市場参加者の入札行動に与える効果を見るべきで、監視対象は数か月前の LNG トレンドではなく LNG スポット。

## 2. データ・市場・期間
- JEPX 前日市場、30分値、FY2020（2020-04-01〜2021-03-31、in-sample、17,520 観測）と FY2021（out-of-sample）。システム価格・エリア価格、買い/売り入札量、入札曲線。
- LNG: JKM 1か月先物（Platts、investing.com 経由）日次をスポットの代理。週末・日内は定数補間。ラグなし（Fig. 9 の相関分析に基づく）。
- Table 1（FY2020 価格分布、円/kWh）: 平均 11.209、中央値 5.630、SD 23.729、最小 0.010、最大 251.000、歪度 5.655、尖度 39.771。価格上下限 0.01〜999 円/kWh。0.01 円にヒストグラムのスパイク。
- 制度背景: 2017 年 JEPX 取引比率 6.8%（METI）、2017 年からグロスビディング（市場メイク）開始、2021 年 12 月時点で参加者 275 社。FY2019 以前のスパイクは約 50 円/kWh（Kanamura & Bunn 2022）。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 予備分析（§2.1, Fig. 2）: LNG と電力価格のクロス相関の最大ラグが 2017 年の約1か月 → 20 日未満 → 2020 年はほぼ即時に短縮。
- 構造モデル（§2.2）:
  - 過剰供給量 Ṽ_t = S̃_t − B̃_t（式3、売り入札量 − 買い入札量）。
  - 価格曲線 P̃_t = (1 − a Ṽ_t / c)^{1/a} 型（式4）、LNG による需要曲線シフト Ṽ_N = α + β log Ñ_t（式6）を組み込み式5。
  - LNG 価格は Schwartz 型 1 ファクター OU（式7）、量は単純拡散（式8）、相関 ρ（式9）。電力価格の拡散（式10–13）で σ_P, μ_P を導出。
  - 推定は Box–Cox 変換（a = 0.1 を ML で推定、Fig. 10）後の回帰。
- 「変動性」は σ_P（式11–12: σ_V, β, σ_N, ρ から合成）として構造的に定義される。
- 重要な観察: 取引所の板は「ほぼ非弾力的な供給曲線と弾力的な需要曲線」（教科書的な卸市場と逆、Fig. 4）。

## 4. 主要結果（数値を必ず。表番号を付す）
- Table 5（価格式係数、全て有意）: b0 = −0.3419 (s.e. 0.0726)、b1 = 0.3940 (0.01165, t = 33.8)、b2 = −1.830E−07 (1.573E−09, t = −116.3)。β > 0 で LNG 価格上昇は価格曲線を上方シフト。
- Table 2–4: LNG 過程 γ0, γ1 有意、量の μ_V は非有意。
- Fig. 11（in-sample FY2020）: 調整済 R² 0.607、残差 SD 0.781（標本 SD 23.729）。2021 年 1 月のスパイクを捕捉。
- Fig. 12（out-of-sample FY2021）: 調整済 R² 0.622、残差 SD 0.678（標本 SD 9.994）。2022 年 1〜3 月のスパイクも捕捉。
- Table 6（先行研究との対比）: Sakaguchi & Fujii (2021) を「グロスビディングは約定価格を上げ、間接オークションは下げた」と要約。本研究は「価格は市場情報をより効率的に反映」「LNG 価格が価格曲線を正にシフト」「過剰需要（scarcity）が価格の良い説明変数」。
- 解釈（§4）: LNG ショックのニュースで、旧一電は市場メイクを一時停止するか 999 円/kWh の買戻し入札を置き、小売もインバランス料金回避のため高値入札 → 需要曲線の上方シフト。「such interactions are signs of a healthy market」。

## 5. 著者が挙げる限界・今後の課題
- LNG→電力の一方向モデル。長期のフィードバックは未考慮。
- 価格上限なし・グロスビディング期間が短くデータ不足。
- 2021 年 1 月のスパイクには市場ルール（リスク評価・入札戦略に影響する制度）など LNG 以外の要因が絡むが、本研究は LNG に限定。今後は市場ルールが入札戦略に与える効果の理論分析。
- 200 円超のスパイクは初めてで他期間での頑健性は未検証。

## 6. 本研究との関係
- 引用予定箇所: 第3章制度（2021年1月危機、LNG 価格パススルー、グロスビディング下の買戻し行動、0.01〜999 円の価格帯、0.01 円床のヒストグラム・スパイク）、第2章2.3（右裾＝スパイクは再エネではなく燃料・入札行動で説明されるという「変動性の源泉の切り分け」）。
- 支持する点: 本研究が FY2023–25 の北海道で「風力は水準を下げるが日内スプレッドを広げない」と言うとき、右裾の分散は LNG・需給逼迫（scarcity）が支配するという本論文の主張と補完的。分位点回帰で τ=0.9 の風力 MOE が縮むのは、右裾が LNG/scarcity に支配される期間（FY2021–22）を含むためという説明に使える。
- 対立点／注意: システム価格ベースで北海道エリアの分断は扱わない。再エネ変数は入っていない。「価格が効率化した」という規範的評価は Li & Bu (2025) の「制度的機能不全」評価と対照的（第3章で両論併記）。
- 手法の源流としての位置づけ: 板データ（買い−売り入札量）を scarcity 変数として使う発想は Kanamura & Bunn (2022) の BS_t と同系統。本研究の TB4h／分位点分析には板データは使わないが、ロバストネスで「売り−買い入札量」を制御変数に入れる余地。
- 新規性チェック: 本論文はスパイク形成の構造モデルであり、再エネ MOE も蓄電池価値も扱わない。本研究は LNG 期を含む/除く期間分割で風力 MOE を再推定し、蓄電池の価値がスパイク（右裾）ではなく日内形状（TB4h）で決まることを示す点が新しい。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "In January 2021, the spot price at the JEPX soared to a record high of 250 yen (100 yen for the 24-hour average), which is more than ten times the average daily price."（§1, p.2）
2. "The time lag corresponding to the maximum correlation between LNG and electricity price is getting shorter with time. … In 2020, the time lag has shrunk to nearly instant impact."（§2.1, p.3）
3. "The curves in the exchange do not follow the stylized assumption of power markets, but rather a nearly inelastic supply curve and an elastic demand curve were observed during FY 2020."（§5, p.10）
4. "utilities may temporarily withdraw from market-making or place high-price buyback bids (such as 999 yen/kWh) to ensure secure delivery of electricity. Similarly, the retail sector also tends to react to such news by placing higher bids since failure to procure electricity at their offered prices can result in imbalance fees."（§4, p.9）
5. "we suggest that scarcity (i.e., excess volume) is a better determinant of price in comparison to demand, buy bid, and trading volume."（§4, p.9）
