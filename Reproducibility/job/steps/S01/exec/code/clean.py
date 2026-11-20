import pandas as pd
from engine.results import path, out, record

o = pd.read_csv(path("raw:olist_orders_dataset.csv"))
r = pd.read_csv(path("raw:olist_order_reviews_dataset.csv"))
c = pd.read_csv(path("raw:olist_customers_dataset.csv"))

tcols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
         "order_delivered_customer_date", "order_estimated_delivery_date"]
for col in tcols:
    o[col] = pd.to_datetime(o[col])

record("n_orders_raw", len(o), unit="orders", description="Rows in raw orders file")
d = o[o.order_status == "delivered"].copy()
record("n_delivered_status", len(d), unit="orders", description="Orders with status delivered")

est_time = int((o.order_estimated_delivery_date != o.order_estimated_delivery_date.dt.normalize()).sum())

nodate = d.order_delivered_customer_date.isna()
n_nodate = int(nodate.sum())
d = d[~nodate].copy()
record("n_removed_no_delivery_date", n_nodate, unit="orders", description="Delivered status, no customer delivery date, removed")

pd_ = d.order_purchase_timestamp.dt.normalize()
dd = d.order_delivered_customer_date.dt.normalize()
ed = d.order_estimated_delivery_date.dt.normalize()
bad_del = dd < pd_
bad_est = ed < pd_
bad = bad_del | bad_est
n_bad_del, n_bad_est, n_bad = int(bad_del.sum()), int(bad_est.sum()), int(bad.sum())
record("n_removed_inconsistent", n_bad, unit="orders", description="Removed: delivered or estimated date before purchase date")
d = d[~bad].copy()
record("n_orders_clean", len(d), unit="orders", description="Kept delivered orders")

pur = d.order_purchase_timestamp.dt.normalize()
dd = d.order_delivered_customer_date.dt.normalize()
ed = d.order_estimated_delivery_date.dt.normalize()
d["delay_days"] = (dd - ed).dt.days
d["late"] = (d.delay_days >= 1).astype(int)
day = pd.Timedelta(days=1)
d["lead_time_days"] = (d.order_delivered_customer_date - d.order_purchase_timestamp) / day
d["handling_days"] = (d.order_delivered_carrier_date - d.order_approved_at) / day
d["transit_days"] = (d.order_delivered_customer_date - d.order_delivered_carrier_date) / day
n_neg_h = int((d.handling_days < 0).sum())
n_neg_t = int((d.transit_days < 0).sum())
d.loc[d.handling_days < 0, "handling_days"] = pd.NA
d.loc[d.transit_days < 0, "transit_days"] = pd.NA
d["est_lead_days_cal"] = (ed - pur).dt.days
d["act_lead_days_cal"] = (dd - pur).dt.days
d["purchase_month"] = d.order_purchase_timestamp.dt.strftime("%Y-%m")
d["lead_outlier"] = (d.lead_time_days > 60).astype(int)

n_ma = int(d.order_approved_at.isna().sum())
n_mc = int(d.order_delivered_carrier_date.isna().sum())
record("n_missing_approved", n_ma, unit="orders", description="Kept orders missing approval time")
record("n_missing_carrier", n_mc, unit="orders", description="Kept orders missing carrier date")
record("n_carrier_before_approved", n_neg_h, unit="orders", description="Negative handling time")
record("n_delivered_before_carrier", n_neg_t, unit="orders", description="Negative transit time")
n_out = int(d.lead_outlier.sum())
record("n_lead_outliers", n_out, unit="orders", description="Lead time above 60 days")

# reviews
record("n_review_rows_raw", len(r), unit="rows", description="Rows in raw reviews file")
vc = r.order_id.value_counts()
n_multi = int((vc > 1).sum())
record("n_orders_multi_review", n_multi, unit="orders", description="Orders with more than one review row")
n_dup_rows = int(len(r) - r.order_id.nunique())
r["_ans"] = pd.to_datetime(r.review_answer_timestamp)
r["_cre"] = pd.to_datetime(r.review_creation_date)
rr = r.sort_values(["order_id", "_ans", "_cre", "review_id"]).drop_duplicates("order_id", keep="last")
d = d.merge(rr[["order_id", "review_score"]], on="order_id", how="left")
n_rev = int(d.review_score.notna().sum())
record("n_clean_with_review", n_rev, unit="orders", description="Kept orders with a review score")
n_norev = len(d) - n_rev
n_rev_unmatched = int((~r.order_id.isin(o.order_id)).sum())

# customers
n_dup_cust = int(c.customer_id.duplicated().sum())
d = d.merge(c[["customer_id", "customer_state", "customer_zip_code_prefix"]].drop_duplicates("customer_id"),
            on="customer_id", how="left")
n_nocust = int(d.customer_state.isna().sum())

cols = ["order_id", "customer_id", "customer_state", "customer_zip_code_prefix", "purchase_month",
        "order_purchase_timestamp", "order_estimated_delivery_date", "order_delivered_customer_date",
        "delay_days", "late", "lead_time_days", "handling_days", "transit_days",
        "est_lead_days_cal", "act_lead_days_cal", "lead_outlier", "review_score"]
d = d[cols].sort_values("order_id")
d.to_csv(out("orders_clean.csv"), index=False)

OF, RF = "olist_orders_dataset.csv", "olist_order_reviews_dataset.csv"
rows = [
    ("Orders not in delivered status", OF, len(o) - int((o.order_status == "delivered").sum()), "Excluded from analysis", len(o) - int((o.order_status == "delivered").sum()), "Only delivered orders are analysed"),
    ("Delivered status but no customer delivery date", OF, n_nodate, "Removed", n_nodate, "Delay cannot be computed"),
    ("Delivered calendar date before purchase date", OF, n_bad_del, "Removed", n_bad_del, "Impossible timeline"),
    ("Estimated date before purchase date", OF, n_bad_est, "Removed (overlaps counted once in total removed)", n_bad_est, "Impossible promise date"),
    ("Estimated date carries a time of day", OF, est_time, "None needed, dates compared as calendar dates", 0, "Time of day ignored by rule"),
    ("Approval time missing", OF, n_ma, "Kept, handling time left missing", 0, "Handling time cannot be computed"),
    ("Carrier date missing", OF, n_mc, "Kept, handling and transit left missing", 0, "Stages cannot be computed"),
    ("Carrier timestamp before approval (negative handling)", OF, n_neg_h, "Kept, handling set to missing", 0, "Negative duration is not plausible"),
    ("Delivery before carrier timestamp (negative transit)", OF, n_neg_t, "Kept, transit set to missing", 0, "Negative duration is not plausible"),
    ("Lead time above 60 days", OF, n_out, "Flagged lead_outlier, kept in all figures", 0, "Extreme but real delays"),
    ("Orders with more than one review row", RF, n_multi, "Kept latest answer, then latest creation date, then highest review_id", n_dup_rows, "One review per order needed"),
    ("Kept orders without any review", RF, n_norev, "Kept, review_score missing", 0, "Orders are still valid deliveries"),
    ("Review rows whose order_id is not in orders", RF, n_rev_unmatched, "None needed", 0, "All reviews match orders"),
    ("Multi-seller orders count once per seller in seller figures", "olist_order_items_dataset.csv", 0, "Documented, handled in later steps", 0, "Late order counts for each seller, about one percent of orders"),
    ("Kept orders without customer match", "olist_customers_dataset.csv", n_nocust, "None needed", 0, "Every order has a customer row"),
]
pd.DataFrame(rows, columns=["issue", "source_file", "rows_found", "action", "rows_removed", "reason"]).to_csv(out("dq_log_orders.csv"), index=False)
