SELECT order_id, seller_id, lane, delay_days, shipping_limit_date, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, handling_days, transit_days,
  CASE WHEN order_delivered_carrier_date IS NULL OR CAST(order_delivered_customer_date AS TIMESTAMP) < CAST(order_delivered_carrier_date AS TIMESTAMP) THEN 'unclassified'
       WHEN CAST(order_delivered_carrier_date AS DATE) <= CAST(shipping_limit_date AS DATE) THEN 'carrier only'
       WHEN (CAST(order_delivered_customer_date AS DATE) - CAST(order_delivered_carrier_date AS DATE)) > (CAST(order_estimated_delivery_date AS DATE) - CAST(shipping_limit_date AS DATE)) THEN 'both'
       ELSE 'seller only' END AS split_class,
  CASE WHEN delay_days BETWEEN 1 AND 3 THEN '1-3' WHEN delay_days BETWEEN 4 AND 7 THEN '4-7' WHEN delay_days BETWEEN 8 AND 14 THEN '8-14' ELSE '15+' END AS days_late_band
FROM read_csv_auto('{steps}/S02/exec/outputs/order_seller.csv')
WHERE late = 1
