# López Prol & Schill (2021) The Economics of Variable Renewable Energy and Electricity Storage
- 書誌: Javier López Prol and Wolf-Peter Schill, *Annual Review of Resource Economics* 13 (2021) 443–467. DOI 10.1146/annurev-resource-101620-081246（JEL C63, Q42, Q58）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- レビュー論文。VRE 浸透の市場ダイナミクス（メリットオーダー効果＝卸価格低下、共食い効果＝VRE 自身の価値低下）と、蓄電・その他柔軟性オプションが両効果をどう緩和するかを整理し、様式化オープンソースモデル（DIETER 系、Schill & Zerrahn 2020）で図解する。
- 概念整理: 絶対的共食い（VRE 単位収入の低下）と相対的共食い（value factor＝単位収入／平均卸価格の低下）、クロス共食い（風力↔太陽光）。value factor の推移は「価値の観点からの統合費用」（Hirth et al. 2015）と解釈可能。
- Summary points: (2) VRE 浸透は卸価格を下げる、(3) VRE は自らの価値を下げる、(4) VRE には蓄電と他の柔軟性が必要、(5) 100% に近づくと長時間蓄電の必要が急増、(6) 蓄電はメリットオーダー効果と共食い効果の両方を緩和。

## 2. データ・市場・期間
- レビューのため独自データはなし。図解用に California（CAISO）と Germany の 2016年風力・太陽光正規化プロファイル（Fig.1）、様式化ドイツ1ノードモデル（石炭、OCGT、CCGT、太陽光、風力＋揚水型蓄電1種、需要非弾力的）で VRE シェア 0–90% を制約で強制。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 様式化モデル: 費用最小化、エネルギー制約の双対を卸価格と解釈（Brown & Reichenberg 2021 と同様）。VRE シェア制約は「エネルギーベースのプレミアム」と解釈。負価格は VRE 制約が拘束することから生じる（CO2 価格で駆動すれば負にならない、Supplemental Fig.3）。
- 蓄電の価値分類（§3.1.2）: 裁定、柔軟性（ランプ削減）、予備力、容量、系統関連。「Many model-based studies nonetheless focus on only one or two sources of storage value, and hardly any cover all of them.」
- 蓄電の価値評価手法の3類型（§3.2）: (1) 価格テイカー裁定モデル（歴史価格; Sioshansi et al. 2009 等。「by design, cannot say much about the long-run value of storage in settings with higher renewable penetration」）、(2) VRE 出力・負荷の時系列モデル、(3) 電力セクター（容量拡張）モデル＝高 VRE シナリオの state of the art。
- システム価値: 蓄電導入による総システム費用削減。VRE と蓄電は補完的（一方の浸透が他方の価値を上げる）だが、VRE 過剰容量＋抑制で蓄電を代替できる点で代替的でもあり、蓄電には**逓減的限界収益**がある。

## 4. 主要結果（数値を必ず。表番号を付す）
- **価格変動性（§2.4）の実証は混在**: 効果は (a) 時間枠（時間・日・週）、(b) 技術（太陽光／風力）、(c) 系統条件に依存。Rintamäki et al. (2017): 週次変動は独・丁で増加するが、日次では風力はデンマークで減少・ドイツで増加、太陽光はドイツで減少。Kyritsis et al. (2017): 太陽光はピーク電源の利用を減らして変動を下げ、風力は柔軟性需要を増やして変動を上げる。Seel et al. (2018): 太陽光（風力はより小さく）で変動が増加。
- **メリットオーダー効果**: 太陽光の方が風力より強い（昼間に集中するため、Fig.1）。米国では効果はガス価格の影響より小さい（Mills et al. 2020）。
- **共食い**: 事後計量では浸透率とともに共食いが強まる（López Prol et al. 2020: CAISO で風力は自他の価値を下げ、太陽光は自らの価値を下げるが風力の value factor を上げる＝クロス共食い）。事前モデルでは容量ミックスが適応するため市場価値は安定化（Hirth 2013）。Mills & Wiser (2014): 風力の価値低下緩和には地理的分散、太陽光には低コスト蓄電が最有効。
- **様式化モデル（§3.3, Fig.4, Fig.6）**: VRE 20% 超で負の残余負荷時間が急増、90% でほぼ2時間に1回は余剰。市場価値は太陽光で特に低下、40% までは MV > LCOE（費用最小シェアが40%強）。蓄電なしでは太陽光の価値低下と抑制による LCOE 上昇がより急。
- 結論: 「VRE and electricity storage are complementary ... However, they are to some degree also substitutes ... Storage also shows diminishing marginal returns because each additional unit of capacity provides lower value to the system.」

## 5. 著者が挙げる限界・今後の課題
- 様式化モデルは定性的洞察のためで数値は目的ではない（§3.3）。
- 今後: 系統用蓄電と分散型蓄電（PV+蓄電池、EV/V2G）の相互作用、セクターカップリング（Power-to-X）の柔軟性、市場設計・規制枠組みの調整（各柔軟性オプションが提供する価値を回収できるように）。
- 蓄電の複数価値を同時に扱う研究がほとんどない。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2: **価格変動性への VRE 効果は「時間枠×技術×系統条件」で符号が変わる**という整理（§2.4）は、本研究が変動性を「水準／日内スプレッド（TB4h）／時間スケール」に分解し、太陽光と風力を区別して推定する設計の直接の動機付け。Rintamäki et al. (2017) の「風力はデンマークで日次変動を減らす」という知見を北海道の風力と対比。
  - 第2章2.2（蓄電の価値評価手法の分類）: 本研究のバックテスト（価格テイカー裁定）が「高浸透の長期価値については語れない」という限界の指摘を受け、本研究は π(K) の共食いを組み込むことでこの限界に部分的に対応すると位置づける。
  - 第8章8.3: 蓄電の価値源泉の分類（裁定・柔軟性・予備力・容量・系統）は、本研究の政策ウェッジ分解（スポット裁定／容量市場／LTDA／BTM 抑制回避／需給調整）の整理に対応。「ほとんどの研究が1–2の価値源泉しか扱わない」というギャップを、本研究は複数市場の収入を参入条件に並べる形で埋める。
  - 第9章: 分散型（BTM）蓄電と系統用蓄電の相互作用が未解明という指摘を、本研究の BTM 併設価値（エリア価格に現れない）の議論と接続。
- 支持する点: 蓄電の逓減的限界収益、VRE と蓄電の補完／代替の二面性（抑制が起きるまでは代替的）。
- 対立・留意点: レビューの大半は太陽光主導・欧州/CAISO の知見。風力主導で日内スプレッドが広がらない系統での蓄電価値の低さは、Hirth (2013) §5.8 と Rintamäki の日次変動の知見から間接的に示唆されるのみ。
- 手法の源流: value factor／共食いの定義（絶対・相対・クロス）を、本研究で蓄電池の π_spot(K) の「自己共食い」を定義する際の用語の参照元とする。
- 新規性チェック: 既に行われていること＝概念整理と文献の体系化。本研究が新たに行うこと＝北海道（風力主導・単一価格ゾーン）での実証と自由参入均衡。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. §2.4 (p.448): "the empirical evidence on the effect of VRE penetration on price volatility is mixed. The effects are specific to (a) the considered time frame (hourly, daily, or weekly volatility), (b) the VRE technology (solar or wind have different generation patterns and therefore differing effects), and (c) the conditions of the electricity system itself (market design, availability of flexibility options, demand patterns, etc.)."
2. §2.4 (p.449): "Rintamäki et al. (2017) find that although weekly volatility increases in both Germany and Denmark due to increasing wind and solar penetration, the daily volatility patterns differ. Wind decreases daily volatility in Denmark, but increases it in Germany, whereas solar decreases daily volatility in Germany."
3. §2.3 (p.448): "In general, the merit-order effect of solar is stronger than that of wind, as its generation pattern is more concentrated during daytime hours."
4. §3.2.1 (p.453): "Such studies generally focus on the arbitrage value of storage and, by design, cannot say much about the long-run value of storage in settings with higher renewable penetration."
5. §4 Conclusions (p.460): "VRE and electricity storage are complementary in the sense that higher penetration of one increases the value of the other. However, they are to some degree also substitutes, as storage can be replaced by VRE overcapacity and curtailment. Storage also shows diminishing marginal returns because each additional unit of capacity provides lower value to the system."
6. §3.1.2 (p.452): "Many model-based studies nonetheless focus on only one or two sources of storage value, and hardly any cover all of them."
