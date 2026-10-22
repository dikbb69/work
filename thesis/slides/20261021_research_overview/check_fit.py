#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pptx の各テキストボックス・表のセルについて、文字が枠に収まるかをフォントの実測で確かめる

PowerPoint を自動操作せずに版面の崩れを検出するための検査（描画はしない）。
游ゴシック（Office 同梱の YuGothR/YuGothB）で各段落の幅を測り、枠の幅で折り返して必要な高さを求め、
枠の高さ（表のセルは行の高さ）を超えるものを報告する。行送りは pptxgenjs の lineSpacingMultiple を反映する。
使い方: python check_fit.py deck.pptx
"""
import sys

from PIL import ImageFont
from pptx import Presentation
from pptx.util import Emu

FONT_DIR = "/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts/"
_fonts = {}


def font(size_pt, bold):
    key = (round(size_pt * 4), bold)
    if key not in _fonts:
        path = FONT_DIR + ("YuGothB.ttc" if bold else "YuGothR.ttc")
        _fonts[key] = ImageFont.truetype(path, int(round(size_pt * 4)))  # 1pt=4px で測る
    return _fonts[key]


def text_width_pt(text, size_pt, bold):
    if not text:
        return 0.0
    return font(size_pt, bold).getlength(text) / 4.0


def wrap_lines(text, width_pt, size_pt, bold):
    """日本語は文字単位、英数字は語単位でおおまかに折り返す"""
    lines = 0
    for raw in text.split("\n"):
        if raw == "":
            lines += 1
            continue
        cur = ""
        n = 1
        for ch in raw:
            if text_width_pt(cur + ch, size_pt, bold) > width_pt and cur:
                n += 1
                cur = ch
            else:
                cur += ch
        lines += n
    return lines


def para_props(p, default_size):
    size, bold = None, False
    for r in p.runs:
        if r.font.size:
            size = r.font.size.pt
        if r.font.bold:
            bold = True
    if size is None and p.font.size:
        size = p.font.size.pt
    return size or default_size, bold


def check_frame(tf, w_pt, h_pt, label, problems, margin_pt=0.0, default_size=18.0, lsm=1.15):
    need = 0.0
    for p in tf.paragraphs:
        text = "".join(r.text for r in p.runs)
        size, bold = para_props(p, default_size)
        indent = 14.0 if p.level == 0 and text and getattr(p, "_p", None) is not None and p._p.find(".//{*}buChar") is not None else 0.0
        if p.level > 0:
            indent = 24.0
        avail = max(10.0, w_pt - 2 * margin_pt - indent)
        n = wrap_lines(text, avail, size, bold) if text else 1
        ls = lsm
        lnsp = p._p.find(".//{*}lnSpc/{*}spcPct")
        if lnsp is not None:
            ls = int(lnsp.get("val")) / 100000.0
        spc_after = 0.0
        sa = p._p.find(".//{*}spcAft/{*}spcPts")
        if sa is not None:
            spc_after = int(sa.get("val")) / 100.0
        need += n * size * 1.2 * ls + spc_after
    avail_h = h_pt - 2 * margin_pt
    if need > avail_h * 1.02:
        problems.append((label, round(need, 1), round(avail_h, 1)))


def main(path):
    prs = Presentation(path)
    problems = []
    for si, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            w = Emu(sh.width).pt if sh.width else 0
            h = Emu(sh.height).pt if sh.height else 0
            if sh.has_text_frame and sh.text_frame.text.strip():
                check_frame(sh.text_frame, w, h, f"p{si} text '{sh.text_frame.text[:24]}'", problems)
            if sh.has_table:
                tbl = sh.table
                for ri, row in enumerate(tbl.rows):
                    rh = Emu(row.height).pt
                    for ci, cell in enumerate(row.cells):
                        cw = Emu(tbl.columns[ci].width).pt
                        if cell.text_frame.text.strip():
                            check_frame(cell.text_frame, cw, max(rh, 1), f"p{si} table r{ri}c{ci} '{cell.text_frame.text[:18]}'", problems, margin_pt=3.6, default_size=10, lsm=1.0)
    # 表は行の高さが自動で伸びるので、表全体が版面を超えるかを別に見る
    for si, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if sh.has_table:
                total = 0.0
                for ri, row in enumerate(sh.table.rows):
                    rowneed = Emu(row.height).pt
                    for ci, cell in enumerate(row.cells):
                        cw = Emu(sh.table.columns[ci].width).pt
                        size = 10.0
                        for p in cell.text_frame.paragraphs:
                            s, _ = para_props(p, 10.0)
                            size = s
                        n = sum(wrap_lines("".join(r.text for r in p.runs), max(10, cw - 7.2), size, False) for p in cell.text_frame.paragraphs)
                        rowneed = max(rowneed, n * size * 1.2 + 7.2)
                    total += rowneed
                bottom = Emu(sh.top).pt + total
                if bottom > 7.5 * 72 - 18:
                    problems.append((f"p{si} table bottom", round(bottom, 1), 7.5 * 72 - 18))
    table_cell = [p for p in problems if " table r" in p[0]]
    other = [p for p in problems if " table r" not in p[0]]
    for p in other:
        print("OVERFLOW", p)
    print(f"{len(other)} overflow(s) in text boxes / table extents; {len(table_cell)} table cells taller than their nominal row (rows grow automatically)")
    return len(other)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)
