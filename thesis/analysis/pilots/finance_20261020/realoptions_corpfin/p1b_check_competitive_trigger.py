#!/usr/bin/env python3
"""検算: Dixit-Pindyck 第8章型の競争産業均衡（収入 P = Y·D(K)、Y は対数正規のマルチンゲール、参入で P は P̄ に反射）。
反射壁 P̄ で参入した企業の収入現在価値 E∫e^{-rt}P_t dt が投資額 I に等しい（＝正しく計算した NPV=0）のは
P̄ = β/(β−1)·r·I のときであることをモンテカルロで確かめる。静学（P が続くと置く）なら P = r·I で参入する。"""
import numpy as np
rng = np.random.default_rng(1)
r, sig, dt, Tm, n = 0.06, 0.30, 1 / 52, 150, 20000
beta = 0.5 + np.sqrt(0.25 + 2 * r / sig ** 2)
target = (beta - 1) / (beta * r)          # E∫e^{-rt} Y_t/M_t dt の理論値（P̄=1 当たり）
steps = int(Tm / dt)
lnY = np.zeros(n); M = np.zeros(n); pv = np.zeros(n)
for k in range(steps):
    t = k * dt
    pv += np.exp(-r * t) * np.exp(lnY - M) * dt
    lnY += -0.5 * sig ** 2 * dt + sig * np.sqrt(dt) * rng.standard_normal(n)
    M = np.maximum(M, lnY)
print(f"β={beta:.3f}, β/(β−1)={beta/(beta-1):.3f}")
print(f"反射壁つき収入の PV（P̄=1当たり）: MC={pv.mean():.3f}（SE {pv.std()/np.sqrt(n):.3f}）, 理論 (β−1)/(βr)={target:.3f}, 反射なし 1/r={1/r:.3f}")
print(f"⇒ 正しく計算した NPV=0 となる参入閾値 P̄/(rI) = {1/(r*pv.mean()):.3f}（静学なら 1.000）")
