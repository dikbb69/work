# Würzburg, K., Labandeira, X., & Linares, P. (2013) Renewable generation and electricity prices: Taking stock and new evidence for Germany and Austria
- 書誌: *Energy Economics* 40 (2013), S159–S171（頁の「S」接頭辞は Supplement 号を示す。PDF に "Supplement 1" の明記はなし）。DOI 10.1016/j.eneco.2013.09.011（Available online 2013-09-20）。JEL Q41, Q42, Q48。所属: Economics for Energy／Univ. de Vigo (Rede)（Würzburg, Labandeira, Linares）、Univ. Pontificia Comillas（Linares）。
- 書誌の照合状況: DOI・誌名・巻・年・頁は PDF 本文（p.S159 の脚注「Energy Economics 40 (2013) S159–S171」と doi 表記）で確認済み。Crossref での外部照合は api.crossref.org が組織のエグレス制限で 403 となり未実施。
- 出所: Drive 格納PDF（`1-s2.0-S0140988313002065-main.pdf`、fileId 1Xsgp2S9ExbSHJHUEza4XRzs6KqJ4cMnW）を Drive 経由でテキスト抽出して 2026-09-29 精読。**表2・表3は平坦な文字列として抽出された**ため、列と行の対応は列間の算術関係（列(6)/(9)=(8)、(8)/(10)=(11)）で検算して復元した。数値を引用するときは原PDFの表で最終確認（CLAUDE.md ルール5）。頁は雑誌頁。

## 1. 問いと貢献（著者の主張する新規性）
- 要旨: 再エネ増加が短期の卸価格を下げる（MOE）ことは経済理論の予測。本論文は (i) 先行研究を「シミュレーション」「実証」「数量化が弱い研究」に分けて概観し、報告単位がばらばらの推定値を**「追加 1 GWh の再エネ発電当たりの価格変化（€/MWh）」に換算**して比較（Table 2, Fig. 1）、(ii) ドイツ・オーストリア（単一価格ゾーン）の日次データによる新しい実証（Table 3）を行う。結論は、MOE は地域と評価手法で異なるが、**市場規模で規準化すると市場間の分散は先行研究が示唆するより小さい**（Abstract）。
- 貢献: 比較可能性を整えた Table 2（列(8)〜(11)の換算）と、独に関する実証の空白を埋める多変量推定（それまでの独の実証は Neubarth et al. 2006 の単変量のみ、§3.3 末, p.S168）。
- 理論面の整理（p.S159–S160）: 再エネは限界費用ほぼゼロで入札し供給曲線を右へずらす。ただし MOE は「生産者から消費者への**移転**」（市場均衡が限界費用価格の場合）で、低価格は投資シグナルを弱め既存電源の固定費回収を難しくする。再エネ拡大でバックアップ容量が要る場合などは、長期の電力価格を逆方向に動かし当初の短期 MOE を相殺しうる（Jonsson et al. 2010; Nicolosi & Fürsch 2009; Green & Vasilakos 2011）。

## 2. データ・市場・期間
- レビュー対象: 独・西・デンマーク・ノルドプール・蘭・愛・テキサス。Table 2 は数量化した 20 研究（独 9、西 4、デンマーク 2、テキサス 2、ノルドプール・蘭・愛 各 1、筆者集計）。Table 1 は数量化が弱い 17 研究で、方向のみ記載（p.S162）。
- 新実証: 独墺、2010-07-01〜2012-06-30、日次 731 観測。被説明変数は Phelix 前日価格（EEX ライプツィヒ、DE–AT で単一価格）の日次平均。説明変数は負荷予測（ENTSO-E, APG）、風力＋太陽光の前日予測（EEX、独 4 TSO、APG）、前日ガス価格（Gaspool, NetConnect Germany）、10 隣国との越境フロー（予測が無く**実績値**、脚注25）。量は 24 時間の時間平均。期間が 2 年なのは、独で風力・太陽光の発電量公表が義務化された 2010 年 7 月より前は信頼できるデータがないため（脚注26）。
- 市場の背景（§3.1）: 独が墺の約 8 倍。2012 年初の設備は風力 独 29,700 MW／墺 1,150 MW、太陽光 独 24,500 MW／墺 107 MW。独の再エネ発電量は 2001 年 40 TWh→2011 年 120 TWh。

## 3. 手法
- レビューの換算（§2.4）: 列(8)＝共通指標（€/MWh per 追加 1 GWh の再エネ）、列(9)＝シナリオ間の時間平均発電量差（GW）、列(10)＝1 GWh が年の時間平均需要に占める割合（%）、列(11)＝(8)/(10)（市場規模 1% 当たりの価格低下）。「GWh」は実質「時間当たり平均発電量が +1 GW」の意味で、脚注8 で power units を使うと断る。
- 実証の式(1): ΔP_elec,t = β0 + β1·ΔLoad_t + β2·ΔRE_t + β3·ΔP_gas,t + β4·ΔExIm_t + β5…·dummies + ε_t（Δ は 1 階差、曜日・月・祝日ダミー）。ADF 検定で大半が I(1) のため階差を取る。OLS、Newey–West (1987) 頑健標準誤差。
- モデル: M1（ダミーのみ）、M2（＋Load）、M3（全変数）、3A/3B（1 年目／2 年目）、3C/3D（高負荷日＝上位 1/4／低負荷日＝下位 1/4）、3E（風力と太陽光を分離）、3F（週次）。

## 4. 主要結果
### 4.1 先行研究レビュー（Table 2, p.S163; 共通指標は €/MWh per 追加 1 GWh、負号は価格低下）
- **著者がまとめた国別レンジ**（§4, p.S168）: ノルドプール −1.7／独 −0.24〜−2.83／西 −1.1〜−3.99（大市場は小さい）。蘭 −6.17／デンマーク −1.33〜−9.87／愛 −9.9（小市場は大きい）。1 GWh が小市場では市場の大きな部分を占めるため。
- 独の 9 研究は「概ね −0.5〜−2.5 €/MWh の帯、大半は −1 未満（絶対値 1 未満の意と読める）」で、外れは Neubarth et al. (2006)（単変量でバイアスの可能性）と Weigt (2009)（§2.5, p.S164）。独の共通指標について著者は「2001〜2030 予測を通じて増加傾向は見られない」と評価（脚注15: 「全量 vs なし」の差は再エネ増で増える）。ただし表では Weigt (2009) の 2006→2008（−1.78→−2.83）や Sensfuß 2006（−1.34）は上昇。西の 4 研究は約 −2 で一致するが年次の傾向は不一致（Sáenz de Miera は 2006→2007 に急増、Gelabert は同期間に減少）。テキサスは手法と系統の違いで最も比較困難。
- 市場規模で規準化した列(11)（Fig. 1B; 筆者が表から集計）: 独 −0.15〜−2.05、西 −0.30〜−1.26、デンマーク −0.06〜−0.48、蘭 −0.75、愛 −0.32、テキサス −0.16〜−4.04（Nicholson）／−0.82〜−2.76（Woo）。著者は化石電源が価格決定電源となる系統（独・西・蘭・愛・デンマーク）で効果は「かなり似る」と評価。水力貯水池が多いノルドプールも同規模の独・西と近いが、単一研究で独自手法のため推測は控える（p.S164, S168）。
- Table 2 の内訳（列(6)報告値／列(8)共通指標。S=シミュレーション、E=実証）:
  | 国 | 研究 | 期間 | 報告値（€/MWh） | 共通指標 |
  |---|---|---|---|---|
  | 独 | Sensfuß et al. (2008) S | 2001, 04, 05, 06 | −1.70, −2.50, −4.25, −7.83（無 vs 通常） | −0.94, −0.60, −0.86, −1.34 |
  | 独 | Sensfuß (2011) S | 2007–10 | −5.82, −5.83, −6.09, −5.27 | −0.77, −0.71, −0.71, −0.55 |
  | 独 | Bode & Groscurth (2006) S | 2005頃 | −0.50〜−0.60 per GW | −0.50〜−0.60 |
  | 独 | Neubarth et al. (2006) E（単変量・風力） | 2004–05 | −1.89 per GW | −1.89 |
  | 独 | Weber & Woll (2007) S 風力 | 2006 | −4.04（無風 vs 通常） | −1.15 |
  | 独 | Weigt (2009) S 風力 | 2006–08 | −6.26, −10.47, −13.13 | −1.78, −2.30, −2.83 |
  | 独 | Traber & Kemfert (2011) S 風力 | 2007–08 | −3.70 | −0.80 |
  | 独 | Fürsch et al. (2012) S 予測 | 2015/20/25/30 | −2, −4, −5, −10（2010 年比の追加分） | −0.40, −0.35, −0.37, −0.61 |
  | 独 | Traber et al. (2011) S 予測 | 2020 vs 2010 | −3.20 | −0.24 |
  | 西 | Gelabert et al. (2011) E | 2005–10 | −3.80, −3.40, −1.70, −1.50, −1.10, −1.70 per GW | 同左 |
  | 西 | Gil et al. (2012) E 風力 | 2007–10 | −9.72（無風 vs 通常） | −2.15 |
  | 西 | Linares et al. (2008) S | 2020 予測 | −1.74 | −0.70 |
  | 西 | Sáenz de Miera et al. (2008) S 風力 | 2005–07 | −7.08, −4.75, −12.44 | −2.99, −1.83, −3.99 |
  | ノルドプール | Holttinen et al. (2001) S 風力 | 2010 予測 | −2.00 per 10 TWh/年の追加 | −1.70 |
  | デンマーク | Jonsson et al. (2010) E 風力 | 2006–07 | 約 −40%（低風 vs 高風） | −9.87 |
  | デンマーク | Østergaard et al. (2006) E 風力 | 2004–06 | −1.00, −4.00, −2.50 | −1.33, −5.28, −3.58 |
  | 蘭 | Nieuwenhout & Brand (2011) E 風力 | 2006–09 | −5% | −6.17 |
  | 愛 | O'Mahoney & Denny (2011) E 風力 | 2009 | −9.9 per GW | −9.90 |
  | テキサス | Nicholson et al. (2010) E 風力 | 2007–09 | −0.67〜−16.4 US$/MWh per GW | −0.47〜−11.60 |
  | テキサス | Woo et al. (2011) E 風力 | 2007–10 | −13〜−44 US$/MWh（15 分・1 GW 増） | −2.34〜−7.91 |
- Table 1（17 研究, p.S162）: 価格低下 13 本、方向が条件次第 3 本（Hindsberger 2003; Palmer & Burtraw 2005; Traber & Kemfert 2009）、価格上昇 1 本（Milstein & Tishler 2011、長期）。「電力価格は再エネ増加で概ね下がる」と結論づける。

### 4.2 独墺の実証（Table 3, p.S168; 被説明変数は前日価格の日次 1 階差、係数は €/MWh per MWh）
- **M3（全期間, n=731, 調整済 R² 0.72）: ΔRE（風力＋太陽光の予測）＝ −0.00103（SE 0.000081）、すなわち予測再エネが +1 GWh（時間平均 +1 GW）で前日価格 約 −1.03 €/MWh**。全モデルで負・有意（p<0.05）。他の係数は負荷 +0.000243（SE 0.0000836、有意）、ガス価格 +0.953（SE 0.372、有意）、越境フロー −0.00006（SE 0.000318、非有意）。
- **風力と太陽光の分離（M3E, n=731）: 風力 −0.00103（SE 0.000082）＝ −1.03 €/MWh per GWh、太陽光 −0.00126（SE 0.000243）＝ −1.26 €/MWh per GWh**。差は有意でない。太陽光が需要ピークと重なるため大きいと予想されたが、日次平均のため日内パターンを捉えられない可能性（結論, 脚注31）。
- 期間分割（3A/3B）: 1 年目 −0.000963（SE 0.000133）、2 年目 −0.001036（SE 0.000112）で差は小さい。2011 年中頃の原発 7 基停止（独の原子力の約 1/3）でも MOE の大きさは変わらず、有意になる変数が負荷（1 年目）からガス価格（2 年目）へ入れ替わっただけ。
- 高負荷日（3C, n=183）−0.00109（SE 0.000127）、低負荷日（3D, n=183）−0.00093（SE 0.000227）で高負荷日の方が大きいが有意差なし（ガス価格を除くと −0.001018 vs −0.000834、脚注30）。週次（3F, n=104）−0.000853（SE 0.00012）。
- 規模感（§3.3, p.S167）: 期間の平均再エネ発電量は約 7.6 GW で、係数（約 1 €/MWh per GW）×7.6 GW ≒ 平均 7.6 €/MWh の価格低下。期間の平均価格は約 48 €/MWh で、1 GW 当たりの効果は価格の約 2%（7.6 €/MWh は同約 16%、筆者計算）。この推定値は既存の独研究の帯（約 −0.5〜−2.5）の内側。

## 5. 著者が挙げる限界・今後の課題
- 市場構造（市場支配力）を考慮していない。非再エネ電源の構成をより詳しく入れると推定が変わりうる（§3.3 末）。
- データ期間が 2 年に限られる（再エネ発電量データが 2010 年 7 月以降のみ）。2013 年以降のデータで時間的推移を見る必要（§3.3 末）。
- 日次平均のため日内パターン（とくに太陽光）を捉えられない（結論, 脚注31）。越境フローは予測でなく実績値（脚注25）。
- レビュー側: 換算に使う追加データが原研究の前提と一致しない可能性、単変量推定のバイアス、取引所価格と相対取引の比率の国差（Hildmann et al. 2013）、長期の設備構成調整の扱いの違い（Fürsch 2012, Sensfuß 2011, Traber 2011 は設備構成を修正した反実仮想、他は非再エネ設備を固定）（§2.4）。Pöyry (2010) の比較は単位を揃えず誤解を招くと指摘（脚注13）。
- 各国での効果が似ていても原因が同じとは限らない。価格決定の時間帯パターンや燃料費など決定要因の分析が今後の課題（結論）。

## 6. 本研究との関係
- 引用予定箇所: 第2章の MOE 節（国際的な実証の要約とレビュー）。節番号は既存ノートで 2.1〜2.3 に揺れがある（Ketterer/Woo は 2.1、Hirth は 2.2、Maekawa/Sakaguchi/Ma の日本の系譜は 2.3）ため要確定。国際の MOE 概念・原典は 2.1 の冒頭、日本の系譜は 2.3 へつなぐ配置を想定。
- 位置づけ: 「MOE 推定の比較可能性を単位換算で整えたレビュー（2013 年時点）＋独墺の日次 OLS」。二次資料なので、個々の研究の数値は原典を優先し、本論文は (a) 符号は一貫して負、(b) 市場規模で規準化すると欧州内の差は小さい、(c) 手法間の比較可能性の限界、(d) MOE の理論的含意（移転・投資シグナル・長期の逆効果）の典拠として引く。
- 支持: (i) 小さな系統ほど per-GWh の効果が大きい（デンマーク・蘭・愛）。北海道のような小規模系統の推定値は列(11)の規準化で比べるのが筋。Sakaguchi & Fujii (2021)（sakaguchi-fujii2021.md）の MOE も「追加 1 GWh 当たりの価格低下」形式で、円↔€ の換算をすれば Table 2 と並べられる（値は原PDFで要確認）。(ii)「MOE は移転であり、投資シグナルを弱め、長期には逆向きの調整が入りうる」（p.S160）＝ 容量の内生調整と自由参入均衡を扱う本研究の動機。Sensfuß et al. (2008) の Table 11（設備の廃止・休止で MOE が 5.0→2.1 bn €）と同じ論点。(iii) 日次集計の限界の自認（脚注31）は Tselika (2022)「日次集計は再エネ効果を過小評価、特に太陽光」（tselika2022.md）と同方向。
- **対比・注意**:
  - 日次平均・1 階差の推定で、日内形状は見えない。風力≈太陽光という結果は日次集計の産物の可能性があり、時間別の日内形状（TB4h）を被説明変数にする本研究が埋める部分。
  - 識別は日々の再エネ予測変動（天候由来）で、短期効果。容量調整を含む長期均衡の効果ではない（長期は理論的議論と 3A/3B の年次比較のみ）。
  - 対象は大規模で他国と強く連系する DE–AT（13 隣国、§3）。小規模な単一価格ゾーンである北海道へは、規準化（列(11)）と連系条件の違いを確認せずに直接外挿しない。
  - 2013 年までのレビューで、Ketterer (2014)、Paraschiv (2014)、Rintamäki (2017)、Tselika (2022) など本研究の既存ノート群は含まれない（ketterer2014.md は MOE の時間的な縮小を報告）。
- **引用時の注意**:
  1. Table 2 の共通指標は Würzburg らが換算した値で、原研究の報告値ではない。原研究の数値は原典で確認し、換算値は「Würzburg et al. (2013) の換算」と明記する。
  2. 「1 GWh」は実質「時間平均出力が +1 GW」（脚注8）。エネルギー量の GWh と読まない。
  3. **表内の不整合**（要原PDF目視）: (a) Sensfuß et al. (2008) 2006 年行は列(6)/(9)＝−7.83/5.59＝−1.40 だが列(8)は −1.34（列(11)の −0.97 は (8) と整合、同研究の他 3 行は整合）。(b) Holttinen 行の列(11)は −0.02 と印字されるが (8)/(10)＝−1.70/2.18≒−0.78。
  4. 独の範囲の表記が箇所で異なる: §2.5（p.S164）と §3.3（p.S167）は約 −0.5〜−2.5、§3.3 末（p.S168）は符号なしの 0.5〜2.5、§4 の結論は −0.24〜−2.83（表の最小・最大）。どの箇所の数字かを明示する。
  5. 独墺の推定は 2 年のみ・日次 1 階差。風力と太陽光の差（−1.03 vs −1.26）、高負荷日と低負荷日の差（−1.09 vs −0.93）はいずれも有意でない。平均 7.6 €/MWh は限界係数の線形外挿で、反実仮想シミュレーションではない。
- 新規性チェック: 手法は既存文献のレビューと、Gelabert et al. (2011)（西）を独墺へ適用した日次 OLS。水準のみで、時間別・分位点・変動性は扱わない。本研究は（a）日内形状（TB4h）と帯域分解、（b）風力主導の小規模ゾーン、（c）蓄電池の内生化と自由参入均衡へ進む点で異なる。

## 7. 引用に使える原文
- "we show that the merit-order effect varies depending on the region and the assessment method chosen. We also find that the size of this effect is less dispersed throughout different markets than previously suggested by the literature."（Abstract, p.S159）
- "the merit-order effect is only a transfer of wealth from producers to consumers, at least if market equilibrium is formed at prices equal to marginal costs, with gains and losses potentially shared unevenly among different types of generators ... lower prices send lower investment signals and make it more difficult to recover capital costs for existing producers."（§1, p.S160）
- "Taken together, the nine studies on Germany report rather consistent results, quantifying the merit-order effect in a band between roughly −0.5 and −2.5 €/MWh, with most studies reporting reactions below −1 €/MWh."（§2.5, p.S164）
- "Ceteris paribus, day-ahead electricity prices for Germany and Austria decrease by roughly 1 €/MWh for each additional expected GWh produced by renewable sources (solar and wind)."（§3.3, p.S167）
- "when results are converted into homogeneous units (€/MWh per each additional GWh of renewable production), the smallest merit-order effects are found in large European markets (Nordpool −1.7; Germany −0.24 to −2.83; Spain −1.1 to −3.99), in contrast to much higher price effects in small markets (Netherlands −6.17; Denmark −1.33 to −9.87; Ireland −9.9)."（§4, p.S168）
- "the effects could be quite different with a higher data frequency (i.e., distinguishing between different times of the day). In this case, the effect of solar production is potentially higher because its production pattern coincides with demand peaks ... Yet, such intra-day specialties cannot be captured or represented in a study based on daily averages."（脚注31, p.S167）
