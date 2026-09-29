# Schmalensee (2020/2022) Competitive Energy Storage and the Duck Curve
- 書誌: Richard Schmalensee, MIT CEEPR Working Paper WP 2020-012, July 2020（WP-2019-009 の大幅改訂版）。公刊版は *The Energy Journal* 43(2), 2022（フォルダ名の「2022」は公刊年）。引用時は公刊版を確認し DOI を補うこと。本ノートは CEEPR WP 版に基づく。
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: FERC Order 841 や EU Clean Energy Package が前提とする「エネルギー市場の競争は蓄電投資にも（発電と同様に）ほぼ最適な誘因を与える」という命題は、ダックカーブ問題の文脈で成り立つか。
- 貢献: Boiteux (1960, 1964)–Turvey (1968) 型のピークロード・プライシングモデルに、太陽光（昼のみ確率的出力）、ガス（昼夜）、短期蓄電（往復損失 η）を組み込み、**期待システム費用最小化の一階条件が、再エネ・ガス・蓄電それぞれのゼロ期待利潤条件（長期競争均衡）と一致する**ことを示す。
- 主張（Abstract）: "In the most interesting cases, if energy market prices are uncapped, all expected cost minima are long-run competitive equilibria, and the long-run equilibrium value of storage capacity minimizes expected system cost conditional on generation capacities."
- 脚注7で先行の裁定収益性研究（Salles et al. 2017, Giulietti et al. 2018）を「現行価格では資本費を賄えないという発見は、市場が与える投資誘因の一般的最適性については何も語らない」と位置づける。

## 2. データ・市場・期間
- 理論論文。動機付けに CAISO の日内平均 DA-LMP（2010, 2015, 2016, 2017 年、年平均で正規化した Joskow 2019 の Figure 2）を用い、「太陽光浸透とともに日内価格差が拡大した」ことを示す。
- モデル設定: 昼（太陽光あり）と夜（なし）が交互に来る同長の期間。昼夜の需要と太陽光出力は独立の確率変数、需要は完全非弾力的。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 4技術・規模に関して収穫一定: ガス（容量 G、資本費 C_G、限界費用 c）、再エネ（容量 R、資本費 C_R、限界費用0、昼の出力 θR、θ∈[θ̲,1]）、不足（資本費0、VOLL v）、蓄電（容量 S、資本費 C_S、往復効率 η<1）。パラメータ制約 C_G < C_R、c < v、C_R < c。焦点は S < θ̲R（蓄電が太陽光の最小出力より小さい）の場合。
- 扱いやすさのため**毎夜に蓄電を完全放電**する制約を課す（脚注14: これがないと Geske & Green 2019 のように数値解法が必要）。Section 3 で「ガスの限界費用と夜の期待価格の関係」により3つのレジームを区別し、各レジームでの競争的蓄電運用ルール（昼: 蓄電が需要曲線を垂直→水平→垂直の階段状にする Figure 3）を導出。
- **均衡概念**: 連続体の無限小な価格テイカー（発電・蓄電）による長期競争均衡＝各技術のゼロ期待利潤。式(4.6a)(4.6b)(4.6c) が R, G, S それぞれの「資本費＝期待単位純営業収入」条件。蓄電については、蓄電が満充電になる事象の確率×満充電時の夜の期待収入（η 倍）が資本費に等しい。
- 二階条件: ヘッセ行列の対角要素は正（(4.7a)–(4.7c)）だが正定値性は証明できず → 「他の2つの容量を所与とすれば、3番目の長期競争均衡値は期待費用を最小化する」。

## 4. 主要結果（数値を必ず。表番号を付す）
- 数値結果はない。命題的結果:
  - 3レジームすべてで、期待総費用最小化の一階必要条件⇔再エネ・ガス・蓄電の零期待利潤（§5: "all minima of expected system cost can be supported as zero-expected-profit long-run competitive equilibria"）。
  - 一部のパラメータで効率的でない零利潤均衡が存在する可能性は排除できないが「odd and unusual cases」に限られると推測。
  - **価格上限がある場合**（米欧の大半、ERCOT を除く）: Boiteux–Turvey の論理により発電投資誘因が不足するのと同様、**蓄電の裁定投資誘因も不足**する。"caps on wholesale energy prices will lead to inadequate incentives for investment in storage for energy arbitrage." → 蓄電にも「容量メカニズム」の類が必要になると予想するが、適切な蓄電容量水準の決め方は不明。

## 5. 著者が挙げる限界・今後の課題
- 昼夜の需要と再エネ出力の独立性（天候相関を排除）は「強い仮定だが緩め方が不明」（§2）。
- 毎夜完全放電の制約（脚注14）。
- 需要の完全非弾力性（費用最小化＝厚生最大化、脚注11）。
- ヘッセ行列の正定値性が未証明（§4–5）。
- 蓄電は裁定用途のみ（脚注3: 周波数調整、送配電投資繰延、予備力は対象外）。
- 蓄電の容量メカニズムにおける「適正容量」の決め方は未解決（§5）。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 「価格上限のない競争的エネルギー市場では蓄電の自由参入（零利潤）均衡が費用最小解を支持する」という理論的ベンチマークとして。本研究の merchant 層ゼロレント条件はこの長期競争均衡の直接的な適用。
  - 第8章8.3〜8.4（政策ウェッジ）: 「価格上限がある市場では蓄電の裁定投資誘因が不足し、容量メカニズムが必要になる」という主張は、本研究が JEPX の実質的価格上限（インバランス料金上限・スパイク抑制）とフロア 0.01 円の下で容量市場・LTDA を政策ウェッジの構成要素と位置づける根拠。missing money 問題の蓄電版として引用。
  - 第9章: 「適切な蓄電容量水準をどう決めるか不明」という問いに対し、本研究の K*（自由参入均衡）と政策層の容量（2.3 GW）の比較が一つの答え方になる、と位置づける。
- 支持する点: 蓄電の価値は日内価格差（昼の低価格 vs 夜の高価格）で決まるというダックカーブ的構造（本研究の TB4h 指標の理論的背景）。太陽光の日内パターンが裁定価値を生む。
- 対立・留意点: モデルは太陽光（昼のみ出力）に特化しており、**風力（昼夜を問わず出力）には日内スプレッドを生む構造がない**。本研究の「風力は水準を下げるが日内スプレッドを広げない」という主張は、Schmalensee のモデル構造から自然に導かれる帰結として説明できる（風力は θR が昼夜双方に入るため、昼夜差を作らない）。
- 手法の源流: 二層参入の merchant 層＝Boiteux–Turvey 型の零利潤条件。本研究は静学的で不確実性を捨象するため、Schmalensee の「不足確率×VOLL」による発電の資本費回収部分を容量市場収入 κ·P_cap に置き換えていると解釈できる。
- 新規性チェック: 既に行われていること＝競争的蓄電の長期均衡が効率的であることの理論証明、価格上限下での誘因不足の指摘。本研究が新たに行うこと＝風力主導ゾーンでの実証的 π(K) と K*、価格上限・フロアの下での政策ウェッジの定量分解。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "In the most interesting cases, if energy market prices are uncapped, all expected cost minima are long-run competitive equilibria, and the long-run equilibrium value of storage capacity minimizes expected system cost conditional on generation capacities."
2. §1 (p.3): "The pattern in Figure 2 suggests that with sufficient solar penetration, competitive storage providers could find it profitable to buy at mid-day when prices are low and sell a few hours later as solar generation begins to drop off and prices become high, thus mitigating or perhaps solving the duck curve problem."
3. §4 (p.17): "Conditions (4.6) thus establish that all minima of expected total cost can be supported as equilibria of markets with continua of infinitesimal, price-taking suppliers of generation and storage."
4. §5 (p.19): "Just as caps on wholesale energy prices reduce incentives for investment in generation, it follows from the Boiteux-Turvey-style analysis here that caps on wholesale energy prices will lead to inadequate incentives for investment in storage for energy arbitrage."
5. §5 (p.19): "it does seem likely that some analog to 'capacity mechanisms' may come to be felt to be necessary to supplement energy arbitrage revenues to increase the supply of storage. 'Capacity mechanisms' use reliability to determine the appropriate level of generation capacity; it is not clear how the appropriate level of storage capacity of various sorts would sensibly be determined."
