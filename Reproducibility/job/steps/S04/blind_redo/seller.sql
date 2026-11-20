SELECT seller_id, COUNT(*) AS delivered, SUM(late) AS late,
  100.0*SUM(late)/COUNT(*) AS late_rate_pct,
  COUNT(*) >= 30 AS ranked
FROM read_csv_auto('{steps}/S02/exec/outputs/order_seller.csv')
GROUP BY seller_id
ORDER BY late_rate_pct DESC, delivered DESC, seller_id
