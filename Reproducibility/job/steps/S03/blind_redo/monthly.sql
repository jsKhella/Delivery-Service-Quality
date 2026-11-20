SELECT purchase_month AS month,
  COUNT(*) AS delivered,
  SUM(CASE WHEN delay_days>=1 THEN 1 ELSE 0 END) AS late,
  100.0*AVG(CASE WHEN delay_days<=0 THEN 1.0 ELSE 0.0 END) AS on_time_rate_pct,
  100.0*AVG(CASE WHEN delay_days>=1 THEN 1.0 ELSE 0.0 END) AS late_share_pct,
  AVG(lead_time_days) AS lead_mean_days,
  COUNT(*) >= 500 AS shown
FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv')
GROUP BY purchase_month ORDER BY purchase_month
