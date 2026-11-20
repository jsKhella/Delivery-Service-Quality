WITH o AS (SELECT * FROM read_csv_auto('{steps}/S01/exec/outputs/orders_clean.csv'))
SELECT 'delivered_orders' AS metric, CAST(COUNT(*) AS DOUBLE) AS value, 'orders' AS unit FROM o
UNION ALL SELECT 'on_time_rate_pct', 100.0*AVG(CASE WHEN delay_days<=0 THEN 1.0 ELSE 0.0 END), 'percent' FROM o
UNION ALL SELECT 'late_share_pct', 100.0*AVG(CASE WHEN delay_days>=1 THEN 1.0 ELSE 0.0 END), 'percent' FROM o
UNION ALL SELECT 'n_late_orders', CAST(COUNT(*) AS DOUBLE), 'orders' FROM o WHERE delay_days>=1
UNION ALL SELECT 'lead_mean_days', AVG(lead_time_days), 'days' FROM o
UNION ALL SELECT 'lead_median_days', MEDIAN(lead_time_days), 'days' FROM o
UNION ALL SELECT 'lead_p90_days', quantile_cont(lead_time_days, 0.9), 'days' FROM o
UNION ALL SELECT 'mean_delay_late_days', AVG(delay_days), 'days' FROM o WHERE delay_days>=1
UNION ALL SELECT 'handling_mean_days', AVG(handling_days), 'days' FROM o
UNION ALL SELECT 'transit_mean_days', AVG(transit_days), 'days' FROM o
