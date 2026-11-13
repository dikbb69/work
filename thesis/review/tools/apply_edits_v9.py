# -*- coding: utf-8 -*-
"""v9: v8 + the opening paragraph of the abstract rewritten from the author's draft (third round, green).
Run:  python3 -I apply_edits_v9.py   (runs apply_edits_v8.py first, then edits the same tree and saves again)
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ns = runpy.run_path(HERE + '/apply_edits_v8.py', run_name='__main__')
import ed

find, set_text, save, ptext = ns['find'], ed.set_text, ed.save, ed.ptext

p = find('再生可能エネルギー（再エネ）が増えると、電力の卸売価格が下限まで下がる時間が増え')
OLD = ptext(p)
NEW = ('再生可能エネルギー（再エネ）が増えると、電力の卸売価格（スポット価格）に下落圧力が働き、火力発電は売電の収入で固定費を賄えなくなる。'
       '電力系統の安定のために運転を続ける必要がある火力発電には、価格が燃料費を下回る時間において運転損失が生じる。'
       '現行の制度では、固定費や運転損失の補填は、容量市場や送配電事業者による支払いなど、スポット市場の外で行われる。'
       'それでも採算が合わない火力発電所は、廃止される。'
       '系統用蓄電池の参入を論じた先行研究は、発電設備を固定した短期のモデルで価格を作るので、こうした補填や火力の廃止を扱っていない。'
       'そのため、火力の収入不足（固定費の不足と運転損失）をスポット市場の中で回収するか外で補うかによって、'
       '価格の形と、価格差を収益源とする蓄電池の採算がどう変わるかは分かっていない。')
set_text(p, NEW, red=ed.GREEN)
print('abstract opening: %d -> %d characters' % (len(OLD), len(NEW)))
save(ns['tree'], ns['DST'] + '/word/document.xml')
print('saved v9')
