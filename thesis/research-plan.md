# 修士論文 研究計画書（案）

## 変動性再エネの拡大と系統用蓄電池の普及による電力価格ボラティリティの市場均衡分析
### — JEPX北海道エリアプライスを対象とした均衡普及量の推定 —

- 分野: 金融工学（エネルギーファイナンス / 実証産業組織）
- 作成日: 2026年7月20日
- ステータス: ドラフト（指導教員との協議前）

---

## 0. 本計画書の構成と使い方

本計画書は、(1) 研究テーマの確定、(2) 指導教員への説明、(3) 実際の研究着手、の3つに使えるように書かれている。

- 中核の提案は **第2章（リサーチクエスチョン）** と **第4章（方法論の3段構成)**。
- テーマを比較検討したい場合は **第10章（代替リサーチクエスチョン8案の評価）** を参照。
- すぐ動き出すためのタスクは **第13章（最初の90日のアクション）** にまとめた。
- 本計画の根拠となった詳細調査（市場制度・北海道の系統実態・先行研究・データソース）は `notes/` ディレクトリの調査ノート01〜07に整理してある。本文中の（→ノートN）はその参照。

---

## 1. 研究の背景

### 1.1 問題意識：再エネとボラティリティ、蓄電池と均衡

太陽光・風力といった変動性再エネ（VRE）は限界費用がほぼゼロであるため、卸電力市場の供給曲線（メリットオーダー）を右にシフトさせて価格水準を押し下げる（merit order effect）。一方で出力が天候に依存するため、残余需要（需要 − VRE出力）の変動を通じて価格の**ボラティリティ**を増大させる。晴天日の昼間は価格が下限に張り付き、夕方に急騰する「ダックカーブ」、寒波時の上方スパイクなど、価格分布は上下双方向に裾が厚くなる。

このボラティリティ（特に日内価格スプレッド）は、蓄電池にとっては**裁定収益の源泉**である。安値コマで充電し高値コマで放電する裁定行動は、それ自体が残余需要を平準化し、スプレッドとボラティリティを縮小させる。つまり蓄電池は普及するほど自らの収益源を侵食する（arbitrage value cannibalization）。この自己安定化メカニズムは、

> 再エネ増 → ボラティリティ増 → 蓄電池の裁定収益増 → 蓄電池参入 → ボラティリティ減 → 参入停止

というフィードバックループを形成し、**蓄電池の普及量には市場均衡として定まる内生的な水準が存在する**ことを意味する。カリフォルニア（CAISO）では蓄電池収益が2023年から2025年にかけて約半減し、豪州NEMでも2024年後半から2026年にかけてスプレッドが半分以下になるなど、カニバリゼーションは既に現実の市場で顕在化している（→ノート4）。日本はまだスプレッド拡大局面にあり、「均衡がどこに来るか」を**事前に**推定できる貴重なタイミングにある。

### 1.2 日本・JEPXの制度的文脈（→ノート1）

- JEPXスポット市場は30分48コマのブラインド・シングルプライスオークション。連系線制約時には「市場分断」により9エリア別のエリアプライスが成立する。
- FIT特例③によりFIT再エネはTSOが最低価格0.01円/kWhで売り入札するため供給曲線の最左端を形成し、太陽光の増加が昼間の下限張り付きを構造的に生む。下限価格の撤廃（マイナス価格導入）が審議会で議論中。
- 2021年1月には最高251円/kWhの歴史的スパイクが発生。上方スパイクと下限張り付きが併存する上下非対称のボラティリティ構造。
- 蓄電池の収益源はスポット裁定のほか、需給調整市場（EPRX、2024年度に全商品市場化）、容量市場・長期脱炭素電源オークション（初回で蓄電池109.2万kW落札）の3層スタッキング。

### 1.3 なぜ北海道か（→ノート2）

北海道エリアは、本研究の問いを構成する全要素が同時進行する日本で唯一のエリアである。

| 要素 | 北海道の状況 |
|---|---|
| 再エネ急増 | 太陽光236万kW・風力136万kW（2025年3月末接続量）。太陽光は2012年度末比約23倍 |
| 将来の再エネ | 洋上風力: 2025年7月に松前沖・檜山沖が道内初の促進区域指定。有望区域5海域（石狩市沖114万kW等）で数百万kW級の追加見通し |
| 出力制御 | 2022年5月8日に道内初実施（18.8万kW・1,916カ所）。以後、需給制約による制御が発生 |
| 蓄電池集中 | 系統用蓄電池の接続申込が2022年7月末時点で既に61件・160万kW（エリア平均需要約350万kWの約5割）。北豊富240MW/720MWh（2023年3月稼働・国内最大級）、札幌50MW/100MWh（2025年11月運開）等 |
| 連系線制約 | 北本連系設備90万kWのみで市場分断率は2023年度平均8.5%。2027年度末に120万kWへ増強、さらに日本海ルートHVDC 200万kW構想 |
| 小規模系統 | 冬季ピーク型（厳寒想定567万kW）。エリアプライスが他エリアと独立した価格動態を持つことが先行研究でも確認されている |

小規模で分断されやすい系統だからこそ、(a) 再エネ・蓄電池の限界的増加が価格分布に与える影響が観測されやすく、(b) 北海道エリアプライスを「一つの市場」として均衡モデルで閉じることが正当化しやすい。加えて蓄電池申込量が需要規模比で全国最大級であるため、「申込1.6GW超のうち均衡的に持続可能なのは何MWか」という問いが実務・政策上も切実である。

---

## 2. リサーチクエスチョンと仮説

### 2.1 主リサーチクエスチョン

> **RQ: 北海道エリアのJEPXスポット市場において、再エネ（太陽光・風力）導入量の増加は価格ボラティリティをどの程度増大させ、蓄電池の裁定収益が資本コストと一致する自由参入均衡においては、再エネ導入量の関数として何MW/MWhの蓄電池が普及し、ボラティリティはどの水準に収束するか。**

これを3つのサブクエスチョンに分解する。

- **RQ-1（ボラティリティ生成関数）**: 太陽光と風力は、北海道エリアプライスのボラティリティ（実現ボラティリティ・日内スプレッド・スパイク頻度）をそれぞれどの向き・大きさで変化させてきたか。
- **RQ-2（蓄電池の価格インパクト）**: 蓄電池フリートの充放電裁定は、価格分布・スプレッドをどの程度圧縮するか。その限界効果は普及量に対してどう逓減するか。
- **RQ-3（均衡普及量）**: 裁定収益＝年換算固定費となるゼロ利潤・自由参入均衡での蓄電池容量 K\*(R) と均衡ボラティリティ σ\*(R) は、再エネ導入シナリオ R（現状／2030年洋上風力等）ごとにいくらか。社会厚生を最大化する容量 K^W(R) と乖離するか。

### 2.2 作業仮説

- **H1（非対称性）**: 太陽光は日中形状（コマ間）ボラティリティを拡大させる一方、風力は日次ボラティリティとスパイクの双方向に効く。北海道では風力が高価格帯の抑制（スパイク緩和）に働く可能性がある（Sakaguchi & Fujii 2021の北海道での知見と整合するか検証）。
- **H2（カニバリゼーション）**: 蓄電池は日内スプレッドを縮小させ、その限界効果は普及量に対して逓減する（Butters et al. 2025、Lamp & Samano 2022のJEPX版検証）。
- **H3（均衡ボラティリティの下限）**: 均衡ではボラティリティはゼロにならず、**「均衡スプレッドは蓄電池の年換算固定費を回収する水準で下から支えられる」**。すなわち再エネがどれだけ増えても、均衡日内スプレッドは概ね蓄電池の限界コスト（円/kWh-cycle）に収束する。これは「ボラティリティの均衡価格」という金融工学的に明快な命題であり、本論文の理論的な看板になりうる。

---

## 3. 先行研究と本研究の位置づけ（→ノート3・4）

### 3.1 再エネと価格・ボラティリティ（merit order effect系）

- 価格水準の押し下げ: Sensfuß, Ragwitz & Genoese (2008, Energy Policy)、Cludius et al. (2014, Energy Econ)（独）、Gelabert et al. (2011)（西）、Csereklyei et al. (2019)（豪）。
- ボラティリティへの効果: Woo et al. (2011, Energy Policy) が「風力は価格水準を下げ分散を拡大する」トレードオフをERCOTで実証。Ketterer (2014, Energy Econ) はARX-GARCHで同様の結果（独）。Rintamäki, Siddiqui & Salo (2017, Energy Econ) は**太陽光は日中ボラを下げ、風力は日次ボラを上げる**という電源種・市場構造による非対称性を示した。
- スパイク・下限: Fanone et al. (2013)（負価格）、Christensen et al. (2012)（スパイク予測）。

### 3.2 日本・JEPX対象の実証

- Maekawa et al. (2018, Energies): 太陽光の昼間価格押し下げ。
- Sakaguchi & Fujii (2021, Frontiers in Sustainability): エリア別・分位点回帰。**北海道では風力のMOEが高価格分位で最大**という本研究に直結する知見。
- Fuke & Ohashi (2025, J. Commodity Markets): 九州の太陽光とボラティリティの季節性。
- Rassi & Kanamura (2023, Energy Policy): 入札カーブ構造モデルによる2021年1月スパイク分析。
- Ciarreta et al. (2017, ISER DP): JEPX実現ボラティリティへのHAR適用の先例。

### 3.3 蓄電池の裁定・カニバリゼーション・市場均衡

- 裁定価値と自己侵食の古典: Sioshansi et al. (2009, Energy Econ)。最適運用のADP: Jiang & Powell (2015)。
- カニバリゼーションの実証: Lamp & Samano (2022, Energy Econ)（CAISOでスプレッド縮小）、Rangarajan et al. (2023, Energy Econ)（豪州、調整力市場費用の低下が先行）。
- 貯蔵の長期均衡理論: Schmalensee (2022)、Junge, Mallapragada & Schmalensee (2022)（**社会最適容量＝競争均衡容量で貯蔵はゼロ超過利潤**）、Korpås & Botterud (2020) / Tarel et al. (2024)（VRE＋貯蔵のみの均衡価格形成）。
- 市場支配力: Andrés-Cerezo & Fabra (2023, RAND)、Karaduman (2021, MIT CEEPR WP)（南豪州の動学的構造均衡: 価格インパクト無視は収益を約2倍過大評価）、Huang et al. (2021, IEEE TNSE)（Cournot貯蔵）。
- **最重要ベンチマーク**: Butters, Dorsey & Gowrisankaran (2025, *Econometrica*)「Soaking Up the Sun」。再エネ×蓄電池の自由参入均衡をカリフォルニアで構造推定し、最初の5,000MWhは卸価格を5.6%下げるが25,000→50,000MWhでは2.6%にとどまる収益逓減、均衡では補助なしに普及が進まないことを定量化。**本研究はこの枠組みの簡略版を、市場分断・下限価格・風力主導という異なる制度環境（JEPX北海道）に適用するものと位置づけられる。**

### 3.4 研究ギャップ（本研究の新規性）

1. 日本のエリア別実証は九州（太陽光）に偏り、**風力主導で蓄電池が集中する北海道**の価格・ボラティリティ分析はほぼ空白。
2. 「再エネによるボラ増」と「蓄電池によるボラ減」を**同一均衡モデル内で扱い、日本のデータで均衡普及量を推定した研究は見当たらない**（国内学会誌・CiNii・J-STAGEでの体系的確認は着手時に実施）。
3. JEPX特有の**下限価格0.01円/kWh（マイナス価格なし）**の下でのボラティリティ・スパイクのモデリング自体に方法論的新規性がある（打ち切り分布・Tobit型の扱い）。
4. 均衡分析の対象として**市場分断エリア**（連系線容量が状態変数になる）を扱う点も、単一市場を仮定する米欧研究との差分。

---

## 4. 理論的枠組みと方法論：3段構成

修士2年間で確実に完成させるため、**各段階が単体でも論文の章として成立する**逐次的な設計とする（→ノート5）。

### 4.0 全体設計

```
第1段階（誘導形・実証）        第2段階（構造モデル）              第3段階（均衡分析）
北海道エリアプライスの         残余需要×ビッドスタックによる      自由参入ゼロ利潤条件で
定型事実とボラ生成関数         価格生成 + 蓄電池最適運用          均衡蓄電池容量 K*(R) を解く
  HAR-RV / EGARCH-X /            P_t = g(N_t + c_t − d_t)          Π(K*;R) = 年換算固定費
  分位点回帰 / 構造変化検定       蓄電池DP（SoC制約付き）           σ*(R) = Vol(P; K*(R), R)
        │                              │                                │
        └── 「再エネ→ボラ」の実証 ──→ 構造パラメータの推定 ──→ 反実仮想・シナリオ分析
```

### 4.1 第1段階：誘導形実証 — ボラティリティ生成関数（RQ-1）

**データ**: 北海道エリアプライス30分値（JEPX、2012年度〜）、北海道電力NWエリア需給実績（太陽光・風力実績出力を含む30分値、2016年4月〜）、アメダス気象データ。

**ボラティリティ指標**（複数定義で頑健性を確保）:
- 日次実現ボラティリティ: $RV_d = \sum_{i=1}^{48} (P_{d,i} - P_{d,i-1})^2$（下限0.01円張り付きコマの扱いは対数リターンでなく水準差分で対応）
- 日内スプレッド: $\max_i P_{d,i} - \min_i P_{d,i}$ および「上位4時間平均 − 下位4時間平均」（4時間蓄電池の理論粗利に対応する**Top-Bottom 4hスプレッド**）
- スパイク頻度: 閾値超過回数、Hawkes過程の強度・自己励起性
- 下限張り付き率: 0.01円コマ数の比率（下方「ボラティリティ」の代理変数）

**モデル**:
- HAR-RV（Ciarreta et al. 2017のJEPX先例に接続）＋再エネ出力を外生変数に加えたHAR-RV-X
- EGARCH-X（上下非対称・逆レバレッジ効果の検証）
- 分位点回帰（Sakaguchi & Fujii 2021の北海道特化版・最新データへの拡張。太陽光と風力を分離）
- 構造変化検定: 2019年3月（新北本）、2022年4月（FIP）、2022年5月（出力制御開始）、2023年3月（北豊富運開）、2025年11月（札幌蓄電池運開）等をイベントとするBai-Perron検定・イベントスタディ
- 識別への配慮: 再エネ出力の内生性には気象変数（風速・日射量）を操作変数として利用。燃料価格（LNG・石炭）・需要・分断有無を統制

**成果物**: 「太陽光+1GW／風力+1GWが各ボラ指標を何%動かすか」の弾力性推定 = ボラティリティ生成関数 $\sigma(R_{PV}, R_{wind}; X)$。

### 4.2 第2段階：構造モデル — 残余需要×ビッドスタック＋蓄電池最適運用（RQ-2）

**価格生成**: Barlow (2002)・Wagner (2014) 系の残余需要アプローチ。

$$P_t = g\left(D_t - G^{PV}_t - G^{wind}_t + c_t - d_t - F_t\right)$$

- $g(\cdot)$: 北海道の供給曲線（メリットオーダー）。推定は (a) JEPX公開の入札カーブ画像の数値化、または (b) 価格と残余需要の観測ペアからの誘導的推定（区分線形／Box-Cox型）、の二本立てで検討。0.01円下限と上限をそのまま曲線の端点として保持
- $F_t$: 北本連系線潮流。**分断レジーム**（潮流が容量制約に到達しているか否か）で価格形成が切り替わる2レジーム構造とし、非分断時は東北・システムプライスとの裁定条件、分断時は道内供給曲線で価格が決まる
- 需要・再エネ出力は季節性＋確率過程（風況・日射のブートストラップまたはパラメトリックモデル）でシミュレート

**蓄電池運用**: 容量 $K$（MW）・継続時間 $h$（4時間を基準）・往復効率 $\eta$ のフリートについて、SoC制約付き充放電最適化:

$$\max_{\{c_t, d_t\}} \; \mathbb{E}\left[\sum_t P_t (d_t - c_t)\right] - \text{劣化費用}, \quad \text{s.t.} \;\; SoC_{t+1} = SoC_t + \eta c_t - d_t, \;\; 0 \le SoC_t \le hK$$

- 個々のユニットは価格テイカーの動的計画法（DP）で解くが、**フリート全体の充放電が残余需要をシフトして価格に跳ね返る**構造（価格インパクトの内生化）を不動点反復で解く。Karaduman (2021) の簡略版であり、MPEC/EPECには踏み込まない
- 蓄電池フリートの異質性: 北豊富型（風力併設・変動緩和目的）と市場裁定型を区別。長期脱炭素電源オークション落札分は収益還付により市場価格感応度が低い点も感応度分析で扱う

**検証**: 第1段階のイベントスタディ（大型蓄電池運開前後のスプレッド変化）とモデル予測を突合し、構造モデルの妥当性を確認する。

### 4.3 第3段階：均衡分析 — 自由参入ゼロ利潤条件による均衡普及量（RQ-3）

**均衡の定義**（主）: 限界的な参入者の年間裁定収益が年換算固定費（資本費×資本回収係数＋固定O&M）と一致する自由参入均衡。

$$\pi(K^*; R) \equiv \frac{\partial \Pi(K; R)}{\partial K}\bigg|_{K=K^*} = AFC \quad \Rightarrow \quad K^*(R), \;\; \sigma^*(R) = \text{Vol}\left(P;\, K^*(R), R\right)$$

- 再エネシナリオ $R$: 現状／接続申込ベース／2030年洋上風力（促進区域・有望区域）等の複数シナリオ
- 蓄電池コストは経産省審議会・調達価格等算定委の公表値に将来低下シナリオを重ねる
- **主要アウトプット**: $R$ を横軸にとった均衡容量曲線 $K^*(R)$ と均衡ボラティリティ曲線 $\sigma^*(R)$ —「再エネがXGWのとき蓄電池はYGWh普及し、スプレッドはZ円/kWhに落ち着く」という本研究の中心的な図

**ベンチマーク**（副）: 社会厚生（消費者余剰＋生産者余剰−蓄電池費用）を最大化する容量 $K^W(R)$ を同一モデルで計算し、私的均衡との乖離を評価。理論上は完全競争下で両者は一致する（Junge et al. 2022）ため、乖離が生じる要因（下限価格・出力制御ルール・市場分断・調整力収益の欠落）の分解が政策的含意になる。

**感応度分析**: (i) 北本120万kW／日本海HVDC 200万kW、(ii) 泊3号機再稼働、(iii) マイナス価格導入（下限撤廃）、(iv) 需給調整市場・容量市場収益の包含（包含しない場合は均衡容量の下限推定である旨を明示）、(v) 完全競争 vs 単一支配的事業者（Cournot的行動）。

### 4.4 スコープ管理（やらないことの明示）

- フルのSFE（供給関数均衡）・MPEC/EPECによる戦略的入札の内生化は**行わない**（非凸・複数均衡で修士2年のリスクが大きい。→ノート5の実現可能性評価）
- 深層強化学習による運用最適化は**行わない**（DPで十分であり再現性を優先）
- 9エリア全体の広域均衡モデルは**行わない**（北海道＋連系線潮流の外生／簡易内生化で閉じる）

---

## 5. データ計画（→ノート6）

| # | データ | 提供元 | 粒度・期間 | 費用 | 備考 |
|---|---|---|---|---|---|
| 1 | スポット約定価格（システム＋9エリア）・約定量・売買入札量 | JEPX「市場情報」 | 30分48コマ、2005年度〜（現行UIでの確実な確認は2012年度〜） | 無料 | サイトは自動取得を拒否するため手動DL |
| 2 | 入札カーブ（需給曲線） | JEPX | 2021年2月27日〜、48コマ | 無料だが**画像のみ** | 数値化スクリプト or 第三者数値化データ or JEPXへ研究目的の提供依頼 |
| 3 | 時間前市場約定 | JEPX | 30分値 | 無料 | 補助的利用 |
| 4 | エリア需給実績（需要・太陽光/風力実績・揚水・連系線潮流） | 北海道電力NW | 30分値、2016年4月〜 | 無料 | **掲載は当年度＋過去5カ年ローリングの可能性 → 直ちに全量アーカイブ（最優先タスク）** |
| 5 | ユニット別発電実績（京極揚水等） | 北海道電力NW | 公開CSV | 無料 | 揚水の実運用復元・比較分析用 |
| 6 | 北本連系線潮流・運用容量・空容量 | OCCTO系統情報サービス | 5分値ベース | 無料 | 分断レジーム判定に使用 |
| 7 | 出力制御実績・見通し | 北海道電力NW／OCCTO検証資料 | イベント別 | 無料 | 2022年5月8日初実施以降 |
| 8 | 需給調整市場約定結果（5商品・エリア別） | EPRX「取引情報」 | 2021年度〜 | 無料 | マルチマーケット拡張用。CSV仕様は要確認 |
| 9 | 容量市場・長期脱炭素電源オークション約定結果 | OCCTO | 年度別 | 無料 | 蓄電池の固定収入の把握 |
| 10 | 蓄電池コスト・導入統計（接続検討/申込/連系済） | 経産省系統WG・OCCTO統計 | 審議会資料 | 無料 | 3段階の統計の性格差に注意 |
| 11 | 気象（風速・日照・気温） | 気象庁アメダス／全天日射は札幌等官署 | 10分〜時別 | 無料 | 操作変数・シミュレーション用 |
| 12 | 気象格子データ（MSM-GPV） | 京大RISHアーカイブ | 5km格子 | 研究目的無償 | 日射量要素は2018年1月〜 |
| 13 | 電力先物 | JPX（日次無料）／EEX（有料） | 東・西エリアのみ（北海道は非上場） | 一部有料 | リスクプレミアム検証の補助。主軸にしない |

**データ上の主要リスクと対応**: 入札カーブが画像のみ→第4.2節の(b)誘導的推定を主線に据え、数値化は上乗せ精度改善と位置づける。北海道電力NWの需給実績のローリング掲載→着手初週にアーカイブ。

---

## 6. 論文の章立て（案）

1. **序論** — 問題意識、RQ、貢献の要約
2. **制度的背景** — JEPX市場設計、FIT/FIP、北海道エリアの系統・再エネ・蓄電池・連系線（ノート1・2が下書きの素材）
3. **先行研究** — MOE／ボラティリティ／蓄電池均衡の3系譜と研究ギャップ（ノート3・4が素材）
4. **北海道エリアプライスの実証分析** — 定型事実、ボラティリティ生成関数の推定（第1段階）
5. **構造モデル** — 残余需要×ビッドスタック、蓄電池最適運用、価格インパクト（第2段階）
6. **均衡分析** — 自由参入均衡 K\*(R)・σ\*(R)、社会最適との比較、シナリオ・感応度（第3段階）
7. **政策的含意と結論** — 蓄電池普及目標・補助設計・連系線増強との代替性、限界と今後の課題

---

## 7. 研究スケジュール（案）

2026年8月開始・2028年1月提出を仮置きした18カ月構成（所属専攻の実際のマイルストーンに合わせて要調整）。

| 期間 | フェーズ | 主なタスク | マイルストーン |
|---|---|---|---|
| 1〜2カ月目（2026/8-9） | 立ち上げ | データ全量アーカイブ（最優先: 北海道電力NW需給実績）、JEPX・EPRXデータ整備パイプライン構築、CiNii/J-STAGE国内先行研究の体系的確認、主要文献precise読み（Butters et al., Karaduman, Rintamäki, Sakaguchi & Fujii） | 研究計画の指導教員承認 |
| 3〜6カ月目（2026/10-2027/1) | 第1段階 | 定型事実の整理、ボラ指標構築、HAR/EGARCH-X/分位点回帰の推定、構造変化・イベントスタディ | 中間報告①（実証結果）。学内発表 or 国内学会（エネルギー・資源学会等）投稿検討 |
| 7〜10カ月目（2027/2-5） | 第2段階 | 供給曲線推定（誘導的＋入札カーブ数値化の試行）、需要・再エネ確率過程、蓄電池DP実装、価格インパクトの不動点計算、イベントスタディとの突合検証 | 中間報告②（構造モデル動作） |
| 11〜14カ月目（2027/6-9） | 第3段階 | 均衡計算 K\*(R)・σ\*(R)、厚生ベンチマーク、シナリオ・感応度分析 | 主結果の確定 |
| 15〜16カ月目（2027/10-11） | 執筆前半 | 第1〜5章執筆、結果の頑健性チェック追補 | ドラフト提出 |
| 17〜18カ月目（2027/12-2028/1） | 執筆後半 | 第6〜7章、全体推敲、審査対応 | **修士論文提出・発表** |

各段階は前段の成果だけで章として成立するため、後段が計画より遅延した場合も「第1段階＋第2段階＋簡易均衡（感応度を絞る）」への縮退が可能。

---

## 8. 想定されるリスクと対応

| # | リスク | 影響 | 対応 |
|---|---|---|---|
| 1 | 入札カーブの数値データが取得できない | 供給曲線推定の精度低下 | 価格×残余需要からの誘導的推定を主線に設計（4.2節）。画像数値化・JEPXへの提供依頼は上乗せ |
| 2 | 再エネ出力の内生性（需要・燃料価格との交絡） | ボラ生成関数のバイアス | 気象操作変数、燃料価格・需要統制、分位点回帰の頑健性 |
| 3 | 均衡計算の計算負荷 | 第3段階の遅延 | 価格テイカーDP＋不動点の簡略構造、代表日サンプリング、MPEC回避（4.4節） |
| 4 | 蓄電池フリートの異質性（北豊富は風力併設・変動緩和用でJEPX裁定運用でない可能性） | 「蓄電池=裁定プレイヤー」仮定の過大評価 | フリートを併設型／裁定型に区分。イベントスタディの処置定義は裁定型（例: 札幌50MW）で行う |
| 5 | 需給調整市場・容量市場収益の捨象 | 均衡容量の過小推定 | 主分析は「スポット裁定のみ＝下限推定」と明示し、EPRX約定データで収益上乗せの感応度分析 |
| 6 | 分析期間中の構造変化（北本120万kW化2027年度末、泊3号再稼働目標2027年、ラピダス等の需要増、マイナス価格導入議論） | 推定の不安定化・前提の陳腐化 | 構造変化点を明示した期間設計。連系線容量・需要・価格下限をシナリオ変数として外生化 |
| 7 | 北海道電力NW需給実績の掲載期間（過去5カ年ローリングの可能性） | 過去データの喪失 | **着手初週に全量アーカイブ** |
| 8 | 下限0.01円による価格分布の打ち切り | 標準的ボラ推定の歪み | 水準ベース指標＋Tobit/打ち切り対応。下限張り付き率を独立の指標として扱う |
| 9 | 出力制御実績の日数不足（2024年度実施分の検証対象は2日間） | 制御を組み込んだ実証の困難 | 出力制御は実証の主対象とせず、構造モデルの制約条件・見通し資料ベースのシナリオとして扱う |

---

## 9. 期待される貢献

- **学術**: (1) 日本の卸電力市場を対象とした初の「再エネ×蓄電池の均衡普及量」推定。(2) 下限価格制約・市場分断という米欧と異なる制度環境での貯蔵均衡モデルの適用可能性の検証。(3) 風力主導エリアのボラティリティ生成関数という日本では手薄な実証。
- **実務**: 北海道に殺到する蓄電池投資（申込1.6GW超）に対する、カニバリゼーションを織り込んだ収益・適正容量の定量的目安。「均衡スプレッド≒蓄電池固定費」というプライシングの視点。
- **政策**: 蓄電池導入目標・補助設計（長期脱炭素オークションの規模）・接続許容量の議論、および連系線増強（新々北本・日本海HVDC）と域内蓄電池の代替性評価への定量的インプット。

---

## 10. 多角的に検討した代替・発展リサーチクエスチョン（→ノート7）

調査段階で8つのRQ候補を立てて評価した。本命はRQ1（上記の主RQ）だが、以下は指導教員との相談材料・発展章・切り替え先として保持する。

| RQ | 内容 | 手法（金融工学との接点） | 実現可能性 | 新規性 | 位置づけ |
|---|---|---|---|---|---|
| 1 | **蓄電池自由参入均衡によるボラ均衡点の推定（本命）** | 構造モデル＋DP＋ゼロ利潤均衡 | 高 | 高 | 本計画の主軸 |
| 2 | 太陽光vs風力のボラティリティ寄与の計量分解 | GARCH-X・分位点回帰・Hawkes | 最高（低リスク） | 中 | 第1段階に吸収済み |
| 3 | 蓄電池のマルチマーケット価値評価（スポット＋EPRX＋容量市場） | SDP・LSMによる切替オプション評価 | 中 | 高 | 感応度分析＋発展章候補 |
| 4 | 北本連系線増強の実物オプション評価と蓄電池との代替性 | 2エリアOU過程・スプレッドオプション（Margrabe） | 中 | 高 | 発展章候補。間接送電権価格との突合が面白い |
| 5 | 出力制御の経済損失と蓄電池の「保険価値」 | 制約付き最適運用・curtailment insurance | 低〜中（実績日数不足） | 中 | 将来課題として言及に留める |
| 6 | 北海道エリアのスパイクリスクのクロスヘッジ設計（先物・間接送電権） | ジャンプ/Hawkesモデル＋最小分散ヘッジ | 中 | 高 | テーマ切替先の第一候補（より純金融工学寄り） |
| 7 | 柔軟性資源比較: 蓄電池 vs 京極揚水 vs 連系線 | 厚生分析・ユニット別実績からの運用復元 | 中（範囲を絞れば） | 高 | 厚生ベンチマーク（4.3節）に部分吸収 |
| 8 | 大型蓄電池運開のイベントスタディ（スパイク自己励起性の減衰） | 時変Hawkes・DiD・合成コントロール | 中（識別が難所） | 高 | 第2段階のモデル検証に組み込み |

**判断理由の要約**: RQ1は (a) *Econometrica* 級の確立された理論枠組みに接ぎ木でき、(b) データが公開情報で完結し、(c) RQ2・RQ8を部品として吸収できる拡張性を持ち、(d) 北海道という対象選択の必然性を最も活かせるため主軸とした。純粋なデリバティブ・ヘッジ設計に寄せたい場合はRQ6への切替が最も自然。

---

## 11. 指導教員と早期に協議すべき論点

1. **均衡概念の選択**: 自由参入ゼロ利潤均衡を主とする本計画の設計でよいか。厚生最大化・Cournotをどこまで扱うか。
2. **ボラティリティの操作的定義**: 金融工学の論文としてRV系を主指標にするか、蓄電池経済性に直結するTop-Bottomスプレッドを主指標にするか。
3. **需給調整市場収益の扱い**: 「スポットのみ＝下限推定」の割り切りで審査に耐えるか、マルチマーケット化を必須とするか（作業量が大きく変わる）。
4. **構造モデルの深さ**: 誘導的供給曲線推定で足りるか、入札カーブ数値化まで要求するか。
5. **投稿戦略**: 中間成果（第1段階）を国内学会・英文誌（Energy Economics系）のどちらに向けるか。
6. **計算環境**: シミュレーション・不動点計算の計算資源（研究室サーバ等）の確保。

---

## 12. 要確認事項（本計画の前提のうち一次資料での検証が必要なもの）

調査はWeb情報に基づくため、以下は着手時に一次資料・実データで確認する（→ノート6末尾）。

- [ ] JEPXスポットCSVの取得可能な最古年度（2005年度まで遡れるか）
- [ ] 北海道電力NW需給実績の掲載保持期間（過去5カ年ローリングか）→ 確認前にまずアーカイブ
- [ ] OCCTO連系線潮流CSVの正確な時間粒度
- [ ] EPRX約定結果CSVの粒度・仕様
- [ ] 「JEPX日次スプレッドが2020年約4円→2024年約20円/kWhに拡大」（業界資料の数値）の公表データによる再計算
- [ ] 需給調整市場の2026年度以降の制度改定（上限価格・募集量）のEPRX一次資料での確認
- [ ] 長期脱炭素電源オークションの他市場収益還付率の一次資料確認
- [ ] マイナス価格（下限撤廃）議論・同時市場検討の最新状況
- [ ] Sensfuß et al. (2008) 等、引用予定文献の具体的推定値の原典確認

---

## 13. 直近のアクション（最初の90日）

**Week 1-2: データ保全（最優先）**
1. 北海道電力NWエリア需給実績（2016年4月〜）を全量ダウンロード・アーカイブ
2. JEPXスポット・時間前CSV（全年度）を手動ダウンロード
3. EPRX約定結果・OCCTO連系線データの取得と仕様確認

**Week 3-6: 文献と定型事実**
4. 精読リスト: Butters et al. (2025)、Karaduman (2021)、Lamp & Samano (2022)、Rintamäki et al. (2017)、Sakaguchi & Fujii (2021)、Ciarreta et al. (2017)、Junge et al. (2022)、Andrés-Cerezo & Fabra (2023)
5. CiNii・J-STAGE・エネルギー・資源学会誌で国内先行研究を体系的に確認（研究ギャップの最終確認）
6. 北海道エリアプライスの記述統計: 年度別の平均・分布・スプレッド・0.01円張り付き率・分断率・スパイク頻度の可視化（→そのまま論文第4章の冒頭になる）

**Week 7-12: 計画確定と第1段階着手**
7. 本計画書を基に指導教員と協議し、第11章の論点を確定
8. ボラティリティ指標の実装とHAR-RV/EGARCH-Xの初回推定
9. 中間発表資料の骨子作成

---

## 参考文献（主要・カテゴリ別）

### 再エネと価格・ボラティリティ
- Sensfuß, F., Ragwitz, M., & Genoese, M. (2008). The merit-order effect: A detailed analysis of the price effect of renewable electricity generation on spot market prices in Germany. *Energy Policy*, 36(8).
- Cludius, J., Hermann, H., Matthes, F. C., & Graichen, V. (2014). The merit order effect of wind and photovoltaic electricity generation in Germany 2008–2016. *Energy Economics*, 44.
- Woo, C. K., Horowitz, I., Moore, J., & Pacheco, A. (2011). The impact of wind generation on the electricity spot-market price level and variance: The Texas experience. *Energy Policy*, 39(7).
- Ketterer, J. C. (2014). The impact of wind power generation on the electricity price in Germany. *Energy Economics*, 44.
- Rintamäki, T., Siddiqui, A. S., & Salo, A. (2017). Does renewable energy generation decrease the volatility of electricity prices? An analysis of Denmark and Germany. *Energy Economics*, 62.
- Csereklyei, Z., Qu, S., & Ancev, T. (2019). The effect of wind and solar power generation on wholesale electricity prices in Australia. *Energy Policy*, 131.
- Fanone, E., Gamba, A., & Prokopczuk, M. (2013). The case of negative day-ahead electricity prices. *Energy Economics*, 35.

### 日本・JEPX
- Maekawa, J., Hai, B. H., Shinkuma, S., & Shimada, K. (2018). The effect of renewable energy generation on the electric power spot price of the Japan Electric Power Exchange. *Energies*, 11(9).
- Sakaguchi, M., & Fujii, H. (2021). The impact of variable renewable energy penetration on wholesale electricity prices in Japan between FY 2016 and 2019. *Frontiers in Sustainability*, 2:770045.
- Fuke, F., & Ohashi, H. (2025). Seasonal variation in the impact of solar power generation on electricity price level and variability. *Journal of Commodity Markets*, 40.
- Rassi, S., & Kanamura, T. (2023). Electricity price spike formation and LNG prices effect under gross bidding scheme in JEPX. *Energy Policy*, 177.
- Ciarreta, A., Muniain, P., & Zarraga, A. (2017). Modelling realized volatility in electricity spot prices: New insights and application to the Japanese electricity market. ISER Discussion Paper No. 991.

### 蓄電池・貯蔵と市場均衡
- Butters, R. A., Dorsey, J., & Gowrisankaran, G. (2025). Soaking up the sun: Battery investment, renewable energy, and market equilibrium. *Econometrica*, 93(3), 891–927.
- Karaduman, Ö. (2021). Economics of grid-scale energy storage in wholesale electricity markets. MIT CEEPR Working Paper 2021-005.
- Sioshansi, R., Denholm, P., Jenkin, T., & Weiss, J. (2009). Estimating the value of electricity storage in PJM: Arbitrage and some welfare effects. *Energy Economics*, 31(2).
- Lamp, S., & Samano, M. (2022). Large-scale battery storage, short-term market outcomes, and arbitrage. *Energy Economics*, 107.
- Schmalensee, R. (2022). Competitive energy storage and the duck curve. *The Energy Journal*, 43(2).
- Junge, C., Mallapragada, D., & Schmalensee, R. (2022). Energy storage investment and operation in efficient electric power systems. *The Energy Journal*, 43(6).
- Tarel, G., Korpås, M., & Botterud, A. (2024). Long-term equilibrium in electricity markets with renewables and energy storage only. *Energy Systems*.
- Andrés-Cerezo, D., & Fabra, N. (2023). Storing power: Market structure matters. *RAND Journal of Economics*, 54(1).
- Huang, Q., Xu, Y., & Courcoubetis, C. (2021). Strategic storage operation in wholesale electricity markets: A networked Cournot game analysis. *IEEE Transactions on Network Science and Engineering*, 8.
- Virasjoki, V., Siddiqui, A. S., Oliveira, F., & Salo, A. (2020). Utility-scale energy storage in an imperfectly competitive power sector. *Energy Economics*, 88.
- Rangarajan, A., Foley, S., & Trück, S. (2023). Assessing the impact of battery storage on Australian electricity markets. *Energy Economics*, 120.
- Jiang, D. R., & Powell, W. B. (2015). Optimal hour-ahead bidding in the real-time electricity market with battery storage using approximate dynamic programming. *INFORMS Journal on Computing*, 27(3).

### 価格モデリング・手法
- Lucia, J. J., & Schwartz, E. S. (2002). Electricity prices and power derivatives: Evidence from the Nordic Power Exchange. *Review of Derivatives Research*, 5(1).
- Cartea, Á., & Figueroa, M. G. (2005). Pricing in electricity markets: A mean reverting jump diffusion model with seasonality. *Applied Mathematical Finance*, 12(4).
- Barlow, M. T. (2002). A diffusion model for electricity prices. *Mathematical Finance*, 12(4).
- Wagner, M. (2014). Residual demand modeling and application to electricity pricing. *The Energy Journal*, 35(2).
- Weron, R. (2014). Electricity price forecasting: A review of the state-of-the-art with a look into the future. *International Journal of Forecasting*, 30(4).
- Janczura, J., & Weron, R. (2012). Efficient estimation of Markov regime-switching models: An application to electricity spot prices. *AStA Advances in Statistical Analysis*.
- Corsi, F. (2009). A simple approximate long-memory model of realized volatility. *Journal of Financial Econometrics*, 7(2).
- Bakke, I., Fleten, S.-E., et al. (2016). Investment in electric energy storage under uncertainty: A real options approach. *Computational Management Science*, 13(3).

### 制度・データ（一次資料）
- JEPX 市場情報（スポット市場データ・入札カーブ） https://www.jepx.jp/electricpower/market-data/spot/
- 北海道電力ネットワーク エリア需給実績 https://www.hepco.co.jp/network/con_service/public_document/supply_demand_results/index.html
- 北海道電力ネットワーク「北海道エリアにおける再生可能エネルギー出力制御の実施について」(2022) https://www.hepco.co.jp/network/info/info2022/1251727_1913.html
- 経済産業省 系統WG「5月8日における再エネ出力制御の実施状況について」（北海道電力NW、2022年5月24日） https://www.meti.go.jp/shingikai/enecho/shoene_shinene/shin_energy/keito_wg/pdf/039_03_00.pdf
- OCCTO 広域系統整備委員会資料（北本連系設備・市場分断率） https://www.occto.or.jp/assets/iinkai/kouikikeitouseibi/2025/files/seibi_90_02_01.pdf
- EPRX 取引情報 https://www.eprx.or.jp/information/
- 資源エネルギー庁 系統WG「系統用蓄電池の迅速な系統連系に向けて」(2025) https://www.meti.go.jp/shingikai/enecho/denryoku_gas/saisei_kano/smart_power_grid_wg/pdf/004_04_00.pdf

（各文献の要約・URL・追加文献は `notes/03`・`notes/04`・`notes/05` を参照）
