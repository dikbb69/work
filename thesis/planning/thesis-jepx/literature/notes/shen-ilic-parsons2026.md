# Shen, D., Ilic, M., & Parsons, J. (2026) Peak-Load Pricing and Investment Cost Recovery with Duration-Limited Storage
- 書誌: Daniel Shen（MIT EECS）, Marija Ilic（MIT EECS）, John Parsons（MIT CEEPR）. arXiv:2603.13678v1 [eess.SY], 2026-03-14（プレプリント、2段組・Index Terms 付きの全5頁）。誌名・巻号・頁・DOI は PDF に記載なし。謝辞に匿名査読者への言及があるが、投稿先・査読状況は PDF から不明。資金: MIT Energy Initiative Future Energy Systems Center。謝辞に「文法・文体の補助に ChatGPT を使用」とあり。
- 出所: Google Drive の PDF（fileId 1vVyLQUvEBYrsRd8jFn8nr006m3RXhPEy、2603.13678v1.pdf）。2026-09-29 精読。式(1)(4)(6)(7)(8)–(11)・Table I–III は PDF ページ画像（p.2–5）で原文と照合済み（テキスト抽出では式(4)などが崩れていたため）。
- **命題番号について（重要）**: 本論文に Proposition / Theorem / Lemma の番号付き命題はない。主結果は Section III の**式(6)**（on-peak 価格の分解）と**式(8)–(11)**（費用回収の証明、Section III-B）で、前提は **Assumption 1–3**（Section III-A）。引用は「Shen et al. (2026, eq. (6))」「同, Section III-B, eq. (11)」の形にする。
- 以下、「本ノート算出」は本ノート作成者による検算・換算（論文に明示なし）。「著者」は論文の著者。

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 蓄電は出力（MW）に加えて蓄積エネルギー容量（MWh）で放電継続時間が制約される（duration-limited）。この制約は最適価格と投資費用回収をどう変えるか。「均衡ではピーカーは希少時間帯の収入で固定費にちょうど見合う規模になる」という古典的ベンチマークの蓄電版は何か（§I）。
- 貢献: Steiner (1957)/Boiteux (1960) の2期間ピークロード価格モデルに、出力容量 K_S とエネルギー容量 E の**両方**に上限のある蓄電を加え（式(1)）、on-peak 価格と蓄電の技術パラメータ（固定費・往復効率・ピーク長）を結ぶ閉形式を導く。
- 先行研究との差（§I、著者の位置づけ）: Antweiler & Müsgens (2025, "new merit order")・Korpås & Botterud (2020, CEEPR WP 2020-005) は出力制約のみで継続時間は無制約（蓄積エネルギー制約が非拘束）、Nguyen (1976) も継続時間無制約、**Schmalensee (2022) は継続時間制約あり・出力無制約**。本論文は両方に制約を課す。
- 著者の3主張（§I 箇条書き）: (i) 希少性価格は主に蓄電の**固定費**で決まり、往復損失の運転費ではない。(ii) 継続時間制約により on-peak 価格に**ピークイベント当たり**で効く固定費成分が入り、希少イベントを負荷継続曲線に集約して蓄電を評価することはできない。(iii) 蓄電が最適に規模設定・運転されれば、結果の価格は投資費用回収を保証する。

## 2. データ・市場・期間
- 理論論文で実データはない。数値例（§IV）は NREL Annual Technology Baseline を「様式化」したパラメータ（Table I）。
  - Peaker: 運転費 $100/MWh、年換算投資費 $120,000/MW-年。Baseload: $20/MWh、$240,000/MW-年。
  - 蓄電（Li-ion）: 出力 I_{s,q} = $36,000/MW-年、エネルギー I_{s,E} = $31,000/MWh-年、往復効率 η = 0.85。
- 代表日を n = 365 回繰り返して年次サイクルとする。1日は on-peak 4時間・off-peak 20時間。線形逆需要 p_i = a_i − b_i ℓ_i、需要の弾力性 0.1（off-peak の基準点 10 GW・$20/MWh、on-peak の基準点 15 GW・$100/MWh）。Pyomo で定式化し Gurobi v12.0.3 で求解。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- **均衡概念**: 社会計画者が余剰（消費者便益 − 運転費 − 固定費/n）を最大化する Steiner–Boiteux 型の最適化（式(1a)–(1l)）。「均衡価格」は需給バランス制約(1b)の**双対変数 λ_i**。分権化（自由参入の競争均衡との同値）、不確実性、参入ダイナミクスの議論はない。
- 2期間 i ∈ {on-peak, off-peak}、期間長 T_i。技術は baseload B・peaker P・蓄電 S。固定費は年間ピークサイクル数 n で日次化（1/n）。蓄電は充放電出力 q_i^± ≤ K_S（(1e)(1f)）、往復効率 η を充電側にかけた総エネルギー収支 (1i)、蓄積エネルギー上限 E（(1j)(1k)）。
- 閉形式を得る3仮定（Section III-A）:
  - Assumption 1（Price ordering）: 最適消費の下で on/off 価格差が蓄電投資を誘発するのに十分 → 蓄電は off-peak に充電、on-peak に放電（脚注2: 価格差が閾値未満なら蓄電なしの標準モデルに帰着。off-peak が高価格なら期間名を入れ替える）。
  - Assumption 2（Sufficient off-peak duration）: T_onp < η·T_offp → 出力制約は on-peak 放電でのみ拘束（σ^-_onp > 0、他は 0。式(5)）。
  - Assumption 3（No inter-period carryover value）: 蓄積エネルギーに期間をまたぐ継続価値なし → on-peak 終了時の蓄積エネルギーはゼロ。
  - 著者の想定: 「単一の支配的な日次ピークと長い低純負荷期間」を持つ太陽光主導系（昼に充電し夕方に放電）。Schmalensee (2022) の設定に倣う（脚注1）。
- 導出: KKT-3 と式(5)から σ^-_onp = I_{s,q}/(n·T_onp)、KKT-4 から γ^+ + γ^- = I_{s,E}/n（エネルギー上限の影子価格の合計＝エネルギー容量の日次費用）。これで式(4)の双対変数を消去して式(6)を得る。

## 4. 主要結果（数値を必ず。表番号を付す）
- **式(6)（on-peak 価格の分解）**: λ_onp = λ_offp/η + (1/n)·(I_{s,E} + I_{s,q}/T_onp)。第1項は充電費用を効率で割り戻した変動費相当、第2項が固定費プレミアム。条件: Assumption 1–3、2期間・計画者最適・線形費用・決定論。
- **式(7)（ピーカーとの対比）**: λ_onp = c_P + (1/n)·(I_P/T_onp)。式(6)との違いは、エネルギー容量費 I_{s,E}/n が T_onp で割られないこと。「エネルギー容量プレミアムは年間の on-peak 総時間 n·T_onp に依存せず、年間ピーク回数 n のみに依存する」（p.3）。出力容量費の項 I_{s,q}/(n·T_onp) はピーカーと同様に総ピーク時間で償却される。
- **「ピークイベント単位で回収」の正確な内容**: イベント単位になるのは**エネルギー容量費 I_{s,E} の部分だけ**。E は K_S·T_onp（ピーク中フル出力で放電できる大きさ）に設定されるので、放電した on-peak 1 MWh あたりの I_{s,E} 負担は I_{s,E}/n で T_onp に依存しない（本ノート解釈: E の1 MWh は1イベントに1回しか使えないため n で割られる）。ゆえに「希少イベントを負荷継続曲線に集約して蓄電を評価できない」（§I, §V）。
- **費用回収（Section III-B, 式(8)–(11)）**: 需給バランス制約の双対 λ による一様価格の下で、最適に規模設定・運転された蓄電は、営業利益（on-peak 売電収入 − off-peak 購入費）だけで投資費用 I_{s,q}K_S + I_{s,E}E を**ちょうど（等号で）回収**する（式(11)）。導出に使う条件: 式(6)、エネルギー収支 T_offp·q^+_offp = T_onp·q^-_onp/η（式(9)）、フル出力放電 q^-_onp = K_S（式(10)）、**E = K_S·T_onp**（エネルギー容量が on-peak 全体をフル出力で放電できる大きさに最適設定）。→ 主張は「ゼロ利潤の恒等式」で、最適規模でない場合の回収、不確実性下の回収、参入ダイナミクスは論じていない。
- **数値（§III-A）**: I_{s,q} = $36k/MW-年、I_{s,E} = $31k/MWh-年、λ_offp = $20/MWh、η = 85%、T_onp = 4h で、効率関連項 $23.5/MWh、固定費項 $109.6/MWh（「固定費は効率損失の約5倍」）。
  - 本ノート算出（n = 365）: 固定費項の内訳は I_{s,E}/n = $84.9 と I_{s,q}/(n·T_onp) = $24.7。$23.5 は λ_off/η（= 20/0.85）全体で、効率損失のみ（λ_off/η − λ_off）は $3.5/MWh。固定費項は効率損失の約31倍。
  - 本ノート算出（継続時間の効果、n = 365）: プレミアムは T_onp = 2h で $134.2、4h で $109.6、8h で $97.3/MWh。長いピークで薄まるのは出力費の項だけで、下限は I_{s,E}/n = $84.9。
- **数値例（§IV, Table II・III）**:
  - 蓄電あり: on-peak λ = $142/MWh（ℓ 14.4 GW、q_B 10.5、q^- 3.9 GW）、off-peak λ = $28/MWh（ℓ 9.6、q_B 10.5、q^+ 0.9 GW）。容量 K_B = 10.5 GW、K_P = 0、K_S = 3.9 GW、E = 15.5 GWh（E/K_S ≈ 4.0h）。
  - 蓄電なし: on-peak λ = $182/MWh（ℓ 13.8、q_P 3.8、q_B 10.0 GW）、off-peak λ = $20/MWh。K_B = 10.0 GW、K_P = 3.8 GW。
  - 著者の要約（§V）: 価格スプレッドの縮小（本ノート算出: $162 → $114/MWh）、蓄電によるピーカー代替（3.8 GW → 0）、baseload との補完的投資（+0.5 GW）。
  - 本ノート検算: 蓄電ありの on-peak は式(6)で 28/0.85 + 109.6 = $142.5 と一致。蓄電なしの on-peak は c_P + I_P/(n·T_onp) = 100 + 120,000/(365×4) = $182.2 と一致。
- **価格上限・希少性価格の扱い**: モデル内に価格上限も VOLL（不足エネルギー）もない（線形逆需要のみ）。§IV–§V の定性的記述のみ:
  - (a) 現実の希少性価格は VOLL 基準で $1,000/MWh 超になり得るので、低効率技術（水素、RTE 20–40%）でも効率損失は固定費に比べ小さく、on-peak 価格の大半は投資費用に対応する（§IV）。
  - (b) **希少性価格に補償措置（容量支払い等）なしで価格上限がかかれば、蓄電への投資誘因は不足し、容量ミックスが最適でなくなり総余剰が下がる**（§V）。
  - (c) shoulder 時間帯の裁定収益はあり得るが「回収の大半はピーク時に起きる」と主張。多期間裁定は必要な希少性価格の水準を下げるが、希少期間が主たる回収源であり続けると予想（§V。導出なし）。

## 5. 著者が挙げる限界・今後の課題
- 強い仮定（Assumption 1–3）でピーカーとの1対1比較を可能にした。仮定を緩めると off-peak 期間に関する追加項が出る（未解明）。ただし「継続時間制約により蓄積エネルギー容量費が全希少時間に償却されない」という核心は仮定なしでも成り立つと主張（§V、証明なし）。
- 2期間モデルは蓄電の投資費用がピーク期間のみで回収される前提。実際は shoulder 期間の裁定もある（§V）。
- 今後: ピーク継続時間の不確実性、多期間裁定の取り込み（§V）。
- 明示されていない限界（本ノート所見）: 決定論・単一の日次ピーク・計画者最適のみ。複数日にまたがる持ち越し（Assumption 3 の否定）や風力主導の不規則な価格パターンは対象外。査読状況が不明なプレプリント。

## 6. 本研究との関係
- 引用予定箇所:
  - **第5章5.4.3（均衡条件: 自由参入で限界参入者の収益＝年間固定費）**: 式(8)/(11)（営業利益 = I_{s,q}K_S + I_{s,E}E）が限界参入者のゼロ利潤条件の様式化版。T 時間蓄電1 MW の年間固定費は I_{s,q} + T·I_{s,E}（例: 36,000 + 4×31,000 = $160,000/MW-年）で、必要な営業利益はこの水準（本ノート算出。E = K_S·T より）。式(6)を移項すると必要スプレッドは λ_on − λ_off = λ_off·(1/η − 1) + (I_{s,E} + I_{s,q}/T)/n（本ノート算出）。n（有効サイクル数）が小さいほど 1/n で大きくなる（T = 4h のプレミアムは n = 365 で $109.6、n = 200 で $200、n = 100 で $400/MWh）。
  - **第8章8.4（Schmalensee 2022 との対比）**: 著者自身が Schmalensee を「継続時間制約あり・出力無制約」と位置づけ、出力・エネルギー両制約へ拡張したと主張（§I。schmalensee2022.md でも蓄電は容量 S のみで出力上限を別置きしない）。前提は Schmalensee と同じ太陽光主導系（脚注1）。結論の重なり: 補償なき価格上限では蓄電の投資誘因が不足（Schmalensee §5 と Shen §V）。差分: Shen は継続時間制約が生む「イベント単位の回収」を式(6)で明示。他方 Schmalensee は確率的な太陽光出力・需要と VOLL を入れた競争均衡（零期待利潤）の証明で、Shen は決定論の計画者双対。
  - 第8章8.3 付近（政策ウェッジ）: §V の「補償なき価格上限 → 蓄電の過少誘因」を、JEPX の価格上限・スパイク抑制と容量市場・LTDA の関係を述べる際の理論的裏付けの一つとして補助的に引用可。
- 支持: 蓄電の固定費回収は希少性（スプレッド）に依存し、損失の運転費ではない。蓄電の導入でスプレッドが縮小しピーカーを代替する（Table II–III）。Emmanuel & Denholm (2022) の「導入量に伴う裁定価値の低下」と同方向。[2][3][4]（Sioshansi et al. 2009、Zamani-Dehkordi et al. 2017、Lamp & Samano 2022）を「蓄電はスプレッドを縮める」実証根拠として引用しており、sioshansi2009.md・lamp-samano2022.md と同じ根拠群。
- **引用時の注意**:
  - 「命題」ではなく式(6)・(11)として引用する。「最適規模なら回収が保証される」は、Assumption 1–3・E = K_S·T_onp・計画者双対価格という条件付きで、等号（ゼロ利潤）の主張。「利益が出る」ではない。
  - 「均衡」は計画者最適の双対価格を指す。自由参入の競争均衡や本研究の逐次自由参入 NPV ゼロ経路（CLAUDE.md ルール6）との同値は論じていない。K* の算出法としては引用せず、（i）固定費の構造（出力費＋エネルギー費）と（ii）回収が n（イベント数）に依存する、という解釈枠組みとして使う。単年静学のゼロ利潤で K* を出さない方針と矛盾させない。
  - Assumption 2–3（単一の日次ピーク、長い off-peak、持ち越し価値なし）は太陽光主導系の想定。風力主導の北海道では複数日にまたがる持ち越しや不規則なスプレッドがあり得るため、適用範囲を明記する。「回収の大半は希少ピークで起きる」（§V）も北海道では実証課題。
  - 蓄電の最適継続時間は E/K_S = T_onp（数値例 15.5/3.9 ≈ 4.0h）。本研究が継続時間を4hに固定するなら、それは「ピーク長が4h」という前提と同義（本ノート解釈）。
  - 本文の記述ミス: §IV の文 "With storage, on-peak prices are $182/MWh" は Table II（蓄電あり $142、蓄電なし $182）と矛盾する（$182 は蓄電なしの価格）。引用には式(6)で検算できる Table II の値（142/28）を使う。「効率項 $23.5」は λ_off/η 全体で、効率損失のみなら $3.5。式(2)の ζ^-_j の符号は KKT-2 から導くと + になる（ζ = 0 なので結論に影響なし）。
  - プレプリント（v1）。査読済み版が出たら書誌・式番号を確認する。
- 新規性チェック: 継続時間制約付き蓄電の費用回収の閉形式は本論文の貢献。本研究は（a）風力主導ゾーンの実証的 π(K)、（b）自由参入均衡 K*、（c）価格上限・容量市場を含む政策ウェッジ、を扱う点で異なる。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract (p.1): "Unlike conventional generators, the binding duration constraints lead storage to recover energy capacity costs on a per-peak-event basis instead of amortizing these costs over total peak hours."
2. §III-A (p.3): "Notably, this energy capacity term is not scaled by the on-peak duration T_onp; the energy capacity premium is independent of the total duration of on-peak hours across a year (nT_onp) and is solely dependent on the number of peaks n during a year."
3. §III-B (p.4): "Thus, uniform pricing set by the energy balance dual (1b) in each period ensures an optimally sized storage unit will recover its investment costs through energy profits alone."
4. §V (p.5): "If scarcity prices are administratively capped without accompanying compensation mechanisms (e.g. capacity payments), storage will be under-incentivized, leading to a suboptimal capacity mix and lower total system welfare."
5. §V (p.5): "our underlying takeaway — duration limits restrict stored energy capacity costs from being amortized over all scarcity hours — still holds without adopting these assumptions."
