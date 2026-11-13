# -*- coding: utf-8 -*-
"""Edits on the author's own file (thesis_v8draft_20261113_daiki.docx), 4th round (green):
  1. remove the middle case ("運転損失だけ補填") and the decomposition that depends on it
  2. remove cross-references that point back to definitions already given
Run:  python3 -I apply_daiki.py      (reads d_orig/, writes d_work/)
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed
from ed import *  # noqa

SP = os.path.dirname(HERE)
SRC, DST = SP + '/d_orig', SP + '/d_work'
FIGDIR = '/home/user/work/thesis/figures/hokkaido'
G = ed.GREEN
shutil.rmtree(DST, ignore_errors=True)
shutil.copytree(SRC, DST)
tree = load(DST + '/word/document.xml')
root = tree.getroot()
body = root.find(q('w:body'))
for e in list(root.iter(q('w:lastRenderedPageBreak'))):
    e.getparent().remove(e)
REG.harvest(body)
LOGR = []          # (kind, section, removed, replacement)


def style_of(p):
    pr = p.find(q('w:pPr'))
    st = pr.find(q('w:pStyle')) if pr is not None else None
    return st.get(q('w:val')) if st is not None else ''


def pars(styles=None):
    out = []
    for p in body.iter(q('w:p')):
        if styles is None or style_of(p) in styles:
            out.append(p)
    return out


TOC = ('11', '21', '31')


def find(prefix, nth=0):
    k = norm(prefix)
    hits = [p for p in pars() if style_of(p) not in TOC and norm(ptext(p)).startswith(k)]
    if len(hits) <= nth:
        raise KeyError('paragraph not found: %r (hits=%d)' % (prefix, len(hits)))
    return hits[nth]


def find_cap(prefix):
    k = norm(prefix)
    hits = [p for p in pars(('TableCaption', 'ImageCaption')) if norm(ptext(p)).startswith(k)]
    if len(hits) != 1:
        raise KeyError('caption not found or ambiguous: %r (hits=%d)' % (prefix, len(hits)))
    return hits[0]


def toc_find(prefix):
    k = norm(prefix)
    hits = [p for p in pars(TOC) if norm(ptext(p)).startswith(k)]
    return hits[0] if hits else None


def table_after(p):
    e = p.getnext()
    while e is not None and e.tag != q('w:tbl'):
        e = e.getnext()
    return e


def cut(sec, prefix, old, new='', must=True, kind=None):
    """pure deletion when new == ''; otherwise the replacement (plain text = green, «…» = black)"""
    try:
        p = find(prefix)
    except KeyError:
        if must:
            raise
        LOGR.append(('skip', sec, old, 'paragraph not found'))
        return None
    n = sub(p, old, new, red=G, must=must)
    LOGR.append((kind or ('rewrite' if re.sub(r'«[^»]*»', '', new) else 'cut') if n else 'skip', sec, old, new))
    return p


# ================================================================ 1. 「運転損失だけ補填」を削る
MC = 'middle'
cut('要旨', '主な結果は3点である。',
    '差の約8割は火力の運転損失の回収がスポット価格に上乗せされることによる日内の価格差が広がることによるものである。',
    'この差は、主に火力の運転損失の回収がスポット価格に上乗せされ、日内の価格差が広がることによる。', kind=MC)
cut('1.5', '第2に、電力価格の構造モデル、貯蔵設備の評価、',
    'これにより、回収方法による普及均衡点の差を、運転損失の回収による部分と固定費の不足の回収による部分に分けて示した（6.3節）。さらに、',
    'これにより、', kind=MC)
cut('2.4', 'このように、蓄電池の価値と参入を扱う研究は', '運転損失の回収と固定費の不足の回収に分けて', kind=MC)

# 4.8
cut('4.8', '上乗せ前の粗利 {Πy0} が必要粗利 {Ry} に届かない額は', '運転損失 {Ly}（表A.1）と、', '«運転損失と、»', kind=MC)
cut('4.8', '上乗せ前の粗利 {Πy0} が必要粗利 {Ry} に届かない額は',
    '。両者の差を分けるために、運転損失だけをスポットの外で補填する場合（以下、運転損失だけ補填）も計算する', kind=MC)
t43 = table_after(find_cap('表4.3　'))
for tr in list(t43.findall(q('w:tr'))):
    if ''.join(tr.find(q('w:tc')).itertext()).startswith('運転損失だけ補填'):
        LOGR.append((MC, '表4.3', '行：' + ' | '.join(''.join(tc.itertext()) for tc in tr.findall(q('w:tc'))), ''))
        t43.remove(tr)
pn = find('注）運転損失だけ補填の {μy} は、')
LOGR.append((MC, '表4.3', ptext(pn), ''))
remove(pn)
cut('4.8', '燃料費入札は、現行の制度のもとでの運用と同一であり、',
    'スポット回収と運転損失だけ補填の差を運転損失の回収の効果、運転損失だけ補填と燃料費入札の差を固定費の不足の回収の効果とみる。', kind=MC)

# 図6.1
cap61 = find_cap('図6.1　')
sub(cap61, '普及均衡点の経路と、回収方法による差の内訳（基準シナリオ）', '普及均衡点の経路（基準シナリオ）', red=G)
LOGR.append((MC, '図6.1', '題：普及均衡点の経路と、回収方法による差の内訳（基準シナリオ）', '普及均衡点の経路（基準シナリオ）'))
cut('図6.1 注', '注）普及均衡点は、長期契約なしで採算がとれる最大の量（式4.10）。', '運転損失だけ補填は、差を分けるための場合（4.8節）。', kind=MC)
cut('図6.1 注', '注）普及均衡点は、長期契約なしで採算がとれる最大の量（式4.10）。', '矢印は2040年の差の内訳（6.3節）。', kind=MC)

# 6.1: 上乗せの大半が運転損失の回収であることを、図6.2 の数値から言う（分解の代わり）
cut('6.1', 'この不足をスポット価格で回収する上乗せ {μy} は、2030〜35年には', 'ほど {μy} は上がる。',
    '«ほど {μy} は上がる。»回収する額が必要粗利の83.8億円を大きく上回るのは、マストランの損失によって上乗せ前の粗利が負になるからである。'
    'つまり、上乗せの大半は運転損失の回収にあてられる。', kind='add')
cut('図6.2 注', '注）マストランの損失は、3台が上乗せ前の価格のもとで出す時間ごとの損失で、',
    '損失で、運転損失（表A.1）とは集計の仕方が異なる。', '損失。', kind=MC)

# 6.3: 分解の段落を外し、次の段落とつなぐ
p63 = cut('6.3', '2040年の普及均衡点は、スポット回収で202.1万kW、',
          'である（表6.2）。差の69.4万kW の大半は、運転損失の回収による。運転損失だけを市場の外で補填すると、上乗せは2030年と2035年に0、'
          '2040年でも0.64円/kWh にとどまり、2040年の普及均衡点は145.6万kW と燃料費入札に近い。差のうち56.5万kW（約8割）が運転損失の回収、'
          '12.9万kW が固定費の不足の回収にあたる（図6.1）。',
          'であり、差は69.4万kW である（表6.2、図6.1）。', kind=MC)
p63b = find('現行の容量価格14,972円/kW では、設置量は')
rebuild(p63, segs_of(p63) + segs_of(p63b))
remove(p63b)

cut('6.6', '結論のうち、前提に左右されにくいのは回収方法の間の大小関係と差の内訳であり', 'と差の内訳', kind=MC)
cut('6.6', '結論のうち、前提に左右されにくいのは回収方法の間の大小関係',
    '下回ることはなく、需給と価格の前提を変えた21通りでは、差の半分以上が運転損失の回収による。', '下回ることはない。', kind=MC)
cut('7.1', '回収方法による差の約8割が運転損失の回収による（6.3節）のは、',
    '回収方法による差の約8割が運転損失の回収による（6.3節）のは、損失が大きいことに加えて、',
    '回収方法によって普及均衡点が変わるのは、運転損失が大きいことに加えて、', kind=MC)
cut('8.1', '2040年の普及均衡点は、スポット回収で約202万kW、燃料費入札で約133万kW と約69万kW 違い、',
    'と約69万kW 違い、差の約8割は運転損失の回収による。', 'と約69万kW 違う。', kind=MC)
cut('8.1', 'これらのうち、回収方法の間の大小関係と、',
    'と、差の半分以上が運転損失の回収によることは、確かめた前提の範囲で変わらない。', 'は、確かめた前提の範囲で変わらない。', kind=MC)

# 付録A: 運転損失の測り方の行
tA = table_after(find_cap('表A.1　'))
for tr in list(tA.findall(q('w:tr'))):
    if ''.join(tr.find(q('w:tc')).itertext()).startswith('運転損失の測り方'):
        LOGR.append((MC, '表A.1', '行：' + ' | '.join(''.join(tc.itertext()) for tc in tr.findall(q('w:tc'))), ''))
        tA.remove(tr)

# 付録B
cut('付録B.2', '基準シナリオでは、スポット回収と運転損失だけ補填のそれぞれで11,895点',
    '基準シナリオでは、スポット回収と運転損失だけ補填のそれぞれで11,895点（61の量×15年×13の容量価格）を計算し、そのうち上限に達した点の量を調べた。'
    '上限に達したのは合わせて9点で、再エネ低位・高位シナリオでは7点・11点であった。',
    '基準シナリオでは、スポット回収で11,895点（61の量×15年×13の容量価格）を計算し、そのうち上限に達した点の量を調べた。上限に達したのは5点であった。',
    kind=MC)
cut('付録B.2', '基準シナリオでは、スポット回収で11,895点', 'どれも375万kW 以上の量で、',
    '再エネ低位・高位シナリオで上限に達した点も含め、どれも375万kW 以上の量で、', kind=MC)
cut('付録B.3', '6.4節の電源別のシナリオなどは、より粗い格子で解いた。', '3つの場合とも', '2つの回収方法とも', kind=MC)

# 付録C
cut('付録C', '本付録では、結果がモデルの前提にどれだけ左右されるかを確かめる。', '3つの場合を', '2つの回収方法を', kind=MC)
tC = table_after(find_cap('表C.1　'))
gridC = tC.find(q('w:tblGrid')).findall(q('w:gridCol'))
assert len(gridC) == 5, len(gridC)
wmid = int(gridC[3].get(q('w:w')))
# 外した列の幅を、残る2つの数値の列に半分ずつ足す（見出しが折り返さないように）
for k in (2, 4):
    gridC[k].set(q('w:w'), str(int(gridC[k].get(q('w:w'))) + wmid // 2))
tC.find(q('w:tblGrid')).remove(gridC[3])
for tr in tC.findall(q('w:tr')):
    tcs = tr.findall(q('w:tc'))
    assert len(tcs) == 5, (len(tcs), ''.join(tr.itertext())[:30])
    w3 = tcs[3].find(q('w:tcPr')).find(q('w:tcW'))
    for k in (2, 4):
        wk = tcs[k].find(q('w:tcPr')).find(q('w:tcW'))
        if wk is not None and w3 is not None and wk.get(q('w:type')) == w3.get(q('w:type')):
            wk.set(q('w:w'), str(int(wk.get(q('w:w'))) + int(w3.get(q('w:w'))) // 2))
    tr.remove(tcs[3])
LOGR.append((MC, '表C.1', '列：運転損失だけ補填', ''))
cut('付録C', '表C.1 に載せていない前提も、同じく1つずつ変えて確かめた。',
    '3つの場合の大小関係（スポット回収≧運転損失だけ補填≧燃料費入札）は、確かめたすべての前提で変わらない。'
    'また、需給と価格の前提を変えた21通り（20通りと東北の価格の連動）でも、スポット回収と燃料費入札の差の半分以上（51〜100%）は運転損失の回収による。',
    'スポット回収の量が燃料費入札を下回らないことは、確かめたすべての前提で変わらない。', kind=MC)
cut('付録C', '表C.1 に載せていない前提も、同じく1つずつ変えて確かめた。', '表C.1 の5通りを', '«表C.1 の5通り»（東北の価格の連動を除く）«を»', kind='fix')
cut('付録C', '本州側の条件は、2040年だけを解いて確かめた。', '3つの場合とも量は', '2つの回収方法とも量は', kind=MC)
cut('付録C', '本州側の条件は、2040年だけを解いて確かめた。', '3つの場合の量は', '2つの回収方法の量は', kind=MC)

# 目次の保存表示（リンクの中の文字を直接直す。表4.3 の題は著者が直している）
for p in pars(TOC):
    for t in p.iter(q('w:t')):
        if t.text and '回収方法による差の内訳' in t.text:
            t.text = t.text.replace('普及均衡点の経路と、回収方法による差の内訳（基準シナリオ）', '普及均衡点の経路（基準シナリオ）')
        if t.text and 'と、差の分解に使う場合' in t.text:
            t.text = t.text.replace('と、差の分解に使う場合', '')

# ================================================================ 2. 表6.3 の注：4.11節から消えた感応度の説明を注に入れる
cut('表6.3 注', '注）正味の負担は北海道エリアの値。',
    '感応度の幅は、4.11節の6つの感応度（負担の集計の置き方）の最小と最大。',
    '感応度の幅は、負担の集計の置き方を変えた6通り（FIT/FIP の支援の範囲、泊3号の還付、{k} での換算、LTDA の容量への支払い）の最小と最大。',
    kind='fix')

# ================================================================ 3. 節への参照を削る
X = 'xref'
XR = [
    ('1.5', '第2に、電力価格の構造モデル、貯蔵設備の評価、', '（第2章）', ''),
    ('2.1', 'ただし、蓄電池の評価は価格の作り方に左右される。', '（4.3節）', ''),
    ('2.2', 'そのため、蓄電池の普及は実物投資としての参入の均衡の問題になる。', '（4.7節）', ''),
    ('2.3', 'ピークロード価格の理論（Boiteux, 1960）では', '（1.3節）', ''),
    ('2.3', 'Fraunholz et al.（2021）は欧州で', '（6.6節・付録C）', '«（付録C）»'),
    ('2.3', '火力には固定費のほかに、起動の費用や、', '（4.8節）', ''),
    ('3.2', '市場で支配的な事業者は、余剰の全量を限界費用で入札することを求められる', '（4.4節）', ''),
    ('3.2', '容量市場・LTDA', '（1.2節）', ''),
    ('3.2', '容量市場・LTDA', '（1.1節）', ''),
    ('3.2', '託送　蓄電池は送配電網の使用料', '（4.6節）', ''),
    ('3.3', 'データは、北電NW のエリア需給実績、', '（4.7節）', ''),
    ('4.2', '{Dh} は需要、', 'マストラン3台（3.1節）', '«マストラン3台»'),
    ('4.4', '③の必要粗利 {Ry} は、', '（1.4・3.2節）', ''),
    ('4.5', '④では、1年間運転しない号機は', '（4.8節）', ''),
    ('4.6', '{pτ,(j)(K)} はある日', '完全情報の上限（2.2節）', '«完全情報の上限»'),
    ('4.7', '{Ky*} は普及均衡点', '。1.4節）', '«）»'),
    ('4.7', '{Ky*} は普及均衡点', '98.8万kW（3.1節）', '«98.8万kW»'),
    ('4.8', '燃料費入札は、現行の制度', '（3.1・3.2節）', ''),
    ('4.8', '燃料費入札は、現行の制度', '（1.3・2.1節）', ''),
    ('4.11', '{Hy} は容量市場の調達量で、', '9割が還付される（3.2節）', '«9割が還付される»'),
    ('第5章', '本章では、Beran et al.（2019）にならい、', '（3.2節）', ''),
    ('5.1', '合わないのは、北海道の価格が東北より高い時間', '（3.2節）', ''),
    ('5.2', '火力のスポットの粗利は、モデルが実績の約8割にとどまる', '調整する（4.4節）', '«調整する»'),
    ('5.2', '火力のスポットの粗利は、モデルが実績の約8割にとどまる', '設定した（3.1節）', '«設定した»'),
    ('6.2', '上乗せは1日の値幅を広げ、値差収益を押し上げる。', '（4.3節）', ''),
    ('7.1', '普及均衡点の水準が前提に敏感なのは、', '（6.3節）', ''),
    ('7.3', '量の観点では、2040年の普及均衡点の約202万kW は', '（6.3節）', ''),
    ('7.3', '時期の観点では、', '（6.6節）', ''),
    ('7.4', 'LTDA は、2040年の量を変えずに、', '（6.3節）', ''),
    ('7.5', '第1に、参入の規則は、', '（6.6節）', ''),
    ('7.5', '第3に、本州の需給は', '（6.6節）', ''),
    ('7.5', '第3に、本州の需給は', '（4.3節）', ''),
    ('7.5', '第4に、需要と再エネ', '。6.6節）', '«）»'),
    ('7.5', 'このほか、炭素価格、需給調整市場の収入、', '約6万kW 減り（付録C）', '«約6万kW 減り»'),
]
for sec, prefix, old, new in XR:
    cut(sec, prefix, old, new, must=False, kind=X)
cut('7.5', '回収方法の間の大小関係は前提を変えても保たれるが', '影響が大きいとみられる順に述べる。',
    '«影響が大きいとみられる順に述べる。»以下の数値は、6.6節と付録C による。', kind='add')

# ================================================================ 4. 図の差し替え
rels = open(DST + '/word/_rels/document.xml.rels', encoding='utf-8').read()


def media_of(cap):
    """media file of the picture in the paragraph just before a caption"""
    e = cap.getprevious()
    while e is not None and not list(e.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')):
        e = e.getprevious()
    rid = list(e.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'))[0].get(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    m = re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or \
        re.search(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="%s"' % rid, rels)
    return m.group(1)


m61 = media_of(cap61)
m41 = media_of(find_cap('図4.1　'))
shutil.copy(FIGDIR + '/v2_entry_path_two_rules.png', DST + '/word/' + m61)
shutil.copy(SP + '/out/image1_two.png', DST + '/word/' + m41)
print('images replaced:', m61, m41)

# ================================================================ 5. 設定と保存
sp = DST + '/word/settings.xml'
sx = open(sp, encoding='utf-8').read()
if '<w:updateFields' not in sx:
    for tag in ('<w:hdrShapeDefaults', '<w:footnotePr', '<w:endnotePr', '<w:compat>', '<w:compat '):
        i = sx.find(tag)
        if i > 0:
            sx = sx[:i] + '<w:updateFields w:val="true"/>' + sx[i:]
            break
    open(sp, 'w', encoding='utf-8').write(sx)
    print('updateFields added')
save(tree, DST + '/word/document.xml')
with open(SP + '/out/daiki_edit_log.tsv', 'w', encoding='utf-8') as fh:
    for row in LOGR:
        fh.write('\t'.join(str(x).replace('\n', ' ') for x in row) + '\n')
import collections
print(collections.Counter(r[0] for r in LOGR))
for r in LOGR:
    if r[0] == 'skip':
        print('  skipped:', r[1], r[2][:40], '|', r[3][:30])
