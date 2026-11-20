import pandas as pd
from engine.results import path, out, record

o = pd.read_csv(path("S01:outputs/orders_clean.csv"))
r = pd.read_csv(path("raw:olist_order_reviews_dataset.csv"))
r["review_answer_timestamp"] = pd.to_datetime(r["review_answer_timestamp"])
r["review_creation_date"] = pd.to_datetime(r["review_creation_date"])
r = r.sort_values(["order_id", "review_answer_timestamp", "review_creation_date", "review_id"])
r = r.groupby("order_id", as_index=False).tail(1)

o["deliv"] = pd.to_datetime(o["order_delivered_customer_date"])
o["est"] = pd.to_datetime(o["order_estimated_delivery_date"])
d = o.drop(columns=["review_score"]).merge(
    r[["order_id", "review_score", "review_creation_date", "review_answer_timestamp"]],
    on="order_id", how="inner")
d = d[d["review_score"].notna()].copy()
n = len(d)
record("n_reviewed_orders", n, unit="orders", description="Clean delivered orders with a review score after de-duplication")

def stats(x):
    return len(x), x["review_score"].mean(), 100.0 * (x["review_score"] <= 2).mean()

dd = d["delay_days"]
rows = []
def add(scheme, band, mask):
    c, m, p = stats(d[mask])
    rows.append((scheme, band, c, round(m, 4), round(p, 4)))
    return c, m, p

res = {}
res["3"] = [add("cut3", "on_time", dd <= 0), add("cut3", "late_1_3", (dd >= 1) & (dd <= 3)), add("cut3", "late_gt3", dd > 3)]
for k in (2, 5, 7):
    add(f"cut{k}", "on_time", dd <= 0)
    res[str(k)] = [None, add(f"cut{k}", f"late_1_{k}", (dd >= 1) & (dd <= k)), add(f"cut{k}", f"late_gt{k}", dd > k)]
strict_late = d["deliv"] > d["est"]
res["s"] = [add("strict", "on_time_strict", ~strict_late), add("strict", "late_strict", strict_late)]

bands = pd.DataFrame(rows, columns=["scheme", "band", "n_orders", "mean_score", "pct_low_score"])
bands = bands.sort_values(["scheme", "band"]).reset_index(drop=True)
bands.to_csv(out("review_bands.csv"), index=False)

# stop condition: any band below 100
record("min_band_n", int(bands["n_orders"].min()), unit="orders", description="Smallest band size across all schemes")

u = "score 1-5"
record("review_mean_ontime", res["3"][0][1], unit=u, description="Mean score, on time")
record("review_mean_late_1_3", res["3"][1][1], unit=u, description="Mean score, 1-3 days late")
record("review_mean_late_gt3", res["3"][2][1], unit=u, description="Mean score, >3 days late")
record("review_gap_gt3", res["3"][0][1] - res["3"][2][1], unit="score points", description="On time minus >3 days late")
record("pct_low_ontime", res["3"][0][2], unit="%", description="Share 1-2 stars, on time")
record("pct_low_late_1_3", res["3"][1][2], unit="%", description="Share 1-2 stars, 1-3 late")
record("pct_low_late_gt3", res["3"][2][2], unit="%", description="Share 1-2 stars, >3 late")
record("review_mean_late_1_2", res["2"][1][1], unit=u, description="Mean score, 1-2 late")
record("review_mean_late_gt2", res["2"][2][1], unit=u, description="Mean score, >2 late")
record("review_mean_late_1_5", res["5"][1][1], unit=u, description="Mean score, 1-5 late")
record("review_mean_late_gt5", res["5"][2][1], unit=u, description="Mean score, >5 late")
record("review_mean_late_1_7", res["7"][1][1], unit=u, description="Mean score, 1-7 late")
record("review_mean_late_gt7", res["7"][2][1], unit=u, description="Mean score, >7 late")
record("review_mean_ontime_strict", res["s"][0][1], unit=u, description="Mean score, strict on time")
record("review_mean_late_strict", res["s"][1][1], unit=u, description="Mean score, strict late")
rho = d["delay_days"].rank().corr(d["review_score"].rank())
record("spearman_delay_score", rho, unit="correlation", description="Spearman delay_days vs review_score")

# owner-requested timing checks on late orders (delay_days >= 1)
late = d[d["delay_days"] >= 1]
dday = late["deliv"].dt.normalize()
record("n_late_reviewed", len(late), unit="orders", description="Reviewed late orders")
record("late_creation_before_delivery_pct", 100.0 * (late["review_creation_date"] < dday).mean(), unit="%",
       description="Late reviewed orders whose review creation date is before the delivery date")
record("late_answer_before_delivery_pct", 100.0 * (late["review_answer_timestamp"] < late["deliv"]).mean(), unit="%",
       description="Late reviewed orders whose review answer timestamp is before the delivery timestamp")
record("late_answer_before_estimate_pct", 100.0 * (late["review_answer_timestamp"] < late["est"]).mean(), unit="%",
       description="Late reviewed orders answered before the estimated date")
