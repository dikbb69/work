# Maekawa, Hai, Shinkuma & Shimada (2018) The Effect of Renewable Energy Generation on the Electric Power Spot Price of the Japan Electric Power Exchange
- 書誌: Energies, 11(9), 2215 (16 pp.), doi:10.3390/en11092215（受理 2018-08-23、公開 2018-08-24）
- 出所: Google Drive 参考研究_20260728/SetC（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 再エネ発電（太陽光・風力・水力）の増加は JEPX スポット価格を下げるか（メリットオーダー効果 MOE が日本でも観察されるか）。
- 著者の主張する新規性: "This work is deemed to be the first to measure how renewable energy generation influences the electric power spot price on the JEPX."（§6）。日本の再エネ×JEPX の最初期の実証。先行研究（Gelabert et al.; Zipp 2017）が日次データなのに対し、時間別（hourly）データを使う点、9エリアのパネルで固定効果を推定する点を特徴として挙げる。
- 当時 JEPX は再エネ発電量・取引内訳を公表しておらず、気象データを代理変数として用いるのが最大の特徴かつ弱点（Sakaguchi & Fujii 2021 が「climatic data as a proxy variable」「JEPX 取引比率が10%未満の時期」と批判する箇所）。

## 2. データ・市場・期間
- 被説明変数: JEPX 前日スポットのエリア価格（時間別、ln 変換）。期間 2016-04-01〜2017-06-30（約1会計年度）。
- 単位: パネル i = 9エリア（北海道・東北・関東・中部・北陸・関西・中国・四国・九州）、t = 1時間ブロック。回帰サンプル 93,873（Table 3）。本文では「70,042 observations from eight main regions」と記述されるが表の group numbers は 9 で整合しない（原典の記述ゆれ）。
- 説明変数（Table 1）: エリア需要（MWh/h、各電力会社の需要実績/予測）、前日降水量（水力の代理）、日照時間（太陽光の代理）、風速の3乗（風力の代理）、時間・曜日・祝日・月ダミー、価格の自己回帰項（1日前・1週間前・1か月前）。気象は気象庁。
- 記述統計（Table 2）: スポット価格 平均 8.78 円/kWh、SD 3.54、最小 2.06、最大 49。
- 制度的背景の記述: 2016年時点で JEPX 経由は国内電力量の 4% 未満、2018年で 12.1%（§4, §6）。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 固定効果パネル回帰（Hausman 検定で FE 採用）。
  ln P_it = C + α_i + β1 ln Q_it + β2 R_i(t−24) + β3 S_it + β4 W³_it + Σ β_j D_jit + Σ β_k P_ki(t−l) + e_it（l = 1, 24, 168; 本文では「1日前・1週間前・1か月前」と表記が揺れる）
- 「変動性」は扱わない。価格水準（対数）のみ。MOE を弾力性・準弾力性として読む。
- Model(1) 需要+気象代理、Model(2) +周期ダミー、Model(3) +自己回帰項。

## 4. 主要結果（数値を必ず。表番号を付す）
- Table 3（従属変数 ln スポット価格、全て1%有意）:
  | 変数 | Model(1) | Model(2) | Model(3) |
  |---|---|---|---|
  | ln 地域需要 | 1.35794 | 0.99984 | 0.19153 |
  | 前日降水量 | −0.00345 | −0.00461 | −0.00120 |
  | 日照時間 | −0.03067 | −0.07056 | −0.02751 |
  | 風速の3乗 | −0.0000231 | −0.0000107 | −0.0000165 |
  | 祝日ダミー | — | −0.0855 | −0.01436 |
  | ln 価格(1日前) | — | — | 0.70298 |
  | ln 価格(1週前) | — | — | 0.10515 |
  | ln 価格(1か月前) | — | — | 0.10998 |
  | R² within | 0.5139 | 0.6120 | 0.8951 |
- 解釈: 日照1時間の増加でスポット価格は約 7% 低下（Model 2）、3% 低下（Model 1）。祝日は約 8% 低下。価格の1日前弾力性 0.7 は「JEPX の硬直性（inflexibility）」を示すと著者は解釈（§4）。
- エリア固定効果 α_i（Figure 6）: 関東・関西・中部は負（価格を下げる固有効果）、北海道・北陸・四国は正。北海道については「a big island … the capacity constraint of the transmission lines is strong, and the power supply from other areas is costly. Therefore, the monopoly power of Hokkaido Electric Power will be strong」（§4）。
- 政策含意（§5）: 連系線「先着優先」ルールの見直し、北海道のような地域独占の緩和には送電制約の緩和が不可欠。

## 5. 著者が挙げる限界・今後の課題
- 再エネ発電量が非公表のため気象代理変数を使用（"because of the unavailability of data at the time of research, several proxies are used"）。代理変数はゼロが多く対数化不能で、有意性を正確に測れない可能性を認める。
- LNG・石油・石炭等の他電源を説明変数に含めないため R² が低い可能性。
- JEPX の取引比率が小さく「price has not yet been a proper signal」。
- 今後: JEPX が再エネ発電情報を公開すれば拡張可能。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.3（日本の MOE 実証の系譜の起点）。「日本の MOE 研究は Maekawa et al. (2018) の気象代理変数によるパネル推定に始まり、Sakaguchi & Fujii (2021) が実発電量と分位点回帰で精緻化した」という流れの最初の一文。第3章制度（北海道の連系制約と地域独占、エリア固定効果が正）にも一言。
- 支持する点: 北海道エリアの価格水準が高い固有効果（連系制約・地域独占）は本研究の「北海道は単一価格ゾーンかつ本州との市場分断」の制度前提と整合。風速3乗（風力代理）が有意に負 → 風力は価格水準を下げる、という本研究の(1)「風力は水準を下げる」と方向一致。
- 対立点／限界: 水準のみで日内スプレッド（TB4h）や分位点は扱わない。風力の効果を kWh 単位で解釈できない（風速3乗の係数）。期間が FY2016〜17Q1 で短い。
- 手法の源流としての位置づけ: 価格ラグ（t−24, t−168）を入れる定式化は Sakaguchi & Fujii (2021) と本研究にも引き継がれる。
- 新規性チェック: 本論文は「再エネが価格水準を下げる」ことを代理変数で示したにとどまる。本研究は (a) 実発電量、(b) 北海道単独、(c) 分位点・日内スプレッド、(d) FY2023–25 まで延長、(e) 蓄電池価値への接続、のいずれも本論文にない。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "This paper serves as the first work in this field in Japan and it notes that with the increased share of renewable energies, the JEPX spot price tends to drop."（§6 Concluding Remarks, p.14）
2. "With one additional solar radiation hour, the spot price on the JEPX becomes about 7% lower in model (2)."（§4, p.11）
3. "The strong correlation to the past price implies the inflexibility of the JEPX market. … Less than 4% of Japanese electric power volumes are exchanged through the JEPX as of 2016."（§4, p.11）
4. "Hokkaido, especially, is a big island located north of Japan, so the capacity constraint of the transmission lines is strong, and the power supply from other areas is costly. Therefore, the monopoly power of Hokkaido Electric Power will be strong, so there is a high possibility that the market price will be higher than that of other areas."（§4, p.11）
5. "because of the unavailability of data at the time of research, several proxies are used for regression estimations and analysis."（§6, p.14）
