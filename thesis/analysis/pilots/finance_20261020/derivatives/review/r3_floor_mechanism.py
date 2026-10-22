# 候補3・4の論点の検証: 「下限で打ち切られると風力の平行シフトがスプレッドを広げる」(8.2/10.1/11.3) は成り立つか
# (i) 実績価格（FY2023-25）を一様に δ 円下げ、0.01円で打ち切ったときの完全予見粗利 PF(δ)
# (ii) 比例シフト（θ型）  (iii) 実績の価格-純需要関係（分位ビンの中央値）で下端の傾き（崖）を確認
import numpy as np, pandas as pd
hp = pd.read_csv("/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv", parse_dates=["ts"])
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
hp = hp[hp.fy.isin([2023, 2024, 2025])].copy()
hp["day"] = hp["ts"].dt.normalize(); hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]; A = P.to_numpy()
def pf(A):
    s = np.sort(A, 1); return np.maximum(0, 4*(0.85*s[:, -4:].mean(1) - s[:, :4].mean(1))).mean()*365
print("(i) 一様な下方シフト δ（円/kWh）→ PF（円/kW-年、0.01円打ち切りあり／なし）")
for d in [0, 1, 2, 3, 5, 8]:
    print(f"  δ={d}: 打ち切り {pf(np.maximum(A-d, 0.01)):8.0f}  打ち切りなし {pf(A-d):8.0f}")
print("(ii) 比例縮小 p×k（θ型）")
for k in [1.0, 0.8, 0.6]:
    print(f"  k={k}: {pf(np.maximum(A*k, 0.01)):8.0f}")
# (iii) 価格-純需要（制御前）関係
hp["net"] = hp["demand"] - hp["solar"].fillna(0) - hp["solar_curt"].fillna(0) - hp["wind"].fillna(0) - hp["wind_curt"].fillna(0) - hp["nuclear"].fillna(0)
h = hp.dropna(subset=["p_hokkaido", "net"]).copy()
h["bin"] = pd.qcut(h["net"], 20, labels=False)
g = h.groupby("bin").agg(net=("net", "median"), p_med=("p_hokkaido", "median"), floor_share=("p_hokkaido", lambda x: (x <= 0.011).mean()))
g["傾き(円/kWh per 100MW)"] = g["p_med"].diff() / g["net"].diff() * 100
print("(iii) 純需要20分位ビンの価格中央値（FY2023-25、北海道）")
print(g.round(3).to_string())
