SELECT category, COUNT(*) AS delivered, SUM(late) AS late,
  100.0*SUM(late)/COUNT(*) AS late_rate_pct,
  COUNT(*) >= 30 AS ranked
FROM read_csv_auto('{steps}/S02/exec/outputs/order_category.csv')
GROUP BY category
ORDER BY late_rate_pct DESC, delivered DESC, category
