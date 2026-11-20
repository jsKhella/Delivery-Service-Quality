import duckdb, csv
from engine.results import path, out, record

O = str(path("raw:olist_orders_dataset.csv")).replace("\\", "/")
R = str(path("raw:olist_order_reviews_dataset.csv")).replace("\\", "/")
C = str(out("orders_clean.csv")).replace("\\", "/")
con = duckdb.connect()
def q(s): return con.execute(s).fetchone()[0]
ob = f"read_csv_auto('{O}')"
dl = f"{ob} WHERE order_status='delivered'"
n_raw = q(f"select count(*) from {ob}")
n_del = q(f"select count(*) from {dl}")
n_nod = q(f"select count(*) from {dl} and order_delivered_customer_date is null")
n_inc = q(f"""select count(*) from {dl} and order_delivered_customer_date is not null and
 (cast(order_delivered_customer_date as date) < cast(order_purchase_timestamp as date)
  or cast(order_estimated_delivery_date as date) < cast(order_purchase_timestamp as date))""")
cl = f"read_csv_auto('{C}')"
n_clean = q(f"select count(*) from {cl}")
n_ma = q(f"select count(*) from {cl} where order_approved_at is null")
n_mc = q(f"select count(*) from {cl} where order_delivered_carrier_date is null")
n_cba = q(f"select count(*) from {cl} where order_delivered_carrier_date < order_approved_at")
n_dbc = q(f"select count(*) from {cl} where order_delivered_customer_date < order_delivered_carrier_date")
n_lo = q(f"select count(*) from {cl} where lead_time_days > 60")
n_rr = q(f"select count(*) from read_csv_auto('{R}')")
n_mr = q(f"select count(*) from (select order_id from read_csv_auto('{R}') group by 1 having count(*)>1)")
n_cr = q(f"select count(*) from {cl} where review_score is not null")
n_dup_extra = q(f"select count(*) - count(distinct order_id) from read_csv_auto('{R}')")
for k, v in dict(n_orders_raw=n_raw, n_delivered_status=n_del, n_removed_no_delivery_date=n_nod,
    n_removed_inconsistent=n_inc, n_orders_clean=n_clean, n_missing_approved=n_ma,
    n_missing_carrier=n_mc, n_carrier_before_approved=n_cba, n_delivered_before_carrier=n_dbc,
    n_lead_outliers=n_lo, n_review_rows_raw=n_rr, n_orders_multi_review=n_mr,
    n_clean_with_review=n_cr).items():
    record(k, int(v))

rows = [
 ("Orders not delivered status", "orders", n_raw-n_del, "excluded", n_raw-n_del, "Only delivered orders analysed"),
 ("Delivered without customer delivery date", "orders", n_nod, "removed", n_nod, "Delay cannot be computed"),
 ("Delivered date or estimated date before purchase date", "orders", n_inc, "removed", n_inc, "Inconsistent timestamps"),
 ("Approval timestamp missing", "orders", n_ma, "kept, handling set missing", 0, "Handling time not computable"),
 ("Carrier timestamp missing", "orders", n_mc, "kept, handling and transit set missing", 0, "Not computable"),
 ("Carrier timestamp before approval", "orders", n_cba, "kept, handling set missing", 0, "Negative duration"),
 ("Customer delivery before carrier timestamp", "orders", n_dbc, "kept, transit set missing", 0, "Negative duration"),
 ("Lead time above 60 days", "orders", n_lo, "flagged lead_outlier, kept", 0, "Extreme but plausible"),
 ("Duplicate reviews per order", "reviews", n_dup_extra, "kept latest answer by ROW_NUMBER", n_dup_extra, "One review per order needed"),
 ("Delivered clean orders without review", "reviews", n_clean-n_cr, "kept, review_score missing", 0, "No review exists"),
]
with open(out("dq_log_orders.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["issue","source_file","rows_found","action","rows_removed","reason"])
    for i, (a, s, n, ac, rr, rs) in enumerate(rows):
        src = "olist_order_reviews_dataset.csv" if s == "reviews" else "olist_orders_dataset.csv"
        w.writerow([a, src, int(n), ac, int(rr), rs])
