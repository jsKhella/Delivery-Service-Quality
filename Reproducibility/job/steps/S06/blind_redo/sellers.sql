WITH g AS (
  SELECT seller_id, SUM(late) AS late, COUNT(*) AS delivered
  FROM read_csv_auto('{steps}/S02/exec/outputs/order_seller.csv')
  GROUP BY seller_id
)
SELECT ROW_NUMBER() OVER (ORDER BY late DESC, seller_id ASC) AS rank,
  seller_id, late, delivered,
  SUM(late) OVER (ORDER BY late DESC, seller_id ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_late,
  100.0 * SUM(late) OVER (ORDER BY late DESC, seller_id ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / SUM(late) OVER () AS cum_late_share_pct
FROM g
ORDER BY rank
