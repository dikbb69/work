import re, sys, subprocess, os
DECK="/private/tmp/claude-501/-Users-matsuba-work-thesis/d0c864fb-2c7b-407c-809f-7a4dc1efcfaf/scratchpad/deck"
OUT="/private/tmp/claude-501/-Users-matsuba-work-thesis/d0c864fb-2c7b-407c-809f-7a4dc1efcfaf/scratchpad/qa"
FIG="/Users/matsuba/work/thesis/figures/"
style=open(DECK+"/STYLE.md",encoding="utf-8").read()
m={}
for row in re.finditer(r"\|\s*([^|]+?\.png)\s*\|\s*(/_blob/[0-9a-f]{32})", style):
    fn=row.group(1).strip()
    p=FIG+("" if "/" in fn else "hokkaido/")+fn
    if not os.path.exists(p): p=FIG+fn
    m[row.group(2)]="file://"+p
for sid in sys.argv[1:]:
    src=open(f"{DECK}/project/slides/{sid}.html",encoding="utf-8").read()
    for k,v in m.items(): src=src.replace(k,v)
    html=f"""<!doctype html><html><head><meta charset=utf-8>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
<style>*{{margin:0;box-sizing:border-box}} body{{width:1920px;height:1080px;overflow:hidden}} section{{width:1920px;height:1080px;position:relative;overflow:hidden}} aside{{display:none}} ul,ol{{padding-left:1.2em}}</style></head><body>{src}
<script>document.fonts.ready.then(()=>{{const s=document.querySelector('section');let mx=0;s.querySelectorAll('p,img,table,h2,h3,li').forEach(e=>{{if(e.tagName=='ASIDE')return;const r=e.getBoundingClientRect();if(r.bottom>mx&&getComputedStyle(e).position!='absolute')mx=r.bottom}});document.title='MAXBOTTOM='+Math.round(mx)}})</script></body></html>"""
    f=f"{OUT}/{sid}.html"; open(f,"w",encoding="utf-8").write(html)
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","--headless=new","--disable-gpu","--allow-file-access-from-files","--virtual-time-budget=8000",f"--screenshot={OUT}/{sid}.png","--window-size=1920,1080","--hide-scrollbars","file://"+f],capture_output=True,timeout=90)
    r=subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","--headless=new","--disable-gpu","--allow-file-access-from-files","--virtual-time-budget=8000","--window-size=1920,1080","--dump-dom","file://"+f],capture_output=True,text=True,timeout=90)
    t=re.search(r"<title>(.*?)</title>",r.stdout)
    print(sid, t.group(1) if t else "no title")
