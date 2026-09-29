# Jiang & Powell (2015) Optimal Hour-Ahead Bidding in the Real-Time Electricity Market with Battery Storage Using Approximate Dynamic Programming
- 書誌: INFORMS Journal on Computing, 27(3), 525–543. DOI 10.1287/ijoc.2015.0640
- 出所: Google Drive 参考研究_20260728/SetD（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: NYISO のリアルタイム市場（5分決済）に蓄電池を「1時間前入札」で参加させるとき、時間開始時の充電残量が未知で、かつ時間末の残エネルギー価値も考慮しなければならない下での最適入札は何か。
- 貢献: (i) 問題を MDP として定式化し、価値関数の単調性（Prop.3–4）を示す、(ii) 単調性を利用して収束する ADP アルゴリズム Monotone-ADP-Bidding を提案し、厳密解（後ろ向き DP）との比較で計算上の利点を実証、(iii) 価格過程の分布を仮定しない **distribution-free** 変種（歴史価格で直接学習、Theorem 2）を提案し NYISO 実データで有効性を示す、(iv) ルールベース戦略との比較。

## 2. 設定・データ
- 入札は (b⁻, b⁺)（0≤b⁻≤b⁺≤b_max）の対で、時刻 t に出した入札は区間 (t+1, t+2] で有効（p.527–528）。売り入札 b⁺ < スポット価格なら放電、買い入札 b⁻ > スポット価格なら充電、間なら待機。約束した放電ができないときの罰則 K·P_t（NYISO は K=1）。1時間に M=12 回の5分決済。
- 状態 S_t=(R_t, L_t, b_{t−1}, P^S_t)（残量、寿命、前入札、価格状態）。
- ケーススタディ（第6節、p.538–539）: 1 MW/6 MWh 電池、R_max=72（5分単位）、入札は [0,150] $/MWh を15点に離散化（価格の 98.2% が $150 未満）、価格状態変数なし（P^S_t=∅）、劣化なし（l=1）、平日のみ、同一月の平日で価格が同分布と仮定、月ごとに日次価値関数を学習。訓練 2011 年、訓練・検証 2012 年。ADP Policy 1＝前年同月で訓練、ADP Policy 2＝前月で訓練。

## 3. モデル・手法の要点
- Prop.3（p.530）: 貢献関数 C は R_t, L_t, b⁻_{t−1}, b⁺_{t−1} について非減少。Prop.4（p.530）: 最適価値関数 V*_t も同じく非減少。
- Monotone-ADP-Bidding（第4節、p.530–536）: 非同期近似価値反復＋各更新後に単調性を保つ射影。Theorem 1（p.532）: 仮定1–4 の下で V̄ⁿ_t → V*_t a.s.。単調性射影を外した AVI は「収束証明があっても実際には機能しない」（p.530）。
- 後決定状態（post-decision）版＝distribution-free（第4.4節）: 価格モデルを持たず歴史的価格パスで学習。Theorem 2（p.534）: 仮定4–7 の下で最適後決定価値関数に a.s. 収束。
- ルールベース比較（第6.2節、p.539–540）: A（夜買い昼売り固定時間帯、h*=12）、B（平均価格で上位/下位 k*=10 時間を売買）、C（時間別の分位点 q_α, q_{1−α}、α=0.1 で入札）。添字1＝前年同月、2＝前月のデータで調整。

## 4. 主要結果・命題（数値）
- ベンチマーク問題（Table 2、p.536; 最適値に対する割合）: N=1,000 反復で M-ADP 45.9–73.5% 対 AVI 7.8–66.6%、N=5,000 で M-ADP 64.1–87.2%。「後ろ向き DP に必要な計算資源の 10% 未満で準最適解」（p.542）。
- 実データ（Table 6、p.539; 2012 年平日、1 MW/6 MWh）: ADP Policy 1 年間収入 $76,512.68、ADP Policy 2 $69,247.02。5–7月が最大、6月−2月の差は $9,499.37（Policy 1）/$8,872.08（Policy 2）。日次収入の (5%,95%) 分位点 ($44.13, $453.30)、中央値 $154.12（Policy 2）。
- ルールベース（Table 7、p.540）: A1 $29,291.36、A2 $27,154.52、B1 $26,516.76、B2 $25,385.68、C1 $52,443.88、C2 $38,312.20。最良の C でも ADP の 68.5%（C1/ADP1）・55.3%（C2/ADP2）。C2 は 2012 年7月・11月に負の収入（訓練月と検証月の特性差）。※本文の比率は PDF 抽出で桁が崩れていたため Table 6・7 の値から再計算して確認した。
- 示唆（p.540–541）: 裁定は「少数の高収入月にのみ稼働」が合理的な可能性。蓄電池費用 $160/kWh でも「現状では蓄電費用は潜在収入に比べ高い」。

## 5. 著者が挙げる限界・今後の課題
- 価格受容（自社入札が価格に影響しない）、単一電池、平日のみ、同月内の同分布仮定、劣化モデルなし、価格状態変数を省略（次元削減のため）、比較したルールベースは「業界の独自戦略の最良」ではない、週末は別途学習が必要、周波数調整など他収入源との併用は未検討（Sioshansi et al. 2009 を参照）。

## 6. 本研究との関係
- 引用予定箇所: 第5章(c) 蓄電池ディスパッチのバックテスト。本研究は完全予見 LP を上限、実行可能戦略（前日約定価格に基づく）を実務解とし捕捉率 ≈81–83% を得た。Jiang–Powell は (i) 良く調整したルールベースでも価値関数を考慮する ADP の 55–69%、(ii) ADP 自体もベンチマークで厳密最適の 64–87% であることを示しており、「完全予見に対する 80% 前後の捕捉」が実行可能戦略として妥当な水準であることの外部参照になる。
- 「裁定収入は少数の月に集中する」（p.540）は本研究の季節（風況）帯域による収益偏在の議論（第6–7章）と整合。
- 本研究が単純化した点: JEPX 日前スポット（30分コマ、ゲートクローズ時点で価格既知）を対象とし、時間前入札の (b⁻,b⁺) 構造・5分決済・未達罰則・SOC の不確実性は扱わない。第10章の拡張: 時間前市場・需給調整市場への参加を扱う場合は単調 ADP／distribution-free 学習が雛形。

## 7. 引用に使える原文
- p.525（要旨）: "Energy arbitrage, the process of buying, storing, and selling electricity to exploit variations in electricity spot prices, is becoming an important way of paying for expensive investments into grid-level storage."
- p.525（要旨）: "Furthermore, we propose a distribution-free variant of the ADP algorithm that does not require any knowledge of the distribution of the price process (and makes no assumptions regarding a specific real-time price model)."
- p.540: "Comparing Policy C1 against ADP Policy 1 and comparing Policy C2 against ADP Policy 2, we see the revenues generated are still a disappointing 68.5% and 55.3%, respectively, of the ADP revenues, suggesting that it is difficult, even after tuning, for simple rule-based heuristics to perform at the level of a well-trained ADP policy that considers downstream value."
- p.540: "These results suggest that perhaps energy arbitrage should not be a year-round investment but rather one that is active only during months with potential for high revenue."
- p.540–541: "As mentioned earlier, with optimal storage control strategies and decreased capital costs, energy arbitrage can soon become profitable on its own; as it currently stands, storage costs are still relatively high compared to potential revenue."
- p.542: "In fact, our empirical results show that near-optimal solutions can be generated using less than 10% of the computational resources necessary for backward dynamic programming."
