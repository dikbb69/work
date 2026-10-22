# 査読: 恒久成分 σ_ξ の頑健性（標本期間・モデル仕様）。リポジトリは読むだけ。
import os, warnings
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings("ignore")
PROC = "/Users/matsuba/work/thesis/data/processed"
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"], usecols=["ts", "p_system", "p_hokkaido", "fy"])
hp["m"] = hp["ts"].dt.to_period("M").dt.to_timestamp()
mon = hp.groupby("m")[["p_system", "p_hokkaido", "fy"]].mean()
mon["fy"] = mon["fy"].round().astype(int); mon["cal"] = mon.index.month
base = mon[mon["fy"].between(2023, 2025)].groupby("cal")[["p_system"]].mean()
mon["proxy"] = mon["p_system"] / mon["cal"].map(base["p_system"])
mon = mon[mon.index >= "2016-04-01"]
print("months:", len(mon), mon.index.min().date(), mon.index.max().date())
def fit(y, irregular=False, label=""):
    mod = sm.tsa.UnobservedComponents(y, level=("local level" if irregular else "random walk"), autoregressive=1)
    res = mod.fit(disp=False, maxiter=3000)
    p = dict(zip(mod.param_names, res.params))
    out = {"label": label, "n": len(y), "sigma_xi_ann": np.sqrt(p["sigma2.level"]*12), "phi_m": p["ar.L1"],
           "sigma_chi_m": np.sqrt(p["sigma2.ar"]), "llf": res.llf, "xi_end": np.exp(res.filtered_state[0][-1])}
    if irregular: out["sigma_irr"] = np.sqrt(p["sigma2.irregular"])
    return out
rows = []
y = np.log(mon["proxy"].to_numpy())
rows.append(fit(y, False, "全期間 RW+AR1（パイロットと同じ）"))
rows.append(fit(y, True, "全期間 RW+AR1+観測誤差"))
for a, b in (("2016-04-01", "2021-03-01"), ("2023-04-01", "2026-06-01"), ("2016-04-01", "2020-12-01")):
    s = mon.loc[a:b]
    rows.append(fit(np.log(s["proxy"].to_numpy()), False, f"{a[:7]}〜{b[:7]}"))
df = pd.DataFrame(rows); print(df.round(3).to_string(index=False))
# 年次: 年度平均の対数の AR(1) と単位根の検定（標本10、参考）
fy = hp[hp["fy"] <= 2025].groupby("fy")["p_system"].mean(); ly = np.log(fy / fy.loc[2023:2025].mean())
print("\n年度 log θ 代理:", ly.round(2).to_dict())
from statsmodels.tsa.stattools import adfuller
print("ADF(月次, 定数):", adfuller(y, regression="c", autolag="AIC")[:2])
# 年次ランダムウォーク分散比（月次 log の12か月差の分散 / (12×1か月差の分散)）
d1 = np.diff(y); d12 = y[12:] - y[:-12]; d24 = y[24:] - y[:-24]; d36 = y[36:] - y[:-36]
print("分散比 VR(12)=%.2f VR(24)=%.2f VR(36)=%.2f" % (d12.var()/(12*d1.var()), d24.var()/(24*d1.var()), d36.var()/(36*d1.var())))
print("12か月差の SD(年率σの粗い上限)=%.3f, 24か月差SD/√2=%.3f, 36か月差SD/√3=%.3f" % (d12.std(), d24.std()/np.sqrt(2), d36.std()/np.sqrt(3)))
