WITH r AS (
  SELECT delay_days AS x, review_score AS y
  FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv')
  WHERE review_score IS NOT NULL
),
k AS (
  SELECT RANK() OVER (ORDER BY x) + (COUNT(*) OVER (PARTITION BY x) - 1) / 2.0 AS rx,
         RANK() OVER (ORDER BY y) + (COUNT(*) OVER (PARTITION BY y) - 1) / 2.0 AS ry
  FROM r
)
SELECT CORR(rx, ry) AS spearman, COUNT(*) AS n FROM k
