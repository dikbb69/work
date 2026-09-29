# Maciejowska (2020) Assessing the impact of renewable energy sources on the electricity price level and variability – A quantile regression approach
- 書誌: *Energy Economics* 85, 104532. DOI 10.1016/j.eneco.2019.104532
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）
- 位置づけ: 本研究の分位点回帰・IQR 手法の**直接の源流**（Sakaguchi & Fujii 2021、Fuke & Ohashi 2025 が踏襲）。

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 風力と太陽光はドイツのスポット価格の**分布**（水準＝中央値、変動性＝分位点間レンジ IQR）にどう異なる影響を与えるか。
- 貢献: (1) 分位点自己回帰（Koenker & Xiao 2006）で τ=0.1…0.9 の各分位点にメリットオーダー効果を推定。(2) 需要水準（低・中・高）で効果を条件付ける非線形モデル。(3) 変動性を IQR$_t=P_t(0.9)-P_t(0.1)$ で定義し、その係数 $\beta^*=\beta_{0.9}-\beta_{0.1}$ で「変動性効果」を検定。(4) 風力は分布の**下側**、太陽光は**上側**の裾により強く効くという非対称性を示す。
- 主結論: 中央値への効果は風力・太陽光で同じ（区別不要）。変動性は、風力は低需要時に増・高需要時に減、太陽光は中需要時に減。

## 2. データ・市場・期間
- 市場: ドイツ EPEX 日前価格 $P_{ht}$。
- 期間: 2015年1月1日〜2018年1月29日。
- 説明変数: TSO 公表の**予測**負荷 $L$、予測風力 $W$、予測太陽光 $S$（ENTSO-E transparency）。曜日ダミー（月・土・日・祝、非公式連休含む）。
- **日次化**: 時間値を「daily（全時間平均）」「peak（9–20時平均、営業日のみ）」「off-peak（0–8時・21–23時平均）」の3指数に算術平均で集約。以後の分析はこの3系列を**別々に**扱う。
- 記述統計（Table 2）: 価格は厚い裾（尖度≫3）、負値あり。ADF で定常（太陽光 off-peak を除く）。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 線形モデル (1): $P_t(\tau)=\alpha_{0,\tau}D_t+\beta^L_\tau L_t+\beta^W_\tau W_t+\beta^S_\tau S_t+\sum_{i=1}^{p}\theta_{i,\tau}P_{t-i}$、$p$=7（daily, off-peak）、5（peak）。
- 非線形モデル (2): 負荷の無条件分位点で $I_{1,t}=1[L_t<L^{(0.1)}]$、$I_{2,t}$（中間）、$I_{3,t}=1[L_t>L^{(0.9)}]$ を定義し、$L_{j,t}=I_{j,t}L_t$ 等の交差項で係数を需要水準別に分ける（閾値 0.15/0.85、0.2/0.8 で頑健性、Table 7–8）。
- 変動性: IQR$_t=P_t(0.9)-P_t(0.1)$。線形なら (4) $IQR_t=\alpha_0D_t+\beta^LL_t+\beta^WW_t+\beta^SS_t+\sum\theta_iP_{t-i}$、$\beta^*=\beta^*_{0.9}-\beta^*_{0.1}$。$\beta^*>0$ なら変動性増。
- 推定: 分位点自己回帰（Koenker & Xiao 2006）。90%信頼区間を図示（Fig. 4）。

## 4. 主要結果（数値を必ず。表番号を付す）
- メリットオーダー（Table 4, Fig. 4）: 風力係数は全分位点・全需要水準で負。太陽光も負。中央値では風力と太陽光の差は非有意→「水準のモデル化には合計 RES で十分」。
- Table 7（非線形モデル、L=0.15/H=0.85、daily）: 低需要 $\beta^W_1$ は τ=0.1 で −0.353、τ=0.9 で −0.210（低分位点ほど強い）。高需要 $\beta^W_3$ は −0.145（τ=0.1）→ −0.268（τ=0.9）（高分位点ほど強い）。太陽光 $\beta^S_1$ −0.448→−0.354、$\beta^S_2$ −0.057→−0.235、$\beta^S_3$ −0.051（n.s.）→ −0.368。
- **Table 6（IQR 効果）**:
  - 線形 (4): 負荷 0.081（daily, n.s.）/0.102**（peak）/0.117***（off-peak）；風力 **−0.006**（daily, n.s.）/−0.055**（peak）/−0.009（off-peak）；太陽光 **−0.200\*\*\***（daily）/−0.181***（peak）/−0.299***（off-peak）。
  - 非線形 (5): 風力 低需要 $\beta^W_1$ **+0.179\*\***（daily）、+0.104（off-peak, n.s.）；高需要 $\beta^W_3$ **−0.184\*\*\***（daily）/−0.295*（peak）/−0.058**（off-peak）。太陽光 中需要 $\beta^S_2$ **−0.181\*\*\***（daily）/−0.176***（peak）/**−0.386\*\*\***（off-peak）；低・高需要は非有意。
- 頑健性（Table 8）: 閾値 0.15/0.20 で符号・有意性は維持。

## 5. 著者が挙げる限界・今後の課題
- 日次・ピーク・オフピーク指数への集約を前提としており、時間別分布は扱わない（本文では明示的な限界としては述べないが、Gianfreda & Bunn 2018 の時間別結果との整合に言及）。
- 分位点ごとの係数は需要3区分で条件付けるのみで、より一般の非線形性（浸透率のU字など）は未検討。
- 政策含意は「風力・太陽光のバランス」に留まる。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.2（変動性の計測法）、第3章（分位点回帰と IQR の定式化の出典）、第4章の結果解釈（Fuke & Ohashi との比較）。
- 何を言うために引用するか: (i) IQR＝$P(0.9)-P(0.1)$ と $\beta^*=\beta_{0.9}-\beta_{0.1}$ という定義の原典。(ii) 「風力は下側の裾、太陽光は上側の裾」という非対称性。(iii) **決定的な注意点**: この IQR は**日次指数（24時間平均など）の条件付き分布**の分位点間レンジであり、「同じ需要・風力・太陽光の下で日次平均価格が日をまたいでどれだけ散らばるか」（日間変動性）を測る。日内形状（TB4h、ダックカーブ）は日次平均化で消えている。
- 支持する点: 風力の IQR 効果は線形モデルで −0.006（非有意）と極小（Table 6）→「風力は変動性を系統的に動かさない」。太陽光は高分位点（ピーク価格）を下げる＝昼ピークの切り下げ、これは低浸透期のドイツでは変動性縮小として現れる。
- 対立する点: 「太陽光は変動性を下げる」（日間 IQR）vs 本研究「太陽光は日内スプレッドを拡げる」。対象が異なる（日間 vs 日内）ため矛盾ではないが、論文中で必ず明示する。
- 手法の源流: 本研究の第1段（Sakaguchi & Fujii／Fuke & Ohashi 型の分位点回帰）はこの論文の直系。
- 新規性チェック: Maciejowska は daily/peak/off-peak を**別々に**推定し、peak と off-peak の**差**（＝日内スプレッド）を被説明変数にはしていない。本研究は (a) 日内スプレッド TB4h を直接の被説明変数とし、(b) 変動性を日内／1–7日／7日超に帯域分解し、(c) それを蓄電池の裁定価値と結び付ける点で新規。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "Conditional on the level of the total demand, the wind generation would either increase (when the demand is low) or decrease (when the demand is high) the IQR. Meanwhile, the increase of solar power stabilizes the price variance for moderate demand level." (Abstract)
2. "The time series are next transformed from hourly observations into daily, peak and off-peak indexes. The indexes are computed as an arithmetic mean of corresponding variables across all hours, peak hours (9:00–20:00) and off-peak hours (0:00–8:00 and 21:00–23:00), respectively." (Sec. 2 Data)
3. "In this research, the variability of spot prices is described by the inter-quantile range. It provides information about the shape of the distribution of prices and is closely related to the price variance. The IQR$_t$ could be directly derived from models (1) or (2) by subtracting IQR$_t$ = $P_t(0.9) - P_t(0.1)$." (Sec. 4.2)
4. "it is found out that wind has a stronger reducing impact on lower tails, whereas solar on higher tails of the price distribution." (Sec. 5 Conclusions)
5. "The distinction between different types of energy sources (wind and solar) becomes relevant only, when the tails or higher moments of the distribution are to be analyzed." (Sec. 4.1.1)
