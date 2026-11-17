# -*- coding: utf-8 -*-
"""Build the workbook: the advisor's comments and the proposed responses.
usage: python3 build_response_xlsx.py <transcription.md> <out.xlsx>
"""
import os
import re
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from responses import FIGS, QUESTIONS, R, TERMS  # noqa: E402

MD, OUT = sys.argv[1], sys.argv[2]
md = open(MD, encoding='utf-8').read()

# ------------------------------------------------------------------ parse the transcription
sec2 = md[md.index('## 2. '):md.index('## 3. ')]
sec3 = md[md.index('## 3. '):md.index('## 4. ')]
sec4 = md[md.index('## 4. '):md.index('## 5. ')]


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


rows = []
for line in sec2.split('\n'):
    if re.match(r'^\| G\d ', line):
        i, note, conf = cells(line)
        rows.append(dict(id=i, target='表紙（論文の全体について）', note=note, kind='説', conf=conf))
for line in sec3.split('\n'):
    if re.match(r'^\| (A\d|\d-\d+b?) ', line):
        i, target, note, kind, conf = cells(line)
        rows.append(dict(id=i, target=target, note=note, kind=kind, conf=conf))
assert len(rows) == 92, len(rows)

# notes on uncertain readings (section 4 of the transcription)
NOTE = {}
for line in sec4.split('\n'):
    if not re.match(r'^\| (A\d|\d-\d+b?) ', line):
        continue
    c = cells(line)
    if len(c) == 4 and c[0] in ('1-6', '1-7', '1-8'):
        NOTE[c[0]] = '推定の箇所：%s／別の読み：%s／対応への影響：%s' % (c[1], c[2], c[3])
    elif len(c) == 4:
        NOTE[c[0]] = '分からない点：%s／採った解釈：%s／別の解釈：%s' % (c[1], c[2], c[3])
    elif len(c) == 3:
        NOTE[c[0]] = '分からない点：%s／採った解釈：%s' % (c[1], c[2])
assert len(NOTE) == 17, len(NOTE)

KIND = {'主': '主目的の強調', '説': '説明の追加・書き直し', '説・図表': '説明の追加・書き直し', '図表': '図表の追加・変更',
        '図表・説': '図表の追加・変更', '語': '用語・表記', '問': '先生からの質問', '評': '評価'}
CONF = {'○': '確か', '△読': '読みに推定あり', '△対': '対象・意図に解釈あり'}


def section(i):
    if i.startswith('G'):
        return '全体'
    if i.startswith('A'):
        return '要旨'
    ch, n = i.split('-')
    n = int(re.sub(r'\D', '', n))
    table = {
        '1': [(4, '1.1節'), (8, '1.2節'), (11, '1.3節'), (14, '1.4節'), (16, '1.5節')],
        '2': [(3, '2.1節'), (6, '2.2節'), (9, '2.3節'), (14, '2.4節')],
        '3': [(2, '3.1節'), (10, '3.2節'), (14, '3.3節')],
        '4': [(1, '4.1節'), (4, '4.2節'), (5, '4.3節'), (6, '4.6節'), (7, '4.7節（表4.2）'), (8, '4.9節'), (15, '4.11節')],
        '5': [(1, '第5章の冒頭'), (5, '5.1節')],
        '6': [(5, '第6章の冒頭'), (8, '6.1節'), (12, '6.2節'), (13, '6.3節'), (15, '6.4節'), (16, '6.5節')],
        '7': [(2, '7.1節'), (3, '7.5節')],
        '8': [(1, '8.2節')],
    }[ch]
    for upto, name in table:
        if n <= upto:
            return name
    raise KeyError(i)


def page(i):
    if i.startswith('G'):
        return 1
    if i.startswith('A'):
        return 2
    ch, n = i.split('-')
    n = int(re.sub(r'\D', '', n))
    table = {
        '1': [(6, 6), (9, 7), (14, 8), (16, 9)],
        '2': [(4, 10), (9, 11), (14, 12)],
        '3': [(8, 13), (14, 14)],
        '4': [(1, 15), (3, 16), (5, 18), (6, 20), (7, 21), (8, 22), (15, 24)],
        '5': [(5, 25)],
        '6': [(7, 27), (9, 28), (10, 29), (12, 30), (13, 31), (15, 32), (16, 33)],
        '7': [(2, 36), (3, 38)],
        '8': [(1, 41)],
    }[ch]
    for upto, pg in table:
        if n <= upto:
            return pg
    raise KeyError(i)


# ------------------------------------------------------------------ styles
FONT = '游ゴシック'
f_base = Font(name=FONT, size=10)
f_bold = Font(name=FONT, size=10, bold=True)
f_head = Font(name=FONT, size=10, bold=True, color='FFFFFF')
f_title = Font(name=FONT, size=14, bold=True)
f_note = Font(name=FONT, size=9, color='595959')
fill_head = PatternFill('solid', fgColor='1F3864')
fill_in = PatternFill('solid', fgColor='FFF2CC')          # cells the user edits
fill_star = PatternFill('solid', fgColor='FCE4D6')
fill_dbl = PatternFill('solid', fgColor='DDEBF7')
fill_sub = PatternFill('solid', fgColor='F2F2F2')
thin = Side(style='thin', color='BFBFBF')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap_top = Alignment(wrap_text=True, vertical='top')
center_top = Alignment(wrap_text=True, vertical='top', horizontal='center')
center = Alignment(wrap_text=True, vertical='center', horizontal='center')


def put(ws, r, c, v, font=f_base, align=wrap_top, fill=None, bd=True):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    cell.alignment = align
    if fill is not None:
        cell.fill = fill
    if bd:
        cell.border = border
    return cell


def header(ws, r, names, widths):
    for c, (n, w) in enumerate(zip(names, widths), start=1):
        put(ws, r, c, n, font=f_head, align=center, fill=fill_head)
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.row_dimensions[r].height = 34


wb = Workbook()

# ================================================================== 1. 指摘と対応案
ws = wb.active
ws.title = '指摘と対応案'
MAIN = ws.title
put(ws, 1, 1, '指導教員の指摘と対応案（初稿、2026年11月15日返却）', font=f_title, align=Alignment(vertical='center'), bd=False)
put(ws, 2, 1, '使い方：黄色の列（状態、メモ）を書き換えて進み具合を管理する。件数はシート「集計」に自動で出る。'
              'ID は書き起こし（20261116_advisor_comments_on_first_draft.md）と同じ。ページは PDF の通し番号で、本文のページ番号は通し番号−5。',
    font=f_note, align=Alignment(vertical='center'), bd=False)
HEAD = ['No.', 'ID', '印', '章・節', 'PDF\nページ', '本文\nページ', '対象の箇所（提出版の本文）', '先生の書き込み', '種類', '読みの確度',
        '読み・解釈の注', '対応方針', '対応案（文案・作業の内容）', '修正が及ぶ箇所', '作業の種類', '作業量', '優先度', '追加の計算',
        '先生への\n確認', '状態', 'メモ']
WIDTH = [5, 6, 4, 11, 6, 6, 40, 46, 14, 11, 34, 32, 78, 20, 14, 6, 6, 13, 8, 9, 24]
HR = 4
header(ws, HR, HEAD, WIDTH)
COL = {n.replace('\n', ''): i for i, n in enumerate(HEAD, start=1)}
r = HR
for k, row in enumerate(rows, start=1):
    r += 1
    i = row['id']
    resp = R[i]
    mark = '☆' if row['note'].startswith('☆') else '◎' if row['note'].startswith('◎') else ''
    note = re.sub(r'^[☆◎]\s*', '', row['note'])
    pg = page(i)
    vals = [k, i, mark, section(i), pg, (pg - 5) if pg > 5 else '−', row['target'], note, KIND[row['kind']], CONF[row['conf']],
            NOTE.get(i, ''), resp[0], resp[1], resp[2], resp[3], resp[4], resp[5], resp[6], resp[7], '未着手', '']
    for c, v in enumerate(vals, start=1):
        al = center_top if c in (1, 2, 3, 5, 6, 16, 17, 19, 20) else wrap_top
        cell = put(ws, r, c, v, align=al)
    if mark == '☆':
        for c in (2, 3):
            ws.cell(row=r, column=c).fill = fill_star
            ws.cell(row=r, column=c).font = f_bold
    elif mark == '◎':
        for c in (2, 3):
            ws.cell(row=r, column=c).fill = fill_dbl
            ws.cell(row=r, column=c).font = f_bold
    for c in (COL['状態'], COL['メモ']):
        ws.cell(row=r, column=c).fill = fill_in
LAST = r
ws.freeze_panes = ws.cell(row=HR + 1, column=5)
ws.auto_filter.ref = 'A%d:%s%d' % (HR, get_column_letter(len(HEAD)), LAST)
dv = DataValidation(type='list', formula1='"未着手,作業中,済,保留"', allow_blank=False)
dv.error = '未着手・作業中・済・保留から選ぶ'
ws.add_data_validation(dv)
SC = get_column_letter(COL['状態'])
dv.add('%s%d:%s%d' % (SC, HR + 1, SC, LAST))
# rows that are done turn grey
ws.conditional_formatting.add('A%d:%s%d' % (HR + 1, get_column_letter(len(HEAD)), LAST),
                              FormulaRule(formula=['$%s%d="済"' % (SC, HR + 1)], font=Font(name=FONT, size=10, color='A6A6A6')))
ws.sheet_view.zoomScale = 90
ws.page_setup.orientation = 'landscape'
ws.page_setup.paperSize = ws.PAPERSIZE_A3
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_title_rows = '%d:%d' % (HR, HR)


def rng(name):
    c = get_column_letter(COL[name])
    return "'%s'!$%s$%d:$%s$%d" % (MAIN, c, HR + 1, c, LAST)


# ================================================================== 2. 集計
ws2 = wb.create_sheet('集計')
put(ws2, 1, 1, '集計（シート「指摘と対応案」の状態の列から自動で数える）', font=f_title, align=Alignment(vertical='center'), bd=False)
STATES = ['未着手', '作業中', '済', '保留']


def block(top, title, key, values):
    put(ws2, top, 1, title, font=f_bold, bd=False)
    for c, n in enumerate([key] + STATES + ['計'], start=1):
        put(ws2, top + 1, c, n, font=f_head, align=center, fill=fill_head)
    rr = top + 1
    for v in values:
        rr += 1
        put(ws2, rr, 1, v)
        for c, st in enumerate(STATES, start=2):
            put(ws2, rr, c, '=COUNTIFS(%s,$A%d,%s,%s$%d)' % (rng(key), rr, rng('状態'), get_column_letter(c), top + 1), align=center_top)
        put(ws2, rr, 6, '=SUM(B%d:E%d)' % (rr, rr), align=center_top, font=f_bold)
    rr += 1
    put(ws2, rr, 1, '計', font=f_bold, fill=fill_sub)
    for c in range(2, 7):
        L = get_column_letter(c)
        put(ws2, rr, c, '=SUM(%s%d:%s%d)' % (L, top + 2, L, rr - 1), align=center_top, font=f_bold, fill=fill_sub)
    return rr + 2


nxt = block(3, '種類ごと', '種類', ['主目的の強調', '説明の追加・書き直し', '図表の追加・変更', '用語・表記', '先生からの質問', '評価'])
nxt = block(nxt, '優先度ごと', '優先度', ['高', '中', '低', '−'])
nxt = block(nxt, '作業量ごと', '作業量', ['大', '中', '小', '−'])
put(ws2, nxt, 1, '印の付いた指摘', font=f_bold, bd=False)
for c, n in enumerate(['印'] + STATES + ['計'], start=1):
    put(ws2, nxt + 1, c, n, font=f_head, align=center, fill=fill_head)
rr = nxt + 1
for v in ['☆', '◎']:
    rr += 1
    put(ws2, rr, 1, v, align=center_top)
    for c, st in enumerate(STATES, start=2):
        put(ws2, rr, c, '=COUNTIFS(%s,$A%d,%s,%s$%d)' % (rng('印'), rr, rng('状態'), get_column_letter(c), nxt + 1), align=center_top)
    put(ws2, rr, 6, '=SUM(B%d:E%d)' % (rr, rr), align=center_top, font=f_bold)
legend_top = rr + 3
put(ws2, legend_top, 1, '凡例', font=f_bold, bd=False)
LEG = [
    ('印', '☆と◎は先生が付けた印。☆が最も重く、◎がそれに次ぐとみられる。'),
    ('読みの確度', '「読みに推定あり」は字の一部が推定。「対象・意図に解釈あり」は、何を指すか・何を求めているかに解釈が入っている。採った解釈は「読み・解釈の注」の列にある。'),
    ('優先度', '高：☆・◎の指摘、主目的に関わる指摘、「わかりません」と書かれた箇所。中：説明の追加、質問への回答。低：用語と表記の修正。'),
    ('作業量', '小：語句や1〜2文の修正。中：段落の書き直し、表1点の追加。大：図の作成や、複数の節にまたがる書き直し。'),
    ('追加の計算', '「要」は、データの集計・作図・モデルの実行が要るもの。'),
    ('先生への確認', 'Q1〜Q4 は、シート「先生への確認事項」の番号。「任意」は、聞かなくても進められるもの。'),
    ('状態・メモ', '黄色の列。状態は 未着手／作業中／済／保留 から選ぶ。「済」にすると、その行が灰色になる。'),
    ('文案', '対応案の中の文案は、提出版の本文と数値をもとにした案。本文に入れるときに前後とのつながりを整える。'),
]
for j, (a, b) in enumerate(LEG, start=legend_top + 1):
    put(ws2, j, 1, a, font=f_bold)
    put(ws2, j, 2, b)
    ws2.merge_cells(start_row=j, start_column=2, end_row=j, end_column=6)
    ws2.row_dimensions[j].height = 32
ws2.column_dimensions['A'].width = 24
for c in 'BCDEF':
    ws2.column_dimensions[c].width = 12

# ================================================================== 3. 用語の置き換え
ws3 = wb.create_sheet('用語の置き換え')
put(ws3, 1, 1, '用語と表記の置き換え', font=f_title, align=Alignment(vertical='center'), bd=False)
put(ws3, 2, 1, '回数は、提出版の Word の本文（第1〜8章）と付録を機械的に数えた値。目次・参考文献は含まない。', font=f_note, align=Alignment(vertical='center'), bd=False)
header(ws3, 4, ['No.', 'いまの語', '置き換え', '対応する指摘', '本文の\n回数', '付録の\n回数', '備考', '状態'], [5, 30, 44, 22, 8, 8, 52, 9])
for k, (a, b, c_, n1, n2, memo) in enumerate(TERMS, start=1):
    rr = 4 + k
    for c, v in enumerate([k, a, b, c_, n1 if n1 is not None else '−', n2 if n2 is not None else '−', memo, '未着手'], start=1):
        put(ws3, rr, c, v, align=center_top if c in (1, 5, 6, 8) else wrap_top)
    ws3.cell(row=rr, column=8).fill = fill_in
dv3 = DataValidation(type='list', formula1='"未着手,作業中,済,保留"', allow_blank=False)
ws3.add_data_validation(dv3)
dv3.add('H5:H%d' % (4 + len(TERMS)))
ws3.freeze_panes = 'A5'

# ================================================================== 4. 追加する図表
ws4 = wb.create_sheet('追加する図表')
put(ws4, 1, 1, '追加・変更する図表', font=f_title, align=Alignment(vertical='center'), bd=False)
put(ws4, 2, 1, '図表の番号は仮のもの。置く場所（本文か付録か）は、先生への確認（Q1・Q3）の結果で変わりうる。', font=f_note, align=Alignment(vertical='center'), bd=False)
header(ws4, 4, ['No.', '種類', '内容', '置く場所', '対応する指摘', 'もとになるデータ', '追加の計算', '先生への\n確認', '状態'], [5, 14, 58, 14, 20, 40, 18, 8, 9])
for k, row in enumerate(FIGS, start=1):
    rr = 4 + k
    for c, v in enumerate(list(row) + ['未着手'], start=1):
        put(ws4, rr, c, v, align=center_top if c in (1, 8, 9) else wrap_top)
    ws4.cell(row=rr, column=9).fill = fill_in
dv4 = DataValidation(type='list', formula1='"未着手,作業中,済,保留"', allow_blank=False)
ws4.add_data_validation(dv4)
dv4.add('I5:I%d' % (4 + len(FIGS)))
ws4.freeze_panes = 'A5'

# ================================================================== 5. 先生への確認事項
ws5 = wb.create_sheet('先生への確認事項')
put(ws5, 1, 1, '先生への確認事項', font=f_title, align=Alignment(vertical='center'), bd=False)
put(ws5, 2, 1, 'Q1〜Q4 は修正の前に聞くもの。「任意」は、聞かなくても対応案のとおりに進められるもの。', font=f_note, align=Alignment(vertical='center'), bd=False)
header(ws5, 4, ['番号', '項目', '聞く内容（こちらの案を添えて、可否で答えてもらう）', '関係する指摘', '回答', '状態'], [7, 26, 80, 26, 40, 9])
for k, (a, b, c_, d) in enumerate(QUESTIONS, start=1):
    rr = 4 + k
    for c, v in enumerate([a, b, c_, d, '', '未確認'], start=1):
        put(ws5, rr, c, v, align=center_top if c in (1, 6) else wrap_top)
    ws5.cell(row=rr, column=5).fill = fill_in
    ws5.cell(row=rr, column=6).fill = fill_in
dv5 = DataValidation(type='list', formula1='"未確認,質問済,回答あり,聞かない"', allow_blank=False)
ws5.add_data_validation(dv5)
dv5.add('F5:F%d' % (4 + len(QUESTIONS)))
ws5.freeze_panes = 'A5'

for w in (ws, ws2, ws3, ws4, ws5):
    w.sheet_view.showGridLines = False
    w.row_dimensions[1].height = 26
    w.row_dimensions[2].height = 18

wb.save(OUT)
print('saved', OUT, 'rows', len(rows), 'last row', LAST)
