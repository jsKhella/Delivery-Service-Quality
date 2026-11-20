import numpy as np
import pandas as pd
from engine.results import path, out, record

oc = pd.read_csv(path("S01:outputs/orders_clean.csv"))
log = pd.read_csv(path("S01:outputs/dq_log_orders.csv"))
raw_o = pd.read_csv(path("raw:olist_orders_dataset.csv"),
                    usecols=["order_id", "order_approved_at", "order_delivered_carrier_date"])
it = pd.read_csv(path("raw:olist_order_items_dataset.csv"))
se = pd.read_csv(path("raw:olist_sellers_dataset.csv"))
pr = pd.read_csv(path("raw:olist_products_dataset.csv"))
tr = pd.read_csv(path("raw:product_category_name_translation.csv"))
geo = pd.read_csv(path("raw:olist_geolocation_dataset.csv"))

record("n_item_rows_raw", len(it), unit="rows", description="Rows in raw order items file")

# geo
g = geo.groupby("geolocation_zip_code_prefix").agg(
    lat=("geolocation_lat", "mean"), lng=("geolocation_lng", "mean")).reset_index()
g = g.rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"}).sort_values("zip_code_prefix")
g.to_csv(out("geo_zip_avg.csv"), index=False)
record("n_zip_prefixes_geo", len(g), unit="prefixes", description="Distinct zip prefixes in geolocation file")

# stop checks
clean_ids = set(oc.order_id)
ci = it[it.order_id.isin(clean_ids)].copy()
n_noitems = len(clean_ids - set(ci.order_id))
record("n_clean_orders_no_items", n_noitems, unit="orders", description="Clean orders with no item rows")
if n_noitems > 50:
    raise SystemExit("STOP: more than 50 clean orders without items")
missing_sellers = int((~it.seller_id.isin(se.seller_id)).sum())
if missing_sellers:
    raise SystemExit("STOP: seller_id in items missing from sellers file")
states = set(se.seller_state) | set(oc.customer_state)
if not all(isinstance(s, str) and len(s) == 2 and s.isupper() for s in states):
    raise SystemExit("STOP: bad state codes")
BR = {"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"}
if not states <= BR:
    raise SystemExit("STOP: non-Brazilian state codes " + str(states - BR))

# order_seller
ci["shipping_limit_date"] = pd.to_datetime(ci.shipping_limit_date)
pair = ci.groupby(["order_id", "seller_id"]).agg(
    shipping_limit_date=("shipping_limit_date", "max"), n_items=("order_item_id", "size")).reset_index()
pair = pair.merge(se[["seller_id", "seller_state", "seller_zip_code_prefix"]], on="seller_id", how="left")
pair = pair.merge(oc[["order_id", "customer_state", "customer_zip_code_prefix", "order_estimated_delivery_date",
                      "order_delivered_customer_date", "delay_days", "late", "est_lead_days_cal",
                      "act_lead_days_cal", "handling_days", "transit_days"]], on="order_id", how="left")
pair = pair.merge(raw_o.rename(columns={"order_delivered_carrier_date": "order_delivered_carrier_date"})
                  [["order_id", "order_delivered_carrier_date"]], on="order_id", how="left")
pair["lane"] = pair.seller_state + "-" + pair.customer_state
gi = g.set_index("zip_code_prefix")
s = gi.reindex(pair.seller_zip_code_prefix.values)
c = gi.reindex(pair.customer_zip_code_prefix.values)
la1, lo1, la2, lo2 = [np.radians(x.values) for x in (s.lat, s.lng, c.lat, c.lng)]
a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
pair["distance_km"] = (2 * 6371.0088 * np.arcsin(np.sqrt(a))).round(3)
n_nogeo = int(pair.distance_km.isna().sum())
cols = ["order_id", "seller_id", "seller_state", "customer_state", "lane", "shipping_limit_date", "n_items",
        "distance_km", "delay_days", "late", "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date", "est_lead_days_cal", "act_lead_days_cal", "handling_days", "transit_days"]
pair = pair[cols].sort_values(["order_id", "seller_id"])
pair.to_csv(out("order_seller.csv"), index=False)
record("n_order_seller_pairs", len(pair), unit="pairs", description="Rows of order_seller.csv")
nseller = pair.groupby("order_id").seller_id.nunique()
record("n_multi_seller_orders", int((nseller >= 2).sum()), unit="orders", description="Clean orders with 2+ sellers")
record("n_sellers_active", pair.seller_id.nunique(), unit="sellers", description="Distinct sellers in order_seller")
record("n_lanes_active", pair.lane.nunique(), unit="lanes", description="Distinct lanes in order_seller")
record("n_pairs_no_geo", n_nogeo, unit="pairs", description="Pairs with missing distance")

# order_category
pc = pr[["product_id", "product_category_name"]].merge(tr, on="product_category_name", how="left")
pc["category"] = pc.product_category_name_english.fillna(pc.product_category_name)
ci = ci.merge(pc[["product_id", "category", "product_category_name"]], on="product_id", how="left")
n_nocat = int(ci.category.isna().sum())
n_notrans = int((ci.category.notna() & ci.product_category_name.notna()
                 & ~ci.product_category_name.isin(tr.product_category_name)).sum())
ci["category"] = ci.category.fillna("unknown")
oct_ = ci[["order_id", "category"]].drop_duplicates().merge(oc[["order_id", "delay_days", "late"]], on="order_id")
oct_ = oct_.sort_values(["order_id", "category"])
oct_.to_csv(out("order_category.csv"), index=False)
record("n_order_category_pairs", len(oct_), unit="pairs", description="Rows of order_category.csv")
record("n_items_no_category", n_nocat, unit="items", description="Item rows of clean orders with no category")

# dq log
n_items_nonclean = len(it) - len(ci)
n_dup_pairs = len(ci) - len(pair)
IF = "olist_order_items_dataset.csv"
new = [
    ("Clean orders with no item rows", IF, n_noitems, "None needed" if n_noitems == 0 else "Kept in order figures, absent from seller and category figures", 0, "Seller and category figures need items"),
    ("Item rows belonging to orders not in the clean set", IF, n_items_nonclean, "Excluded from seller and category tables", n_items_nonclean, "Only clean delivered orders are analysed"),
    ("Item rows of clean orders without a product category", "olist_products_dataset.csv", n_nocat, "Labelled unknown", 0, "Category missing in source"),
    ("Product categories without an English translation", "product_category_name_translation.csv", n_notrans, "Portuguese name used", 0, "Translation file incomplete"),
    ("Item rows beyond the first for the same order and seller", IF, n_dup_pairs, "Merged into one order-seller pair with item count", 0, "Seller figures are per order-seller pair"),
    ("Orders with items from two or more sellers", IF, int((nseller >= 2).sum()), "Kept, counted once per seller in seller and lane figures", 0, "Late order counts for each seller involved"),
    ("Geolocation rows beyond one per zip prefix", "olist_geolocation_dataset.csv", len(geo) - len(g), "Averaged to one coordinate per prefix", 0, "Several coordinates per prefix"),
    ("Order-seller pairs with no coordinates for seller or customer zip prefix", "olist_geolocation_dataset.csv", n_nogeo, "Kept, distance_km left missing", 0, "Distance cannot be computed"),
]
log = log[~log.issue.str.startswith("Multi-seller orders count once")]
full = pd.concat([log, pd.DataFrame(new, columns=log.columns)], ignore_index=True)
full.to_csv(out("dq_log.csv"), index=False)
