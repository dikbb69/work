# Tselika, K. (2022) The impact of variable renewables on the distribution of hourly electricity prices and their variability: A panel approach
- 書誌: *Energy Economics* 113, 106194. DOI 10.1016/j.eneco.2022.106194（OA, CC BY）
- 出所: ユーザー提供PDF（一橋図書館経由、2026-09-29 精読）→ Drive SetE に保存予定

## 1. 問いと貢献（著者の主張する新規性）
- 再エネ（風力・太陽光）が電力価格の**分布全体**と**変動性**に与える効果を、時間値を24時間の個体とするパネル分位点回帰（Machado & Santos Silva の MMQR）で推定。主貢献は「時刻固有の固定効果を考慮した時間値パネル」と、MMQR の**尺度（scale）推定値を変動性の指標**とすること（§1）。
- 先行研究の大半が日次集計の時系列であることに対し、「日次集計は再エネ効果を過小評価し、特に太陽光で顕著」（§6, §8）。

## 2. データ・市場・期間
- デンマーク（DK1）とドイツ、2015〜2020年の時間値。前日予測の風力・太陽光・負荷（外生、脚注4）。観測数 DK 51,696、DE 51,576（Table 2）。

## 3. 手法
- モデル1（線形）: 分位点 τ=0.1〜0.9、時刻固定効果。モデル2: 需要3水準（低・中・高＝負荷の無条件分位点）との交差項。
- **変動性の定義**: MMQR の位置–尺度モデルの尺度パラメータ。時刻固定効果で日内の平均形状を除いた後の**条件付き分布の散らばり**であり、日間の散らばりと日内の形状からの乖離が混在する（本研究の3分解では日間＋日内残差）。ブートストラップ・クラスター標準誤差。

## 4. 主要結果
- Table 2（水準）: 風力は全分位で負、**低分位ほど強い**（DK −6.159→−4.848、DE −0.233→−0.150）。太陽光（DE）は −0.131→−0.135 で**高分位ほどわずかに強い**。負荷は高分位ほど強い。
- **Table 3（尺度＝変動性）**: 風力 DK **+0.429\*\*\***、DE **+0.027\*\*\***（変動性を高める）。太陽光 DE −0.001（n.s.）。負荷 DK +2.334、DE +0.014。→ 著者自身が「デンマークでも風力が変動性を高めるのは Rintamäki et al. (2017) と逆で驚き」と明記（§5.1, §8）。
- Table 4/5（需要条件付き）: 風力は低・中需要で変動性を上げ、高需要で下げる（DK, DE）。太陽光（DE）は高需要時のみ変動性を下げ、その効果は風力より強い。
- §6: 同じ変数で日次集計の分位点時系列を推定すると再エネ効果が過小評価される。時間値を時系列として扱っても過小評価は残る → 差は頻度ではなく**時刻固有効果**による。

## 5. 著者が挙げる限界・今後の課題
- 変動性の指標が先行研究と大きく異なるため直接比較は困難と明記（§5.2）。横断（時刻）次元の重要性を今後の研究へ。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1.2（変動性の定義が結論を分ける例として最重要）、第1章1.3（日次集計の過小評価）、第6章6.5.4。
- 支持: 風力は下側の裾、太陽光は上側の裾（Maciejowska と同方向）。日次集計の限界（F&O の自認する限界と同じ）。
- **対比・注意**: 本論文は「風力はデンマークでも変動性を高める」と結論するが、その変動性は時刻固定効果を除いた後の残差の散らばり。本研究の TB4h（日内形状そのもの）とは対象が異なり、風力が日内形状を広げない（北海道）ことと矛盾しない。第2章では「同じ国でも指標が違えば符号が変わる（Rintamäki 日内分散↓ vs Tselika 尺度↑）」の例として使う。
- 新規性チェック: 時間値パネル×分位点は既出。本研究は（a）日内形状（TB4h）を被説明変数にする、（b）帯域分解、（c）蓄電池均衡への接続、で異なる。

## 7. 引用に使える原文
- "The main contribution is the use of the hourly data in a panel setting that accounts for time-invariant (or fixed) hourly effects."（§1）
- "The results show that wind increases price variability in both countries. While this result is already established in Germany ..., it comes as a surprise in Denmark."（§8）
- "The aggregated data appear to underestimate the RES impact on the electricity price distribution with the difference being more prominent on solar power."（§8）
- "Research to date has measured price variability in various ways, using different frequencies, and reaching diverse findings"（§5.2）
