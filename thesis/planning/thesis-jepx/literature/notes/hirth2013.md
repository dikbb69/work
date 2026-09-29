# Hirth (2013) The market value of variable renewables: The effect of solar wind power variability on their relative price
- 書誌: Lion Hirth, *Energy Economics* 38 (2013) 218–236. DOI 10.1016/j.eneco.2013.02.004（JEL C61, C63, Q42, D40）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 風力・太陽光の**変動性**は、それらが市場で受け取る価格（市場価値）にどう影響し、浸透率・政策・価格でどう変わるか。
- 枠組み: 市場価値 ＝ システム基準価格（時間加重平均卸価格）との相対価格「value factor」（風力加重平均価格／時間加重平均価格）。基準価格との差を profile cost（変動性）、balancing cost（不確実性）、grid-related cost（立地）に分解（Fig.1）。本論文は profile cost に集中。
- 変動性が市場価値に効く2つの機構: **correlation effect**（VRE出力が需要と正相関なら高い価格を受け取る）と **merit-order effect**（非限界的な VRE 容量は残余負荷曲線を左にシフトして価格を下げ、設置容量が大きいほど下落が大きい）。「The fundamental reason for the merit-order effect is that the short-term supply function is upward sloping because a) there exists a set of generation technologies that differ in their variable-to-fix costs ratio and b) electricity storage is costly.」
- 貢献の新規性: 文献レビュー（Table 1–2）、**市場データの回帰分析**（value factor を浸透率に回帰するのはこの分野で新奇）、欧州電力市場モデル EMMA による定量化の三本立て。

## 2. データ・市場・期間
- 実証: ドイツの風力・太陽光 value factor（2001–2012、Table 3）、複数欧州国の風力 value factor（Table 4）。DA スポット価格は EPEX-Spot, Nordpool, APX、in-feed は TSO データ。
- モデル EMMA: 北西欧州6か国（独・白・波・蘭・仏＋）の様式化された給電・投資モデル。11技術、時間解像度は時間値、mid-term（既存設備を考慮）と long-term（グリーンフィールド）。揚水は含むが**貯水池水力は非モデル化**（最大の限界と著者自身が言明）。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- value factor の定義（§3.1）: 基準価格 p̄ = p′t/t′t、風力価格 p̄_w = p′g/g′t、v_w = p̄_w/p̄。
- 回帰（§3.3, Table 5）: value factor を市場シェアに回帰し、水力系統と火力系統でダミー交差。
- EMMA: 各 VRE 浸透率について残りの系統の新均衡（費用最小化＝競争均衡）を求め、value factor を算出。蓄電池は明示的に扱わず、揚水容量（0／現状／2倍）の感応度のみ（§5.8）。

## 4. 主要結果（数値を必ず。表番号を付す）
- **Table 3（ドイツ）**: 風力 value factor は 2001年 1.02（シェア2.0%）→ 2012年 0.89（8.0%）、平均 0.94。太陽光は 2006年 1.33（0.4%）→ 2012年 1.05（4.5%）、平均 1.16。風力シェア 2%→8% で value factor −13 pt、太陽光 0→4.5% で −28 pt。
- **Table 4**: 北欧（水力）の風力 value factor は 1 近傍、火力系統（独）は浸透率に敏感。デンマークは北欧との連系で下落が抑制。
- **Table 5（回帰）**: 風力シェア +1 pt で value factor は水力系統で −0.22 pt、火力系統で −1.62 pt。切片は水力 0.98、火力 1.04。全係数 5% 有意（ただし観測数が少なくバイアスに注意と明記）。
- **EMMA mid-term（§5.1, Fig.8–9）**: 風力 value factor は低浸透で 1.1、30% で 0.5。絶対値では基準価格 66→35 €/MWh の間に風力平均収入 73→18 €/MWh。学習率5%でも費用低下を収入低下が上回り競争力なし。17% シェアを補助なしで達成するには LCOE 30 €/MWh が必要。30% 風力（200 GW）でも可制御容量は 40 GW しか減らず、**蓄電投資はゼロ**、連系線投資は約1.5倍。30% で年1,000時間が価格ゼロ（must-run が価格設定）、風力発電の28%がゼロ価格で売却。
- **太陽光（§5.2, Fig.14）**: value factor は 15% シェアで 0.5 を下回る（プロファイルが「peaky」なため、Fig.15）。
- **文献レビュー総括**: 風力 value factor は 30% で約 0.7、太陽光は 10–15% で 0.7。
- **蓄電（§5.8, Fig.27）**: 揚水を0→2倍にしても風力 value factor の差は mid-term で 1 pt、long-term で 5 pt のみ（揚水は6–8時間で満水になる設計で、風力の変動はより長い時間スケール）。太陽光は 15% シェアで mid-term +5 pt、long-term +9 pt。**低浸透では蓄電は正午ピークを削ることで太陽光の価値を下げる**。
- 結論（§7）: 風力の価値は 30% で 0.5–0.8、太陽光は 15% で同水準。統合オプション（送電、火力の柔軟化、風車設計）は有効だが、高炭素価格だけでは競争力は出ず、補助が2020年以降も必要。

## 5. 著者が挙げる限界・今後の課題
- 回帰: 観測数が非常に少なく、浸透率が将来水準より小さく、系統が適応しうるため外挿に注意（§3.3）。
- EMMA: 「highly stylized」。最大の限界は貯水池水力の欠如。蓄電技術は揚水のみ。
- 今後: 蓄電技術の多様化・需要側管理・長距離連系・熱貯蔵の評価、北欧・仏・西・アルプスの貯水池、balancing cost と grid cost の研究（§7）。
- Brown & Reichenberg (2021) は本論文の「市場価値低下」が VRE 支援政策（シェア強制）の含意であると批判（→ brown-reichenberg2021.md 参照）。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2（再エネと価格）: メリットオーダー効果と value factor の概念、**風力と太陽光で価値低下の速さが異なる**（太陽光は集中したプロファイルのため早い）という基本的知見。本研究の「風力は水準を下げるが日内スプレッドは広げない／太陽光はダックカーブで TB4h を広げる」の理論的先行例。特に「揚水（短時間蓄電）は風力の価値をほとんど改善しない（風力変動は日内より長い時間スケール）が、太陽光は日内変動が顕著なため大きく改善する」（§5.8）は、本研究の「蓄電池のスポット価値は日内形状で決まり、風力主導ゾーンでは小さい」という主張の直接的な支持。
  - 第3章／第5章: 「低浸透では蓄電が正午ピークを削って太陽光価値を下げる」（§5.8）は Butters/Karaduman の「蓄電は再エネ収入を減らす」と同じ知見。
  - 第7章: 30% 風力でも EMMA の最適解に蓄電投資がゼロという結果は、本研究の純市場均衡 K*=0 と整合。
- 支持する点: 風力の日内平準性（"wind fluctuations occur mainly on longer time scales"）が蓄電池（4h）の裁定価値を小さくする。
- 対立・留意点: Hirth の value factor は再エネ側の価値指標であり、蓄電側の指標（TB4h）ではない。北海道は連系線（北本）で本州とつながるが、Hirth の「連系線が value factor 低下を緩和する」（デンマーク）論理を蓄電に当てはめると、連系線増強は蓄電の裁定価値をさらに削ぐ可能性がある（本研究第8章の連系線議論に接続）。
- 手法の源流: 電源別に価格指標を浸透率へ回帰する設計（Table 5）は、本研究の TB4h／水準の回帰の先行例。
- 新規性チェック: Hirth が既に行っていること＝欧州データで VRE の市場価値（水準）低下を電源別に定量化、蓄電（揚水）の風力/太陽光への効果の非対称性を指摘。本研究が新たに行うこと＝日内スプレッド指標（TB4h）に対する電源別効果を JEPX 北海道で識別し、それを蓄電池の裁定価値・自由参入均衡に接続。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "We find the value of wind power to fall from 110% of the average power price to 50–80% as wind penetration increases from zero to 30% of total electricity consumption. For solar power, similarly low value levels are reached already at 15% penetration."
2. §1 (p.219): "The fundamental reason for the merit-order effect is that the short-term supply function is upward sloping because a) there exists a set of generation technologies that differ in their variable-to-fix costs ratio and b) electricity storage is costly."
3. §3.3 (p.224): "increasing the market share of wind by one percentage point is estimated to reduce the value factor by 0.22 percentage points in hydro systems (β1) and by 1.62 percentage points in thermal systems (β1+β2)."
4. §5.8 (p.231): "The effect on wind is very limited: at 30% penetration, the difference in value factors between zero and double storage capacity is only one percentage point in the mid-term and five points in the long term (Fig. 27). ... pumped hydro plants ... are usually designed to fill the reservoir in six to eight hours while wind fluctuations occur mainly on longer time scales."
5. §5.8 (p.231): "For solar, the situation is different. Due to its pronounced diurnal fluctuations, solar power benefits much more from additional pumped hydro storage ... At low penetration levels, however, storage actually reduces the value of solar power by shaving the noon peak."
6. §5.2 (p.227): "The solar profile is more 'peaky' than wind, with a considerable amount of generation concentrated in few hours."
