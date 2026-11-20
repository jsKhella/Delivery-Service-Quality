import pandas as pd
from engine.results import path, out, record

df = pd.read_csv(path("S02:outputs/order_seller.csv"))
total_late = int(df["late"].sum())
n_s_active = df["seller_id"].nunique()
n_l_active = df["lane"].nunique()


def pareto(key):
    g = df.groupby(key).agg(late=("late", "sum"), delivered=("order_id", "size")).reset_index()
    g = g.sort_values(["late", key], ascending=[False, True]).reset_index(drop=True)
    g["rank"] = g.index + 1
    g["cum_late"] = g["late"].cumsum()
    g["cum_late_share_pct"] = g["cum_late"] / total_late * 100
    return g[["rank", key, "late", "delivered", "cum_late", "cum_late_share_pct"]]


def n_for(g, frac):
    return int((g["cum_late"] >= frac * total_late).idxmax() + 1)


s = pareto("seller_id")
l = pareto("lane")
assert s["cum_late"].iloc[-1] == total_late and l["cum_late"].iloc[-1] == total_late
s.round({"cum_late_share_pct": 4}).to_csv(out("pareto_sellers.csv"), index=False)
l.round({"cum_late_share_pct": 4}).to_csv(out("pareto_lanes.csv"), index=False)

record("n_sellers_with_late", int((s["late"] > 0).sum()), unit="count", description="Sellers with at least one late pair")
n50 = n_for(s, 0.5)
n80 = n_for(s, 0.8)
record("n_sellers_for_50pct_late", n50, unit="count", description="Top sellers to reach 50% of late pairs")
record("pct_sellers_for_50pct_late", n50 / n_s_active * 100, unit="%", description="Share of active sellers for 50%")
record("n_sellers_for_80pct_late", n80, unit="count", description="Top sellers to reach 80% of late pairs")
record("pct_sellers_for_80pct_late", n80 / n_s_active * 100, unit="%", description="Share of active sellers for 80%")
record("top20_sellers_late_share_pct", s["late"].head(20).sum() / total_late * 100, unit="%", description="Top 20 sellers share of late pairs")
record("n_lanes_with_late", int((l["late"] > 0).sum()), unit="count", description="Lanes with at least one late pair")
nl80 = n_for(l, 0.8)
record("n_lanes_for_80pct_late", nl80, unit="count", description="Top lanes to reach 80% of late pairs")
record("pct_lanes_for_80pct_late", nl80 / n_l_active * 100, unit="%", description="Share of active lanes for 80%")
record("top20_lanes_late_share_pct", l["late"].head(20).sum() / total_late * 100, unit="%", description="Top 20 lanes share of late pairs")
print(total_late, n_s_active, n_l_active, n50, n80, nl80)
