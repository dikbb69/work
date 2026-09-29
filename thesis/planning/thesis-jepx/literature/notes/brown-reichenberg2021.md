# Brown & Reichenberg (2021) Decreasing market value of variable renewables can be avoided by policy action
- 書誌: T. Brown and L. Reichenberg, *Energy Economics* 100 (2021) 105354. DOI 10.1016/j.eneco.2021.105354（Received 13 Feb 2020, accepted 25 May 2021）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 「風力・太陽光80%超の系統も経済的」とする研究と、「VRE は自らの市場価値を共食いし費用回収できない（統合に限界）」とする市場価値研究の矛盾をどう解くか。
- 主張: 市場価値研究が見出す価値低下は、**VRE を補助・割当で系統に「押し込む」という暗黙の政策仮定の帰結**であり、変動性の帰結ではない。技術が変動的であるか否かに関係なく、技術固有の支援で最適シェア以上に押し込めば市場価値は数学的に必ず低下する（原子力でも同じ、Fig.8）。代わりに **CO2 価格・上限**で VRE を引き込めば、80%超の浸透でも MV=LCOE が保たれる。
- 貢献: 長期均衡モデルで、市場価値が「参入させる政策手段」に依存することを理論（§2–3）と数値（§5, EMMA 改変）で示す。先行の市場価値研究（Hirth 2013, Mills & Wiser 2013, 2015 等）を「暗黙の政策仮定」「複数の交絡因子の同時変更」「市場価値の無視」により本質を見落としたと批判。

## 2. データ・市場・期間
- Hirth (2013) の EMMA を改変した長期最適化（グリーンフィールド、揚水のみ既存・8h）。独・波・仏・蘭・白、2010年の時間値負荷・気象。VOLL 1,000 €/MWh、割引率 7%、NTC は 2010年夏の値。風力 1,040 €/kW、太陽光 510 €/kW（2030年の DEA 予測）、原子力 6,000 €/kW。ユニットコミットメント・ベースロードプレミアム・予備力は非モデル化。CO2 価格の既定値 20 €/t は除去。
- 柔軟性シナリオ: 国間送電増強、蓄電池、地下水素貯蔵の新設を許可。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- **零利潤ルール**（§2.1）: 完全競争・自由参入退出・線形費用の長期均衡では各技術 s について MV_s = LCOE_s (1)。LCOE は「実際に発電した（抑制後の）エネルギー」で平均する定義。
- **支援政策**（§2.2）: MV_s = LCOE_s − μ_s (2)、μ_s は等価 Feed-in Premium（シェア制約 (19) のシャドウ価格）。高いシェアほど μ_s が大きく MV が下がる。価格が下がる2機構: (a) 供給曲線の右シフト（メリットオーダー効果）、(b) 技術 s が価格設定するとき補助分だけ低い実効限界費用で入札。
- **CO2 政策**（§3.4）: CO2 上限 (24) のシャドウ価格 μ_CO2 に対し LCOE_s = MV_s − e_s μ_CO2 (27)。排出ゼロの技術は零利潤ルールを満たし続ける。
- §3.5・付録B: 蓄電、多ノード、凸費用、設置上限などを加えても結論は不変。需要が完全非弾力的なら「特定技術への補助＝他技術への課税」と同値（価格を一定量持ち上げるだけ）。

## 4. 主要結果（数値を必ず。表番号を付す）
- **Fig.2**: VRE 支援政策では MV は浸透率とともに低下し **50% でゼロ**（負にもなる）。CO2 政策では MV はわずかに下がった後、70% で 80 €/MWh 超まで緩やかに上昇。
- **Fig.3**: 支援政策下では LCOE はほぼ一定（風→太陽光→風の混合変化と抑制で微増）、FiP が差を埋めて上昇。
- **Fig.6（柔軟性込み）**: CO2 政策で送電・蓄電池・水素貯蔵を許すと MV は 100% 浸透まで規則的で約 71 €/MWh でプラトー。柔軟性なしでは 70% 超で抑制の急増により LCOE が上がり MV も急上昇。100% VRE でシステム平均費用 114 €/MWh、CO2 価格は 50% で 55 €/t → 100% で 165 €/t。全 VRE でも相対市場価値（RMV）は 0.62 までしか下がらない（Fig.E.25）。
- **Fig.7**: 水素貯蔵が最後の排出除去に不可欠。「蓄電と送電の裁定が価格を設定し始め、VRE 豊富時の需要側入札と希少時の供給側入札により価格の特異性（ゼロ／極端の二極化）は生じない」（付録 E.6）。
- **Fig.8**: 原子力支援政策でも MV は低下（34 €/MWh から）、CO2 政策では MV=LCOE。

## 5. 著者が挙げる限界・今後の課題
- 需要の完全非弾力性（脚注4: 弾力的需要なら支援と課税の差が大きくなる）。
- ユニットコミットメント、予備力市場、ベースロードプレミアムを省略（理論との整合のため）。
- 単年（2010年）の気象、NTC 固定（拡張シナリオ以外）。
- ハイブリッド政策（CO2 価格＋支援）は投資家リスクと資金調達費用を下げうるとして §6.2 で議論、最適設計は今後の課題。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: 長期均衡の**零利潤ルール MV=LCOE** と「支援政策は MV = LCOE − μ」という定式化は、本研究の自由参入条件 π_spot(K)·c + κ·P_cap − c_req = 0 において、政策収入（κ·P_cap、LTDA、補助）を μ に対応する「市場外収入」として位置づける根拠。**本研究の「政策ウェッジ」は Brown & Reichenberg の μ_s（等価 FiP）の蓄電池版**として明示的に接続できる。
  - 第8章8.3〜8.4: 「特定技術を最適シェア以上に押し込めば、その技術の市場価値（本研究では蓄電池の π_spot）は必然的に下がる」という論理は、北海道の政策層参入（≈2.3 GW）が merchant 層の spot rent を枯渇させる（K* = 0）ことの理論的説明。さらに「VRE 支援政策で押し込まれた風力が価格水準を下げる」ことが蓄電池の価値低下にも波及する経路。
  - 第9章: 「CO2 価格で引き込めば共食いは起きない」という結果は、日本の政策設計（GX-ETS、炭素賦課金）が進めば蓄電池の市場価値が回復しうるという含意として。
- 支持する点: 補助・義務で入った容量が市場価値を下げるのは政策の含意であり技術の欠陥ではない、という視点は、本研究が「政策ウェッジ」を正常な均衡現象として扱う立場を支える。
- 対立・留意点: 本研究は蓄電池の市場価値（π_spot）を扱い、Brown & Reichenberg は VRE の市場価値を扱う。蓄電池は CO2 排出ゼロなので、CO2 政策下では蓄電池も MV=LCOE を満たすはずだが、日本の現状は支援政策レジームであり μ>0 が観測される、と整理する。また彼らは長期均衡（既存設備なし）を扱うのに対し、本研究は既存系統の短期〜中期。
- 手法の源流: シャドウ価格を等価 FiP と解釈する方法は、本研究で「契約済み 2.3 GW を所与としたときの必要補助額（= c_req − π_spot(K)·c − κ·P_cap）」を計算する際の解釈枠組み。
- 新規性チェック: 既に行われていること＝VRE の市場価値低下が政策レジーム依存であることの理論・数値証明。本研究が新たに行うこと＝同じ論理を蓄電池の参入に適用し、北海道の実データで政策ウェッジを分解して定量化。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "The decline in average revenue seen in some recent literature is due to an implicit policy assumption that technologies are forced into the system, whether it be with subsidies or quotas. This decline is mathematically guaranteed regardless of whether the subsidised technology is variable or not."
2. §2.1 (p.2): "In a long-term equilibrium, where generator capacity is optimised along with power system operation, producers make zero profit under idealised conditions of perfect market competition, free entry and exit, linear cost functions and without any further constraints (Boiteux, 1949; Boiteux, 1960). ... MV_s = LCOE_s (1)"
3. §2.2 (p.2): "The subsidy required to cover costs can be translated into an equivalent Feed-in Premium (FiP) μ_s > 0 paid per unit of generated energy, thus modifying the zero-profit condition at equilibrium to MV_s = LCOE_s − μ_s (2)."
4. §3.3 (p.5): "forcing in the penetration of a particular technology above its unconstrained optimal share depresses the market prices λ_t at the times when it is generating."
5. §5.1 (p.7): "MV declines with rising penetration, eventually dropping to zero at a VRE penetration of 50%. The CO2 policy shows a quite different trend: the MV dips slightly, then increases gently up to just over 80 €/MWh at 70% penetration."
6. §7 (p.10): "A policy regime of subsidy for a particular technology will drive down its market value regardless of its variability, location, fuel cost or the rest of the generation mix."
