import pandas as pd
from engine.results import out, record

k = pd.read_csv(out("kpi_overall.csv")).set_index("metric")["value"]
m = pd.read_csv(out("monthly.csv"))
for i in ["on_time_rate_pct","late_share_pct","n_late_orders","lead_mean_days","lead_median_days",
          "lead_p90_days","mean_delay_late_days","handling_mean_days","transit_mean_days"]:
    record(i, float(k[i]))
s = m[m["shown"]]
record("n_months_all", int(len(m)))
record("n_months_shown", int(len(s)))
record("best_month_on_time_pct", float(s["on_time_rate_pct"].max()))
record("worst_month_on_time_pct", float(s["on_time_rate_pct"].min()))
