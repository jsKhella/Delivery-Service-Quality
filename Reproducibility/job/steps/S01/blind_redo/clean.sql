WITH o AS (
  SELECT order_id, customer_id,
    CAST(order_purchase_timestamp AS TIMESTAMP) AS p,
    CAST(order_approved_at AS TIMESTAMP) AS a,
    CAST(order_delivered_carrier_date AS TIMESTAMP) AS c,
    CAST(order_delivered_customer_date AS TIMESTAMP) AS d,
    CAST(order_estimated_delivery_date AS TIMESTAMP) AS e
  FROM read_csv_auto('{raw}/olist_orders_dataset.csv')
  WHERE order_status = 'delivered'
),
r AS (
  SELECT order_id, review_score,
    ROW_NUMBER() OVER (PARTITION BY order_id
      ORDER BY CAST(review_answer_timestamp AS TIMESTAMP) DESC,
               CAST(review_creation_date AS TIMESTAMP) DESC,
               review_id DESC) AS rn
  FROM read_csv_auto('{raw}/olist_order_reviews_dataset.csv')
),
cu AS (
  SELECT customer_id, customer_state, customer_zip_code_prefix
  FROM read_csv_auto('{raw}/olist_customers_dataset.csv', types={'customer_zip_code_prefix':'VARCHAR'})
)
SELECT o.order_id, o.customer_id, cu.customer_state, cu.customer_zip_code_prefix,
  o.p AS order_purchase_timestamp, o.a AS order_approved_at, o.c AS order_delivered_carrier_date,
  o.d AS order_delivered_customer_date, o.e AS order_estimated_delivery_date,
  strftime(o.p, '%Y-%m') AS purchase_month,
  date_diff('day', CAST(o.e AS DATE), CAST(o.d AS DATE)) AS delay_days,
  CASE WHEN date_diff('day', CAST(o.e AS DATE), CAST(o.d AS DATE)) >= 1 THEN 1 ELSE 0 END AS late,
  epoch(o.d - o.p) / 86400.0 AS lead_time_days,
  CASE WHEN o.a IS NOT NULL AND o.c IS NOT NULL AND o.c >= o.a THEN epoch(o.c - o.a) / 86400.0 END AS handling_days,
  CASE WHEN o.c IS NOT NULL AND o.d >= o.c THEN epoch(o.d - o.c) / 86400.0 END AS transit_days,
  date_diff('day', CAST(o.p AS DATE), CAST(o.e AS DATE)) AS est_lead_days_cal,
  date_diff('day', CAST(o.p AS DATE), CAST(o.d AS DATE)) AS act_lead_days_cal,
  CASE WHEN epoch(o.d - o.p) / 86400.0 > 60 THEN 1 ELSE 0 END AS lead_outlier,
  r.review_score
FROM o
LEFT JOIN cu ON o.customer_id = cu.customer_id
LEFT JOIN r ON o.order_id = r.order_id AND r.rn = 1
WHERE o.d IS NOT NULL
  AND CAST(o.d AS DATE) >= CAST(o.p AS DATE)
  AND CAST(o.e AS DATE) >= CAST(o.p AS DATE)
