import pandas as pd
from engine.results import path, out, record

d = pd.read_csv(path("S01:outputs/orders_clean.csv"))
n = len(d)
late = d.delay_days >= 1
ontime = d.delay_days <= 0
on_pct = ontime.sum() / n * 100
late_pct = late.sum() / n * 100
assert abs(on_pct + late_pct - 100) < 0.01

vals = {
    "on_time_rate_pct": (on_pct, "%"),
    "late_share_pct": (late_pct, "%"),
    "n_late_orders": (int(late.sum()), "orders"),
    "lead_mean_days": (d.lead_time_days.mean(), "days"),
    "lead_median_days": (d.lead_time_days.median(), "days"),
    "lead_p90_days": (d.lead_time_days.quantile(0.9), "days"),
    "mean_delay_late_days": (d.loc[late, "delay_days"].mean(), "days"),
    "handling_mean_days": (d.handling_days.mean(), "days"),
    "transit_mean_days": (d.transit_days.mean(), "days"),
}
rows = [("delivered_orders", n, "orders")]
for k, (v, u) in vals.items():
    rows.append((k, round(float(v), 4), u))
    record(k, float(v), unit=u, description=k)
pd.DataFrame(rows, columns=["metric", "value", "unit"]).to_csv(out("kpi_overall.csv"), index=False)

g = d.groupby("purchase_month")
m = pd.DataFrame({
    "delivered": g.size(),
    "late": g["delay_days"].apply(lambda s: int((s >= 1).sum())),
    "lead_mean_days": g["lead_time_days"].mean().round(4),
})
m["on_time_rate_pct"] = ((m.delivered - m.late) / m.delivered * 100).round(4)
m["late_share_pct"] = (m.late / m.delivered * 100).round(4)
m["shown"] = (m.delivered >= 500).astype(int)
m = m.reset_index().rename(columns={"purchase_month": "month"})
m = m[["month", "delivered", "late", "on_time_rate_pct", "late_share_pct", "lead_mean_days", "shown"]].sort_values("month")
m.to_csv(out("monthly.csv"), index=False)

s = m[m.shown == 1]
record("n_months_all", len(m), unit="months", description="distinct purchase months")
record("n_months_shown", len(s), unit="months", description="months with >=500 delivered")
record("best_month_on_time_pct", float(s.on_time_rate_pct.max()), unit="%", description="best month on-time")
record("worst_month_on_time_pct", float(s.on_time_rate_pct.min()), unit="%", description="worst month on-time")
print(m.to_string())
print(rows)
