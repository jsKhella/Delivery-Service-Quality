import pandas as pd
from engine.results import path, out, record

df = pd.read_csv(path("S01:outputs/orders_clean.csv"))
df = df[df["review_score"].notna()].copy()
df["delivered"] = pd.to_datetime(df["order_delivered_customer_date"])
df["est"] = pd.to_datetime(df["order_estimated_delivery_date"])
d = df["delay_days"]
s = df["review_score"]

rows = []
def add(scheme, band, mask):
    sub = s[mask]
    rows.append({"scheme": scheme, "band": band, "n_orders": int(len(sub)),
                 "mean_score": round(float(sub.mean()), 4),
                 "pct_low_score": round(float((sub <= 2).mean() * 100), 4)})

for k in (3, 2, 5, 7):
    sc = f"cutoff_{k}"
    add(sc, "on_time", d <= 0)
    add(sc, f"late_1_{k}", (d >= 1) & (d <= k))
    add(sc, f"late_gt{k}", d > k)
add("strict", "on_time_strict", df["delivered"] <= df["est"])
add("strict", "late_strict", df["delivered"] > df["est"])
res = pd.DataFrame(rows)
res.to_csv(out("review_bands.csv"), index=False)

def g(scheme, band, col):
    return float(res[(res.scheme == scheme) & (res.band == band)][col].iloc[0])

def exact(mask):
    return float(s[mask].mean())

record("n_reviewed_orders", int(len(df)), unit="orders", description="Reviewed clean orders")
record("review_mean_ontime", exact(d <= 0), unit="score", description="mean score on time")
record("review_mean_late_1_3", exact((d >= 1) & (d <= 3)), unit="score", description="mean score 1-3 late")
record("review_mean_late_gt3", exact(d > 3), unit="score", description="mean score >3 late")
record("review_gap_gt3", exact(d <= 0) - exact(d > 3), unit="score points", description="on time minus >3 late")
record("pct_low_ontime", float((s[d <= 0] <= 2).mean() * 100), unit="%", description="low share on time")
record("pct_low_late_1_3", float((s[(d >= 1) & (d <= 3)] <= 2).mean() * 100), unit="%", description="low share 1-3 late")
record("pct_low_late_gt3", float((s[d > 3] <= 2).mean() * 100), unit="%", description="low share >3 late")
record("review_mean_late_1_2", exact((d >= 1) & (d <= 2)), unit="score", description="mean 1-2 late")
record("review_mean_late_gt2", exact(d > 2), unit="score", description="mean >2 late")
record("review_mean_late_1_5", exact((d >= 1) & (d <= 5)), unit="score", description="mean 1-5 late")
record("review_mean_late_gt5", exact(d > 5), unit="score", description="mean >5 late")
record("review_mean_late_1_7", exact((d >= 1) & (d <= 7)), unit="score", description="mean 1-7 late")
record("review_mean_late_gt7", exact(d > 7), unit="score", description="mean >7 late")
record("review_mean_ontime_strict", exact(df["delivered"] <= df["est"]), unit="score", description="strict on time")
record("review_mean_late_strict", exact(df["delivered"] > df["est"]), unit="score", description="strict late")
rho = d.rank(method="average").corr(s.rank(method="average"))
record("spearman_delay_score", float(rho), unit="rho", description="Spearman delay vs score")

# stop-condition check: review creation before delivery for late orders?
rv = pd.read_csv(path("raw:olist_order_reviews_dataset.csv"))
rv["ans"] = pd.to_datetime(rv["review_answer_timestamp"])
rv["cre"] = pd.to_datetime(rv["review_creation_date"])
rv = rv.sort_values(["order_id", "ans", "cre", "review_id"]).groupby("order_id").tail(1)
m = df.merge(rv[["order_id", "cre"]], on="order_id")
late = m[m["delay_days"] >= 1]
share = float((late["cre"] < late["delivered"].dt.normalize()).mean())
print("min band n:", res["n_orders"].min())
print("late orders with review created before delivery date share:", share)
print(res.to_string())
