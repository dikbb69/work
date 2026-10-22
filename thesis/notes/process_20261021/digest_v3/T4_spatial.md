# 監査対応の追加分析ダイジェスト: T4_spatial

**優先順位: 検証の修正（corrected_*）＞ build の値。数値はこのファイルか出力 CSV からのみ取る。**

## スクリプト
- analysis/47_spatial_dispersion_v3.py

## 出力
- data/processed/spatial_dispersion_v3_calibration.csv
- data/processed/spatial_dispersion_v3_table64.csv
- data/processed/spatial_dispersion_v3_phase.csv
- data/processed/spatial_dispersion_v3_validation.csv
- data/processed/spatial_dispersion_v3_correction.csv
- figures/hokkaido/spatial_dispersion_v3.png
- （参考・リポジトリ外）/private/tmp/claude-501/-Users-matsuba-work-thesis/d0c864fb-2c7b-407c-809f-7a4dc1efcfaf/scratchpad/t4/capsens47.py と capsens47.log、capsens_out/（T7 の容量補正を当てた感応度）

## 検証の判定: fixed（再実行の一致: True）

## 検証で直した点
1) Re-ran a copy of 47 with its outputs sent to the scratchpad (scratchpad/t4v/run47.py → out/). All five CSVs and the PNG match the repository files by md5 (run time about 41 s). The figures below come from that re-run.
2) Reviewed the code: definitions, units, fiscal years, seasons, missing data, grid, EWC, root-finding and price-model wiring. Found no bugs.
   - The EWC routine matches 37 (Σ_j of √2·cos projections, divided by ν; T=1,096; ν=42).
   - Checked that the price is identical between the default net demand of predict_A and the replaced net_syn (λ=1 completed-foresight gross margin 8,265.667 in both).
   - The logit round trip gives R=0.9999. Daily energy is exactly preserved (error 0.000%).
   - The fleet diurnal peaks (0h, 14h, 18–19h) and troughs (7h, 21–22h) are confirmed in the profile.
   - The Fig.6 readings (AUS 0.086/0.353, CAN 0.059/0.245, BPA 0.046/0.316) and ξmax/βℓ match planning/thesis-jepx/literature/notes/st-martin2015.md §4.3–4.4.
   - The 0.17 gap between the sum of seasonal completed-foresight gross margins and the annual value comes from 26 rounding each fiscal year; negligible.
3) Fixed one problem myself (edited 47 and re-ran it in place). The sensitivity-ratio intervals in (D)(iii) covered only the error in the actual coefficient and held the model coefficient fixed. The model's summer coefficient has t=2.35 (9.75, SE 4.15), so this interval was too narrow.
   - Added ewc_joint_cov: the joint EWC covariance of the actual and model coefficients, from influence functions stacked over the same right-hand side and the same days. Its diagonal is confirmed by assert to match ewc_fit's SEs, and it is consistent with the SE of the difference regression.
   - Added fieller: a Fieller 95% interval for the ratio.
   - Added columns to spatial_dispersion_v3_correction.csv: sensitivity ratio Fieller 95% low/high per season, and corrected ΔPF(%)_{all seasons, summer only}_Fieller95% low/high. Existing columns are unchanged.
   - Added these to the docstring and the log printout.
   - After the in-place re-run, the calibration, table64, phase and validation CSVs and the PNG are unchanged by md5. Only the correction CSV changed (new columns).
   - Result: summer ratio 4.73, Fieller [1.91, 29.40] against [1.97, 7.48] from the actual coefficient's error alone. Under the extra-controls specification the interval is unbounded.
4) Confirmed the writing rules were followed.
   - hokkaido_cf_series.csv, price_level_theta.csv, spatial_dispersion.csv/png, 26 and 29 are unchanged (md5 and mtime).
   - git status is identical before and after my run.
   - The manuscript files were last modified on Oct 20, before this workflow; T4 did not touch them.
   - analysis/12_fit_capacity_series.py and data/README.md were modified at 03:48 on Oct 21 (docstring/README additions that cite 51_cf_correction). These belong to another track (T7) and are outside T4, so I did not revert them.
5) Checked that each issue in the track file is resolved.
   - A6-4-2 high: the upper-bound row matches the calibrated variance ratio (R_ns 16.880, R 18.186). Met.
   - A6-4-1 calibration: the R and N ranges in the manuscript instructions can be reproduced from the CSV. Met.
   - A6-4-1 band-specific: all full-component rows are within ±5%. The stochastic-component middle row fails at +11% in the 6–24h band; this is disclosed.
   - A6-4-2 medium: criterion "corrected upper bound above +15%" holds. The upper bound is +18.8% before correction and +32.5% after; the Fieller lower end is +22.1%.
   - A6-4-3: done except the German profile, which is disclosed.
   - A6-4-2 low: met.
6) Corrected overstatements and minor errors in the manuscript instructions. Details are in corrected_instructions.

## 検証後の主要数値（build より優先）
Re-run reproduced every value. Main results (stochastic-component amplification, price model spec A with θ=1, FY2023–25; ΔPF is the change in completed-foresight gross margin relative to the actual fleet, 8,266 yen/kW-yr):
- Lower calibration, R_ns 2.81: PF 8,463 (+2.4%).
- Middle calibration, R_ns 4.40: PF 8,640 (+4.5%), TB4h 8.20 (+2.9%), floor-hit hours 116.
  - Wind→TB4h coefficients, summer/winter/off-peak: −0.009/+0.007/+0.148.
  - Change from the actual fleet: +0.032/+0.027/+0.007. "0.03 or less" is not accurate; "about 0.03" is.
- Upper calibration, R_ns 16.88: PF 9,819 (+18.8%), TB4h 9.03 (+13.4%), floor-hit hours 140.
  - Coefficients +0.104 (p=0.042) / +0.087 (p=0.005) / +0.175.
- Full-component upper (R 18.19): +18.0%.
- Band-specific stochastic-component: middle +3.8%, upper +17.9%.
  - Unrounded winter coefficients for the band-specific stochastic rows: lower −0.00146, middle +0.00548, upper +0.05547. The manuscript table values (−0.001/+0.005/+0.055) are correct.
- Old additive λ=4: realized R 7.40, +7.0%.

Diurnal phase:
- At a=0.3: night +2.6%, midday +3.6%, evening −6.1% (R 1.85–2.0).
- Uniform amplification at the same R: +0.76 to +0.90% (full component) and +1.10 to +1.31% (stochastic component).
- Ratio of phase effect to uniform amplification, in absolute value:
  - against stochastic-component uniform: night 2.0x, midday 3.3x, evening 4.9x;
  - against full-component uniform: 2.9x, 4.8x, 7.1x.
  - So the correct range is 2 to 7 times, not 2 to 5 times.
- After adding the diurnal cycle, the amplitude is 0.62–0.70 (nominal 0.6). Daily-energy error is at most 0.97%.

Correction by sensitivity ratio (summer only, stochastic component; new Fieller intervals in brackets):
- FY and season FE specification, ratio 4.73:
  - actual coefficient's error only: [1.97, 7.48];
  - Fieller [1.91, 29.40].
  - Lower: +3.3% (actual-only [2.6, 4.0], Fieller [2.6, 9.6]).
  - Middle: +6.7% ([5.1, 8.3], Fieller [5.05, 20.9]).
  - Upper: +32.5% ([22.4, 42.6], Fieller [22.1, 123.1]).
- Extra-controls specification, ratio 10.0. The model coefficient is not significant, so the Fieller interval is unbounded.
  - Middle +9.7% ([6.1, 13.3]), upper +51.8% ([28.9, 74.8]).
- Even the Fieller lower end of the upper bound (+22%) is above the +15% threshold. However, the upper end of the corrected middle calibration reaches +21%, so "small even after correction" holds only at the point estimate.
- T7 capacity sensitivity (outside the repository): upper +18.8%→+18.7%, middle +4.5%→+4.6%. Confirmed.

## 原稿への指示の修正（検証）
Apply T4's manuscript instructions with the following corrections. Everything not listed here stands as written.
(a) 06_results1 6.4, paragraph 1 draft: change "m は、合成系列で測った日内帯域の分散比（実フリート=1。以下 R）が後述の校正値に一致するよう" to "m は、合成系列で測った日内帯域の分散比（実フリート=1。以下 R。主の確率成分の版では確率成分で測った同じ比 R_ns）が後述の校正値に一致するよう".
(b) 6.4, paragraph 2 (results): change "動きは0.03以下である" to "動きは0.03程度である（夏+0.032、冬+0.027、不需要期+0.007）".
(c) 6.4, phase paragraph:
  - Change "（日次エネルギーは保存）" to "（0と設備容量での打ち切りと日次エネルギーへの再スケールを3回くり返す。日次エネルギーの誤差は最大1%）".
  - Change "a=0.3（日周振幅0.6。実フリートは0.17）" to "a=0.3（付与後の日周振幅0.6〜0.7。実フリートは0.17）".
  - Change "同じ実現分散比の一様な増幅（+0.9〜1.3%）と比べると2〜5倍の大きさで、符号も変わる" to "同じ実現分散比の一様な増幅（+0.8〜1.3%）と比べると絶対値で2〜7倍（確率成分の一様増幅に対して2.0〜4.9倍、全成分の一様増幅に対して2.9〜7.1倍）で、符号も変わる".
  - In table 6.4b, add the column 'ΔPF/(R−1)' for the phase and both uniform versions; it is in phase.csv.
(d) 6.4, validation paragraph:
  - Change "下側の裾（p05 5.57対3.86円）…を小さく出す" to "下側の裾を浅く（p05 5.57対3.86円）、下限張り付き時間と完全予見粗利を小さく出す".
  - Replace the sentences from "季節別の感応度比（実績/モデル。夏4.7、95%区間2.0〜7.5）で…" through "…モデルの係数の推定誤差は含まない。" with: 「季節別の感応度比（実績/モデル。夏4.7）でモデルの夏の完全予見粗利の増分を補正すると（参考値）、中央の校正で+6.7%、上限で+32%になる。比の95%区間は、実績の係数の誤差だけを考えると2.0〜7.5（補正後は中央5.1〜8.3%、上限22〜43%）である。モデルの係数の誤差も含めた Fieller 区間は1.9〜29（同5.1〜21%、22〜123%）で、上側に長い。モデルの夏の感応度そのものが粗くしか推定できない（t=2.35）ためである。需要・太陽光の日内変動などを追加統制した仕様では、比は10.0（中央+9.7%、上限+52%）で、モデルの係数が有意でないため Fieller 区間は有界にならない。補正は、感応度比が一定で ΔPF が比に比例するという仮定に立つ概算である。」
(e) 6.4, conclusion paragraph: change "以上から、中央の校正では集中立地の効果は小さく（完全予見粗利+4〜5%、感応度を補正しても+7%程度）、日内形状への効果を決めるのは系統的な日内位相であるという順位が、この価格過程の上で成り立つ。" to 「以上から、中央の校正では、この価格過程の上での集中立地の効果は小さく（完全予見粗利+4.5%）、日内形状への効果を決めるのは系統的な日内位相であるという順位が成り立つ。夏の感応度の過小を補正しても点推定は+7〜10%だが、補正の区間は上側に長く、上端は+2割に達する。」 For the upper-bound sentence, add "（補正後の点推定+32%、Fieller 区間の下端でも+22%）".
(f) Table 6.4c (iii): take values from spatial_dispersion_v3_correction.csv, rows "ロジット一様・確率成分（主）" for the lower, middle and upper calibration. Show both specifications (FY and season FE; extra controls) with these columns: summer-only corrected ΔPF, actual-coefficient-only 95% interval, and Fieller 95% interval (columns 補正後ΔPF(%)_夏のみ_Fieller95%下/上; NaN is shown as "unbounded"). Add the ratio intervals by season (感応度比Fieller95%下/上_*) in a note.
(g) 11_discussion 11.3:
  - Change "日内分散が分散比2程度でも、系統的な日周を加えると、位相次第で完全予見粗利が+6%から−6%まで動き" to "日内分散比が1.3〜2.0にとどまる系統的な日周（振幅 a=0.2〜0.3）でも、位相次第で完全予見粗利が+6%から−6%まで動き".
  - Change "分散1単位あたりで、位相は一様な増幅の2〜5倍効き" to "分散1単位あたりで、位相は一様な増幅の2〜7倍効き".
  - Change "しかも価格過程は夏の日内変動への感応度を実績より小さく出す（6.4）" to "しかも価格過程は夏の日内変動への感応度を実績より小さく出し、これを補正すると上限側は+3割前後（Fieller 区間の下端でも+2割強）になる（6.4）".
(h) 11.2 (l.47) and table 11.1, "併設の平滑化" row:
  - Change "6時間未満帯の確率的な変動を21倍" to "6時間未満帯の確率的な変動を分散で21倍（振幅で約4.6倍）".
  - Change "6時間未満帯を80倍、6〜24時間帯を4.7倍" to "分散で6時間未満帯を80倍、6〜24時間帯を4.7倍".
  - In table 11.1, write "分散で21倍" and "上限（分散で80倍）".
  - If adding the new "集中立地" row, change "モデルの夏の感応度を補正すると+3割前後" to "モデルの夏の感応度を補正すると+3〜5割（点推定。Fieller 区間の下端でも+2割強、上端は情報がない）".
(i) 05_methods table 5.1, key-results column: change "同じ分散なら日周位相の効果は2〜5倍" to "同じ分散なら日周位相の効果は2〜7倍".
(j) No changes to the numbers in table 6.4 panels A and B, 2.5, 6.7, 5.2.5, figure 6.5 or 14_appendix; I checked them against the CSVs. Add one line to the 14_appendix description of 47: "（感応度比の補正には実績のみの区間と Fieller 区間を併記）".

## 残る問題（検証）
(1) The version using the German onshore wind diurnal shape has not been built, because the repository has no source with usable numbers.
(2) The calibration depends on the Fig.6 readings (±3–5%), the area formula, and approximate municipal placement: coordinates ±5 km, removals and repowering since 2018 not reflected, plants in the same municipality treated as perfectly correlated. Band-pass ξ_b has not been estimated, so the area-formula N2 (1.24) is below the capacity-weighted N2 (2.41). The "middle" calibration (AUS × whole-Hokkaido area, R_ns 4.40) is above the capacity-weighted values for the actual fleet (2.81–3.87). In this sense the middle case leans toward an upper bound; the manuscript instructions already say so.
(3) The stochastic-component, band-specific middle row misses its target by +11% in the 6–24h band (m2=0).
(4) Because of the logit nonlinearity, the diurnal amplitude rises to 0.42 even in the stochastic-component version at the upper bound. The season × hour mean only approximates the paper's 4th-order harmonics on a 90-day window.
(5) The sensitivity-ratio correction is a reference value.
  - Even with the new Fieller interval, the upper side is uninformative (middle up to +21%, upper up to +123%), and under the extra-controls specification the interval is unbounded.
  - It assumes ΔPF scales with the ratio.
  - The summer gap comes mainly from September and may be confounded by typhoons and fronts.
  - Of the corrected values, the lower end (upper bound +22%) is robust; the upper end is not.
(6) The counterfactual does not change the price-zone structure. Coefficient significance on model prices describes the model only.
(7) The T7 capacity-correction sensitivity (change of 0.2 pt or less) exists only in the scratchpad, not as a repository output.
(8) The 6.1.2 statement that "high frequencies cancel through fleet aggregation" should carry the 11.2 caveat about smoothing (outside T4).
(9) Another track modified analysis/12_fit_capacity_series.py and data/README.md at 03:48 on Oct 21 (docstring and README additions citing 51_cf_correction). This is not T4, so I left it; the main session should check it against T7's rules.
(10) Re-checking the 47 changes: the re-run took about 40 s. The edit only added the Fieller columns to the correction CSV; I confirmed by md5 that the other outputs are unchanged. Pre-edit backup: scratchpad/t4v/47_backup_before_verify.py.

---
## build の主要数値
中断後の再開時の状態: 47（検証段階で修正済みの版）を再実行した。出力の CSV 5本と PNG は md5 が前回と一致し、ログも一致した（約16秒）。git status は再実行の前後で変わらない。29・26・hokkaido_cf_series.csv・spatial_dispersion.csv/png・manuscript は変更していない。

データ: FY2023〜25 の北海道風力（制御前）、26,304時間・1,096日。設備容量の平均 1,211MW。価格は仕様A・θ=1（26 を exec）。推論は EWC（暦日の格子、T=1,096、ν=42）。

【A 校正（St. Martin et al. 2015 の再現。spatial_dispersion_v3_calibration.csv）】
実フリートの帯域シェア: <6h 1.92%、6–24h 8.84%、1日超 71.32%（s1=13.1%）。確率成分（季節×時刻の平均を除いた部分）: <6h 1.68%（帯域内の日周 12.6%）、6–24h 8.74%。
式(2) の包絡（τ0=38h）の ξ/ξmax: 6h 0.019〜0.156、24h 0.150〜0.534。Fig.6 の読み取り値: AUS 0.086/0.353（ξmax 368）、CAN 0.059/0.245（ξmax 273）。
| 役割 | ξ | 広がり | ξ6h/ξ24h km | N1 | N2 | R（全成分） | R_ns | √R | s1 |
| 下限 | AUS型 | 容量加重 | 31.6/129.9 | 4.87 | 2.41 | 2.85 | 2.81 | 1.69 | 30.1% |
| 中央 | AUS型 | 北海道全域 83,424km² | 31.6/129.9 | 20.82 | 1.24 | 4.73 | 4.40 | 2.18 | 41.7% |
| 中央（交差） | CAN型 | 容量加重 | 16.1/66.9 | 6.29 | 3.41 | 3.92 | 3.87 | 1.98 | 37.2% |
| 上限 | CAN型 | 北海道全域 | 16.1/66.9 | 80.39 | 4.66 | 18.19 | 16.88 | 4.26 | 73.3% |
上限の感応度: 北方領土を除く面積で R 17.10（R_ns 15.87）、発電所数70で抑えると 16.33（15.20）。日本海側主要14市町村の凸包（23,771km²）では AUS 1.88、CAN 5.18。式(2) の包絡で幅を取ると、北海道全域で R は 1.95〜155 になる。
旧原稿（N1=13〜78、N2=1〜4、s1 32〜72%、λ≈1.8〜4）は、新しい中央・上限（s1 42%・73%、√R 2.2・4.3）とおおむね整合するが、式と ξ が書かれていなかった。

【B 表6.4 の新版（spatial_dispersion_v3_table64.csv）。完全予見粗利は円/kW-年、括弧内は実フリート8,266 に対する変化】
旧版（加法・打ち切り。29 と同一）: 名目λ=1.5/2/3/4 の実現 R は 1.98/3.12/5.41/7.40、√R は 1.41/1.77/2.33/2.72、s1 は 22.6/31.0/43.2/50.7%。打ち切り前に0以下となる時間は 5.0/10.5/18.5/23.8%。日次エネルギーの誤差は λ=4 で平均0.20%・最大21.2%。PF は 8,344/8,456/8,673/8,846（λ=4 で +7.0%）。
主（ロジット・確率成分の一様増幅。日次エネルギーは厳密に保存）:
- 下限 R_ns 2.81: PF 8,463（+2.4%）、TB4h 8.10、下限張り付き 115h、β −0.025/−0.005/+0.146
- 中央 4.40: PF 8,640（+4.5%）、TB4h 8.20（+2.9%）、116h、β −0.009/+0.007/+0.148
- 交差 3.87: PF 8,585（+3.9%）
- 上限 16.88: PF 9,819（+18.8%）、TB4h 9.03（+13.4%）、140h、β +0.104（p=0.04）/+0.087（p=0.005）/+0.175（Δβ +0.144/+0.106/+0.034）
- 上限の感応度: 15.87 で +17.6%、15.20 で +17.0%
全成分の一様（フリートの日周も増幅）: 下限 R 2.85 で +1.7%、中央 4.73 で +3.9%、上限 18.19 で +18.0%（TB4h 9.00、147h、β +0.086/+0.054/+0.177）、17.10 で +16.8%（監査の独立検算 +16.7% と一致）。
帯域別 (N1,N2):
- 全成分: 下限 +1.6%、中央 +3.5%、交差 +2.8%、上限 +17.6%。4行とも帯域別の目標の ±5% 以内。
- 確率成分: 下限 +2.3%、中央 +3.8%、交差 +3.8%、上限 +17.9%。中央だけは 6–24h 帯が 1.38（目標1.24、+11%）で ±5% に入らない。m2 が下限の0に達し、<6h からの漏れを打ち消せないため。
→ 同じ実現分散比なら、作り方（加法かロジットか、一様か帯域別か、全成分か確率成分か）による差は 1〜2pt にとどまる。旧版の λ=4 の +7% は、実現 R が 7.4 で校正の上限に届いていなかったための過小評価である。

【C 日周位相（spatial_dispersion_v3_phase.csv）】
a=0.3 の場合（日周振幅0.6。実フリートは0.17）:
- 夜 h0=3: R 2.00、PF +2.6%
- 昼 h0=13: R 1.85、PF +3.6%（下限張り付き 154h）
- 夕方 h0=18: R 1.96、PF −6.1%
同じ実現分散比の一様増幅は +0.9%（全成分）・+1.3%（確率成分）。分散1単位あたりで位相は 2〜5倍効き、符号も変える。
a=0.2 でピーク時刻を掃引すると、PF は 0時 −2.8%、3時 +1.6%、6時 +5.1%、9時 +6.0%、12時 +3.6%、15時 −0.6%、18時 −4.3%、21時 −5.2%。
夏の係数の動き: 夜 +0.054、昼 +0.020、夕方 −0.111、a=0.2 の6時 +0.070。同じ R の一様増幅では 0.003 以下。
フリート自身の日周（0時・14時・18〜19時に山）を3倍・6倍にすると、PF は −1.2%・−2.2%。

【D 価格過程の検証（spatial_dispersion_v3_validation.csv）】
(i) 実績とモデル（λ=1）:
- 下限張り付き 202.7h 対 115.0h、TB4h中央値 8.85 対 7.96、p05 3.86 対 5.57、p95 19.10 対 18.08、PF 10,317 対 8,266
- 風力日量→TB4h の差: 夏 +0.129（p=0.31）、冬 −0.093（0.29）、不需要期 −0.166（0.018）
- 日次 TB4h の相関（年度×季節内）: 0.25/0.20/0.43
(ii) 風力の日内SD（GW）→TB4h:
- FY・季節FE: 夏 実績46.1（SE13.3、p=0.001）対 モデル9.7、差36.3（p=0.007）。冬の差 3.4（0.60）、不需要期の差 −7.9（0.12）
- 追加統制: 夏 43.3 対 4.3、差38.9（p=0.004）
- システムプライスの TB4h を加えると: 夏 32.5 対 3.2（p=0.007）
- 年月FE: 7〜8月 20.5（p=0.26）対 3.2、9月 56.7（p=0.013）対 4.0。差の p は 0.30 と 0.027
(iii) 感応度比（FY・季節FE）: 夏 4.73［1.97, 7.48］、冬 2.98、不需要期 0.33。補正後の ΔPF は次のとおり（spatial_dispersion_v3_correction.csv）。
- 夏のみ補正: 確率成分の下限 +3.3%［2.6, 4.0］、中央 +6.7%［5.1, 8.3］、上限 +32.5%［22.4, 42.6］。追加統制版の比では上限 +51.8%［28.9, 74.8］
- 全季節補正: 上限 +39.0%［−30.8, +108.8］
→ 判定基準「補正後の上限が +15% を超える」に該当する。補正前のモデル値でも +18.8% である。

【感応度（リポジトリ外）】T7 の容量計上の補正（hokkaido_cf_series_corrected.csv の wind_kw）を当てても、主要行の変化は 0.2pt 以下だった。例: 確率成分の上限 +18.8%→+18.7%、中央 +4.5%→+4.6%、旧版λ=4 +7.0%→+7.2%。

## 解消した問題
- A6-4-2 (high, both) 名目λと実現増幅の不一致: 設備利用率のロジット空間で増幅し、各日のロジットの平行移動（二分法60回）で日次エネルギーを厳密に保存した。容量の上下限も自然に守られる。増幅率 m は、実現した日内分散比が目標に一致するよう Brent 法で求めた。表の上限行は、校正の上限と同じ実現分散比をもつ（全成分 R=18.186、確率成分 R_ns=16.88。どちらも誤差1e-3以内）。旧版の名目λも、実現 R・√R・s1・打ち切り率・日次エネルギー誤差とともに再計算した。上限で PF は +18.0%（全成分）・+18.8%（確率成分）で、原稿の +7% は過小評価だった。
- A6-4-1 (medium, both) 校正が再現できない: (A) で校正の全組合せを CSV に出力した。入力は次の3つ。ξ の出典は、式(2) の包絡（下限・上限・幾何平均・算術平均）と Fig.6 の読み取り値（AUS・CAN、参考に BPA。βℓ 基準も併記）。ξmax は 273/368（参考に 89）。空間の広がりは、北海道全域・北方領土を除く面積・2種の凸包・容量加重の指数相関・発電所数70の上限。出力は N1・N2・R・√R・s1・R_ns。式・ξ・N・R の範囲は本文の指示と CSV で一致させた。ξ_τ が累積値であること、A/(2ξ)² が上限式であること、Malvaldi の値は全帯域であることを docstring と本文の指示に明記した。
- A6-4-1 (medium, analysis) 帯域別の校正を一様λで代用: 帯域別の (N1,N2) を、下限・中央・交差・上限の4組について、m1・m2 の交互の根探し（4周）で実現させた。全成分版は4組すべて目標の ±5% 以内に入った。確率成分版は中央の 6–24h 帯だけが +11% で外れる（m2 が下限0に達するため。表に注記）。同じ実現分散比の一様増幅との差は 1〜2pt で、監査の見立て（1〜3pt）と整合する。
- A6-4-2 (medium, both) 価格過程の日内感応度が未検証: (D) で検証表を作った。(i) 実績とモデルの価格指標、風力→TB4h の3季節の係数と差の EWC p、日次 TB4h の相関。(ii) 日内SD への感応度を、FY・季節FE、追加統制、システムプライスTB4h 付き、年月FE で7〜8月と9月に分けた版で推定した。夏の差は36.3（p=0.007）で、主に9月による。(iii) 感応度比（95%区間つき）による補正幅を、全季節版と夏のみ版で出した（線形外挿は使わない）。補正後の上限は +32%（夏のみ）なので、判定基準により 6.4・11.3 の結論文を改める指示を出した。9月の交絡の可能性も明記した。
- A6-4-3 (medium, both) 日周位相の検定がない: (C) で、h0∈{3,13,18}・a∈{0.1,0.2,0.3} と、a=0.2 で h0 を 0〜21時の3時間刻みに動かす掃引、フリート自身の日周×3・×6 を、日次エネルギーを保存して作った。実現分散比をそろえた一様増幅（全成分・確率成分）と比べると、分散1単位あたり位相は2〜5倍効き（a=0.3）、符号も変える。係数への効果は一様増幅より1桁以上大きい。文言は「位相が既存の安値時間（未明〜昼）に重なれば広げ、夕方〜深夜に重なれば縮める」とした。ドイツの陸上風力の日周形状を当てた版は、出典となる数値がリポジトリにないため作っていない（残課題）。
- A6-4-2 (low, text) 「分散効果×単一価格ゾーンの価値」: 限界（風力系列だけを置き換え、ゾーン構成は動かさない）を docstring に記した。原稿の 5.2.5 と 6.7（06_results1 l.267）の書き換え指示を出した。

## 原稿への指示（build。検証の修正を必ず当ててから使う）
### 06_results1.md 6.4 第1段落（l.81、設計と旧版の説明）
全面的に差し替える。文案: 「5.2.5の設計に従い、北海道の風力が日内形状を変えない性質が、地理的分散による日内高周波の相殺にどの程度依存するかを、集中立地の反実仮想で検証した。FY2023〜25の実フリート風力（制御前、26,304時間）を6.1.2と同じ移動平均カスケードで帯域分解すると、6時間未満と6〜24時間の日内帯域の分散は総分散の1.9%と8.8%を占める（1〜7日40.1%、7日超31.2%）。帯域分散の和に占める日内2帯域の割合（以下 s1）は13.1%である。反実仮想では、設備利用率をロジット変換した系列を同じカスケードで分解し、日内2帯域の確率成分（季節×時刻の平均、すなわち系統的な日周を除いた部分）を m 倍に増幅する。そのうえで、各日のロジットの平行移動により日次エネルギーを実績に厳密に一致させる（出力は0と設備容量の間に収まる）。m は、合成系列で測った日内帯域の分散比（実フリート=1。以下 R）が後述の校正値に一致するよう数値的に求める。合成系列を水準係数付き価格過程（θ=1、FY2023〜25パス）に通した結果を表6.4と図6.5に示す。旧版の作り方（日内帯域を加法で λ 倍し、0と設備容量で打ち切ってから日次エネルギーに再スケール）では、名目の λ と実際の増幅が一致しない。名目 λ=2・3・4 で実現する R は3.1・5.4・7.4（振幅倍率 √R は1.8・2.3・2.7）にとどまり、λ=4 では日次エネルギーも平均0.2%、最大21%ずれる（表6.4の参考行）。」

### 06_results1.md 6.4 第1段落の後半（λ の目安の部分。新しい第2段落）
「λ の目安は St. Martin…4を上限として読む。」をすべて削除し、次の文案に替える。「R は St. Martin, Lundquist and Handschy (2015) で校正する。彼らの相関距離 ξ_τ は、日周の高調波（4次まで）と季節成分を除いた確率的な変動のうち、窓幅 τ より速い成分すべての地点間相関を距離で積分した累積値であり、帯域通過の値ではない。論文は τ=6時間・24時間の ξ を数値で報告していない。そこで論文 Fig.6 の地域別の点を読み取り、τ=6・24時間に対数内挿した（豪州の発電量で ξ6h=32km・ξ24h=130km、カナダの風速で16km・67km。最も遅い変動の ξmax はそれぞれ368km・273km）。論文の式(2) の経験的包絡（τ0=38時間）からは ξ6h/ξmax=0.019〜0.156、ξ24h/ξmax=0.150〜0.534 と幅の広い値が出る。Fig.6 の値はその中ほどにある。帯域 b の分散の減衰 N_b は2通りで求める。一つは、論文の「面積 A の領域には最大で A/(2ξ)² 個の無相関な地点がある」に基づく上限式 N_b=A/(2ξ_b)² である（領域を発電所で埋め尽くした場合の値で、発電所の数が少なければその数で決まる）。もう一つは、市町村別の容量配分に指数相関 exp(−d/ξ_b) を当てた容量加重の N_eff=1/(wᵀCw) である。ξ6h を6時間未満帯、ξ24h を6〜24時間帯に当て、R=(s6·N1+s24·N2)/(s6+s24) とする（s6・s24 は実フリートの帯域シェア）。校正の下限・中央・上限は次のとおりである（表6.4パネルA）。下限は豪州型×容量加重で、N1=4.9、N2=2.4、R=2.85、√R=1.69、s1=30%。中央は豪州型×北海道全域（8.3万km²）で、N1=20.8、N2=1.2、R=4.73、√R=2.18、s1=42%。上限はカナダ型×北海道全域で、N1=80.4、N2=4.7、R=18.2、√R=4.26、s1=73%。上限は、北海道全域を約32km間隔の独立な地点で埋め尽くした場合の理論値である。北方領土を除く面積では17.1、発電所数（約70）で抑えると16.3 になる。実際のフリート配置（容量加重）では2.9〜3.9、日本海側の主要立地の凸包（約2.4万km²）では1.9〜5.2 にとどまる。ξ は日周を除いた確率成分の値なので、主の反実仮想は日周成分を増幅しない。R も確率成分で測った比 R_ns（下限2.81・中央4.40・上限16.88）に合わせる。日周成分まで増幅した版（全成分）は感応度として併記する。Malvaldi et al. (2017) の国別出力と欧州10か国集約の分散比（2.1〜6.5倍）は全帯域の値なので、日内帯域の校正には用いない。」すべての数値は spatial_dispersion_v3_calibration.csv の「校正での役割」列の行から再現できる。

### 06_results1.md 6.4 第2段落（l.83、結果）
差し替える。文案: 「結果は、校正のどこを取るかで結論の強さが変わることを示す（表6.4パネルB）。中央の校正（R_ns=4.40、振幅で約2.1倍）では、TB4h中央値は7.96円から8.20円/kWh（+3%）、完全予見粗利（前日スポット・1日1サイクルでの上界。以下、完全予見粗利）は8,266円から8,640円/kW-年（+4.5%）、下限張り付き時間は115時間から116時間に増えるにとどまる。風力の日次発電量がTB4hに与える係数（表6.2と同じ仕様をモデル価格上で推定）は、夏−0.040→−0.009、冬−0.019→+0.007、不需要期+0.141→+0.148 で、動きは0.03以下である。下限（R_ns=2.81）では完全予見粗利は+2.4%である。これに対し上限（R_ns=16.88、振幅で約4.1倍）では、TB4h中央値は9.03円（+13%）、完全予見粗利は9,819円（+19%）、下限張り付き時間は140時間になる。夏と冬の係数は+0.104と+0.087 に転じる（モデル価格上の EWC で夏 p=0.04、冬 p=0.005）。日周も含めて増幅した版（上限 R=18.2 で+18.0%）や、6時間未満帯と6〜24時間帯を校正の (N1, N2) どおり別々に増幅した版（上限+17.9%、中央+3.8%）でも、実現分散比が同じなら結果はほぼ同じである。価格の応答を決めるのは、増幅の作り方ではなく実現した日内分散の大きさである。旧版で「λ=4（上限）で+7%」としていたのは、実現分散比が7.4で校正の上限に届いていなかったためである。」「単一サイト並みの4倍」「λ=4（上限）」という表現は削除する。

### 06_results1.md 6.4 新しい段落（日周位相。第2段落の後）と表6.4b
追加する。文案: 「日内の分散の大きさが同じでも、系統的な日周の位相は効果を大きく変える（表6.4b）。実フリートに x·(1+a·cos(2π(h−h0)/24)) の日周を付与し（日次エネルギーは保存）、実現分散比をそろえた一様な増幅と比べた。a=0.3（日周振幅0.6。実フリートは0.17）では、未明（h0=3時）にピークを置くと R=2.00 で完全予見粗利+2.6%、昼（13時）では R=1.85 で+3.6%、夕方（18時）では R=1.96 で−6.1% である。同じ実現分散比の一様な増幅（+0.9〜1.3%）と比べると2〜5倍の大きさで、符号も変わる。a=0.2 でピーク時刻を動かすと、3〜12時では+1.6〜+6.0%、15〜0時では−0.6〜−5.2% になる。風力→TB4h の夏の係数は位相によって−0.11〜+0.07動くが、同じ実現分散比の一様な増幅では0.003以下しか動かない。実フリート自身の弱い日周（0時・14時・18〜19時に山）を3倍にすると、完全予見粗利はむしろ1.2%下がる。モデルの上では、日内形状への効果を決めるのは分散の大きさより位相である。位相が既存の安値時間（未明〜昼）に重なればスプレッドを広げ、夕方〜深夜に重なれば縮める。」表6.4b は spatial_dispersion_v3_phase.csv から作る。列は、付与（夜・昼・夕方・掃引・フリートの日周×k）、a、h0、R、日周振幅、下限張り付き時間、TB4h中央値、完全予見粗利と Δ%、同じ R の一様増幅（確率成分）の Δ%、Δβ 夏／冬／不需要期。a=0.3 の3行と、a=0.2 の掃引の行、フリートの日周×3・×6 の行を載せる。

### 06_results1.md 6.4 新しい段落（価格過程の検証）と表6.4c
既存の第3段落の「なお、この反実仮想はモデル価格上の比較である…λ間の差で判断している。」を、次の文案に置き換える。「この反実仮想はモデル価格上の比較なので、モデルの感応度を実績と比べておく（表6.4c）。λ=1 のモデルは実績に比べ、下限張り付き時間（115対203時間/年）、下側の裾（p05 5.57対3.86円）、完全予見粗利（8,266対10,317円/kW-年）を小さく出す。年度×季節内の日次TB4hの相関は0.20〜0.43である。風力日量→TB4h の係数の実績とモデルの差は、不需要期（−0.166、p=0.02。モデルは供給曲線の下端の急勾配の効果を実績より強く出す。8.6）を除いて有意でない（夏+0.129、p=0.31。冬−0.093、p=0.29）。他方、風力の日内変動（日内帯域の日次標準偏差、GW）に対するTB4hの感応度は、夏に実績46.1（SE 13.3）、モデル9.7 で、差36.3は有意である（p=0.007。需要・太陽光の日内変動などを追加統制しても差38.9、p=0.004）。年月固定効果の下で夏を分けると、実績の感応度は7〜8月20.5（p=0.26）、9月56.7（p=0.013）で、主に9月によって生じている。9月の値には、台風や前線の通過で風と価格が同時に動く交絡が含まれうる。冬と不需要期では差は有意でない。季節別の感応度比（実績/モデル。夏4.7、95%区間2.0〜7.5）でモデルの夏の完全予見粗利の増分を補正すると（参考値）、中央の校正で+6.7%（5.1〜8.3%）、上限で+32%（22〜43%）になる。この補正は感応度比が一定という仮定に立つ概算で、モデルの係数の推定誤差は含まない。」表6.4c は spatial_dispersion_v3_validation.csv から作る。(i) 価格指標5行と、風力日量→TB4h の3季節（実績・モデル・差・差の EWC p。ν=42）。(ii) 日内SD の感応度を、FY・季節FE、追加統制、年月FE（7〜8月・9月・冬・不需要期）の3仕様で、実績（SE、p）・モデル・差・差の p。(iii) 補正後の ΔPF（spatial_dispersion_v3_correction.csv の「確率成分 一様」の下限・中央・上限の、夏のみ補正の値と95%区間）。

### 06_results1.md 6.4 第3段落（l.85、結論）
冒頭の「したがって11.3で述べる二つの機構のうち…補助機構にとどまる。」を次に替える。「以上から、中央の校正では集中立地の効果は小さく（完全予見粗利+4〜5%、感応度を補正しても+7%程度）、日内形状への効果を決めるのは系統的な日内位相であるという順位が、この価格過程の上で成り立つ。ただし校正の上限では、完全予見粗利は+19%になり、夏・冬の係数は正に転じる。さらにモデルは夏の日内変動への感応度を過小に出すので、上限側の効果は無視できるとはいえない。もっとも上限は北海道全域を独立な地点で埋め尽くした場合の理論値で、実際のフリート配置から測った減衰（R=2.9〜3.9）は下限〜中央に近い。広域単一価格ゾーンでの集約は、ほぼ一様な引下げ（6.6）を滑らかにする補助機構と位置づける。ただし洋上風力の道北への集中などでサイト間相関が上がれば、この位置づけは変わりうる。」続く「ドイツで…（Paraschiv…）のは夜間に偏った系統的な日内位相があるため」は残し、「表6.4bのとおり、モデルの上でも、安値時間に重なる日周は分散1単位あたり一様な増幅の2〜5倍スプレッドを広げる」を補う。最後に次の1文を加える。「なお、この反実仮想は風力系列だけを置き換え、価格ゾーンの構成（連系制約・地点別価格）は動かしていない。測っているのは集中立地（分散効果の除去）の価値であり、単一価格ゾーンの寄与は識別していない。」

### 06_results1.md 表6.4（l.87〜95）
旧表を2パネルの表に差し替える。パネルA（校正）の列は、役割、ξ の出典、空間の広がり、ξ6h/ξ24h(km)、N1、N2、R、R_ns、√R、s1。行は次の4つ: 下限 AUS型・容量加重 31.6/129.9・4.9・2.41・2.85・2.81・1.69・30.1%。中央 AUS型・北海道全域 31.6/129.9・20.8・1.24・4.73・4.40・2.18・41.7%。中央（交差）CAN型・容量加重 16.1/66.9・6.3・3.41・3.92・3.87・1.98・37.2%。上限 CAN型・北海道全域 16.1/66.9・80.4・4.66・18.19・16.88・4.26・73.3%。注に、北方領土を除く面積 R 17.10、発電所数70で抑制 16.33、日本海側凸包 1.88〜5.18 を書く。パネルB（反実仮想）の列は、仕様、実現R（全成分）、R_ns、√R、s1、下限張り付き(h/年)、TB4h中央値、p95、完全予見粗利(Δ%)、風力→TB4h 夏／冬／不需要期。行は次のとおり。
実フリート 1.00・1.00・1.00・13.1%・115・7.96・18.08・8,266・−0.040／−0.019／+0.141
確率成分・下限 2.75・2.81・1.66・29.1%・115・8.10・18.15・8,463(+2.4%)・−0.025／−0.005／+0.146
確率成分・中央（交差） 3.79・3.87・1.95・36.0%・116・8.16・18.22・8,585(+3.9%)・−0.013／+0.005／+0.147
確率成分・中央 4.30・4.40・2.08・39.0%・116・8.20・18.26・8,640(+4.5%)・−0.009／+0.007／+0.148
確率成分・上限 16.61・16.88・4.08・70.3%・140・9.03・18.54・9,819(+18.8%)・+0.104／+0.087／+0.175
全成分・下限 2.85・2.83・1.69・29.9%・116・8.05・18.14・8,409(+1.7%)・−0.033／−0.016／+0.145
全成分・中央 4.73・4.68・2.18・41.3%・120・8.14・18.25・8,584(+3.9%)・−0.021／−0.004／+0.151
全成分・上限 18.19・17.89・4.26・72.2%・147・9.00・18.51・9,751(+18.0%)・+0.086／+0.054／+0.177
帯域別（確率成分）下限(4.9,2.41) 2.76・2.81・1.66・29.3%・115・8.06・18.16・8,458(+2.3%)・−0.023／−0.001／+0.147
帯域別 中央(20.8,1.24)* 4.47・4.52・2.11・41.3%・119・8.13・18.09・8,577(+3.8%)・−0.002／+0.005／+0.153
帯域別 上限(80.4,4.66) 16.82・16.94・4.10・73.1%・150・9.00・18.40・9,741(+17.9%)・+0.103／+0.055／+0.178
参考: 旧版 加法 名目λ=2 3.12・3.09・1.77・31.0%・117・8.10・18.16・8,456(+2.3%)・−0.030／−0.017／+0.146
参考: 旧版 名目λ=4 7.40・7.29・2.72・50.7%・126・8.31・18.31・8,846(+7.0%)・−0.007／+0.006／+0.161
注: *は 6–24h 帯の実現比が1.38 で目標+11%（m2 が0に達するため）。旧版の日次エネルギー誤差は λ=4 で平均0.2%・最大21%、打ち切り前に0以下となる時間は23.8%。キャプション: 「表6.4 集中立地の反実仮想（実現した日内分散比を校正に合わせた合成系列）と価格指標（水準係数付き価格過程 θ=1、FY2023〜25パス。R は合成系列の6時間未満・6〜24時間帯の分散の和の実フリート比、R_ns は各帯域から季節×時刻の平均を除いた確率成分で測った同じ比、s1 は帯域分散の和に占める日内2帯域の割合。TB4h・p95は円/kWh、係数は円/kWh per GWh/日で、FY・季節ダミー・太陽光×季節・需要をコントロール）」。旧表の列「日内帯域の分散シェア」（総分散に対する割合。λ=1 で10.8%）は、校正の s1 と分母が違うため廃止する。

### 06_results1.md 図6.5
図を figures/hokkaido/spatial_dispersion_v3.png に差し替える。(a) は日内分散比と完全予見粗利の変化（確率成分・全成分の一様、帯域別、旧版、日周付与、校正の下限・中央・上限の線）。(b) は風力→TB4h の係数。キャプション: 「図6.5 空間分散シミュレーション（実現した日内分散比で校正に合わせた集中立地の反実仮想と日周位相の付与。仕様A・θ=1・FY2023〜25パス）」。

### 05_methods.md 5.2.5（l.84）
「（ii）同一導入量・同一日次エネルギーのまま…『分散効果×単一価格ゾーンの価値』として定量化する。$\lambda$ は…併記する。」を次に替える。「（ii）同一導入量・同一日次エネルギーのまま、日内帯域（6時間未満と6〜24時間）の確率的な変動を増幅した合成系列（集中立地の反実仮想）を、同じ価格過程に通す。増幅は設備利用率のロジット空間で行い、各日の平行移動で日次エネルギーを厳密に保存する。増幅率は、合成系列で実現した日内分散比が校正値に一致するように数値的に求める。校正値は St. Martin, Lundquist and Handschy (2015) の相関距離と、北海道の面積またはフリートの容量配分から求めた下限・中央・上限である。日内スプレッドと下限張り付き時間の差を、集中立地（分散効果の除去）の価値として定量化する。この反実仮想は風力系列だけを置き換え、価格ゾーンの構成は動かさないので、単一価格ゾーンの寄与は識別しない。あわせて、系統的な日周（振幅 a、ピーク時刻 h0）を付与した系列を、実現分散比をそろえた増幅と比べ、日内位相の効果を検定する。」「分散シェアは λ² で効き、出力は0と設備容量で打ち切る」は削除する。

### 05_methods.md 表5.1（l.26 空間分散シミュレーションの行）
方法の列を「風力の日内帯域の確率的な変動を設備利用率のロジット空間で増幅し（日次エネルギーは保存）、実現した日内分散比を St. Martin, Lundquist and Handschy (2015) の相関距離で校正した下限・中央・上限に合わせて価格過程に通す。日周位相を付与した系列とも比べる」に改める。主な結果の列を「中央の校正（日内分散比4.4）で完全予見粗利+4.5%、上限（16.9。北海道全域を独立地点で埋め尽くした理論値）で+19%（このモデル上。モデルは夏の日内感応度を過小に出す）。同じ分散なら日周位相の効果は2〜5倍」に改める。

### 11_discussion.md 11.3 第1段落（l.33）
「前者が本質、後者がほぼ一様な水準の低下を「滑らかにする」補助機構である。6.4の反実仮想はこの順位を定量的に裏付ける。日内帯域を単一サイト並みの4倍に増幅してもTB4hは+4%、完全予見粗利は+7%しか動かず、風力の日次発電量がTB4hに与える係数はほぼ不変であった。」を次に替える。「6.4の反実仮想は、この価格過程の上で、両者の順位を次のように示す。日内の確率的な変動を、文献の相関距離で校正した中央の値（日内分散比4.4、振幅で約2倍）まで増やしても、完全予見粗利は+4.5%、TB4hは+3%にとどまり、風力の係数もほぼ動かない。これに対し、日内分散が分散比2程度でも、系統的な日周を加えると、位相次第で完全予見粗利が+6%から−6%まで動き、夏の係数も−0.11〜+0.07動く。分散1単位あたりで、位相は一様な増幅の2〜5倍効き、符号も決める。したがって中央の校正では、前者（日内位相の不在）が本質で、後者は補助機構である。ただし校正の上限（北海道全域を独立な地点で埋め尽くした場合の理論値、日内分散比17）まで集中度を上げると、完全予見粗利は+19%になり、夏・冬の係数は正に転じる。しかも価格過程は夏の日内変動への感応度を実績より小さく出す（6.4）。このため上限側の効果は無視できるとはいえない。」続く「6.4の反実仮想は、日内の高周波を増幅しても系統的な位相がなければ形状が変わらないことを示しており」は、「6.4の反実仮想は、中央の校正の範囲では、日内の高周波を増幅しても系統的な位相がなければ形状はほとんど変わらず、位相が既存の安値時間に重なれば広がり、夕方〜深夜に重なれば縮むことを示しており」に改める。末尾の「洋上風力が道北に集中してサイト間相関が高まれば減衰しうる」の後に、「（6.4の上限側では、完全予見粗利で+2割程度の拡大に相当する）」を加える。

### 11_discussion.md 11.2（l.47、併設の平滑化の段落）
「6.4の反実仮想では、6時間未満と6〜24時間の日内帯域の振幅を4倍にしても、TB4hは+4%、完全予見粗利は+7%しか動かなかった。」を次に替える。「6.4の反実仮想では、6時間未満帯の確率的な変動を21倍（校正の中央。6〜24時間帯はほぼそのまま）にしても、TB4hは+2%、完全予見粗利は+4%しか動かなかった。6時間未満帯を80倍、6〜24時間帯を4.7倍にする校正の上限では、完全予見粗利は+18% になる。」その後の「平滑化による過小がこの範囲に収まる限り…結論は変わらない」は、「平滑化による過小が校正の中央程度に収まる限り」に改める。

### 11_discussion.md 表11.1「併設の平滑化」の行（l.87）の頑健性の列
「日内帯域を4倍にしてもTB4h+4%（6.4）、11.3」を「6時間未満帯の確率成分を21倍（校正の中央）にして TB4h +2%・完全予見粗利 +4%。上限（80倍）では +18%（6.4、表6.4）、11.3」に改める。結論への影響の列の「TB4hは4時間尺度なので影響は小さい」は、「TB4hは4時間尺度なので、校正の中央の範囲では影響は小さい」とする。表11.1 に「集中立地（洋上の道北集中など）」の行を加えてもよい。その場合の内容は、前提「フリートの空間分散は現状のまま」、外したときの方向「日内形状を広げる側（上限で完全予見粗利+19%、モデルの夏の感応度を補正すると+3割前後）。K*=0 を弱める側」、確認箇所「6.4」。

### 02_literature.md 2.5（l.65）
「6時間スケールでは数km〜30kmで無相関化する一方、1日を超える低周波は270〜370kmまで相関が残る」を次に替える。「風力の相関距離（τ より速い変動の地点間相関を距離で積分した値）は窓幅 τ とともに伸び、最も遅い変動では273〜368km（豪州は βℓ で447km）に達することを示した。6時間・24時間の値は論文に数値がないため、本研究で Fig.6 から読み取り、式(2) の包絡で確かめた。6時間でおよそ16〜32km（式(2) の包絡では5〜57km）、24時間で67〜130km（同41〜197km）である」。Malvaldi et al. (2017) の記述は「全帯域の分散比」と明記し、λ や日内帯域との対応づけをしない。

### 06_results1.md 6.7（l.267）
「北海道の市場・系統構造（単一価格ゾーンと分散立地）の下での記述であり、普遍法則ではない（6.4）」を次に替える。「北海道の市場・系統構造（系統的な日内位相をもたない風力と、それが広域単一ゾーンで集約されること）の下での記述であり、普遍法則ではない。6.4の反実仮想では、位相が主で分散は補助の機構である。ただし風力の集中度が校正の上限に近づけば、日内形状を広げる側に働きうる」。

### 14_appendix.md 図表・スクリプト対応（l.106・l.135・l.212）
次の3行を更新する。図6.5は `spatial_dispersion_v3.png`／`47_spatial_dispersion_v3.py`。表6.4は `spatial_dispersion_v3_table64.csv`（パネルA は `spatial_dispersion_v3_calibration.csv`）／47。表6.4b は `spatial_dispersion_v3_phase.csv`、表6.4c は `spatial_dispersion_v3_validation.csv`・`spatial_dispersion_v3_correction.csv`。スクリプト一覧に「47_spatial_dispersion_v3.py: 6.4 空間分散シミュレーション v3（校正の再現、ロジット空間での増幅と実現分散比の根探し、帯域別・確率成分の版、日周位相の付与、価格過程の日内感応度の検証）」を加え、29 は旧版（参考）と記す。


## build の残る問題
(1) ドイツの陸上風力の平均日周形状を当てた版は作っていない。リポジトリに、数値で引ける出典がないため。必要なら出典（例: 再解析や TSO の時刻別平均）を確保してから追加する。
(2) 校正は文献の相関距離（Fig.6 の読み取り誤差 ±3〜5%）、面積式、市町村単位の概略配置（座標 ±5km、2018年以降の撤去やリプレースは未反映、同じ市町村の発電所は完全相関）に依存する。北海道の単一サイトの出力で R を直接測ったものではない。帯域通過の ξ_b は推定しておらず、N2 には累積値の ξ24h を当てている。そのため、6〜24時間帯では面積式の N2（AUS 型で1.24）が容量加重の N2（2.41）を下回る。面積式は、領域が ξ の数倍しかない場合には粗い。
(3) 確率成分の帯域別・中央の行は、6–24h 帯が目標の +11% で、±5% の基準を満たさない（m2=0 でも <6h からの漏れが残る）。表に注記する。
(4) 確率成分の版でも、ロジットの非線形のため出力空間の日周振幅は上限で 0.17→0.42 に上がる（全成分版では 0.84、帯域別の全成分では 1.32）。季節×時刻の平均は、論文の「90日移動窓の4次の日周高調波」の近似である。
(5) 感応度比による補正は参考値である。比の95%区間は実績の係数の誤差だけを反映し、モデルの係数は固定している。また ΔPF が比に比例するという仮定に立つ。夏の差は主に9月によるもので、台風や前線による交絡の可能性がある。全季節を補正する版は、冬の比の区間が広いため［−31%, +109%］と情報が少ない。
(6) 反実仮想は価格ゾーンの構成を動かさない。価格過程は仕様A・θ=1 で、供給曲線は FY2023〜25 に固定している。モデル価格の係数の有意性（上限での夏 p=0.04 など）は、モデル上の記述にすぎない。
(7) T7 の容量計上の補正の感応度（変化0.2pt 以下）は、スクラッチ上で確認しただけで、リポジトリの出力にはしていない。原稿の注にするなら、T7 の cf_correction_lambda.csv（旧版の λ）と合わせて一行で足りる。
(8) 6.1.2（06_results1 l.15）の「6時間未満帯が小さいのはフリート集約で相殺されるため」には、11.2 の併設平滑化の留保（一部は平滑化の可能性）を付けるのが望ましい（本トラックの範囲外）。