# 査読: パイロット1 の閾値・参入確率・待機価値を、FY2023-26 部分標本の σ_ξ≈0.11 と 0.15 で再計算（関数はパイロットから複製）
import numpy as np
from scipy.stats import norm
A=0.81*8265.; F=5300+6900+4*365*1.2-12500; I0=4*6.8e4; FLOOR=4*2.3e4; T=20
PIK=np.interp(np.arange(201),[0,10,25,50,100,150,200],[8265,7144,5113,3416,961,198,12])
XG=np.linspace(np.log(0.02),np.log(80.),1201); TH=np.exp(XG)
def crf(r,n=T): return r*(1+r)**n/((1+r)**n-1)
def ts(I,r): return (I*crf(r)+F)/A
def P_(sd):
    e=np.concatenate([[-np.inf],(XG[:-1]+XG[1:])/2,[np.inf]]); c=norm.cdf((e[None,:]-(XG-0.5*sd**2)[:,None])/sd); return np.diff(c,axis=1)
def solve(s,r,g,H=80):
    It=np.maximum(FLOOR,I0*(1-g)**np.arange(H+1)); k=np.arange(1,T+1); pv=(A*TH-F)*np.sum((1+r)**-k)
    P=P_(s); W=np.maximum(pv-It[H],0); thr=np.full(H+1,np.nan)
    for t in range(H-1,-1,-1):
        npv=pv-It[t]; cont=(P@W)/(1+r); ex=(npv>=cont)&(npv>0); W=np.where(ex,npv,cont)
        if ex.any(): thr[t]=TH[np.argmax(ex)]
    return thr,W,It
rng=np.random.default_rng(7)
for s in (0.11,0.15,0.30):
  for g in (0.0,0.05):
    thr,W,It=solve(s,0.06,g)
    th0=1.17 if s==0.11 else 1.218
    i=np.argmin(abs(TH-th0)); i1=np.argmin(abs(TH-1.0))
    # 参入が開く確率（年次 GBM、2040 年度まで）
    n=20000; H=14; z=rng.standard_normal((n,H)); lt=np.log(th0)+np.cumsum(-0.5*s*s+s*z,axis=1); thp=np.exp(lt)
    sta=np.array([ts(It[t],0.06) for t in range(H+1)])
    od=np.zeros(n,bool); os_=np.zeros(n,bool); res={}
    for t in range(1,H+1):
        od|=thp[:,t-1]>=thr[t]; os_|=thp[:,t-1]>=sta[t]
        if 2026+t in (2035,2040): res[2026+t]=(od.mean(),os_.mean())
    print(f"σ={s:.2f} g={g:.2f}: θ̄0={thr[0]:.2f}（静学{ts(I0,.06):.2f}、倍率{thr[0]/ts(I0,.06):.2f}） W0(θ=1)={W[i1]:,.0f} W0(θ0={th0})={W[i]:,.0f}円/kW  "
          f"P(開く) 2035 動学{res[2035][0]:.2%}/静学{res[2035][1]:.2%}  2040 動学{res[2040][0]:.2%}/静学{res[2040][1]:.2%}")
