# Sioshansi (2010) Welfare Impacts of Electricity Storage and the Implications of Ownership Structure
- 書誌: Ramteen Sioshansi, *The Energy Journal*, Vol. 31, No. 2 (2010), pp. 173–198. DOI 10.5547/ISSN0195-6574-EJ-Vol31-No2-7（IAEE）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 大規模蓄電は価格を平準化して自らの裁定価値を下げるが、消費者・発電事業者に大きな外部厚生効果を生む。では**誰が蓄電を所有するか**（merchant／消費者／発電事業者）で蓄電の使われ方と厚生はどう変わるか。
- 位置づけ: Sioshansi et al. (2009) が「単一 merchant 所有」を仮定し「merchant は外部効果を考慮しないため社会最適に使わない可能性」を示唆したことを受け、所有構造の比較を理論（命題）と数値（ERCOT 2005）で行う。
- 結論: merchant と発電事業者は蓄電を**過少利用**、消費者は**過剰利用**。完全競争極限では3者とも社会最適に収束（Corollary 1）。現実的な効率（0.65–0.85）では merchant 所有が厚生損失を最小化。混合所有では merchant 主体＋一部消費者所有が最適（1,000 MW・効率0.89で merchant 865 MW＋消費者 135 MW）。

## 2. データ・市場・期間
- ERCOT 2005 年の日次データ（各日の最小・最大時間負荷を2期間の負荷とする）。発電部門は対称複占（TXU, Texas Genco）、小売も対称複占（Reliant, TXU Energy Retail）としてモデル化。価格–負荷関係は線形化した限界発電費用（熱率×燃料スポット価格＋SO2 許可証＋変動O&M）から推定。
- 蓄電: 放電容量 δ̄ MW、充電容量 δ̄/η MW（1時間充電で1時間フル放電）、往復効率 η∈(0,1)。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 2期間（オフピーク l₁、オンピーク l₂）、需要は価格非弾力的（時間不変の小売料金）、価格は p(l) = c₀ + c₁l（c₀≥0, c₁>0）。φ = 1/η。
- 厚生変化: ΔCS（面積 D+E−A）、ΔPS（A+B−D）、裁定利潤 Π_arb(δ) = δ p(l₂−δ) − φδ p(l₁+φδ) = δ[c₀(1−φ) + c₁(l₂−φl₁)] − δ²c₁(1+φ²)。社会厚生 ΔW = ΔCS + ΔPS + Π_arb は δ について強凹（ΔW″ = −c₁(1+φ²)）。
- 社会最適 δ^W（式(2)）と、N 人の対称エージェントの純戦略ナッシュ均衡（Prop.2–4、付録で対称性を証明）。merchant の均衡使用量は式(8)で δ^M = (N/(N+1))·δ^W 型（境界非拘束時）、N→∞ で δ^W に収束。
- 混合所有（§5）: M 発電・Z merchant・N 消費者の同時最適化を相補性問題として PATH ソルバーで解く。

## 4. 主要結果（数値を必ず。表番号を付す）
- Prop.1: 社会最適使用は ΔCS ≥ 0、ΔPS ≤ 0（消費者へ大きな富の移転）。
- Prop.2: N≥1 の対称 merchant は過少利用（外部厚生を内部化せず、スプレッド縮小に「過敏」）。Prop.3: 発電事業者は N=1 なら一切使わず、N≥2 でも過少利用。Prop.4: 消費者は過剰利用（生産者余剰損失を無視）。Corollary 1: N→∞ で社会最適。
- **Fig.2**: 1,000 MW、効率 0.60 未満では誰も使わない。効率上昇とともに merchant/発電は社会最適を下回り、消費者は上回る。
- **Fig.3–5**（厚生損失、社会最適利得に対する%）: merchant 所有は効率・容量に鈍感で常に **12% 未満**。発電所有は効率 0.75 未満で **100% 損失**（使用ゼロ）。消費者所有は効率 0.74 で過剰利用により純厚生が蓄電なしより悪化。効率 0.92 超では消費者所有が merchant を下回る（現実の技術範囲外）。
- **Fig.6–8**（混合所有、1,000 MW、効率 0.89）: 最適配分は merchant 865 MW＋消費者 135 MW。より競争的（発電5社・消費者5社）だと消費者配分が増えるが、発電所有は依然として過少利用。
- 前作（Sioshansi et al. 2009）の引用: 1 GW の蓄電で価格平準化により裁定価値が価格テイカー比 20% 超減少、年間消費者余剰 +$16–35M、生産者余剰 −$14–31M。

## 5. 著者が挙げる限界・今後の課題
- 価格–負荷関係の線形性（起動費等の非凸性や技術の段差で非線形・階段状になりうる）。「our analysis is illustrative」。
- 他の所有形態（自治体、協同組合、垂直統合ユーティリティ＝両余剰を考慮するのでより社会最適に近い可能性、完全規制下の統合ユーティリティは最適を再現）や、外部効果を補償する市場メカニズム・契約の設計は今後の課題。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 「merchant 蓄電は自らのスプレッド縮小に敏感で社会最適より過少利用」「N→∞ の価格テイカー極限で社会最適」という命題は、本研究が merchant 層を価格テイカーのゼロレント参入として扱う根拠（Corollary 1 に対応）。同時に、北海道の参入者が有限数（数社）であれば過少利用・過少投資の方向にバイアスが出ることを注記。
  - 第7章: 裁定利潤の δ に関する二次式（Π_arb = a·δ − b·δ²）は、本研究の π(K) が K に対して凹で急速に枯渇する最も単純な理論形。1 GW で 20% 超の価値減少（PJM）を、北海道の市場規模（PJM の 1/30 程度）で 1 GW が枯渇点になる、というスケール比較に使う。
  - 第8章8.3〜8.4: 「merchant は外部効果（消費者余剰増）を内部化しないため投資誘因が不足」という論理は、政策ウェッジ（容量市場・LTDA）の正当化根拠。所有形態（発電事業者＝北海道電力系による蓄電所有、BTM 併設の発電事業者所有）ごとの運用バイアスの議論にも使える: 発電事業者所有は自社の生産者余剰損失を避けるため**過少利用**（Prop.3）→ 併設蓄電池はスポット裁定に消極的になりうる、という本研究の BTM 議論の理論的補強。
- 支持する点: 大規模蓄電の価格平準化による自己共食い、merchant の過少投資と政策介入の必要性。
- 対立・留意点: 2期間・線形価格・ERCOT 2005（ガス火力主導、再エネなし）。再エネ主導の価格形状（日内形状が TB4h で決まる）は扱わない。
- 手法の源流: 本研究の π(K) は Sioshansi 型の「観測価格＋線形価格影響」で推計するので、直接の方法論的先祖。
- 新規性チェック: 既に行われていること＝所有構造別の運用誘因と厚生順位の理論化。本研究が新たに行うこと＝実データで π(K) と自由参入 K* を求め、政策収入と所有形態（BTM）を組み合わせて北海道の参入を説明。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract (p.173): "Large utility-scale electricity storage can decrease the value of energy arbitrage by smoothing differences in prices on- and off-peak, however this price-smoothing effect can result in significant external welfare gains by reducing consumer energy costs and generator profits. As such, the incentives of merchant storage operators, consumers, and generators may not be properly aligned to ensure socially-optimal storage use."
2. §1 (p.174): "Sioshansi et al. (2009) show that the price-smoothing effect of large-scale storage can reduce the arbitrage value of 1 GW of storage by more than 20%, compared to the arbitrage value for a price-taker."
3. §3 (p.179): "Merchant storage operators underuse storage because they do not internalize the net external welfare gain that results from storage use and are 'overly sensitive' to reducing the price spread between periods 1 and 2—since this price spread yields arbitrage profits."
4. Corollary 1 (p.179): "A perfectly competitive market with all the storage assets owned by either symmetric merchant storage operators, consumers, or generators will yield the social welfare-maximizing usage of storage."
5. §6 (p.189): "Importantly, our results suggest that regulatory and government authorities should be wary of encouraging consumer or generator investment in storage, since merchant storage tends to minimize welfare losses."
