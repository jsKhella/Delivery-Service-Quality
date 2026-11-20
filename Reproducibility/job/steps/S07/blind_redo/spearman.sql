WITH r AS (
  SELECT delay_days AS x, review_score AS y
  FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv')
  WHERE review_score IS NOT NULL
),
w AS (
  SELECT rank() OVER (ORDER BY x) AS rx, COUNT(*) OVER (PARTITION BY x) AS cx,
         rank() OVER (ORDER BY y) AS ry, COUNT(*) OVER (PARTITION BY y) AS cy
  FROM r
)
SELECT COUNT(*) AS n, corr(rx + (cx-1)/2.0, ry + (cy-1)/2.0) AS spearman FROM w
