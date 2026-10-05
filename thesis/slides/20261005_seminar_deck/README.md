# 2026-10-05 ゼミ進捗報告デッキ（Slides アーティファクトのソース）

- 公開先: https://claude.ai/artifact/Gx3MiVNqDP1YgVWYcTdf1y （非公開。共有はページの Share メニューから）
- 構成: `project/deck.json`（並び順・章立て・書体）＋ `project/slides/<id>.html`（1枚1ファイル、最後の `<aside>` が台本）。本編49枚（p.1〜49）＋付録11枚（p.50〜60）。10/5 にレビューを反映（v5、ページ番号は振り直し済み）。ソースの正本はこのフォルダ（scratchpad のコピーは古い）。
- 図は Artifact の asset（`/_blob/…`）として登録済み。対応表は `STYLE.md` 末尾。図を描き直したら asset として再アップロードし、スライドの `src` と対応表の id を差し替える（10/5 に kwind_sweep・spatial_dispersion・btm_case・negative_price_pi_k を差し替え）。
- `QA_20261005.md`: 10/5 のレビュー結果（想定問答・答えの骨子・事実関係）。発表前に目を通す。
- 書式・色・書体・用語のルールは `STYLE.md`。`python lint.py project/slides/*.html` で書式チェック（24px 未満の文字、使えない CSS、未登録の画像、使用禁止語など）。
- `render_preview.py` は手元の Chrome での簡易描画（DECK を このフォルダ、OUT を任意の出力先に書き換えて使う。MAXBOTTOM が 975 を超えると下端の出典行にかかる）。矢印（x-shape）は簡易描画では灰色の四角になる。
- 修正して再公開するときは、変更したファイルだけを Artifact の publish（url＝上記、root＝このフォルダ）で送る。並び順を変えたときは deck.json も送る。ページ番号（右下）は手書きなので、並び替えたら振り直す。
