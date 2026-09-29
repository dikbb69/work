# Mercier, Olivier & De Jaeger (2023) The value of electricity storage arbitrage on day-ahead markets across Europe
- 書誌: Thomas Mercier, Mathieu Olivier, Emmanuel De Jaeger, *Energy Economics* 123 (2023) 106721. Available online 18 May 2023. DOI 10.1016/j.eneco.2023.106721（JEL Q02, Q42, L94, M21, N74, O52）
- 出所: Google Drive 参考研究_20260728/SetB（原文精読 2026-09-29）

## 1. 問いと貢献（著者の主張する新規性）
- 問い: 欧州の全入札ゾーン・全年で、蓄電所有者の視点から見た DAM 裁定の歴史的価値はどれだけか。往復効率・継続時間の感応度、系統利用料（グリッドフィー）の影響は。
- 新規性: 「the widest geographical and temporal scope studied to date」（EU-28＋NO・CH・TR の全入札ゾーン、2000〜2021年、54,450 通りの評価）。技術中立（往復効率と継続時間のみで蓄電を記述）の MILP。ベルギーのサイズ依存グリッドフィーを扱う拡張 MILP。先行研究（Table 1）は数か国・数年・特定技術に限られる。
- 主結果（Abstract）: 裁定価値は地理的・時間的に大きく変動、往復効率の影響が大きく、**継続時間の限界価値は 4〜6h を超えると非常に小さい**。グリッドフィーは裁定価値を 20〜50% 減らし DAM 参加を劇的に減らす。

## 2. データ・市場・期間
- ENTSO-E／各取引所の時間値 DAM 価格、ゾーンにより 2000〜2017 年開始、2021 年まで。495 ゾーン年 × 効率11水準（50–100%、5pt刻み）× 継続時間10水準（1–10h）。
- ベルギー: 2016–2021、3地域、3サイズ（25／100／1,000 MW）の TSO グリッドフィー（Table 2–3、年間充電量に依存する逓減料金と上限）。

## 3. モデル・手法（均衡概念、蓄電池の扱い、推定式の要点）
- 価格テイカー・完全予見の MILP（Fig.1）: 目的は収入最大化、二値変数で同時充放電を禁止、蓄電水準制約、期首期末水準。
- **ローリング手法**: 各日 D について D〜D+6 の7日間で解き、初期水準は前回の run の1日目終了時水準。年間価値は日次価値の和。「the impact of forecast uncertainty on the first-day optimal dispatch decreases along the 7-day horizon, with only the first days being critical」。
- 完全予見の正当化（§3）: Sioshansi et al. (2009) のバックキャスト 85–90% を引用。Antweiler (2021) がオンタリオ RT 市場で予測により価値が半減以下と報告したのに対し、「RT markets are completely different markets than European day-ahead markets」— DA は前日の清算で情報が揃っており予測が容易、さらに EPEX の exclusive/loop ブロック入札が充放電時間の選択を容易にする。
- 価格テイカー仮定の妥当性: 既存の蓄電（規模を問わず歴史価格に晒された）と、価格に影響しない小規模の限界的蓄電に有効。REMIT（EU 1227/2011）の容量差し控え禁止により、価格メーカー的な入札は市場操作とみなされうる、と補足。
- 均衡概念はない（価値評価のみ）。

## 4. 主要結果（数値を必ず。表番号を付す）
- **Fig.5（効率75%・5h、k€/MW/年）**: 2009年以前の高値から 2015–2020 年の安値へ大幅低下、2021年ガス危機で急騰。高低比は多くの国で2超、イタリア（IT1–IT5）は 2007年 125 超 → 2018–2020 年 25 弱で比5、フィンランド 6、英国 6、スウェーデン SE4 で 12。
- 地理: ノルウェー（NO1–5）が最低（10 k€/MW/年以下、2020年は 5 未満）、スウェーデン北部、スペイン・ポルトガル（2016–2020）も低い（水力・原子力主導で安定価格）。2020年上位はエストニア 54、ラトビア 52、リトアニア 52。2018–2020 平均ではシチリア（IT6）61、アイルランド 46。2021年は英国が最高。
- **Fig.6（効率×継続時間の等価値線）**: 価値は両方に単調増加。継続時間の限界価値は正だが逓減し、**3〜5h（国により）を超えると無視できる**（結論では 4〜6h）。効率の限界価値は逆に増加（高価値国ほど大きい）。50% 効率では 75% 比で価値が大幅低下。低価値国（NO, ES, PT, CH）は効率100%・10h でも価値は限定的 →「storage value from arbitrage is not just about round-trip efficiency and storage duration, but it is also and above all inherently linked to the price dynamics at play in the local DAM」。
- **Fig.7**: 裁定価値の決定因は年平均価格より**年次ボラティリティ**。Fig.8: 価格スパイク発生頻度は長期的に減少。Fig.9: 2021 年を除く直近7年は「低価格・低ボラティリティ領域への収斂」（市場結合、低燃料価格、低限界費用再エネの浸透）。
- **Fig.10（負荷率）**: 効率75%で 23 k€/MW/年までは裁定価値と負荷率（充放電時間／年間時間）が線形、負荷率は最大60%弱。低価値国では蓄電はほとんど稼働しない。
- **Table 4／Fig.11（ベルギー、グリッドフィー）**: 効率75%・5h で 2016–2020 のグリッドフィーは裁定価値を 20%（2020年 1,000 MW・フランドル/ワロン）〜50%（25 MW・ブリュッセル）減少。負荷率は 40% 超から 8〜27 pt 低下。逓減料金のため小規模ほど不利（level playing field を欠く）。年間 25,000 MWh の充電量閾値に達するために赤字裁定を行う誘因さえ生じる。
- Table 5: 揚水／平均負荷比は AT 57%、CH 32%、ES 22%、PT 23%、他は 10% 未満。ただし AT/CH の方が ES/PT より裁定価値が高い（連系の違い）。

## 5. 著者が挙げる限界・今後の課題
- 完全予見・価格テイカーは「overoptimistic」だが比較の共通基盤。結論は既存蓄電と価格に影響しない小規模追加に限定。
- 価格ダイナミクスの決定因（電源構成、既存蓄電、再エネ、規制、連系、燃料価格）は定性的議論にとどめ、定量評価は今後の課題。
- **容量報酬、先物、イントラデイ、リアルタイム、予備力市場、アンシラリーサービスの価値は考慮していない**。「the observed decline in arbitrage value on European DAMs up to 2020 may not accurately reflect the true value of storage ... it is essential to put it in perspective with the potential increase in value from other streams, particularly capacity remuneration and all intraday- and reserves-related markets」。
- ガス価格上昇（対露依存低減）により裁定価値低下が反転する可能性は分析外。

## 6. 本研究との関係
- 引用予定箇所:
  - 第2章2.2／第6章（バックテスト設計）: DA 市場では前日に価格が確定するため完全予見に近い運用が可能という論理（RT との違い）は、本研究が JEPX スポット（DA、30分値）で capture ratio 81–83% を得ることの説明。7日ローリング手法は本研究の実行可能戦略の設計の参照。**継続時間の限界価値が 4〜6h で消える**という広範な証拠は、本研究が 4h を基準にすることの根拠（Sioshansi 2009 の「膝 8h」より短い）。
  - 第3章／第5章: 「裁定価値の決定因は水準ではなくボラティリティ」「水力・原子力主導で価格が安定した国では効率100%・10h でも価値が出ない」は、本研究の「風力は水準を下げるが日内スプレッドを広げないので蓄電の価値が小さい」という主張の欧州側の対応物。「低価格・低ボラティリティへの収斂」は再エネ浸透下でも DA スプレッドが自動的に拡大しないことの証拠。
  - 第8章8.3〜8.4: 「グリッドフィーが裁定価値を 20〜50% 減らす」は、本研究で蓄電池の託送料金・需給調整市場の扱いを整理する際の参照。「容量報酬など他の収入源と併せて評価すべき」は二層参入の動機付け。
- 支持する点: DA 裁定価値は市場によって桁違いに異なり、時間とともに低下傾向、継続時間の限界価値は短い。
- 対立・留意点: 価格テイカー分析であり π(K) の共食いは扱わない。2021年のガス危機による急騰は日本の 2021–22 年の LNG 高騰期と対応するので、本研究の期間選択の議論で参照。
- 手法の源流: 技術中立の（効率・継続時間のみの）蓄電表現と、ローリング完全予見 MILP。
- 新規性チェック: 既に行われていること＝欧州全域の価格テイカー DA 裁定価値の網羅的推計と感応度。本研究が新たに行うこと＝日本（北海道）の DA 裁定価値と、価格影響を含む π(K)、政策収入込みの自由参入均衡。

## 7. 引用に使える原文（3〜5文、ページ/節を付す）
1. Abstract: "The results reveal significant variations in storage value from arbitrage, both geographically and temporally, with round-trip efficiency having a major impact on arbitrage value and storage duration having very low marginal value beyond 4 to 6 h."
2. §3 (p.6): "It seems important to stress here that RT markets are completely different markets than European day-ahead markets. ... European day-ahead prices are the result of a clearing made the day before delivery, based on information available just before the clearing. Forecasting one day before delivery should therefore be much easier when it comes to day-ahead prices compared to RT prices."
3. §4.2 (p.10): "This result shows that storage value from arbitrage is not just about round-trip efficiency and storage duration, but it is also and above all inherently linked to the price dynamics at play in the local DAM."
4. §4.3 (p.11): "Overall, between yearly average and yearly volatility of hourly prices, the latter is clearly the determining factor of storage value from arbitrage."
5. §6 (p.16): "in countries where storage value is low, the spreads in DAM prices are not significant enough to trigger the dispatch of energy storages on a regular basis."
6. §6 (p.16): "This paper did not consider the value of capacity remuneration, the value from futures, intra-day, real-time, and reserves markets, nor did it look at the provision of ancillary services ... it is essential to put it in perspective with the potential increase in value from other streams, particularly capacity remuneration and all intraday- and reserves-related markets."
