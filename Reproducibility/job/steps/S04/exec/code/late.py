import pandas as pd
from engine.results import path, out, record

os_ = pd.read_csv(path("S02:outputs/order_seller.csv"), usecols=["order_id", "seller_id", "lane", "late"])
oc = pd.read_csv(path("S02:outputs/order_category.csv"), usecols=["order_id", "category", "late"])
cl = pd.read_csv(path("S01:outputs/orders_clean.csv"), usecols=["order_id", "customer_state", "late"])


def agg(df, key):
    g = df.groupby(key).agg(delivered=("late", "size"), late=("late", "sum")).reset_index()
    g["late_rate_pct"] = (g["late"] / g["delivered"] * 100).round(4)
    g["ranked"] = (g["delivered"] >= 30).astype(int)
    g["rank_worst"] = pd.NA
    g["rank_best"] = pd.NA
    r = g[g.ranked == 1]
    w = r.sort_values(["late_rate_pct", "delivered", key], ascending=[False, False, True])
    b = r.sort_values(["late_rate_pct", "delivered", key], ascending=[True, False, True])
    g.loc[w.index, "rank_worst"] = range(1, len(w) + 1)
    g.loc[b.index, "rank_best"] = range(1, len(b) + 1)
    g["rank_worst"] = g["rank_worst"].astype("Int64")
    g["rank_best"] = g["rank_best"].astype("Int64")
    return g.sort_values(key).reset_index(drop=True)


s = agg(os_, "seller_id")
l = agg(os_, "lane")
c = agg(oc, "category")
st = agg(cl, "customer_state")
s.to_csv(out("late_by_seller.csv"), index=False)
l.to_csv(out("late_by_lane.csv"), index=False)
c.to_csv(out("late_by_category.csv"), index=False)
st.to_csv(out("late_by_state.csv"), index=False)

rs, rl, rc, rt = (x[x.ranked == 1] for x in (s, l, c, st))
record("n_sellers_ranked", len(rs), unit="sellers", description="sellers with >=30 pairs")
record("n_lanes_ranked", len(rl), unit="lanes", description="lanes with >=30 pairs")
record("n_categories_ranked", len(rc), unit="categories", description="categories with >=30 pairs")
record("n_states_ranked", len(rt), unit="states", description="states with >=30 orders")
record("seller_late_rate_median_pct", float(rs.late_rate_pct.median()), unit="%", description="median seller late rate")
record("seller_late_rate_max_pct", float(rs.late_rate_pct.max()), unit="%", description="max seller late rate")
record("seller_late_rate_min_pct", float(rs.late_rate_pct.min()), unit="%", description="min seller late rate")
record("lane_late_rate_max_pct", float(rl.late_rate_pct.max()), unit="%", description="max lane late rate")
record("lane_late_rate_min_pct", float(rl.late_rate_pct.min()), unit="%", description="min lane late rate")
record("category_late_rate_max_pct", float(rc.late_rate_pct.max()), unit="%", description="max category late rate")
record("category_late_rate_min_pct", float(rc.late_rate_pct.min()), unit="%", description="min category late rate")
record("state_late_rate_max_pct", float(rt.late_rate_pct.max()), unit="%", description="max state late rate")
record("state_late_rate_min_pct", float(rt.late_rate_pct.min()), unit="%", description="min state late rate")
tot = int(os_.late.sum())
record("n_late_pairs_total", tot, unit="pairs", description="late order-seller pairs")
hi = rs[rs.late_rate_pct >= 15]
lp = int(hi.late.sum())
record("n_sellers_late_ge15", len(hi), unit="sellers", description="ranked sellers with late rate >=15%")
record("late_pairs_sellers_late_ge15", lp, unit="pairs", description="late pairs of those sellers")
record("share_late_pairs_sellers_late_ge15_pct", lp / tot * 100, unit="%", description="share of late pairs")
