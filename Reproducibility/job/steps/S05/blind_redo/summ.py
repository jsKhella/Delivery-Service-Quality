import pandas as pd
from engine.results import path, out, record

ls = pd.read_csv(out("late_split.csv"))
os_ = pd.read_csv(path("S02:outputs/order_seller.csv"))
n = len(ls)
vc = ls.split_class.value_counts()
classes = ["seller only", "carrier only", "both", "unclassified"]
c = {k: int(vc.get(k, 0)) for k in classes}
summ = pd.DataFrame({"split_class": classes, "late_pairs": [c[k] for k in classes]})
summ["share_pct"] = summ.late_pairs / n * 100
summ.to_csv(out("split_summary.csv"), index=False)

bands = ["1-3", "4-7", "8-14", "15+"]
rows = []
for b in bands:
    s = ls[ls.days_late_band == b].split_class.value_counts()
    rows.append({"days_late_band": b, "seller_only": int(s.get("seller only", 0)), "both": int(s.get("both", 0)),
                 "carrier_only": int(s.get("carrier only", 0)), "unclassified": int(s.get("unclassified", 0))})
pd.DataFrame(rows).to_csv(out("split_by_band.csv"), index=False)

cl = n - c["unclassified"]
record("n_late_pairs", n)
record("n_seller_only", c["seller only"])
record("n_carrier_only", c["carrier only"])
record("n_both", c["both"])
record("n_unclassified", c["unclassified"])
record("pct_seller_only", c["seller only"] / cl * 100)
record("pct_carrier_only", c["carrier only"] / cl * 100)
record("pct_both", c["both"] / cl * 100)
record("pct_seller_involved", (c["seller only"] + c["both"]) / cl * 100)
late = os_[os_.late == 1]
on = os_[os_.late == 0]
record("handling_mean_late_days", late.handling_days.mean())
record("handling_mean_ontime_days", on.handling_days.mean())
record("transit_mean_late_days", late.transit_days.mean())
record("transit_mean_ontime_days", on.transit_days.mean())
oc = on[on.order_delivered_carrier_date.notna()]
hl = pd.to_datetime(oc.order_delivered_carrier_date).dt.normalize() > pd.to_datetime(oc.shipping_limit_date).dt.normalize()
record("pct_ontime_pairs_handover_late", hl.mean() * 100)
