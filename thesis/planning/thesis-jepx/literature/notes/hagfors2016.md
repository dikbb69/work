# Hagfors, Kamperud, Paraschiv, Prokopczuk, Sator & Westgaard (2016) Prediction of extreme price occurrences in the German day-ahead electricity market
- 書誌: *Quantitative Finance* 16(12), 1929–1948. DOI 10.1080/14697688.2016.1211794
- 出所: Google Drive 参考研究_20260728/SetA（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: ドイツ日前市場で、ファンダメンタルズ（需要・風力・太陽光予測、燃料価格、ラグ価格等）は**正スパイク**と**負価格**の発生確率にどう影響し、どの程度予測できるか。
- 貢献: 時間帯（trading period）別のロジットモデルで極端価格の発生確率を推定・予測。負価格と正スパイクは全く異なる駆動要因を持つこと、風力予測が負価格の説明に不可欠であることを示す。著者は「再エネ比率が高く負価格が生じる市場での極端価格予測の文献は欠けている」と位置づける。

## 2. データ・市場・期間
- 市場: EPEX ドイツ Phelix 時間別日前価格（各時間帯を別系列としてモデル化）。
- 期間: 2010年1月4日〜2014年5月31日。価格レンジ −222〜+210 €/MWh、標準偏差16.6 €/MWh。
- 説明変数（Table 2–3）: 前日・前週同時刻価格、需要予測、風力予測、太陽光予測、発電所利用可能量（PPA）予測、石炭・ガス・石油・CO2 価格、ボラティリティ。風力・太陽光予測は他変数より標準偏差が大きく正の歪み。
- 電源構成（Table 1）: 風力 6.5%（2009）→8.9%（2014）、太陽光 1.1%→5.7%。

## 3. 手法（被説明変数、変動性の定義、推定式の要点）
- 極端価格の定義: 正スパイク＝上位1%（閾値 €79.2/MWh；€80, 90, 100 でも頑健性）、負価格＝0未満。
- 被説明変数: 時間帯3（夜間、負価格）と時間帯18（夕方、正スパイク）の翌日同時間帯における発生ダミー。
- 推定: 標準ロジット。カットオフ確率（10〜90%）を変えて真陽性・偽陽性を評価。アウトオブサンプルは時間帯2・4（負価格）、17（スパイク）に適用。
- 変動性は説明変数（過去価格の標準偏差）としてのみ登場。

## 4. 主要結果（数値を必ず。表番号を付す）
- Table 4（年別件数、2014年は外挿）: 正スパイク 91/65/131/93/17、負価格 12/15/56/64/72（2010→2014）。標本全体で正スパイク387件、負価格177件。負価格は増加傾向、正スパイクは減少傾向。
- Table 10（ロジット係数）: 時間帯3では需要予測が負、風力予測が正（有意）、ボラティリティは非有意、燃料価格は負価格確率を下げる。時間帯18では需要予測が正、風力・太陽光予測は負（スパイク確率を下げる）、ラグ価格は正。
- 予測精度: 時間帯18でカットオフ10%のとき95件中87件（91.6%）のスパイクを予測。
- Table 18–19（風力を除外）: 時間帯3モデルの AIC 87.5→197.6、BIC 114.4→226.5。風力なしではカットオフ20%以上で真陽性ゼロ。
- Table 20–21: 時間帯18で風力・PV を除いても性能低下は限定的（スパイクの主因は需要と供給不足）。
- 記述: 負価格は夜間に集中し高風力＋低需要で発生。昼間の負価格は PV 予測が非常に高い少数例。夜間の負価格は昼間より深い。

## 5. 著者が挙げる限界・今後の課題
- ロジットは発生確率のみで、極端価格の**大きさ**は予測できない → 分位点回帰や EVT との結合を提案。
- 2時間帯のみの推定。他時間帯（朝の混在時間帯、昼の負価格）や他市場（Nord Pool, UK APX）への拡張が課題。
- 高い閾値（€100）では標本が少なく推定が不安定。

## 6. 本研究との関係
- 引用予定箇所: 第2章2.1（風力と底値・負価格の関係）、第4章（bottom-4h 価格の決定要因を論じる箇所）、第5章（蓄電池の充電機会が「高風力×低需要」事象に依存すること）。
- 何を言うために引用するか: 風力は分布の**下側の裾**（夜間の底値・負価格）を通じて価格に効く、という機構の実証。本研究の帯域分解で風力が「水準」と「1–7日帯域」に効き、日内スプレッドに効かない、という主張と組み合わせると、「風力は底を下げるが、JEPX では価格下限 0.01 円が拘束的なため底値の変動性は圧縮される」という北海道固有の論点につながる。
- 支持する点: 風力の効果は下側裾に集中（Maciejowska 2020 と整合）。太陽光はピーク側のスパイクを抑える。
- 対立する点: 直接の対立はないが、ドイツでは夜間の負価格が深まるため風力が日内レンジを拡げうる。北海道では価格下限と風力の日内平坦性でこの経路が弱いことを示す必要がある。
- 手法の源流: 本研究の手法とは異なる（ロジット）。ただし「ファンダメンタルズ→裾事象」の考え方は、本研究の価格過程シミュレーションで負・低価格の頻度を再現する際の参照点。
- 新規性チェック: Hagfors らは発生確率の予測に特化し、変動性の時間スケールや蓄電池価値は扱わない。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. "Positive spikes are related to high demand, low supply and high prices the previous days, and mainly occur during the morning and afternoon peak hours. Negative prices occur mainly during the night and are closely related to low demand combined with high wind production levels." (Abstract, p.1929)
2. "The scatter plot of wind forecasts vs. spot prices shown in figure 1 confirms that extremely low spot prices are seen nearly exclusively when wind production is high, in accordance with the negative correlation." (Sec. 4.1)
3. "When removing wind as explanatory variable from the model for trading period 3, it performs significantly worse." (Sec. 5.4)
4. "Positive spikes are less frequent if wind/photovoltaic production forecasts are high, as the spikes occur when production forecasts are low, causing demand to exceed supply." (Sec. 6)
5. "The negative prices are, on average, much lower during night than during day, implying the effect of renewable energy sources is strongest at night." (Sec. 6, p.1947)
