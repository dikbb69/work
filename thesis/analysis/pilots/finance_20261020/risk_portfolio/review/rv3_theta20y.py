# A2: 20年年金加重で PF ∝ θ^β の参入条件 avg(θ^β)·tail ≥ θ*_1（=3.55 標準）を評価（rv2 の近似を厳密化）
import numpy as np
rng = np.random.default_rng(11); d = 1 / 1.06; T = 20; M = 60000; sig = 0.267
W = sum(d ** t for t in range(1, T + 1))
for nm, beta, tail in [("×1.25 & β=1.42（二重計上）", 1.42, 1.25), ("β=1.42 のみ", 1.42, 1.0), ("β=1.18 のみ", 1.18, 1.0), ("×1.25 のみ（原稿）", 1.0, 1.25)]:
    for phi in [0.5, 0.9]:
        for med in [1.0, 1.57]:
            se = sig * np.sqrt(1 - phi ** 2); mu = np.log(med); x = np.full(M, np.log(1.57)); acc = np.zeros(M)
            for t in range(1, T + 1):
                x = mu + phi * (x - mu) + rng.normal(0, se, M); acc += d ** t * np.exp(beta * x)
            avg = acc / W * tail
            p1 = (np.exp(beta * rng.normal(mu, sig, M)) * tail >= 3.55).mean()
            print(f"{nm:<22} φ={phi} 長期中央値={med}: P(20年)={(avg >= 3.55).mean():.4f}  P(単年・定常)={p1:.4f}")
