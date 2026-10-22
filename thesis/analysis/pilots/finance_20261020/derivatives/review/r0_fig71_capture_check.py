# 図7.1（analysis/19_hokkaido_extra_figs.py §1）と同じ計算で年度別 c/PF を出す（読み取りのみ、図は書かない）
import numpy as np, pandas as pd
hp = pd.read_csv("/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv", parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize(); hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
days = P.index; wkP = pd.Series(days.dayofweek >= 5, index=days)
arr = P.to_numpy(); ETA = 0.85
def win(v):
    o = np.argsort(v, kind="stable"); return o[-4:], o[:4]
rows = []
for i, d in enumerate(days):
    p = arr[i]; dis, chg = win(p)
    rec = {"day": d, "pf": max(0.0, (p[dis].sum()*ETA - p[chg].sum()))}
    hist = [j for j in range(max(0, i-29), i) if wkP.iloc[j] == wkP.iloc[i]]
    if len(hist) >= 5:
        dc, cc = win(arr[hist].mean(0)); rec["c"] = p[dc].sum()*ETA - p[cc].sum()
    rows.append(rec)
bt = pd.DataFrame(rows); bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
ann = bt[bt.fy.between(2016, 2025)].groupby("fy")[["pf", "c"]].sum()
ann["c/pf"] = ann["c"]/ann["pf"]
print(ann.round(3).to_string())
