WITH r AS (
  SELECT delay_days, review_score,
         CAST(order_delivered_customer_date AS TIMESTAMP) AS dlv,
         CAST(order_estimated_delivery_date AS TIMESTAMP) AS est
  FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv')
  WHERE review_score IS NOT NULL
),
u AS (
  SELECT 'cut3' AS scheme, CASE WHEN delay_days<=0 THEN '1_on_time' WHEN delay_days<=3 THEN '2_late_1_3' ELSE '3_late_gt3' END AS band, review_score FROM r
  UNION ALL
  SELECT 'cut2', CASE WHEN delay_days<=0 THEN '1_on_time' WHEN delay_days<=2 THEN '2_late_1_2' ELSE '3_late_gt2' END, review_score FROM r
  UNION ALL
  SELECT 'cut5', CASE WHEN delay_days<=0 THEN '1_on_time' WHEN delay_days<=5 THEN '2_late_1_5' ELSE '3_late_gt5' END, review_score FROM r
  UNION ALL
  SELECT 'cut7', CASE WHEN delay_days<=0 THEN '1_on_time' WHEN delay_days<=7 THEN '2_late_1_7' ELSE '3_late_gt7' END, review_score FROM r
  UNION ALL
  SELECT 'strict', CASE WHEN dlv<=est THEN '1_on_time_strict' ELSE '2_late_strict' END, review_score FROM r
)
SELECT scheme, band, COUNT(*) AS n_orders, AVG(review_score) AS mean_score,
       100.0*AVG(CASE WHEN review_score<=2 THEN 1.0 ELSE 0.0 END) AS pct_low_score
FROM u GROUP BY scheme, band ORDER BY scheme, band
