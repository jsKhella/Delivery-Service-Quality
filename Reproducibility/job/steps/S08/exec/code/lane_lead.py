import pandas as pd
from engine.results import path, out, record

o = pd.read_csv(path("S01:outputs/orders_clean.csv"))
p = pd.read_csv(path("S02:outputs/order_seller.csv"))

record("est_lead_mean_days", float(o.est_lead_days_cal.mean()), unit="days", description="mean promised lead, clean orders")
record("act_lead_mean_days_cal", float(o.act_lead_days_cal.mean()), unit="days", description="mean actual calendar lead, clean orders")
buf = -o.delay_days.mean()
record("buffer_mean_days", float(buf), unit="days", description="mean estimated minus delivered date")
assert abs(buf - (pd.to_datetime(o.order_estimated_delivery_date) - pd.to_datetime(o.order_delivered_customer_date).dt.normalize()).dt.days.mean()) < 1e-9

p["buffer"] = -p.delay_days
g = p.groupby("lane")
lane = g.agg(delivered=("order_id", "size"), late_pairs=("late", "sum"),
             est_lead_mean_days=("est_lead_days_cal", "mean"),
             act_lead_mean_days=("act_lead_days_cal", "mean"),
             buffer_mean_days=("buffer", "mean")).reset_index()
lane["act_lead_p90_days"] = g.act_lead_days_cal.quantile(0.9).values
lane["late_rate_pct"] = lane.late_pairs / lane.delivered * 100
lane["ranked"] = (lane.delivered >= 30).astype(int)
lane = lane.sort_values("lane")[["lane", "delivered", "late_pairs", "late_rate_pct", "est_lead_mean_days",
                                 "act_lead_mean_days", "buffer_mean_days", "act_lead_p90_days", "ranked"]]
lane.to_csv(out("lane_lead.csv"), index=False, float_format="%.6f")

hi = set(lane[(lane.ranked == 1) & (lane.late_rate_pct >= 15)].lane)
assert (lane.ranked == 1).any()
record("n_lanes_late_ge15", len(hi), unit="lanes", description="ranked lanes late rate >=15%")
m = p.lane.isin(hi)
lp = int(p[m].late.sum())
record("late_pairs_lanes_late_ge15", lp, unit="pairs", description="late pairs on those lanes")
record("share_late_pairs_lanes_ge15_pct", lp / p.late.sum() * 100, unit="%", description="share of all late pairs")
record("buffer_mean_lanes_ge15_days", float(p[m].buffer.mean()), unit="days", description="mean buffer on those lanes")
record("buffer_mean_other_days", float(p[~m].buffer.mean()), unit="days", description="mean buffer on other lanes")
