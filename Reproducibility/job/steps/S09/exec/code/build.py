import math
import pandas as pd
from engine.results import path, out

R = lambda p: pd.read_csv(path(p))

R("S02:outputs/dq_log.csv").to_csv(out("t1_dq_log.csv"), index=False)
R("S03:outputs/kpi_overall.csv")[["metric", "value", "unit"]].to_csv(out("t2_kpis.csv"), index=False)

# T3
rows = []
for dim, f, col in [("lane", "S04:outputs/late_by_lane.csv", "lane"),
                    ("seller", "S04:outputs/late_by_seller.csv", "seller_id"),
                    ("category", "S04:outputs/late_by_category.csv", "category")]:
    d = R(f)
    d = d[d["ranked"] == 1]
    for lst, rc in [("worst", "rank_worst"), ("best", "rank_best")]:
        s = d[d[rc] <= 10].sort_values(rc)
        assert len(s) == 10, (dim, lst, len(s))
        for _, r in s.iterrows():
            rows.append([dim, lst, int(r[rc]), r[col], int(r["delivered"]), int(r["late"]), r["late_rate_pct"]])
pd.DataFrame(rows, columns=["dimension", "list", "rank", "name", "delivered", "late", "late_rate_pct"]).to_csv(out("t3_top_bottom.csv"), index=False)

# T4
ls = R("S05:outputs/late_split.csv")
ss = R("S05:outputs/split_summary.csv")
g = ls.groupby("split_class").agg(mean_handling_days=("handling_days", "mean"), mean_transit_days=("transit_days", "mean")).round(4).reset_index()
t4 = ss.merge(g, on="split_class", how="left")
t4.to_csv(out("t4_split.csv"), index=False)

# T5
rows = []
for dim, f, col in [("seller", "S06:outputs/pareto_sellers.csv", "seller_id"), ("lane", "S06:outputs/pareto_lanes.csv", "lane")]:
    d = R(f).sort_values("rank").head(20)
    for _, r in d.iterrows():
        rows.append([dim, int(r["rank"]), r[col], int(r["late"]), int(r["delivered"]),
                     round(100 * r["late"] / r["delivered"], 4), r["cum_late_share_pct"]])
pd.DataFrame(rows, columns=["dimension", "rank", "name", "late", "delivered", "late_rate_pct", "cum_late_share_pct"]).to_csv(out("t5_pareto.csv"), index=False)

rb = R("S07:outputs/review_bands.csv")
rb.to_csv(out("t6_reviews.csv"), index=False)

m = R("S03:outputs/monthly.csv")
m = m[m["shown"] == 1].sort_values("month")[["month", "on_time_rate_pct", "late_share_pct"]]
m.to_csv(out("c1_monthly.csv"), index=False)

st = R("S04:outputs/late_by_state.csv").rename(columns={"late_rate_pct": "late_share_pct"})
st = st.sort_values(["late_share_pct", "customer_state"], ascending=[False, True])[["customer_state", "late_share_pct"]]
st.to_csv(out("c2_state_late.csv"), index=False)

R("S05:outputs/split_by_band.csv").to_csv(out("c3_split_by_band.csv"), index=False)

ps = R("S06:outputs/pareto_sellers.csv").sort_values("rank").reset_index(drop=True)
n = len(ps)
rows = []
for p in range(1, 101):
    k = min(n, math.ceil(p * n / 100))
    rows.append([p, ps.loc[k - 1, "cum_late_share_pct"]])
pd.DataFrame(rows, columns=["pct_of_sellers", "cum_late_share_pct"]).to_csv(out("c4_pareto_curve.csv"), index=False)

c5 = rb[rb["scheme"] == "cut3"].copy()
order = {"on_time": 0, "late_1_3": 1, "late_gt3": 2}
c5["o"] = c5["band"].map(order)
c5 = c5.sort_values("o").rename(columns={"band": "delay_band"})[["delay_band", "n_orders", "mean_score"]]
c5.to_csv(out("c5_review_bands.csv"), index=False)

ll = R("S08:outputs/lane_lead.csv").sort_values(["delivered", "lane"], ascending=[False, True]).head(20)
ll[["lane", "delivered", "est_lead_mean_days", "act_lead_mean_days"]].round(4).to_csv(out("c6_lane_lead.csv"), index=False)
