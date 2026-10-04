#!/usr/bin/env python3
"""Slide HTML linter for the Slides artifact subset (deterministic checks only).
usage: python lint.py <slide.html> [...]   (exit 1 if any ERROR)
"""
import re, sys, os
from html.parser import HTMLParser

DECK = os.path.dirname(os.path.abspath(__file__))
STYLE = open(os.path.join(DECK, "STYLE.md"), encoding="utf-8").read()
BLOBS = set(re.findall(r"/_blob/[0-9a-f]{32}", STYLE))
TAGS = {"section", "h1", "h2", "h3", "p", "ul", "ol", "li", "br", "b", "i", "u", "a", "span", "div", "img",
        "table", "tr", "th", "td", "svg", "hr", "x-shape", "x-icon", "x-connector", "x-embed", "aside"}
SVG_INNER = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "g", "defs", "lineargradient",
             "radialgradient", "stop", "clippath", "mask", "pattern", "use", "marker", "title", "desc", "filter",
             "fegaussianblur", "feoffset", "feblend", "femerge", "femergenode", "feflood", "fecomposite"}
TEXT = {"h1", "h2", "h3", "p", "ul", "ol", "li", "td", "th", "table"}
BANNED = ["政策ウェッジ", "純市場", "政策層", "マーチャント層", "二層参入", "BTM", "FTM", "裾補正", "中立性",
          "フロンティア", "均衡面", "供給曲線v2", "価格過程v1", "価格過程v2", "必然", "break-even"]
ICONS = set("Activity Book Chart Chat Check CheckCircle Clock Cloud Code Database Globe GraduationCap Home Key Lightbulb Lightning Link Lock PaperPlane Play Search Settings Star ThumbsUp Tool Trust Users Verified Warning Wrench".split())
BAD_CSS = [r"(?<![-\w])margin\s*:", r"z-index", r"\d(em|rem|vw|vh)\b", r"var\(", r"float\s*:", r"grid-template-areas",
           r"grid-area", r"currentcolor", r"!important"]


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errs, self.warns = [], []
        self.stack, self.count, self.sections, self.in_svg = [], 0, [], 0
        self.top_level_text, self.aside_text, self.in_aside, self.last_top_child = "", "", False, None
        self.depth_div = 0
        self.max_div = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.in_svg:
            if tag not in SVG_INNER and tag != "svg":
                self.warns.append(f"svg child <{tag}> may be unsupported")
            if tag == "text":
                self.warns.append("svg <text> warned: put labels as <p> over the svg")
            if tag not in ("br",):
                self.stack.append(tag)
            if tag == "svg":
                self.in_svg += 1
            return
        self.count += 1
        if tag not in TAGS:
            self.errs.append(f"unsupported tag <{tag}>")
        if "class" in a:
            self.warns.append(f"class attribute on <{tag}> is ignored")
        st = a.get("style", "") or ""
        for pat in BAD_CSS:
            if re.search(pat, st):
                self.errs.append(f"forbidden css /{pat}/ on <{tag}>: {st[:90]}")
        for m in re.finditer(r"font-size\s*:\s*([\d.]+)\s*(px|pt)?", st):
            v = float(m.group(1)) * (4 / 3 if m.group(2) == "pt" else 1)
            if v < 24:
                self.errs.append(f"font-size {m.group(1)} < 24px on <{tag}>")
        if "%" in st and tag not in ("td", "th"):
            pinned = "position:absolute" in st.replace(" ", "")
            for m in re.finditer(r"([a-z-]+)\s*:\s*[^;]*?\d+%", st):
                prop = m.group(1)
                if prop in ("line-height", "border-radius", "background", "transform", "opacity", "left", "top", "right", "bottom") or pinned:
                    continue
                if prop in ("width", "height"):
                    self.warns.append(f"% {prop} on non-pinned <{tag}> (ok only along a flex row/column)")
                else:
                    self.warns.append(f"% in {prop} on <{tag}>")
        if tag in ("h1", "h2", "h3"):
            if "font-size" not in st or "font-weight" not in st:
                self.errs.append(f"<{tag}> must set font-size and font-weight explicitly")
        if "position:absolute" in st.replace(" ", ""):
            s2 = st.replace(" ", "")
            if tag not in ("x-connector",) and not (("left:" in s2 or "right:" in s2) and ("top:" in s2 or "bottom:" in s2)):
                self.errs.append(f"pinned <{tag}> needs left/right and top/bottom")
            if tag in TEXT and "width:" not in s2:
                self.errs.append(f"pinned text <{tag}> needs width")
        if tag == "img":
            src = a.get("src", "")
            if src not in BLOBS:
                self.errs.append(f"img src not in asset table: {src}")
            if "alt" not in a:
                self.errs.append("img without alt")
            if "object-fit" not in st:
                self.warns.append("img without object-fit")
        if tag == "x-icon" and a.get("name") not in ICONS:
            self.errs.append(f"unknown x-icon name {a.get('name')}")
        if tag == "section":
            self.sections.append(a.get("id"))
            if "background" not in st:
                self.errs.append("section without background")
        if tag == "div":
            self.depth_div += 1
            self.max_div = max(self.max_div, self.depth_div)
        if tag == "aside":
            self.in_aside = True
        if tag == "svg":
            self.in_svg += 1
            if "aria-label" not in a:
                self.warns.append("svg without aria-label")
        if len(self.stack) == 1:
            self.last_top_child = tag
        if tag not in ("br", "img", "hr", "x-icon", "x-shape", "x-connector"):
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            if tag == "svg":
                self.in_svg -= 1

    def handle_endtag(self, tag):
        if tag in ("br", "img", "hr", "x-icon", "x-shape", "x-connector"):
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errs.append(f"mismatched </{tag}> (open: {self.stack[-3:]})")
        if tag == "svg":
            self.in_svg -= 1
        if tag == "div":
            self.depth_div -= 1
        if tag == "aside":
            self.in_aside = False

    def handle_data(self, data):
        if not self.stack and data.strip():
            self.top_level_text += data.strip()
        if self.in_aside:
            self.aside_text += data


def lint(path):
    src = open(path, encoding="utf-8").read()
    p = P()
    p.feed(src)
    sid = os.path.splitext(os.path.basename(path))[0]
    if p.sections != [sid]:
        p.errs.append(f"must contain exactly one <section id=\"{sid}\"> (found {p.sections})")
    if not src.lstrip().startswith("<section"):
        p.errs.append("file must start with <section")
    if not src.rstrip().endswith("</section>"):
        p.errs.append("file must end with </section>")
    if p.top_level_text:
        p.errs.append("text outside <section>")
    if p.count > 200:
        p.errs.append(f"{p.count} elements > 200")
    if p.max_div > 15:
        p.errs.append(f"div nesting {p.max_div} > 15")
    if len(p.aside_text) > 4000:
        p.errs.append(f"aside {len(p.aside_text)} chars > 4000")
    if "<aside" in src and not re.search(r"</aside>\s*</section>\s*$", src):
        p.errs.append("<aside> must be the section's last child")
    if "<aside" not in src:
        p.warns.append("no speaker notes <aside>")
    body = re.sub(r"<aside>.*?</aside>", "", src, flags=re.S)
    for w in BANNED:
        if w in body:
            p.errs.append(f"banned term in slide text: {w}")
        elif w in p.aside_text:
            p.warns.append(f"banned term in notes: {w}")
    if "data:" in src:
        p.errs.append("data: URI")
    return p.errs, p.warns


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        e, w = lint(f)
        tag = "OK " if not e else "ERR"
        print(f"{tag} {os.path.basename(f)}  errors={len(e)} warnings={len(w)}")
        for x in e:
            print("   ERROR:", x)
        for x in w:
            print("   warn :", x)
        bad += bool(e)
    sys.exit(1 if bad else 0)
