# 査読: パイロット2 (1) の修正。借入余力を θ=1（NPV が大きく負で、そもそも融資が付かない状態）ではなく
# 参入が開く点 θ* で評価する固定点。あわせて MM 命題（税なし）では WACC はレバレッジに依存しないことの確認、
# 法人税ありの簡易 APV（Miles-Ezzell 近似）で節税効果の大きさを示す。DoD を電池部分だけに掛けた場合の θ* も。
import numpy as np
from scipy.optimize import brentq
T=20; OM=5000.; WHEEL=6900.; DEC=0.05; PI0=8265.; CAP=0.81; CHG=1.2; KP=0.836*14972
def ann(r,n): return (1-(1+r)**-n)/r
def crf(r,n=T): return 1/ann(r,n)
def creq(I,r): return I*crf(r)+OM+DEC*I/(1+r)**T*crf(r)+WHEEL
def tstar(I,r,kp=KP): return (creq(I,r)-kp+4*365*CHG)/(CAP*PI0)
I4=4*6.8e4
def cfads(theta): return CAP*PI0*theta-4*365*CHG+KP-OM-WHEEL
print("θ*(6%%)=%.3f  θ*(8%%)=%.3f  θ*(10%%)=%.3f" % (tstar(I4,.06),tstar(I4,.08),tstar(I4,.10)))
print("\n(1') 固定点: θ = θ*(WACC(gear(CFADS(h·θ))))  （パイロットと同じ WACC 式・上限60%）")
for h,lab in ((1.0,"貸し手=中央"),(0.68,"貸し手=P10(0.68θ)")):
  for dscr,ten in ((1.40,12),(1.75,10)):
    for kd,ke in ((0.025,0.10),(0.035,0.12)):
      def g(th):
        D=min(max(cfads(h*th),0)/dscr*ann(kd,ten),0.60*I4); gear=D/I4; w=gear*kd+(1-gear)*ke
        return tstar(I4,w)-th, gear, w
      th=brentq(lambda x:g(x)[0],0.5,20); _,gear,w=g(th)
      print(f"  {lab:14s} DSCR{dscr} {ten}年 kd{kd:.3f} ke{ke:.2f}: 負債比率{gear:5.1%} WACC{w:6.2%} θ*={th:.2f}")
print("\n(MM) 税なしなら WACC=r_A（資産の資本コスト）でレバレッジに依存しない。θ* は r_A だけで決まる:")
for rA in (0.05,0.06,0.07,0.08,0.09,0.10): print(f"  r_A={rA:.0%}: θ*={tstar(I4,rA):.2f}")
print("\n(税) Miles-Ezzell 近似の税引後 WACC = r_A − τ·kd·L·(1+r_A)/(1+kd)（税引前 CF で割る近似ではなく、効果の大きさの目安）")
tau=0.3062
for rA in (0.07,0.09):
  for L in (0.0,0.3,0.6):
    for kd in (0.025,):
      w=rA-tau*kd*L*(1+rA)/(1+kd); print(f"  r_A={rA:.0%} L={L:.0%} kd={kd:.1%}: WACC_after-tax={w:.2%}（節税効果 {rA-w:.2%}pt）")
# DoD: 総額6.8万の内訳（FY2024: 電池4.1・PCS0.6・その他0.7・工事1.4、notes/20）。DoD は電池部分のみに掛ける
for lab,unit in (("全額×1.25（パイロット）",6.8e4/0.8),("電池部分のみ×1.25",6.8e4+4.1e4*0.25)):
  print(f"\nDoD80%: {lab}: 実効 {unit/1e4:.2f}万円/kWh → θ*(6%)={tstar(4*unit,.06):.2f}")
