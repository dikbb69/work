# -*- coding: utf-8 -*-
"""Editing helpers for the unpacked thesis docx. New/changed text is coloured red (FF0000).

Paragraph model: a paragraph is flattened into segments
  ('t', text, rPr_element_or_None, red)   plain text piece
  ('o', element, token)                   any other inline element kept as is (math, bookmarks, footnote refs, fields)
Markup used for new text:
  {linear}     inline math looked up in the registry by its linearised text (e.g. {μy}, {Xy*})
  «...»        text kept black (unchanged wording); everything else is red
  ‹...›        text changed in the second round (blue)
"""
import copy
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'
XML = 'http://www.w3.org/XML/1998/namespace'
NS = {'w': W, 'm': M, 'r': R, 'w14': W14}
RED = 'FF0000'
BLUE = '0070C0'


def _c(col):
    """normalise a colour argument: True -> RED, False/None -> None, str -> itself"""
    if col is True:
        return RED
    if not col:
        return None
    return col


def q(tag):
    p, t = tag.split(':')
    return '{%s}%s' % (NS[p], t)


BEFORE_COLOR = {q('w:' + n) for n in ('rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike',
                                      'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish', 'webHidden')}


def load(path):
    parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False, huge_tree=True)
    return etree.parse(path, parser)


def save(tree, path):
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)


# ---------------------------------------------------------------- run properties
def default_rpr(sz=None):
    r = etree.Element(q('w:rPr'))
    f = etree.SubElement(r, q('w:rFonts'))
    f.set(q('w:asciiTheme'), 'minorEastAsia')
    f.set(q('w:eastAsiaTheme'), 'minorEastAsia')
    f.set(q('w:hAnsiTheme'), 'minorEastAsia')
    f.set(q('w:hint'), 'eastAsia')
    if sz:
        s = etree.SubElement(r, q('w:sz'))
        s.set(q('w:val'), str(sz))
    return r


def set_color(rpr, red):
    red = _c(red)
    for c in rpr.findall(q('w:color')):
        rpr.remove(c)
    if not red:
        return rpr
    col = etree.Element(q('w:color'))
    col.set(q('w:val'), red)
    pos = len(rpr)
    for i, ch in enumerate(rpr):
        if ch.tag not in BEFORE_COLOR:
            pos = i
            break
    rpr.insert(pos, col)
    return rpr


def rpr_key(rpr, red):
    red = _c(red)
    if rpr is None:
        return ('', red)
    c = copy.deepcopy(rpr)
    for x in c.findall(q('w:color')):
        c.remove(x)
    return (etree.tostring(c), red)


def mk_run(text, rpr=None, red=True):
    r = etree.Element(q('w:r'))
    rp = copy.deepcopy(rpr) if rpr is not None else default_rpr()
    for x in rp.findall(q('w:webHidden')):
        rp.remove(x)
    set_color(rp, red)
    r.append(rp)
    t = etree.SubElement(r, q('w:t'))
    t.text = text
    t.set('{%s}space' % XML, 'preserve')
    return r


# ---------------------------------------------------------------- math
def math_text(om):
    return ''.join(om.itertext())


def color_math(om, red=True):
    om = copy.deepcopy(om)
    red = _c(red)
    if not red:
        return om
    for mr in list(om.iter(q('m:r'))):
        wr = mr.find(q('w:rPr'))
        if wr is None:
            wr = etree.Element(q('w:rPr'))
            f = etree.SubElement(wr, q('w:rFonts'))
            f.set(q('w:ascii'), 'Cambria Math')
            f.set(q('w:hAnsi'), 'Cambria Math')
            idx = 0
            if len(mr) and mr[0].tag == q('m:rPr'):
                idx = 1
            mr.insert(idx, wr)
        set_color(wr, red)
    for cp in om.iter(q('m:ctrlPr')):
        wr = cp.find(q('w:rPr'))
        if wr is None:
            wr = etree.SubElement(cp, q('w:rPr'))
            f = etree.SubElement(wr, q('w:rFonts'))
            f.set(q('w:ascii'), 'Cambria Math')
            f.set(q('w:hAnsi'), 'Cambria Math')
        set_color(wr, red)
    return om


def _mr(text, plain=False, scr=None):
    r = etree.Element(q('m:r'))
    if plain or scr:
        rp = etree.SubElement(r, q('m:rPr'))
        if scr:
            s = etree.SubElement(rp, q('m:scr'))
            s.set(q('m:val'), scr)
        if plain:
            s = etree.SubElement(rp, q('m:sty'))
            s.set(q('m:val'), 'p')
    wr = etree.SubElement(r, q('w:rPr'))
    f = etree.SubElement(wr, q('w:rFonts'))
    f.set(q('w:ascii'), 'Cambria Math')
    f.set(q('w:eastAsiaTheme'), 'minorEastAsia')
    f.set(q('w:hAnsi'), 'Cambria Math')
    t = etree.SubElement(r, q('m:t'))
    t.text = text
    return r


def _ctrl(parent):
    cp = etree.SubElement(parent, q('m:ctrlPr'))
    wr = etree.SubElement(cp, q('w:rPr'))
    f = etree.SubElement(wr, q('w:rFonts'))
    f.set(q('w:ascii'), 'Cambria Math')
    f.set(q('w:eastAsiaTheme'), 'minorEastAsia')
    f.set(q('w:hAnsi'), 'Cambria Math')


def m_omath(*children):
    om = etree.Element(q('m:oMath'))
    for c in children:
        om.append(c)
    return om


def m_sub(base, sub):
    e = etree.Element(q('m:sSub'))
    _ctrl(etree.SubElement(e, q('m:sSubPr')))
    b = etree.SubElement(e, q('m:e'))
    b.append(base)
    s = etree.SubElement(e, q('m:sub'))
    s.append(sub)
    return e


def m_subsup(base, sub, sup):
    e = etree.Element(q('m:sSubSup'))
    _ctrl(etree.SubElement(e, q('m:sSubSupPr')))
    b = etree.SubElement(e, q('m:e'))
    b.append(base)
    s = etree.SubElement(e, q('m:sub'))
    s.append(sub)
    s2 = etree.SubElement(e, q('m:sup'))
    s2.append(sup)
    return e


class Registry:
    def __init__(self):
        self.d = {}

    def harvest(self, root):
        for om in root.iter(q('m:oMath')):
            if om.getparent().tag == q('m:oMathPara'):
                continue
            k = math_text(om)
            self.d.setdefault(k, om)

    def add(self, key, om):
        self.d[key] = om

    def get(self, key, red=True):
        if key not in self.d:
            raise KeyError('math not in registry: %r' % key)
        return color_math(self.d[key], red)


REG = Registry()

# ---------------------------------------------------------------- segments
SIMPLE_RUN_CHILDREN = {q('w:rPr'), q('w:t'), q('w:lastRenderedPageBreak')}


def is_red(rpr):
    """colour of a run (RED / BLUE) or None"""
    if rpr is None:
        return None
    c = rpr.find(q('w:color'))
    v = c.get(q('w:val'), '').upper() if c is not None else ''
    return v if v in (RED, BLUE) else None


def obj_token(el):
    if el.tag == q('m:oMath'):
        return '{' + math_text(el) + '}'
    if el.tag == q('w:r'):
        fr = el.find(q('w:footnoteReference'))
        if fr is not None:
            return '[^%s]' % fr.get(q('w:id'))
        if el.find(q('w:drawing')) is not None:
            return '〔図〕'
        if el.find(q('w:tab')) is not None and el.find(q('w:t')) is None and el.find(q('w:fldChar')) is None:
            return '\t'
    return ''


def segs_of(p):
    out = []
    for ch in p:
        if ch.tag == q('w:pPr'):
            continue
        if ch.tag == q('w:r') and all(c.tag in SIMPLE_RUN_CHILDREN for c in ch):
            rpr = ch.find(q('w:rPr'))
            txt = ''.join(t.text or '' for t in ch.findall(q('w:t')))
            if txt:
                out.append(['t', txt, rpr, is_red(rpr)])
            continue
        out.append(['o', ch, obj_token(ch)])
    return out


def rebuild(p, segs):
    for ch in list(p):
        if ch.tag != q('w:pPr'):
            p.remove(ch)
    merged = []
    for s in segs:
        if s[0] == 't' and merged and merged[-1][0] == 't' and rpr_key(merged[-1][2], merged[-1][3]) == rpr_key(s[2], s[3]):
            merged[-1][1] += s[1]
        else:
            merged.append(list(s))
    for s in merged:
        if s[0] == 't':
            if s[1]:
                p.append(mk_run(s[1], s[2], s[3]))
        else:
            p.append(s[1])


PUA0 = 0xE000


def linear(segs):
    """linear string where every object is one private-use char; returns (string, map pos->(seg_idx, char_idx))"""
    s = []
    pos = []
    objs = {}
    n = 0
    for i, sg in enumerate(segs):
        if sg[0] == 't':
            for j, c in enumerate(sg[1]):
                s.append(c)
                pos.append((i, j))
        else:
            c = chr(PUA0 + n)
            n += 1
            objs[c] = sg[2]
            s.append(c)
            pos.append((i, 0))
    return ''.join(s), pos, objs


def visible(segs):
    return ''.join(sg[1] if sg[0] == 't' else sg[2] for sg in segs)


def ptext(p):
    return visible(segs_of(p))


TOKEN = re.compile(r'\{[^{}]*\}|\[\^\d+\]')


def pattern_for(old, objs):
    """regex for `old` (may contain {math} / [^n] tokens); ASCII spaces are optional everywhere"""
    parts = []
    i = 0
    for m in TOKEN.finditer(old):
        parts.append(('lit', old[i:m.start()]))
        parts.append(('tok', m.group(0)))
        i = m.end()
    parts.append(('lit', old[i:]))
    rx = []
    sp = '[  ]*'
    for kind, v in parts:
        if kind == 'lit':
            for c in v:
                if c in '  ':
                    continue
                rx.append(re.escape(c))
        else:
            cs = [c for c, tok in objs.items() if tok == v]
            if not cs:
                return None
            rx.append('[' + ''.join(cs) + ']')
    return re.compile(sp.join(rx))


def parse_markup(markup, like_rpr=None, red=True):
    """markup -> segments. «...» black, {..} math"""
    segs = []
    red = _c(red)
    for piece in re.split(r'(«[^»]*»|‹[^›]*›)', markup):
        if not piece:
            continue
        pr = red
        if piece.startswith('«') and piece.endswith('»'):
            piece = piece[1:-1]
            pr = None
        elif piece.startswith('‹') and piece.endswith('›'):
            piece = piece[1:-1]
            pr = BLUE
        i = 0
        for m in re.finditer(r'\{[^{}]*\}', piece):
            if m.start() > i:
                segs.append(['t', piece[i:m.start()], like_rpr, pr])
            key = m.group(0)[1:-1]
            segs.append(['o', REG.get(key, pr), m.group(0)])
            i = m.end()
        if i < len(piece):
            segs.append(['t', piece[i:], like_rpr, pr])
    return segs


def _slice(segs, pos, a, b):
    """split segs into before[0:a), mid[a:b), after[b:) by linear positions"""
    before, mid, after = [], [], []
    n = len(pos)
    first = {}
    for k, (si, ci) in enumerate(pos):
        first.setdefault(si, k)
    for si, sg in enumerate(segs):
        k0 = first.get(si)
        if k0 is None:           # zero-length (cannot happen: every seg has >=1 position)
            continue
        if sg[0] == 'o':
            (before if k0 < a else mid if k0 < b else after).append(sg)
            continue
        L = len(sg[1])
        k1 = k0 + L
        x0, x1 = max(k0, min(a, k1)), max(k0, min(b, k1))
        if x0 > k0:
            before.append(['t', sg[1][:x0 - k0], sg[2], sg[3]])
        if x1 > x0:
            mid.append(['t', sg[1][x0 - k0:x1 - k0], sg[2], sg[3]])
        if k1 > x1:
            after.append(['t', sg[1][x1 - k0:], sg[2], sg[3]])
    return before, mid, after


LOG = []


def sub(p, old, new, count=1, red=True, must=True, note=None):
    """replace `old` by `new` (markup) inside paragraph p. returns number of replacements"""
    done = 0
    start = 0
    while True:
        segs = segs_of(p)
        s, pos, objs = linear(segs)
        rx = pattern_for(old, objs)
        m = rx.search(s, start) if rx is not None else None
        if not m:
            break
        a, b = m.span()
        before, mid, after = _slice(segs, pos, a, b)
        like = None
        for sg in mid + before[::-1] + after:
            if sg[0] == 't':
                like = sg[2]
                break
        ins = parse_markup(new, like, red) if new else []
        rebuild(p, before + ins + after)
        done += 1
        start = a + sum(len(x[1]) if x[0] == 't' else 1 for x in ins)
        if count and done >= count:
            break
    if must and not done:
        raise ValueError('not found: %r in %r' % (old, ptext(p)[:80]))
    if done:
        LOG.append(('sub', note or '', old, new))
    return done


def sub_regex(p, regex, repl, red=True):
    """regex replace on plain-text parts (objects are opaque). repl: str or callable(match)->markup. returns count"""
    segs = segs_of(p)
    s, pos, objs = linear(segs)
    ms = list(re.finditer(regex, s))
    if not ms:
        return 0
    cur = segs
    for m in reversed(ms):
        s2, pos2, _ = linear(cur)
        a, b = m.span()
        before, mid, after = _slice(cur, pos2, a, b)
        like = None
        for sg in mid + before[::-1] + after:
            if sg[0] == 't':
                like = sg[2]
                break
        new = repl(m) if callable(repl) else m.expand(repl)
        cur = before + (parse_markup(new, like, red) if new else []) + after
    rebuild(p, cur)
    return len(ms)


def set_text(p, markup, red=True, like_rpr=None, keep_objs=()):
    """replace all content of p by markup (bookmarks listed in keep_objs are re-appended first)"""
    segs = segs_of(p)
    if like_rpr is None:
        for sg in segs:
            if sg[0] == 't':
                like_rpr = sg[2]
                break
    keep = [sg for sg in segs if sg[0] == 'o' and sg[1].tag in (q('w:bookmarkStart'), q('w:bookmarkEnd'))]
    starts = [k for k in keep if k[1].tag == q('w:bookmarkStart')]
    ends = [k for k in keep if k[1].tag == q('w:bookmarkEnd')]
    rebuild(p, starts + parse_markup(markup, like_rpr, red) + ends)
    LOG.append(('set', '', '', markup[:60]))


def strip_ids(el):
    for e in el.iter():
        for a in ('{%s}paraId' % W14, '{%s}textId' % W14, q('w:rsidR'), q('w:rsidRPr'), q('w:rsidRDefault'), q('w:rsidP'), q('w:rsidTr')):
            if a in e.attrib:
                del e.attrib[a]
    return el


def new_par(template, markup, red=True, style=None):
    """new paragraph with the pPr of `template` (optionally another style) and the given markup"""
    p = etree.Element(q('w:p'))
    ppr = template.find(q('w:pPr'))
    like = None
    for sg in segs_of(template):
        if sg[0] == 't':
            like = copy.deepcopy(sg[2])
            break
    if like is not None:
        set_color(like, False)
    if ppr is not None:
        ppr = copy.deepcopy(ppr)
        for x in ppr.findall(q('w:pageBreakBefore')):
            ppr.remove(x)
        if style:
            ppr.find(q('w:pStyle')).set(q('w:val'), style)
        p.append(ppr)
    rebuild(p, parse_markup(markup, like, red))
    return p


def set_style(p, style):
    p.find(q('w:pPr')).find(q('w:pStyle')).set(q('w:val'), style)


def norm(s):
    return re.sub(r'[  ]', '', s)


def sentences(s):
    out = re.findall(r'[^。]*。|[^。]+$', s)
    return [x for x in out if x]


def auto(markup, ref_text):
    """mark sentences that appear verbatim (ignoring spaces) in ref_text as black, using the reference wording"""
    refs = {}
    for sen in sentences(ref_text):
        refs.setdefault(norm(sen), sen)
    out = []
    for part in re.split(r'(‹[^›]*›)', markup):          # second-round (blue) parts are kept as they are
        if part.startswith('‹'):
            out.append(part)
            continue
        for sen in sentences(part):
            k = norm(sen)
            if k in refs:
                out.append('«' + refs[k].strip(' ') + '»')
            else:
                out.append(sen)
    return ''.join(out)


# ---------------------------------------------------------------- tables
def mk_cell(width, markup, jc='left', header=False, red=True, sz=20, bottom_border=False, math_para=None):
    tc = etree.Element(q('w:tc'))
    pr = etree.SubElement(tc, q('w:tcPr'))
    w = etree.SubElement(pr, q('w:tcW'))
    w.set(q('w:w'), str(width))
    w.set(q('w:type'), 'dxa')
    if header or bottom_border:
        bd = etree.SubElement(pr, q('w:tcBorders'))
        bt = etree.SubElement(bd, q('w:bottom'))
        for k, v in (('val', 'single'), ('sz', '6'), ('space', '0'), ('color', '000000')):
            bt.set(q('w:' + k), v)
    if header:
        va = etree.SubElement(pr, q('w:vAlign'))
        va.set(q('w:val'), 'center')
    p = etree.SubElement(tc, q('w:p'))
    ppr = etree.SubElement(p, q('w:pPr'))
    st = etree.SubElement(ppr, q('w:pStyle'))
    st.set(q('w:val'), 'Compact')
    sp = etree.SubElement(ppr, q('w:spacing'))
    sp.set(q('w:line'), '280')
    sp.set(q('w:lineRule'), 'exact')
    j = etree.SubElement(ppr, q('w:jc'))
    j.set(q('w:val'), 'center' if header else jc)
    rebuild(p, parse_markup(markup, default_rpr(sz), red))
    return tc


def mk_table(widths, header, rows, aligns, red=True):
    tbl = etree.Element(q('w:tbl'))
    pr = etree.SubElement(tbl, q('w:tblPr'))
    st = etree.SubElement(pr, q('w:tblStyle'))
    st.set(q('w:val'), 'Table')
    tw = etree.SubElement(pr, q('w:tblW'))
    tw.set(q('w:w'), '5000')
    tw.set(q('w:type'), 'pct')
    bd = etree.SubElement(pr, q('w:tblBorders'))
    for side, val in (('top', 'single'), ('left', 'nil'), ('bottom', 'single'), ('right', 'nil'), ('insideH', 'nil'), ('insideV', 'nil')):
        e = etree.SubElement(bd, q('w:' + side))
        e.set(q('w:val'), val)
        if val == 'single':
            e.set(q('w:sz'), '8')
            e.set(q('w:space'), '0')
            e.set(q('w:color'), '000000')
    lay = etree.SubElement(pr, q('w:tblLayout'))
    lay.set(q('w:type'), 'fixed')
    look = etree.SubElement(pr, q('w:tblLook'))
    for k, v in (('val', '0020'), ('firstRow', '1'), ('lastRow', '0'), ('firstColumn', '0'), ('lastColumn', '0'), ('noHBand', '0'), ('noVBand', '0')):
        look.set(q('w:' + k), v)
    grid = etree.SubElement(tbl, q('w:tblGrid'))
    for w in widths:
        g = etree.SubElement(grid, q('w:gridCol'))
        g.set(q('w:w'), str(w))
    tr = etree.SubElement(tbl, q('w:tr'))
    trpr = etree.SubElement(tr, q('w:trPr'))
    etree.SubElement(trpr, q('w:cantSplit'))
    etree.SubElement(trpr, q('w:tblHeader'))
    for w, h in zip(widths, header):
        tr.append(mk_cell(w, h, header=True, red=red))
    for row in rows:
        tr = etree.SubElement(tbl, q('w:tr'))
        trpr = etree.SubElement(tr, q('w:trPr'))
        etree.SubElement(trpr, q('w:cantSplit'))
        for w, c, a in zip(widths, row, aligns):
            tr.append(mk_cell(w, c, jc=a, red=red))
    return tbl


def cell(tbl, r, c):
    return tbl.findall(q('w:tr'))[r].findall(q('w:tc'))[c]


def cell_p(tbl, r, c, k=0):
    return cell(tbl, r, c).findall(q('w:p'))[k]


def clone_row(tbl, r):
    rows = tbl.findall(q('w:tr'))
    new = strip_ids(copy.deepcopy(rows[r]))
    rows[r].addnext(new)
    return new


def insert_after(ref, *els):
    cur = ref
    for e in els:
        cur.addnext(e)
        cur = e
    return cur


def insert_before(ref, *els):
    for e in els:
        ref.addprevious(e)


def remove(el):
    el.getparent().remove(el)
