import duckdb
from engine.results import path, out, record
o = str(path("S01:outputs/orders_clean.csv")).replace("\\", "/")
p = str(path("S02:outputs/order_seller.csv")).replace("\\", "/")
l = str(out("lane_lead.csv")).replace("\\", "/")
c = duckdb.connect()
r = c.sql(f"""select avg(est_lead_days_cal), avg(act_lead_days_cal),
 avg(date_diff('day', CAST(order_delivered_customer_date AS DATE), CAST(order_estimated_delivery_date AS DATE))), -avg(delay_days)
 from read_csv_auto('{o}')""").fetchone()
print(r)
record("est_lead_mean_days", r[0]); record("act_lead_mean_days_cal", r[1]); record("buffer_mean_days", r[2])
c.sql(f"create view lanes as select * from read_csv_auto('{l}')")
c.sql(f"""create view pr as select s.*, date_diff('day', CAST(order_delivered_customer_date AS DATE), CAST(order_estimated_delivery_date AS DATE)) buf,
 (s.lane in (select lane from lanes where ranked and late_rate_pct>=15)) g from read_csv_auto('{p}') s""")
n = c.sql("select count(*) from lanes where ranked and late_rate_pct>=15").fetchone()[0]
lp = c.sql("select sum(late) from pr where g").fetchone()[0]
tl = c.sql("select sum(late) from pr").fetchone()[0]
bg = c.sql("select avg(buf) from pr where g").fetchone()[0]
bo = c.sql("select avg(buf) from pr where not g").fetchone()[0]
print(n, lp, tl, bg, bo)
record("n_lanes_late_ge15", n); record("late_pairs_lanes_late_ge15", lp)
record("share_late_pairs_lanes_ge15_pct", 100*lp/tl)
record("buffer_mean_lanes_ge15_days", bg); record("buffer_mean_other_days", bo)
