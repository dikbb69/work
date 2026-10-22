# analysis/17_wind_battery_deepdive.py §2 の表7.3と同じ計算（読み取りのみ）
import numpy as np, pandas as pd
p = pd.read_csv("/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv", parse_dates=["ts"])
p = p[(p["ts"] >= "2023-04-01") & (p["ts"] < "2026-04-01")].dropna(subset=["p_hokkaido"]).copy()
p["day"] = p["ts"].dt.normalize(); p["hour"] = p["ts"].dt.hour
p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
cnt = p.groupby("day")["hour"].count(); p = p[p["day"].isin(cnt[cnt == 24].index)]
P = p.pivot(index="day", columns="hour", values="p_hokkaido")
srt = np.sort(P.to_numpy(), axis=1)
d0 = pd.DataFrame(index=P.index)
d0["TB4h"] = srt[:, -4:].mean(1) - srt[:, :4].mean(1)
d0["PF"] = np.maximum(0, srt[:, -4:].sum(1)*0.85 - srt[:, :4].sum(1))
d0["wind"] = p.groupby("day")["wind_pre"].sum(); d0["m"] = d0.index.month
for name, ms in [("夏", [7,8,9]), ("冬", [12,1,2]), ("不需要期", [3,4,5,6,10,11])]:
    d = d0[d0.m.isin(ms)].copy(); q = d.wind.quantile([1/3, 2/3])
    d["ter"] = np.select([d.wind <= q.iloc[0], d.wind >= q.iloc[1]], ["小", "大"], "中")
    print(name, d.groupby("ter")[["TB4h", "PF"]].mean().round(2).to_dict(), d.groupby("ter").size().to_dict())
print("panel last ts:", p.ts.max())
