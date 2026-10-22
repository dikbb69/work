# B1 の追加検証: サブサンプル内で季節除去（r2 と同じ）したうえで、水準と k か月変化の HE を比較
# A2 の追加: ×1.25 と β=1.42 を重ねた θ*=2.09 を 20年基準で評価した場合の確率
import glob, os
import numpy as np, pandas as pd
REPO = "/Users/matsuba/work/thesis"; OUT = os.path.dirname(os.path.abspath(__file__))
frames = []
for f in sorted(glob.glob(os.path.join(REPO, "data/raw/jepx/spot_summary_*.csv"))):
    x = pd.read_csv(f, encoding="cp932").iloc[:, [0, 1, 6, 8]]; x.columns = ["date", "slot", "hkd", "tky"]; frames.append(x)
j = pd.concat(frames, ignore_index=True); j["date"] = pd.to_datetime(j["date"]); j["hour"] = (j["slot"] - 1) // 2
for c in ["hkd", "tky"]: j[c] = pd.to_numeric(j[c], errors="coerce")
hr = j.groupby(["date", "hour"])[["hkd", "tky"]].mean().reset_index(); hr = hr[hr.date <= "2026-06-30"]
Mh = hr.pivot(index="date", columns="hour", values="hkd"); Mt = hr.pivot(index="date", columns="hour", values="tky")
Mh, Mt = Mh[Mh.count(axis=1) == 24], Mt[Mt.count(axis=1) == 24]
days = Mh.index.intersection(Mt.index); Mh, Mt = Mh.loc[days], Mt.loc[days]
sh = np.sort(Mh.to_numpy(), axis=1)
D = pd.DataFrame({"X": np.maximum(0.85 * sh[:, -4:].sum(1) - sh[:, :4].sum(1), 0), "base_t": Mt.mean(axis=1).to_numpy()}, index=days)
D["peak_t"] = np.where(days.dayofweek < 5, Mt.loc[:, 8:19].mean(axis=1), np.nan); D["ym"] = days.to_period("M")
Mo = D.groupby("ym").agg(X=("X", "sum"), base_t=("base_t", "mean"), peak_t=("peak_t", "mean"), n=("X", "size"))
Mo = Mo[Mo.n >= 25]; Mo["cal"] = Mo.index.month; Mo["fy"] = Mo.index.year - (Mo.index.month < 4)
rows = []
for nm, sub in {"全期間": Mo, "FY2023-26": Mo[Mo.fy >= 2023], "除FY2020-22": Mo[~Mo.fy.isin([2020, 2021, 2022])]}.items():
    sub = sub.copy()
    for c in ["X", "base_t", "peak_t"]:
        sub[c + "_ds"] = sub[c] - sub.groupby("cal")[c].transform("mean")
    for k in [0, 1, 3, 6]:
        for inst in ["base_t", "peak_t"]:
            if k == 0:
                x, f = sub["X_ds"], sub[inst + "_ds"]
            else:
                lag = sub[["X_ds", inst + "_ds"]].copy(); lag.index = lag.index + k
                x = sub["X_ds"] - lag["X_ds"].reindex(sub.index); f = sub[inst + "_ds"] - lag[inst + "_ds"].reindex(sub.index)
            z = pd.DataFrame({"x": x, "f": f}).dropna()
            h = np.cov(z.x, z.f)[0, 1] / z.f.var(); he = 1 - (z.x - h * z.f).var() / z.x.var()
            rows.append(dict(sample=nm, k=k, inst=inst, n=len(z), h=round(h, 1), HE=round(he, 3)))
r = pd.DataFrame(rows); print(r.pivot_table(index=["sample", "k"], columns="inst", values="HE").to_string())
r.to_csv(os.path.join(OUT, "rv2_hedge_within.csv"), index=False)

# A2: 二重計上ケース（×1.25 かつ β=1.42 → θ*=2.09）を 20年基準で
rng = np.random.default_rng(11); d = 1 / 1.06; T = 20; M = 40000; sig = 0.267
for ts_nm, ts in [("θ*=2.09（×1.25 & β=1.42、二重計上）", 2.09), ("θ*=2.44（β=1.42 のみ）", 2.44), ("θ*=2.84（×1.25 のみ、原稿）", 2.84)]:
    for phi in [0.5, 0.9]:
        se = sig * np.sqrt(1 - phi ** 2); mu = np.log(1.57); x = np.full(M, mu); acc = np.zeros(M)
        for t in range(1, T + 1):
            x = mu + phi * (x - mu) + rng.normal(0, se, M); acc += d ** t * np.exp(x)
        avg = acc / sum(d ** t for t in range(1, T + 1))
        print(f"{ts_nm} φ={phi} 中央値1.57 定着: P(20年加重平均θ ≥ θ*)={(avg >= ts).mean():.4f}")
