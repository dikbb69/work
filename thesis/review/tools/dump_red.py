# dump paragraphs with red segments marked as 【赤:…】 ; math in {..}
import sys, os, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from ed import *
def marked(p):
    out=[]
    def run_red(el):
        rp=el.find(q('w:rPr')); 
        return is_red(rp)
    def math_red(om):
        for wr in om.iter(q('w:rPr')):
            if is_red(wr): return is_red(wr)
        return None
    def walk(parent):
        for ch in parent:
            if ch.tag==q('w:pPr'): continue
            if ch.tag==q('w:hyperlink'): walk(ch); continue
            if ch.tag==q('w:r'):
                t=''.join(x.text or '' for x in ch.findall(q('w:t')))
                if ch.find(q('w:footnoteReference')) is not None: t+='[^%s]'%ch.find(q('w:footnoteReference')).get(q('w:id'))
                if ch.find(q('w:drawing')) is not None: t+='〔図〕'
                if ch.find(q('w:tab')) is not None: t+='\t'
                if t: out.append((t,run_red(ch)))
            elif ch.tag==q('m:oMath'):
                out.append(('{'+math_text(ch)+'}',math_red(ch)))
            elif ch.tag==q('m:oMathPara'):
                out.append(('{{'+''.join(ch.itertext())+'}}',math_red(ch)))
    walk(p)
    s='';cur=None
    op={RED:'【',BLUE:'〖',GREEN:'《'}; cl={RED:'】',BLUE:'〗',GREEN:'》'}
    for t,r in out:
        if r!=cur:
            if cur: s+=cl[cur]
            if r: s+=op[r]
            cur=r
        s+=t
    if cur: s+=cl[cur]
    return s
def dump(path):
    t=load(path); body=t.getroot().find(q('w:body'))
    lines=[]
    for el in body:
        if el.tag==q('w:p'):
            pr=el.find(q('w:pPr')); st=pr.find(q('w:pStyle')).get(q('w:val')) if pr is not None and pr.find(q('w:pStyle')) is not None else ''
            lines.append('[%s] %s'%(st,marked(el)))
        elif el.tag==q('w:tbl'):
            for r in el.findall(q('w:tr')):
                lines.append('   | '+' | '.join(' / '.join(marked(p) for p in c.findall(q('w:p'))) for c in r.findall(q('w:tc'))))
    return lines
if __name__=='__main__':
    L=dump(sys.argv[1]); open(sys.argv[2],'w',encoding='utf-8').write('\n'.join(L)); print(len(L),'lines', sum('【' in l for l in L),'with red', sum('〖' in l for l in L),'with blue', sum('《' in l for l in L),'with green')
