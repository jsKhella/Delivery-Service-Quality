SELECT lane, any_value(seller_state) AS seller_state, any_value(customer_state) AS customer_state,
 count(*) AS delivered, sum(late) AS late_pairs,
 100.0*sum(late)/count(*) AS late_rate_pct,
 avg(est_lead_days_cal) AS est_lead_mean_days,
 avg(act_lead_days_cal) AS act_lead_mean_days,
 avg(date_diff('day', CAST(order_delivered_customer_date AS DATE), CAST(order_estimated_delivery_date AS DATE))) AS buffer_mean_days,
 quantile_cont(act_lead_days_cal, 0.9) AS act_lead_p90_days,
 count(*) >= 30 AS ranked
FROM read_csv_auto('{steps}/S02/exec/outputs/order_seller.csv')
GROUP BY lane ORDER BY lane
