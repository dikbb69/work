# 候補1: Bachelier の当てはまりを季節×年度で確認（年度プールでの一致が「ほぼイントリンジック」による自明な一致かを見る）
# 候補3: 主成分スコア回帰の t 値を Newey-West(7) で再計算
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import norm
hp = pd.read_csv("/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv", parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize(); hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
hp["solar_pre"] = hp["solar"].fillna(0) + hp["solar_curt"].fillna(0)
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]; days = P.index; arr = P.to_numpy()
wk = pd.Series(days.dayofweek >= 5, index=days)
SE = {7:"夏",8:"夏",9:"夏",12:"冬",1:"冬",2:"冬"}
def win(v):
    o = np.argsort(v, kind="stable"); return o[-4:], o[:4]
rows = []
for i, d in enumerate(days):
    p = arr[i]; dis, chg = win(p)
    hist = [j for j in range(max(0, i-29), i) if wk.iloc[j] == wk.iloc[i]]
    if len(hist) < 5: continue
    dc, cc = win(arr[hist].mean(0))
    rows.append({"day": d, "pf": max(0, 4*(0.85*p[dis].mean()-p[chg].mean())), "xc": 4*(0.85*p[dc].mean()-p[cc].mean())})
bt = pd.DataFrame(rows).set_index("day")
bt["fy"] = bt.index.year - (bt.index.month < 4).astype(int); bt["season"] = bt.index.month.map(lambda m: SE.get(m, "不需要期"))
def bach(x):
    mu, sd = x.mean(), x.std(); z = mu/sd
    return mu*norm.cdf(z) + sd*norm.pdf(z)
r = []
for (fy, s), g in bt[bt.fy.between(2016, 2025)].groupby(["fy", "season"]):
    real = g.xc.clip(lower=0).mean(); b = bach(g.xc)
    r.append({"FY": fy, "季節": s, "μ/σ": g.xc.mean()/g.xc.std(), "Bachelier": b, "実現E[max]": real,
              "誤差%": 100*(b/real-1), "時間価値の実現(II)/E[max]": (real-g.xc.mean())/real,
              "Bachelier時間価値/実現時間価値": (b-g.xc.mean())/(real-g.xc.mean()) if real > g.xc.mean() else np.nan})
R = pd.DataFrame(r)
pd.set_option("display.width", 250)
print("季節×年度の Bachelier 誤差（FY2023-25）")
print(R[R.FY >= 2023].round(3).to_string(index=False))
print("\n全40セル（FY2016-25×4…ここでは3季節）での |誤差| の分布: ", R["誤差%"].abs().describe().round(1).to_dict())
print("時間価値の比（Bachelier/実現）の分布: ", R["Bachelier時間価値/実現時間価値"].describe().round(2).to_dict())

# ---- 候補3: PC スコア回帰の NW t 値 ----
info = pd.DataFrame(index=P.index)
info["fy"] = info.index.year - (info.index.month < 4).astype(int)
info["season"] = info.index.month.map(lambda m: SE.get(m, "不需要期"))
g2 = hp.groupby("day")
for c, src in [("wind", "wind_pre"), ("solar", "solar_pre"), ("demand", "demand")]:
    info[c] = g2[src].sum().reindex(info.index) / 1000
keep = info.fy.isin([2023, 2024, 2025]); Pk, ik = P[keep], info[keep]
out = []
for s in ["夏", "冬", "不需要期"]:
    idx = ik.season == s; A = Pk[idx].to_numpy(); I = ik[idx]; grp = I.fy.to_numpy()
    M = np.zeros_like(A)
    for fy in [2023, 2024, 2025]: M[grp == fy] = A[grp == fy].mean(0)
    D = A - M; U, S, Vt = np.linalg.svd(D, full_matrices=False); Z = D @ Vt.T
    X = pd.concat([I[["wind", "solar", "demand"]], pd.get_dummies(I.fy, prefix="fy", drop_first=True).astype(float)], axis=1)
    X = sm.add_constant(X)
    for k in range(2):
        z = Z[:, k] * (np.sign(Vt[k].sum()) if Vt[k].sum() != 0 else 1)
        m3 = sm.OLS(z, X).fit(cov_type="HC3"); mn = sm.OLS(z, X).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
        out.append({"季節": s, "PC": k+1, "t_wind HC3": m3.tvalues["wind"], "t_wind NW7": mn.tvalues["wind"],
                    "t_solar HC3": m3.tvalues["solar"], "t_solar NW7": mn.tvalues["solar"],
                    "スコアの1次自己相関": pd.Series(z).autocorr(1)})
print("\n主成分スコア回帰: HC3 と NW7 の t 値")
print(pd.DataFrame(out).round(2).to_string(index=False))
