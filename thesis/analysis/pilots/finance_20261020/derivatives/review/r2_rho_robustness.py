# 候補2の検証: 風力三分位で ρ が上がるのは構成効果（年度・月）や三分位内の風力分散の違いによるものではないか
import numpy as np, pandas as pd
rng = np.random.default_rng(1)
hp = pd.read_csv("/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv", parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize(); hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
inf = pd.DataFrame(index=P.index)
inf["fy"] = inf.index.year - (inf.index.month < 4).astype(int); inf["m"] = inf.index.month
SEAS = {"夏": [7,8,9], "冬": [12,1,2], "不需要期": [3,4,5,6,10,11]}
inf["wind"] = hp.groupby("day")["wind_pre"].sum().reindex(inf.index) / 1000
ETA, H = 0.85, 4
out = []
for per, fys in {"FY2023-25": [2023,2024,2025], "FY2016-19": [2016,2017,2018,2019]}.items():
    for s, ms in SEAS.items():
        idx = inf.m.isin(ms) & inf.fy.isin(fys)
        A = P[idx]; I = inf[idx].copy()
        o = np.argsort(A.mean().to_numpy()); dw, cw = o[-H:], o[:H]
        I["dis"] = A.iloc[:, dw].mean(1).values; I["chg"] = A.iloc[:, cw].mean(1).values
        q = I.wind.quantile([1/3, 2/3])
        I["ter"] = np.select([I.wind <= q.iloc[0], I.wind >= q.iloc[1]], ["小", "大"], "中")
        # 年度×月の平均を除いた脚（構成効果を除去）
        for c in ["dis", "chg"]:
            I[c+"_dm"] = I[c] - I.groupby(["fy", "m"])[c].transform("mean")
        I["week"] = (I.index - I.index.min()).days // 7
        def stats(df, dm):
            a, b = (df["dis_dm"], df["chg_dm"]) if dm else (df["dis"], df["chg"])
            X = H*(ETA*a - b)
            return np.corrcoef(a, b)[0, 1], X.std(ddof=1), a.std(ddof=1)
        for dm in [False, True]:
            lo, hi = I[I.ter == "小"], I[I.ter == "大"]
            r_lo, sx_lo, sd_lo = stats(lo, dm); r_hi, sx_hi, sd_hi = stats(hi, dm)
            # 週ブロック・ブートストラップ（三分位ごとに週を再抽出）
            bs_r, bs_s = [], []
            wl, wh = lo.week.unique(), hi.week.unique()
            for _ in range(1000):
                bl = pd.concat([lo[lo.week == w] for w in rng.choice(wl, len(wl))])
                bh = pd.concat([hi[hi.week == w] for w in rng.choice(wh, len(wh))])
                a1, b1 = stats(bl, dm)[:2]; a2, b2 = stats(bh, dm)[:2]
                bs_r.append(a2 - a1); bs_s.append(b2 - b1)
            out.append({"期間": per, "季節": s, "年度×月平均を除去": dm,
                        "ρ小": r_lo, "ρ大": r_hi, "Δρ": r_hi - r_lo,
                        "Δρ 95%CI": f"[{np.percentile(bs_r,2.5):.2f}, {np.percentile(bs_r,97.5):.2f}]",
                        "σX小": sx_lo, "σX大": sx_hi, "ΔσX 95%CI": f"[{np.percentile(bs_s,2.5):.1f}, {np.percentile(bs_s,97.5):.1f}]",
                        "σdis小": sd_lo, "σdis大": sd_hi,
                        "三分位内の風力sd 小/大": f"{lo.wind.std():.2f}/{hi.wind.std():.2f}",
                        "FY2025比率 小/大": f"{(lo.fy==2025).mean():.2f}/{(hi.fy==2025).mean():.2f}" if per=="FY2023-25" else ""})
res = pd.DataFrame(out)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(res.round(3).to_string(index=False))
res.to_csv("r2_rho_robustness.csv", index=False, encoding="utf-8-sig")
