# 2026-10-05 ゼミ進捗報告デッキ（Slides アーティファクトのソース）

- 公開先: https://claude.ai/artifact/Gx3MiVNqDP1YgVWYcTdf1y （非公開。共有はページの Share メニューから）
- 構成: `project/deck.json`（並び順・章立て・書体）＋ `project/slides/<id>.html`（1枚1ファイル、最後の `<aside>` が台本）。本編47枚（p.1〜47）＋付録10枚（p.48〜57）。
- 図は Artifact の asset（`/_blob/…`）として登録済み。対応表は `STYLE.md` 末尾。
- 書式・色・書体・用語のルールは `STYLE.md`。`python lint.py project/slides/*.html` で書式チェック（24px 未満の文字、使えない CSS、未登録の画像、使用禁止語など）。
- `render_preview.py` は手元の Chrome での簡易描画（パスは作成時の scratchpad を指しているので、使うときは DECK/OUT/FIG を書き換える）。矢印（x-shape）は簡易描画では灰色の四角になる。
- 修正して再公開するときは、変更したファイルだけを Artifact の publish（url＝上記、root＝このフォルダ）で送る。並び順を変えたときは deck.json も送る。ページ番号（右下）は手書きなので、並び替えたら振り直す。
