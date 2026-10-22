#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""原稿（manuscript/00〜14 の Markdown）を結合して Word 版を作る

手順:
  1. 00_front〜14_appendix を順に結合し、章の間に改ページを入れる（結合版 Markdown も書き出す）
  2. 付録C の「図と出力ファイルの対応」表から 図番号→（題、ファイル）を読み、
     本文で各図を最初に参照する段落の直後に図を挿入する（本文の Markdown には画像リンクを置かない方針のため）
  3. pandoc（pypandoc_binary 同梱）で docx に変換する。数式 $...$ は Word の数式、脚注 [^...] は Word の脚注になる
  4. 参照用 docx のスタイルを日本語向けに整える（本文 游明朝 10.5pt、見出し 游ゴシック）

使い方: python build_docx.py --version v0.4 [--out-dir manuscript]
出力: manuscript/thesis_draft_<version>.md、manuscript/thesis_draft_<version>.docx
限界: 図の位置は「最初に参照した段落の直後」で、Word 上での最終的な配置・サイズの調整は手作業。
"""
import argparse
import glob
import os
import re
import tempfile

import pypandoc
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ORDER = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"]
PAGEBREAK = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'


def chapter_files():
    files = []
    for p in ORDER:
        hit = sorted(glob.glob(os.path.join(HERE, f"{p}_*.md")))
        hit = [h for h in hit if not os.path.basename(h).startswith("thesis_draft")]
        if hit:
            files.append(hit[0])
    return files


def figure_map(appendix_text):
    """付録C の表の行「| 図X.Y 題 | `file.png` … | `script` |」から図の対応を作る"""
    figs = {}
    for line in appendix_text.splitlines():
        m = re.match(r"\|\s*(図\d+\.\d+)\s*([^|]*)\|\s*([^|]*)\|", line)
        if not m:
            continue
        num, cap, files = m.group(1), m.group(2).strip(), m.group(3)
        fm = re.findall(r"`([^`]+\.png)`", files)
        if not fm:
            continue
        fn = fm[0]
        cand = [os.path.join(ROOT, "figures", "hokkaido", fn), os.path.join(ROOT, "figures", "kyushu", fn), os.path.join(ROOT, fn)]
        path = next((c for c in cand if os.path.exists(c)), None)
        if path and num not in figs:
            figs[num] = (cap, path)
    return figs


def insert_figures(body, figs):
    """各図を最初に参照する段落（見出し・表・付録を除く）の直後に挿入する"""
    paras = body.split("\n\n")
    placed = set()
    out = []
    in_appendix = False
    for para in paras:
        out.append(para)
        if para.lstrip().startswith("# 付録") or para.lstrip().startswith("# 参考文献"):
            in_appendix = True
        if in_appendix or para.lstrip().startswith("#") or para.lstrip().startswith("|"):
            continue
        for num in sorted(figs, key=lambda s: [int(x) for x in s[1:].split(".")]):
            if num in placed:
                continue
            if re.search(re.escape(num) + r"(?![0-9])", para):
                cap, path = figs[num]
                rel = os.path.relpath(path, HERE)
                out.append(f"![{num} {cap}]({rel}){{width=15.5cm}}")
                placed.add(num)
    missing = sorted(set(figs) - placed)
    return "\n\n".join(out), placed, missing


def fix_math(text):
    """数式中の日本語を \\text{} で包み、\\cdot上位 のように命令と日本語が続く箇所に空白を入れる（既存の \\text{} は保つ）"""
    def conv(seg):
        seg = re.sub(r"(\\[A-Za-z]+)(?=[^\x00-\x7F])", r"\1 ", seg)
        return re.sub(r"([^\x00-\x7F\s][^\x00-\x7F]*)", lambda k: "\\text{" + k.group(1) + "}", seg)

    def wrap(m):
        parts = re.split(r"(\\(?:text|mathrm|textrm|mbox|operatorname)\{[^{}]*\})", m.group(2))
        body = "".join(p if i % 2 else conv(p) for i, p in enumerate(parts))
        return m.group(1) + body + m.group(3)
    text = re.sub(r"(\$\$)(.+?)(\$\$)", wrap, text, flags=re.S)
    text = re.sub(r"(?<![\\$])(\$)([^$\n]+?)(\$)(?!\$)", wrap, text)
    return text


def reference_docx(path):
    tmp = pypandoc.convert_text("x", "docx", format="md", outputfile=path)
    doc = Document(path)
    st = doc.styles
    for name, font, size in [("Normal", "Yu Mincho", 10.5), ("Body Text", "Yu Mincho", 10.5), ("First Paragraph", "Yu Mincho", 10.5),
                             ("Heading 1", "Yu Gothic", 16), ("Heading 2", "Yu Gothic", 13), ("Heading 3", "Yu Gothic", 11.5),
                             ("Title", "Yu Gothic", 18), ("Caption", "Yu Gothic", 9), ("Image Caption", "Yu Gothic", 9),
                             ("Footnote Text", "Yu Mincho", 9), ("Compact", "Yu Mincho", 9.5)]:
        try:
            s = st[name]
        except KeyError:
            continue
        s.font.name = font
        s.font.size = Pt(size)
        rpr = s.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rfonts)
        for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(k), font)
    doc.save(path)
    return tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v0.4")
    ap.add_argument("--out-dir", default=HERE)
    a = ap.parse_args()
    files = chapter_files()
    texts = [open(f, encoding="utf-8").read().strip() for f in files]
    combined = "\n\n".join(texts) + "\n"
    md_out = os.path.join(a.out_dir, f"thesis_draft_{a.version}.md")
    open(md_out, "w", encoding="utf-8").write(combined)
    appendix = next((t for f, t in zip(files, texts) if os.path.basename(f).startswith("14_")), "")
    figs = figure_map(appendix)
    body = PAGEBREAK.join(texts)
    body = fix_math(body)
    body, placed, missing = insert_figures(body, figs)
    with tempfile.TemporaryDirectory() as td:
        ref = os.path.join(td, "reference.docx")
        reference_docx(ref)
        docx_out = os.path.join(a.out_dir, f"thesis_draft_{a.version}.docx")
        pypandoc.convert_text(body, "docx", format="markdown+tex_math_dollars+pipe_tables+footnotes+raw_attribute+implicit_figures",
                              outputfile=docx_out, extra_args=[f"--reference-doc={ref}", f"--resource-path={HERE}"])
    print(f"結合版: {md_out}")
    print(f"Word 版: {docx_out}（図 {len(placed)} 点を挿入）")
    if missing:
        print("本文で参照が見つからず挿入しなかった図:", ", ".join(missing))


if __name__ == "__main__":
    main()
