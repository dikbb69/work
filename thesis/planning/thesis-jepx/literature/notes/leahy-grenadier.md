# Leahy (1993) QJE ＋ Grenadier (2002) RFS — 競争によるオプション価値の侵食

<!-- SciSpace Chat with PDF の回答ログ（2026-07-28実行）を機械分割したもの。
数式はdocxエクスポート時に崩れているため、引用する際は必ず原PDFで確認すること。 -->


## Competitive Entry, Option Value, and the Myopic NPV Rule


### Erosion of Option Value by Competitive Entry

Competitive entry significantly diminishes the 'option value of waiting' for firms considering investment. While standard real options models suggest that firms invest only at large positive Net Present Values (NPVs) due to the value of waiting, competition drastically reduces this value, pushing investment decisions closer to a zero NPV threshold  (Grenadier, 2002).
- Mechanism of Erosion: The presence of competitors means that delaying an investment risks losing the market to others  (Leahy, 1993). This 'fear of preemption' or 'urgency of potential entrants' compels firms to exercise their investment options sooner, effectively squeezing out the potential value from delay  (Grenadier, 2002)  .
- Impact on Option Premium: Even a small amount of competition drastically reduces the option premium. For instance, with two firms, the option premium can fall by 50%, and with five firms, it can drop to 15%. As the number of competitors increases, the option premium converges to zero  (Grenadier, 2002).
- Monopolistic vs. Competitive Context: For a firm with monopolistic access to a project, the option to wait can be very valuable, leading to investment triggers well above the standard NPV = 0 threshold  (Grenadier, 2002) . However, the introduction of competition reduces the value of this option by decreasing the value of the invested capital  (Leahy, 1993).

### Optimality of the Myopic NPV Rule in Competitive Equilibrium

In a perfectly competitive industry, the option to remain uncommitted becomes worthless because competition eliminates all profits  (Leahy, 1993). The inclusion of competitive access to investment opportunities leads to a rapid erosion of the option to wait, making the standard NPV rule a more accurate description of the actual investment threshold  (Grenadier, 2002).
- Conditions for Optimality: In the limit of a perfectly competitive industry (as the number of firms 'n' approaches infinity), individual optimizing behavior drives competitive firms to enter precisely at a point of zero NPV  (Grenadier, 2002). This means the option premium converges to 0%, leaving the traditional NPV rule intact . Therefore, in perfect competition, the myopic NPV rule, which dictates investment when NPV is zero, becomes optimal.
- Competitive Equilibrium Definition: A competitive equilibrium is defined as a symmetric Nash equilibrium in entry and exit strategies, where no individual firm can optimally deviate from the policy given that all other firms follow it  (Leahy, 1993).
- Propositions: While the provided contexts discuss the concept, they do not explicitly state a numbered proposition for the optimality of the myopic NPV rule in competitive equilibrium. However, the underlying principle is that in a perfectly competitive industry, entry occurs at zero NPV  (Grenadier, 2002) and the option premium becomes zero . Proposition 2 in one context refers to calculating competitive entry and exit strategies, but not directly to the NPV rule's optimality  (Leahy, 1993).

### Survival of Option Value Under Deviations from Perfect Competition

Option value can survive under deviations from perfect competition, such as a finite number of firms or the presence of entry barriers.
- Finite Firms: With a finite number of firms, the option premium does not completely vanish. For example, with just two firms, the option premium falls but still retains 50% of its value, and with five firms, it retains 15%  (Grenadier, 2002). This indicates that some option value persists as long as competition is not perfect.
- Entry Barriers: While not explicitly detailed in the provided contexts regarding option value survival, it is a general economic principle that entry barriers (e.g., quotas) can limit competition. If there is an entry quota, competition might lead firms to enter earlier than under myopic policies, but the existence of the quota itself implies that not all potential entrants can enter, potentially preserving some option value for those who do secure entry rights  (Leahy, 1993). The presence of competition reduces the value of the option, but it does so by reducing the value of the invested capital, not necessarily eliminating the option entirely unless competition is perfect  .

### Application to Battery Storage Entry

In the context of battery storage entry, where each entrant's arbitrage compresses the price spread for later entrants, these results would apply as follows:
- Erosion of Option Value: The entry of each battery storage firm, by arbitraging price differences (buying low, selling high), reduces the available price spread. This directly diminishes the profitability of future arbitrage opportunities for subsequent entrants. This dynamic is analogous to competitive entry eroding the 'option value of waiting.' Firms that wait too long risk finding the profitable price spreads significantly reduced or eliminated by earlier entrants, thus losing the value of their investment opportunity.
- Urgency to Invest: The fear of preemption would drive battery storage developers to invest sooner rather than later. If they wait, the most lucrative locations or times for arbitrage might be taken by competitors, making their option to invest less valuable. This aligns with the idea that competition forces earlier exercise of investment options  (Grenadier, 2002) .
- Shift Towards Myopic NPV: As more firms enter the battery storage market and arbitrage opportunities become scarce, the market would trend towards a competitive equilibrium. In this scenario, the profitability of new battery storage projects would likely approach a zero NPV, meaning that the myopic NPV rule (investing when NPV is zero) would become the optimal decision rule, as the option value of waiting for even larger price spreads would be negligible  (Grenadier, 2002)  .
- Impact of Finite Firms/Barriers: If there are limitations on the number of firms that can enter (e.g., due to grid connection limits, land availability, or regulatory hurdles acting as entry barriers), some option value might still persist for those firms that successfully secure these limited opportunities. However, within the scope of available opportunities, the competitive pressure from a finite but significant number of firms would still substantially reduce the option value compared to a monopolistic scenario  (Grenadier, 2002).
In summary, competitive entry in the battery storage market, characterized by the compression of price spreads, would significantly erode the option value of waiting, pushing firms towards earlier investment decisions and making the myopic NPV rule increasingly relevant as the market approaches saturation.


## 原典精読（2026-09-29）

- 出所: Google Drive 参考研究_20260728/SetD（原文精読 2026-09-29）。以下は SciSpace ログではなく原PDFから直接取った。頁数は掲載誌のもの。

### A. Leahy (1993) Investment in Competitive Equilibrium: The Optimality of Myopic Behavior
- 書誌: Quarterly Journal of Economics, 108(4), 1105–1133. DOI 10.2307/2118461

#### 1. 問いと貢献（著者の主張する新規性）
- 問い: 不可逆投資の実物オプション文献は「価格過程が外生の孤立企業」を前提とする。価格が内生となる競争均衡では、待つオプションはどう扱われるか。
- 主張: 「競争の導入は不可逆投資のタイミングを全く変えない」（p.1106）。他社の参入が価格に与える影響を無視する **myopic firm**（産業産出量について静学的期待、ショックについては合理的期待）の投資トリガーと、完全に合理的な競争企業のトリガーは一致する。
- 貢献: (i) 孤立企業モデルの含意（不確実性と投資の関係）が競争均衡にそのまま持ち込める、(ii) 戦略と価格過程の不動点問題を解かずに競争均衡が計算できる、(iii) myopic firm ↔ 社会計画者（optimal stopping ↔ optimal control）の対応（第VI節）。

#### 2. 設定・データ
- 理論論文。Assumption (*)（p.1113）: 同質企業多数、資本のみを投入する規模に関して収穫一定（1単位資本=1単位産出）、逆需要 p=D(q,x)（xで増加・qで減少）、投資費用 k/単位・撤退費用 l（k+l>0、l=∞で不可逆）、ショック x は拡散過程 dx=μ(x)dt+σ(x)dw、投資は無限分割可能（各無限小資本単位を1企業とみなす）、危険中立、割引率 r。
- Definition (*)（p.1115）: 参入トリガー P̄(q)・撤退トリガー P̲(q) に関する対称ナッシュ均衡＋自由参入（遊休企業の価値=0 → 参入時点の稼働企業価値=k、撤退時点=−l）。価格は [P̲(q), P̄(q)] 内に規制される。

#### 3. モデル・手法の要点
- 第II節: 確定的設定で、myopic 戦略から競争均衡を構成（参入時価格=rk、参入間の利潤の現在価値=k(1−e^{−r(t2−t1)})）。
- 第III節: 不確実性を導入。「不確実性は両者の価格トリガーを同じだけ引き上げる」（p.1111）。
- 第IV節（特殊ケース: 参入が価格過程の平均・分散に影響しない、例: 乗法的ショック＋GBM）→ Proposition 1。第V節（一般ケース）→ Proposition 2（subgame replacement の発想）。

#### 4. 主要結果・命題
- **PROPOSITION 1**（p.1118、原文）: "Let P̄ and P̲ be the optimal entry and exit levels for the exogenous price process defined by (6) dp̃ = μ̃(p̃)dt + σ̃(p̃)dw. Then P̄ and P̲ are competitive equilibrium entry and exit triggers for the endogenous price process: (5) dp = δ(p,q)dq + μ̃(p)dt + σ̃(p)dw."
  - 証明の骨子（p.1118）: 全企業が myopic トリガーと異なる (p_l, p_u) で参入・撤退する状態はナッシュ均衡でない。Bellman 原理により、myopic 価格過程と競争価格過程は次の参入時点まで同一なので、myopic トリガーで動く方が得。
- **PROPOSITION 2**（p.1121、原文）: "The competitive entry and exit strategies P̄(q) and P̲(q) can be calculated as follows. Pick an arbitrary q̄. Let p̄ and p̲ be equilibrium entry and exit barriers for the price process p̃ defined by (7) dp̃ = δ(p̃,q̄)dq + μ̃(p̃,q̄)dt + σ̃(p̃,q̄)dw, where q̄ is fixed at the chosen level. Then, given that the current industry output is q̄, p̄ and p̲ are equilibrium entry and exit barriers for (8) dp = δ(p,q)dq + μ̃(p,q)dt + σ̃(p,q)dw. So P̄(q̄) = p̄ and P̲(q̄) = p̲."
  - "Together Propositions 1 and 2 imply that firms may ignore all effects of entry and exit on the price process."（p.1121）
- Dixit (1989a) 型の例（p.1119）: D=x/q、x が GBM、c=0 のとき myopic 参入トリガー P̄ = α(r−μ)k/(α−1)（α>1）。σ=0 なら P̄=rk、σ↑で P̄ は rk を超える（待つオプションの価値）。この同じ P̄ が競争均衡の参入トリガーになる。
- 直観（p.1106）: 競争はオプション価値を下げるが、同時に投資済み資本の価値も同じだけ下げるので、両者のトレードオフ（＝投資時点）は不変。

#### 5. 著者が挙げる限界・今後の課題（第VII節、pp.1124–1126）
- 無限分割可能性が必須: 投資が離散だと「myopic トリガーで参入すれば価格が離散的に下がり全員が損をする」（p.1125）。需要の不連続も同様。
- 自由参入が必須: 潜在参入者数に上限があれば全企業が正利潤（fn.16、p.1126）。参入枠（quota）＋無限の潜在参入者だと myopic より早い参入になり非効率（Bartolini 1990）。
- 固有ショック（idiosyncratic shocks）の不在: 中間ケースは未解決。
- 拡張可能: 収穫逓減、危険回避、ジャンプ過程・離散時間・非マルコフ過程（第VI節の対応関係に依拠した予想）。

#### 6. 本研究との関係
- 引用予定箇所: 第9章9.2(e)「期待の説明」。本研究の自由参入均衡（K*=0）で、参入者が他社の累積参入による値幅圧縮を織り込まない「近視眼的」期待を置くことの理論的正当化として引用する。Leahy の Prop.1–2 は「他社の参入・退出が価格過程に与える効果を無視してよい」ことを示しており、本研究の「近視眼的参入」は仮定の粗さではなく競争均衡と整合的な行動であると位置づけられる。
- 併せて第9章で「完全競争では待つオプションは無価値」（p.1106）を引き、K*=0 でも参入が続く現象を「オプション・プレミアムがゼロに近い参入」と解釈する土台にする。
- 本研究が単純化した点（第10章の限界で明記）: (i) 本研究の蓄電池参入は MW 単位で離散、参入者数も有限 → Leahy の分割可能性・多数企業条件を満たさない（p.1125 の警告そのもの）。(ii) 本研究は確率的トリガーではなく確定的な二辺自由参入均衡（期待値ベース）であり、オプション価値は明示的に評価していない。(iii) 蓄電池参入は価格の「水準」だけでなく日内形状（スプレッド）を変えるが、Prop.2 はこの種の効果も連続性の下で無視可能としている。

#### 7. 引用に使える原文
- p.1105（要旨）: "This paper shows that the investment strategies that this literature derives may be optimal in competitive equilibrium even though the price process is now endogenous. This provides a simple means for computing equilibrium investment strategies."
- p.1106: "In fact, under perfect competition the option to remain uncommitted is worthless, since competition eliminates all profits."
- p.1106: "Such a myopic firm has static expectations regarding industry output, but rational expectations regarding other shocks that influence price in the market."
- p.1106: "The introduction of competition reduces the value of this option, but does so by reducing the value of the invested capital. Since competition reduces the value of actual and potential capital at the same time, the trade-off between the two is unaffected."
- p.1120: "Competition therefore does not alter the incentive to trade an idle firm for an active firm."
- p.1125: "First, it is important that investment projects be infinitely divisible. ... If they invest at the myopic entry trigger, then their entry will reduce the price discretely, and all firms will lose money."

### B. Grenadier (2002) Option Exercise Games: An Application to the Equilibrium Investment Strategies of Firms
- 書誌: Review of Financial Studies, 15(3), 691–721. DOI 10.1093/rfs/15.3.691

#### 1. 問いと貢献（著者の主張する新規性）
- 問い: 実物オプションの標準モデルは他社との戦略的相互作用を無視する。n 社の Cournot–Nash 産業で、投資（オプション行使）戦略の均衡をどう導くか。
- 貢献: 連続時間 Cournot–Nash 枠組みで「扱いやすい」均衡導出法を与える。結論は「競争は待つオプションの価値を劇的に侵食し、投資は NPV≈0 の閾値近くで起こる」（要旨 p.691）。Leahy (1993) の myopic 解法を寡占に拡張（Prop.2）、さらに寡占均衡＝需要関数を変換した「人工的な完全競争均衡」（第4節）。

#### 2. 設定・データ
- 理論論文。n 社同質、同質財、P(t)=D(X(t),Q(t))、X は拡散過程 dX=μ(X)dt+σ(X)dz、各社は dq_i=dQ/n ずつ無限小増分で能力を増やし費用は単位あたり K、可変費用なし。fn.4（p.695）: 参入固定費 ε を置けば n は内生化できる（F(n)≥ε かつ F(n+1)<ε）。
- ベースケース（p.703）: 定弾力性逆需要 P=X·Q^{−1/γ}（γ>1/n）、X は GBM（r>μ）。

#### 3. モデル・手法の要点
- Prop.1（p.699）: 対称ナッシュ均衡は各社の価値 V^i と共通トリガー X̄(q_i,Q_{−i}) を ODE＋境界条件で特徴付ける（関数空間の不動点問題）。
- Prop.2（p.701）: その均衡トリガーは、Q_{−i} が永久に固定と仮定する myopic 企業のトリガー X^m と一致 → 不動点問題が不要。
- Prop.3（p.701）: 対称性 q_i=Q/n を使い、均衡トリガー X*(Q) は「キャッシュフロー D(X,Q)+(Q/n)D_Q(X,Q)、行使費用 K の永久アメリカン・コール」という標準実物オプション問題の解に帰着（p.702）。
- 第3節: 均衡オプション・プレミアム OP(n)≡[G(X*(Q),Q)−K]/K（式31）。第4節: 変換需要 D̃(X,Q)=D(X,Q)+(Q/n)D_Q(X,Q)（式35）の下での完全競争均衡と同一 → Leahy (1993)・Dixit (1989b, 1991) の結果を流用可能。

#### 4. 主要結果・命題
- **Proposition 2**（p.701、原文）: "The symmetric Nash equilibrium exercise strategy described in Proposition 1 is characterized by each firm increasing output whenever X(t) rises to the myopic trigger function X^m(q_i, Q_{−i}). That is, X̄(q_i, Q_{−i}) = X^m(q_i, Q_{−i})."
  - 証明の直観（Appendix A.1, p.718）: myopic トリガー到達前に先取りされる可能性がないので、競合の将来の行使は自社の増分ペイオフを変えず無視できる。
- ベースケース均衡トリガー（式21、p.703）: X*(Q)=v_n·Q^{1/γ}。n=1 で Dixit–Pindyck (1994) 第11章の独占解、n→∞ で同第9章の完全競争解に一致（p.704）。
- **オプション・プレミアム**（式32–33、p.708）: OP(n)=1/(nγ−1)、lim_{n→∞}OP(n)=0、OP(1)=1/(γ−1)>0、OP'(n)<0、OP''(n)>0。γ=1.5 の数値例（p.709）: 独占 200%、2社 50%、5社 15%、n→∞ で 0%。「一般の仕様でもプレミアムは競争度で減少し 0 に収束する（ただし σ 等に依存）」（p.709）。
- **事後損失の確率**（Figure 2、p.710; μ=0.02, r=0.05, σ=0.175, γ=1.5, K=1, Q0=100）: 投資後 T 年以内に資産価値が投資費用を下回る確率 Π_T。n=1 でほぼ 0、n=5 で5年以内 37%、n=10 で1年以内 10%・5年以内 75%、n=50 で1年以内 75%・5年以内ほぼ確実（p.711）。
- 第4節（p.711）: 寡占均衡の価格過程と戦略は変換需要 D̃ の下の完全競争均衡と同一（Slade 1994 型の fictitious objective でも導ける）。

#### 5. 著者が挙げる限界・今後の課題
- 対称・同質企業、無限小の能力増分（fn.12: 離散投資では別の均衡概念が必要）、退出オプションなし（fn.11: 追加可能）、n は基本外生（fn.4 で内生化の道筋のみ）、可変費用なし。ベースケースの閉形式は定弾力性＋GBM に依存し、代替仕様では σ 等に依存する複雑な解（p.709）。時間遅れ（time-to-build）は第5節で Grenadier (2000a) を使い拡張。

#### 6. 本研究との関係
- 引用予定箇所: 第9章9.2(e)。北海道の蓄電池参入者は有限（n は数社〜十数社）なので Leahy の完全競争極限より Grenadier の有限 n が直接的。「n=5 で OP=15%」（p.709）を引き、少数の競合でも待つ価値はほぼ消えるため、K*=0（NPV≤0）近傍で参入が続くことは実物オプション理論と矛盾しない、と述べる。
- 同じく第9章で Figure 2（p.710）を引き、「競争下では投資後に価値が費用を下回るのが通常（n=10 で5年以内 75%）」→ 本研究のバックテストで捕捉率が 81–83% に留まり、期待収益が資本費を下回る状態で参入が続く現象は Grenadier の予測通り、と位置づける。
- fn.4（参入固定費で n を内生化）は本研究の自由参入条件と同型。第4節の「人工的完全競争均衡」により、Leahy と Grenadier を一つの枠で引用できる（完全競争極限＝Leahy、有限 n＝Grenadier）。
- 本研究が単純化した点: 確率的トリガーではなく確定的な二辺自由参入均衡で K* を求めており、OP(n) や Π_T は計算していない（第10章の拡張候補: 北海道の参入者数 n で OP(n)=1/(nγ−1) 型の目安を示す）。蓄電池は「供給増」ではなく「裁定による値幅圧縮」で他社の収益を下げるが、D_Q<0 と同じ外部性の構造（累積容量が限界収益を下げる）である。

#### 7. 引用に使える原文
- p.691（要旨）: "For example, while standard real options models emphasize that a valuable 'option to wait' leads firms to invest only at large positive net present values, the impact of competition drastically erodes the value of the option to wait and leads to investment at very near the zero net present value threshold."
- p.692: "If firms fear preemption, then the option to wait becomes less valuable. To understand investment in industries with competitive pressure, a game-theoretic analysis of equilibrium exercise strategies is essential."
- p.700: "In this section I demonstrate that the Nash equilibrium exercise strategy also evolves as if it were determined by a firm pursuing a form of myopic exercise strategy."
- p.708: "In the limit of a perfectly competitive industry (as n → ∞), individual optimizing behavior of competitive firms leads to entry precisely at a point of zero NPV. In this sense, the urgency of potential entrants results in an option to wait with zero value; the fear of competitors usurping one's investment opportunity squeezes out all of the potential value from delay."
- p.709: "With just two firms, the option premium falls to 50%. With five firms, the option premium falls to 15%. The option premium converges to 0%, leaving the traditional NPV rule intact."
- p.709: "As was demonstrated, when competitive pressure is introduced into the real options framework, the cushion provided by the investment option premium falls dramatically. We shall find that competitive pressure greatly increases the likelihood of investment values falling below their initial cost."
- p.718: "However, the inclusion of competitive access to the investment opportunity leads to a rapid erosion in the option to wait, and makes the standard NPV rule a much more accurate description of the actual investment threshold."
