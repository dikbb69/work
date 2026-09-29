# 先行研究の追加調査（2026年9月29日）

- 目的: 執筆着手に伴う文献の更新。コア41本（doi-list.md）に加える候補と、既存文献の精読アライン事項
- 方法: Web検索（スニペットベース）。原典PDFの精読は別途

## 1. 既存コア文献の精読アライン事項

### Fuke & Ohashi (2025) J. Commodity Markets 40, 100521
- 手法: **分位点回帰**。対象: 九州エリア、2016年4月〜2020年3月
- 結果: MOEが存在し季節で変わる。太陽光の増加は**四分位範囲（IQR）で測った価格変動性を春・夏に低下**させるが秋・冬には低下させない。解釈: 需要と太陽光発電の相関が季節で変わるため
- 本研究への含意: 変動性の指標がIQR（分布の中央部）であり、本研究のTB4h（分布の裾）と測定対象が異なる。「太陽光は中央を圧縮し裾を広げる」で両立し得る → 第6章6.5で検証（IQR版の回帰を追加）。SSRN版（4990073）も参照可
- 出典: [RePEc](https://ideas.repec.org/a/eee/jocoma/v40y2025ics2405851325000650.html)・[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4990073)

### Butters, Dorsey & Gowrisankaran (2025) Econometrica 93(3), 891–927
- 結果: 補助なしでは2030年まで蓄電池導入はほとんど進まないが、資本費30%低下で大きく進む。各蓄電池が裁定者として価格差を平準化するため大規模貯蔵の均衡価値は限定的。資本費低下を待つオプション価値が投資を遅らせる
- 本研究への含意: 北海道の損益分岐（資本費約8割低下）はCAISOより厳しい → 第8章8.4で比較。再現パッケージ（Zenodo 14977687）は簡約版の参照実装に
- 出典: [Econometric Society](https://www.econometricsociety.org/publications/econometrica/2025/05/01/Soaking-Up-the-Sun-Battery-Investment-Renewable-Energy-and-Market-Equilibrium)・[NBER w29133](https://www.nber.org/papers/w29133)・[Zenodo](https://zenodo.org/records/14977687)

## 2. 追加候補（コア集合への編入検討）

### 2.1 風力の空間分散（系譜E、6.4シミュレーションの根拠）
- "Reduction of wind power variability through geographic diversity"（[arXiv 1608.06257](https://arxiv.org/pdf/1608.06257)）: 広域分散は極端値の発生を減らし平均近傍に集中させる
- Handschy, Rose & Apt (2017) "Is it always windy somewhere?"（[arXiv 1607.06702](https://arxiv.org/pdf/1607.06702)）: 広域でも低風力イベントは同時発生 → 長周期は集約で消えない
- "Collective and nonlinear structure of wind power correlations"（[arXiv 2602.10136](https://arxiv.org/pdf/2602.10136)、2026）: 風力相関の非線形構造（λ校正の参考）
- Montel（実務）: 風力主導の日中変動パターン（[blog](https://montel.energy/resources/blog/wind-driven-intraday-volatility-patterns-risks-and-opportunities)）

### 2.2 蓄電池のカニバリ実績（系譜D、8.3の外部裏付け）
- Modo Energy (2025): ERCOT蓄電池収益 $193/kW（2023）→$56（2024）→$29.4（2025見込み）、容量200MW→14GW（[why-so-low](https://modoenergy.com/research/why-were-ercot-battery-revenues-so-low-in-2025-weather-energy-arbitrage-builodout)・[revenue stack](https://modoenergy.com/research/en/ercot-caiso-june-2025-revenue-stack-batteries-bess-energy-arbitrage-nodal-price-locational-marginal-price-transmission-congestion-price-spreads)）
- pv magazine USA (2025/11): ERCOTの調整力収益が約90%減（[記事](https://pv-magazine-usa.com/2025/11/21/battery-energy-storage-revenues-for-ancillary-services-fall-nearly-90-in-ercot/)）→ EPRXゼロレントの国際的裏付け
- "Economic Capacity Withholding Bounds of Competitive Energy Storage Bidders"（[arXiv 2403.05705](https://arxiv.org/pdf/2403.05705)）: 競争的貯蔵入札者の理論
- CAISO (2025) 2024 Special Report on Battery Storage（[PDF](https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf)）

### 2.3 併設・抑制回避（第9章9.3の根拠）
- J. Energy Storage (2025) 風力＋BESSの技術経済最適化（抑制・劣化考慮）（[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2352152X25002130)）
- Energy & Environmental Science (2026) 併設の収益スタッキングと抑制・資本費削減（[RSC](https://pubs.rsc.org/ee/article/19/13/4469/1267155/Maximising-the-economic-value-of-renewable-and)）
- Renewable Energy (2024) 風力の太陽光・貯蔵併設ハイブリッド化（[ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0960148124021256)）
- LBNL Hybrid Power Plants 2024 edition（[EMP](https://emp.lbl.gov/publications/hybrid-power-plants-status-2)）

### 2.4 国内（学術論文は検索で新規発見なし）
- 実務資料（enegaeru・情熱電力・ScienceX等）に2026年の収益スタック解説あり。学術誌の新規論文は未検出 → 第2章2.3の「国内は誘導形のみ」の主張は維持

## 3. 残タスク
1. F&O原典の精読（IQR定義・説明変数・分位点）→ 6.5のアライン仕様確定【PDFはユーザー保有】
2. 2.1の空間分散文献から単一サイトの帯域構造（λ）を抽出
3. Butters再現パッケージの均衡条件式の確認
4. 追加候補のDOI検証と doi-list.md への編入
