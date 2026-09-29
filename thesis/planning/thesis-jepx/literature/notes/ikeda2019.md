# Ikeda, Shin S. (2019) Illiquidity in the Japan electric power exchange
- 書誌: Journal of Commodity Markets, 14, 16–39, doi:10.1016/j.jcomm.2018.08.001（受理 2018-08-03、小樽商科大学）
- 出所: Google Drive 参考研究_20260728/SetC（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: JEPX 前日スポット（板寄せ・単一価格コールオークション）は「経済的な意味で」流動的か。取引量以外の流動性指標（Kyle の depth／tightness）で測るとどう見えるか。
- 著者の貢献: (i) Amihud (2002) の価格インパクト指標を JEPX に初適用、(ii) Brünner (2012) の理論を根拠に、マーケットメイカー不在のコールオークションでも Roll (1984) 型の「暗黙のスプレッドコスト」を自己共分散から推定できることを示し JEPX で推定、(iii) 動学パネル（RE/FE/Arellano–Bond/Blundell–Bond）で指標間の相互関係と予測リターン式を推定。
- 抄録の5結論: "(a) these illiquidity measures comove to some extent, (b) a higher trading volume of electric power does not lower the spread cost, (c) a positive contribution of the price-impact measure to the return is stronger than that of the spread cost, (d) the great earthquake might disturb the risk-return tradeoff, and (e) a negative return-volatility relationship may stem from overlooked upward spikes in electric power prices."

## 2. データ・市場・期間
- JEPX 前日スポットのシステムプライスと約定量、48 コマ（30分）、2005-08-09（火）〜2015-03-30（月）、3,521 日 = 503 週（完全7日サイクル）。エリア価格ではなくシステムプライス（市場分断による地域差は捨象、と明記）。
- JEPX 制度記述（§3.2）: 板寄せ（Itayose）方式、"periodic, blind, and single-price call auction with batch trading, without formally designated market makers"。最小単位 1,000 kWh/h、最小価格刻み 0.01 円/kWh。前日市場が取引の 97% 超（METI 2012）。
- JEPX の取引比率: FY2010 に卸電力量の 0.6%、2014 年でも 2%。平均システムプライス 11,456 JPY/MWh = 89.95 EUR/MWh（2005–2015、脚注16）。
- サブ期間: S1 震災前（〜2011-03-14）、S2 余震期（2011-03-15〜05-31）、S3 震災後（2011-06-01〜2013-02-24）、S4 活性化期（2013-02-25〜）。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- パネル再解釈: 各「曜日×30分コマ」(id) を横断単位、週 w を時間軸とする週次パネル。
- モデル: 効率的対数価格はランダムウォーク（式1）、観測価格は ±s/2 の暗黙スプレッドで乖離（式2–3）。
- 指標（13週ウィンドウ、skip-13-week サブサンプリング）:
  - スプレッドコスト SC = 2{−Cov(Δln P_w, Δln P_{w−1})}^{1/2}/(1−7/96)（式8、Schultz 2000 のバイアス修正、正の共分散は0で打ち切り）。
  - 価格インパクト PI = Σ|Δln P|/(13·P·V)（式9、Amihud 型、金額ボリュームで除す）。
  - 固有ボラティリティ IV（週次リターンの実現分散型）、さらに上方/下方に分解 IV+・IV−（式17–18）。
- 推定式: (12) PI 方程式、(13) SC 方程式、(14) 予測リターン方程式。時間ダミー・固定効果・ラグ従属変数を含む。
- 「変動性」は週次対数リターンの実現ボラティリティ（IV）として定義され、上方スパイクを IV+ で分離する点が本研究の右裾分析に近い。

## 4. 主要結果（数値を必ず。表番号を付す）
- 国際比較（§6.2）: Amihud 指標を USD 換算すると JEPX は 7.187（日次為替）／8.440（1987–2000平均為替）で、Lesmond (2005) のロシア 9.722 とポルトガル 6.540 の間 → 新興株式市場並みに非流動的。ただし生ボリュームで測ると 6.280×10⁻⁴ で、他の電力市場（10⁻²〜10⁻³ 桁）より価格インパクトは小さい。
- スプレッドコスト: 期間平均 15.72%（電力の内在価値比）。ロシア 47.22%、ハンガリー 11.14% の間。加法換算で 15.33 EUR/MWh、欧州先物・当日市場の平均ビッドアスク 2.53〜3 EUR/MWh の約5倍。
- Table 1（PI 式・SC 式）: PI 式では金額ボリューム係数が有意に負（量が増えると depth は改善）、ln SC・ln IV は正。SC 式では金額ボリュームは SC を下げない（結論(b)）。
- Table 3（予測リターン式、BB 推定）: PI と SC の係数は正（非流動性リスクプレミアム）、PI の方が強い。IV の係数は負＝「idiosyncratic volatility puzzle」（Ang et al. 2006）が JEPX でも観察。
- Table 4: 上方/下方ボラティリティ分解でこの負の関係が上方スパイクに由来することを示唆。
- 日内・週内パターン（§6.1, Fig. 11）: 価格インパクトは火〜金で安定、土曜に改善、週初に悪化。平日 7:30–9:00 と 22:00–0:00 に悪化。
- 政策含意（§7）: (a) JEPX はスプレッドコストの意味で非常に非流動的、(b) 取引量増加はそれを減らさない。スプレッドコストは "an implicit entry barrier for those outside the exchange, or a strong disincentive for less-profitable incumbents to stay"。旧一般電気事業者（GES）は JEPX の最低限の流動性に不可欠だが、市場を育てる誘因が弱く情報優位者として振る舞う。METI (2017, p.318) の TEPCO が限界費用を大きく上回る価格で入札した逸話を引用。

## 5. 著者が挙げる限界・今後の課題
- 板寄せ・単一価格の前日市場である JEPX を連続取引・市場結合型の欧州取引所と比べるのは同条件でなく、同型の板寄せ市場での追試が必要。
- スプレッドコスト概念のコールオークションへの適用は Brünner (2012) 等の間接的正当化に依存。
- レジーム切替型モデルではなく、震災効果の識別は期間区分（S2 の定義）に依存し頑健性検証を要する。
- GES の戦略的行動の解明は政治経済学的分析との接続が必要。

## 6. 本研究との関係
- 引用予定箇所: 第3章制度（JEPX の板寄せ・0.01円刻み・GES 依存・低流動性の実証的裏付け）、第2章2.3（右裾スパイクが「リターン−ボラティリティ」関係を歪めるという指摘＝上方・下方非対称の先行例）、第5章（蓄電池アービトラージに対する暗黙の取引コスト＝スプレッドが realizable value を削る根拠）。
- 支持する点: 「取引量が増えてもスプレッドコストは下がらない」→ 2017年以降グロスビディングで量が増えても価格形成の質は別問題、という本研究の制度整理（Kanamura & Bunn 2022 と併読）に整合。上方スパイクの分離（IV+）は本研究の τ=0.9 分位点分析の動機付けに使える。
- 対立点／注意: サンプルは 2015-03 まで（全面自由化・グロスビディング・間接オークション以前）。システムプライスのみで北海道エリアは扱わない。再エネ変数なし。
- 手法の源流: 週次パネル化・skip-サブサンプリングは本研究では使わないが、「同一コマ×曜日を横断単位にする」発想は本研究の日内形状分析（TB4h）の集計と親和的。
- 新規性チェック: 本論文は流動性指標の測定であり再エネや蓄電池は扱わない。本研究は流動性を直接推定しないが、「蓄電池の実現可能戦略のキャプチャ率 81–83%」を論じる際に、実約定価格が効率的価格から ±s/2 乖離するという本論文のモデルを、理論値と実現値のギャップの一要因として引ける。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "This clearing mechanism is called the Itayose method, which is a version of the periodic, blind, and single-price call auction with batch trading, without formally designated market makers."（§3.2, p.19–20）
2. "The grand mean of the extracted spread costs in the JEPX is about 15.72% of the intrinsic value of electric power."（§6.2.2, p.31）
3. "The resulting number is 15.33 EUR/MWH in the JEPX, which is about five times larger than the average bid-ask spreads ranging from 2.53 to 3 EUR/MWH in the last two studies covering European futures/intraday markets for electric power."（§6.2.2, p.32）
4. "The most crucial policy implications from this study are (a) the JEPX is very illiquid in terms of the spread cost, but (b) a larger volume does not help reducing it."（§7, p.36）
5. "a negative return-volatility relationship may stem from overlooked upward spikes in electric power prices."（Abstract, p.16）
