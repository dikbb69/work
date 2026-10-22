# ファイナンス手法の検討パイロット（2026-10-20）

担当教員のコメント「ファイナンス（金融工学の手法）の使用と成果をもっと明確に」を受けて、既存手法の棚卸しと未使用手法の試算を行った作業の記録。要約と推奨は `notes/31-finance-methods.md`。

- `workflow_result.json`: 棚卸し（3エージェント）・候補とパイロット（4レンズ）・敵対的レビュー（4エージェント）の全出力
- `derivatives/`: 日次スプレッドオプションの層分解（p2）、24時間価格カーブの主成分と因子別感応度（p3）、分散恒等式（p4）、収入フロア・スワップの算術（p5）、日をまたぐ持ち越し LP（p6）。`review/r3_floor_mechanism.py` は下限価格の機構の検証
- `realoptions_corpfin/`: 動学的参入閾値（p1・p1b）、資本構成と c_req（p2）。`review/` に σ の部分標本と MM 整合版の修正
- `fin_econometrics/`: PCA と形状検定（p1・p1b・p1c）、HAC・年月FE・FGLS（p2・p2b）、DM 検定（p3）。`review/review_checks.py` に因子エクスポージャー・Diebold-Li・SPA 前段の計算
- `risk_portfolio/`: CFaR・確実性等価（r1）、ベータとヘッジ（r2）、θ*_β・IRR（r3）。`review/` に期ごとの CE とマーチャント IRR
- `front/`・`results/`: 中断した初回実行の HAC 比較と capture率のブートストラップ

注意: スクリプトの入出力パスはセッションの scratchpad（/private/tmp/...）を指している。再実行するときは `ROOT`・出力先を書き換える。リポジトリの data/processed は読むだけで、書き込みはしない。
