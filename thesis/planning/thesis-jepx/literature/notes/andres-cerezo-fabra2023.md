# Andrés-Cerezo & Fabra (2023) Storing Power: Market Structure Matters
- 書誌: David Andrés-Cerezo and Natalia Fabra, *The RAND Journal of Economics*, Vol. 54, No. 1 (Spring 2023), pp. 3–53. DOI 10.1111/1756-2171.12429（オープンアクセス、CC BY-NC-ND）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 蓄電の**運用と投資**の誘因は市場構造（蓄電側・発電側の市場支配力、垂直統合）にどう依存するか。市場は蓄電投資に適切なシグナルを送るか。
- 貢献（§1 Related literature）: (1) 商品貯蔵の古典理論（Newbery & Stiglitz 1979 等）と異なり、確率的需要を捨象して**戦略的相互作用と所有構造**に焦点を当て、複数の市場構造を単一の扱いやすい枠組みで比較し厚生順位を与える。(2) 先行研究と異なり**内生的な蓄電投資**を市場支配力の程度と関係づける。「生産と蓄電の決定を別々に分析すると市場支配力による厚生歪みを過小評価する」。
- 結論の要点: 完全競争（発電・蓄電とも）は第一最善を再現。発電側の市場支配力は価格曲線を急峻にして裁定を儲かるものにし**過剰投資**を誘発、蓄電側の市場支配力は価格影響を内部化して運用を平準化し**過少投資**を誘発、垂直統合が最悪。
- Butters et al. (2021) を脚注10で「動学的競争均衡の蓄電池採用モデル」として言及、Sioshansi (2014) 等は市場構造を比較するが投資を扱わない、と位置づけ。

## 2. データ・市場・期間
- 純理論論文。実証データなし（動機付けで欧州の蓄電成長見込み 3 GW→26 GW（2030年）等を引用）。
- 需要は「1日」を表す負荷持続曲線 G(θ)（θ = 再エネ控除後の純需要、区間 [θ̲, θ̄]、密度は平均対称）。脚注15: "The assumptions about the demand process make our model well-suited to capture the diurnal problem in solar-dominated electricity systems, with θ being load net of solar generation."

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 発電: 費用 c(q)=q（線形限界費用）、支配的企業が資産の割合 α、フリンジが 1−α を保有（Perry & Porter 1985 型、c_D(q)=q/α, c_F(q)=q/(1−α)）。発電容量は所与。
- 蓄電: 容量 K まで充放電費用ゼロ、充放電速度制約なし、日末で無価値。投資費用 C(K) は増加・（弱）凸。2段階ゲーム: 第1段階で K を一度だけ選択、第2段階で生産・蓄電運用を同時決定。
- 市場構造: (i) 蓄電フリンジ（自由参入）、(ii) 独立蓄電独占、(iii) 支配的発電企業による垂直統合蓄電。ベンチマークは第一最善 FB（計画者が発電と蓄電を決定）と第二最善 SB（発電は市場、蓄電のみ計画者）。
- **競争的蓄電の自由参入条件（Proposition 3, 式(12)）**: C(K)/K = [θ₂^C(K) − θ₁^C(K)]/(1−α²)。すなわち**平均投資費用＝裁定スプレッド（買値 θ₁ と売値 θ₂ の差、市場価格はフリンジの限界費用 θ/(1−α) で決まる）**。"the free entry condition implies that there is investment in storage capacity until the returns from storage just cover the investment costs." Lemma 4: 与えられた K の下で競争的蓄電の運用は第二最善と同一（価格の平準化＝生産の平準化）。
- 結果 (ii): K^C > K^SB > K^FB（過剰投資、α に増加）。理由: 市場価格＝フリンジの限界費用曲線は産業限界費用より急峻で裁定価値が過大、かつ自由参入は限界価値＝**平均**費用で止まり凸費用の下では平均<限界なのでさらに過剰。
- 独占蓄電（Prop.4）: 自らの充放電の価格影響（独占・買手独占）を内部化し、価格ではなく限界収入/限界支出を平準化 → 運用が分散し利潤低下 → 過少投資。垂直統合（Prop.5）: 自社発電への価格影響も内部化し最も歪む。

## 4. 主要結果（数値を必ず。表番号を付す）
- 理論論文のため数値表はない。主要命題:
  - Prop.1/2: K^SB > K^FB（第二最善は市場供給曲線に沿って費用節約を評価するため急峻→容量が多い）。
  - Prop.3: 競争的蓄電 K^C は (12) の一意解、K^C > K^SB > K^FB、α に増加。
  - Prop.6 (i): 任意の K>0 で CS^FB > CS^SB = CS^C > CS^j、W^FB > W^SB = W^C > W^j（j=独立独占 M、垂直統合 I）。(ii) K > K̂（独占が容量制約に当たらない水準）または一様分布のとき CS^M > CS^I、W^M > W^I。
  - §6 拡張: 往復効率 σ<1（式(19)）、負の純需要、充放電速度制約、需要の一般形状、逐次手番でも主要結果は不変。
- 政策含意（§5末尾）: 第二最善の実装法として「小規模事業者の投資を K^SB まで許可」または「K^SB 分の蓄電オークションを小規模事業者限定で実施」。結論: "the same storage capacity in the hands of competitive storage owners is more socially valuable than if it is allocated to large storage firms or to generators." 規制当局は送電–蓄電の統合より**発電–蓄電の統合と蓄電所有の集中**を警戒すべき。

## 5. 著者が挙げる限界・今後の課題
- モデルは「highly stylized」（§2冒頭）。省略事項を §6 で検討: 往復効率、負の純需要、充放電速度制約、非対称需要、逐次手番、蓄電の外部性。
- 脚注19: 発電（再エネを含む）投資を外生とする。「Endogenizing investment in both renewable generation and storage assets is likely to stress a potential complementarity between the two」。
- 確率的需要を捨象（脚注15: 太陽光主導系統では予測可能な変動が不確実な変動より量的に重要）。**風力主導系統の不確実性は扱わない**。
- 結論: 蓄電の正の外部性（供給安定、学習効果、送電投資の代替）を考慮していないが、それらを含めれば支援メカニズム（蓄電容量オークション）の根拠は強まる。分散型蓄電（EV、BTM）は卸価格に晒されていない点も指摘。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 本研究の自由参入条件 π_spot(K)·c + κ·P_cap − c_req = 0 の理論的原型として式(12)（平均投資費用＝裁定スプレッド）を引用。「自由参入は限界価値＝平均費用で止まる」という指摘は、本研究が資本費を kWh 単価（線形）で置く近似の正当化にも使える。
  - 第7章: 「与えられた K の下で競争的蓄電は価格を平準化し、スプレッド θ₂−θ₁ は K に減少」という構造が本研究の π(K) 曲線の理論的裏付け。Lemma 4（競争的運用＝第二最善）は、本研究のバックテストで価格テイカー最適運用を用いることの根拠。
  - 第8章8.3〜8.4: 「発電側に市場支配力があると蓄電は過剰投資になる」は、北海道（北海道電力の高シェア）で観測される参入が純粋な市場シグナル以上になりうる別経路として言及可能（ただし本研究の主張は政策ウェッジであり、市場支配力経路は識別できないと断る）。LTDA（長期脱炭素電源オークション）は著者が推奨する「蓄電容量オークション」の実装例として位置づけられる。
  - 第9章: 拡張課題（再エネ投資の内生化、BTM蓄電が卸価格に晒されない）と本研究のBTM併設価値の議論を接続。
- 支持する点: 競争的蓄電の運用は社会最適だが投資量は市場構造に依存し、市場だけでは最適投資に到達しない → 政策介入（オークション）の理論的根拠。
- 対立・留意点: 本論文では競争的蓄電は**過剰**投資（発電側市場支配力のため）なのに対し、本研究は純市場均衡 K*=0（過少）という逆の状況。違いは (a) 本研究は資本費が高く裁定スプレッドが小さい現実の水準を使う、(b) Andrés-Cerezo & Fabra は費用凸性と限界費用入札を仮定、(c) 太陽光主導の決定論的日内形状を仮定しており、風力主導で日内スプレッドが広がらない北海道では裁定価値自体が小さい。
- 新規性チェック: 既に行われていること＝市場構造別の運用・投資の理論的順位づけ、自由参入条件の定式化。本研究が新たに行うこと＝実データで π(K) を推計し K* を数値的に求め、容量市場・LTDA 等の政策収入を参入条件に明示的に加えた二層参入（政策層外生／merchant層ゼロレント）の実証。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract (p.3): "Market power reduces overall efficiency through two channels: It induces an inefficient use of the storage facilities, and it distorts investment incentives. The worst outcome for consumers and total welfare occurs under vertical integration."
2. §4 Competitive storage (p.14): "The free entry condition implies that there is investment in storage capacity until the returns from storage just cover the investment costs." / "because of the free-entry condition, firms invest in storage capacity up to the level at which the marginal value of storage equals average investment costs."
3. Proposition 3 (p.14–15): "(i) Equilibrium investment, K = K^C, is the unique solution to C(K)/K = [θ₂^C(K) − θ₁^C(K)]/(1 − α²). (ii) There is inefficient over-investment in storage, K^C > K^SB > K^FB, which is increasing in α."
4. §5 (p.22): "it is not enough to promote investments in storage if market power in production remains. The reason is that storage facilities will be inefficiently operated if market prices are distorted due to market power."
5. §7 Conclusions (p.27): "Our results suggest that markets will not deliver optimal incentives regarding storage decisions, unless there is enough competition in both the generation and the storage segments. ... Taking these additional sources of social value into account strengthens the case for putting in place support mechanisms, for example, auctions of storage capacity, similar to the ones that have already been used in various countries."
