import pandas as pd
import numpy as np
from engine.results import path, out, record

df = pd.read_csv(path("S02:outputs/order_seller.csv"))
for c in ["shipping_limit_date", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]:
    df[c] = pd.to_datetime(df[c])

lim = df.shipping_limit_date.dt.normalize()
car = df.order_delivered_carrier_date.dt.normalize()
dele = df.order_delivered_customer_date.dt.normalize()
est = df.order_estimated_delivery_date.dt.normalize()

df["handover_late"] = car > lim
df["transit_budget"] = (est - lim).dt.days
df["transit_actual"] = (dele - car).dt.days
df["carrier_over"] = df.transit_actual > df.transit_budget
unc = df.order_delivered_carrier_date.isna() | (df.order_delivered_customer_date < df.order_delivered_carrier_date)
cls = np.where(unc, "unclassified",
      np.where(~df.handover_late, "carrier only",
      np.where(df.carrier_over, "both", "seller only")))
df["split_class"] = cls

late = df[df.late == 1].copy()
print("missing limit:", df.shipping_limit_date.isna().sum())
co_bad = ((late.split_class == "carrier only") & ~late.carrier_over).sum()
print("carrier only not carrier_over:", co_bad)

late["handover_late"] = late.handover_late.astype(int)
late["carrier_over"] = late.carrier_over.astype(int)
cols = ["order_id", "seller_id", "lane", "delay_days", "shipping_limit_date", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date", "handling_days", "transit_days",
        "handover_late", "transit_budget", "transit_actual", "carrier_over", "split_class"]
late = late[cols].sort_values(["order_id", "seller_id"])
late.to_csv(out("late_split.csv"), index=False)

n = len(late)
vc = late.split_class.value_counts()
order = ["seller only", "carrier only", "both", "unclassified"]
n_unc = int(vc.get("unclassified", 0))
ncl = n - n_unc
summ = pd.DataFrame({"split_class": order,
                     "late_pairs": [int(vc.get(k, 0)) for k in order]})
summ["share_pct"] = (summ.late_pairs / n * 100).round(2)
summ.to_csv(out("split_summary.csv"), index=False)

bins = pd.cut(late.delay_days, [0, 3, 7, 14, 10**6], labels=["1-3", "4-7", "8-14", "15+"])
ct = pd.crosstab(bins, late.split_class).reindex(columns=order, fill_value=0)
band = ct.reset_index().rename(columns={"delay_days": "days_late_band", "seller only": "seller_only",
                                        "carrier only": "carrier_only"})
band["days_late_band"] = band["days_late_band"].astype(str)
band = band[["days_late_band", "seller_only", "both", "carrier_only", "unclassified"]]
band.to_csv(out("split_by_band.csv"), index=False)

record("n_late_pairs", n, unit="pairs", description="late order-seller pairs")
so, co, bo = int(vc.get("seller only", 0)), int(vc.get("carrier only", 0)), int(vc.get("both", 0))
record("n_seller_only", so, unit="pairs", description="seller only")
record("n_carrier_only", co, unit="pairs", description="carrier only")
record("n_both", bo, unit="pairs", description="both")
record("n_unclassified", n_unc, unit="pairs", description="unclassified")
record("pct_seller_only", so / ncl * 100, unit="%", description="seller only share of classified")
record("pct_carrier_only", co / ncl * 100, unit="%", description="carrier only share of classified")
record("pct_both", bo / ncl * 100, unit="%", description="both share of classified")
record("pct_seller_involved", (so + bo) / ncl * 100, unit="%", description="seller involved share of classified")

on = df[df.late == 0]
al = df[df.late == 1]
record("handling_mean_late_days", al.handling_days.mean(), unit="days", description="mean handling, late pairs")
record("handling_mean_ontime_days", on.handling_days.mean(), unit="days", description="mean handling, on-time pairs")
record("transit_mean_late_days", al.transit_days.mean(), unit="days", description="mean transit, late pairs")
record("transit_mean_ontime_days", on.transit_days.mean(), unit="days", description="mean transit, on-time pairs")
o = on[on.order_delivered_carrier_date.notna()]
record("pct_ontime_pairs_handover_late", o.handover_late.mean() * 100, unit="%",
       description="on-time pairs with carrier date after shipping limit date")
print(summ, band, sep="\n")
