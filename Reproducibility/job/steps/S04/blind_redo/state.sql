SELECT customer_state, COUNT(*) AS delivered, SUM(late) AS late,
  100.0*SUM(late)/COUNT(*) AS late_rate_pct,
  COUNT(*) >= 30 AS ranked
FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv')
GROUP BY customer_state
ORDER BY late_rate_pct DESC, delivered DESC, customer_state
