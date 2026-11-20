# Research Brief (research)

## Job type
research

## Research questions
- Q1: How good is Olist's delivery service? Measured by on-time rate, average and 90th-percentile lead time, and share of late orders, overall and by month, lane (seller state to customer state), seller and product category.
- Q2: Where and why does delivery fail? For late orders, how much comes from the seller (slow handover to the carrier) and how much from the carrier (slow transit), and which few sellers and lanes account for most late orders (Pareto)?
- Q3: What does lateness cost in customer satisfaction? How do review scores differ between on-time orders and orders late by 1-3 days and by more than 3 days, and how sensitive is that finding to the cut-off chosen?
- Q4: What should be fixed first? Three concrete, data-backed recommendations (for example a seller scorecard with thresholds, or realistic estimated dates on specific lanes), each tied to the size of the problem it targets.

## Judgement standard
- Answered: the data supports a clear numeric answer under the agreed definitions, with the figures produced by code and independently re-checked where the plan marks a step critical.
- Partly answered: an answer exists but with a stated gap (thin months, small groups below the minimum volume, missing timestamps for part of the orders, or association shown but not causation).
- Not answerable: the data cannot support the question under the agreed definitions.
- Q3 can at best show an association between lateness and lower scores, not proof of cause; the report must say so.
- Q4 is answered when each recommendation cites specific results from Q1-Q3.

## Definitions
- Dataset: Olist Brazilian E-Commerce Public Dataset (9 CSV files), supplied by the owner.
- Fact table: one row per order item, joined on order_id, seller_id, customer_id (and product for category).
- Estimated date: the delivery date promised to the customer at purchase. Actual date: delivery to the customer.
- Delay = actual delivery date minus estimated delivery date, in whole calendar days (dates only, time of day ignored). Positive = late.
- On time = delay <= 0 days. Late = delay >= 1 day. Late share = late orders / delivered orders.
- Seller handling time = handed to carrier minus purchase approved. Carrier transit time = delivered to customer minus handed to carrier.
- Lead time = delivered to customer minus purchase time (to be stated precisely in the plan).
- Seller delay vs carrier delay: a late order is split by comparing the two stages with the plan's approved rule, fixed in the plan before data is seen.
- Lane = seller state to customer state.
- Delay bands for Q3: early or on time (<= 0), 1-3 days late, more than 3 days late; other cut-offs tested as sensitivity.
- Pareto: sellers and lanes ranked by number of late orders (all orders counted, no minimum), with cumulative share of late orders.
- Rankings by late-rate use only sellers, lanes and categories with at least 30 delivered orders (final threshold fixed in the plan).

## Assumptions
- Olist is parcel e-commerce delivery, not full-truckload trucking; the report states that operations-quality methods are applied to a parcel network. [confirmed]
- Only orders with status "delivered" are analysed; every removal (cancelled, missing delivery dates, etc.) is counted and documented. [confirmed]
- Dates are compared as calendar dates, and delivering on the promised day counts as on time. [confirmed]
- All delivered orders count for overall figures; monthly trend charts show only months with enough orders (cut-off set in the plan and documented). [confirmed]
- Geolocation has several coordinates per zip prefix; they are averaged. [confirmed]
- Data-quality checks cover negative durations, deliveries before purchase, estimated date before purchase, extreme outliers and duplicate reviews, with a data-quality log of what was found, fixed and why. [confirmed]
- Report spec below is accepted as listed; the owner raised no changes. [inferred]

## Scope
Brazil, all delivered Olist orders in the dataset (2016 to 2018), all sellers, states and product categories.

## Out of scope
- Causal claims about reviews (association only).
- New data beyond the 9 supplied files; no external benchmarks.
- Freight cost, payment analysis and product-level profitability.

## Report spec
- T1 (table): Data-quality log: what was found, removed or fixed, and why, with counts | answers Q1
- T2 (table): Headline KPIs: on-time rate, mean and 90th-percentile lead time, late share | answers Q1
- T3 (table): Top and bottom lanes, sellers and categories by late-rate (minimum volume applied) | answers Q1
- T4 (table): Late orders split into seller delay and carrier delay | answers Q2
- T5 (table): Pareto table of sellers and lanes behind most late orders | answers Q2
- T6 (table): Review score by delay band, plus sensitivity to other cut-offs | answers Q3
- T7 (table): The three recommendations with the size of the problem each targets | answers Q4
- C1 (chart): On-time rate and late share by month (line) | answers Q1
- C2 (chart): Late rate by customer state or main lanes (bar) | answers Q1
- C3 (chart): Seller delay against carrier delay among late orders (stacked bar) | answers Q2
- C4 (chart): Pareto curve of late orders by seller (bars plus cumulative line) | answers Q2
- C5 (chart): Average review score by delay band (bar) | answers Q3
- C6 (chart): Estimated against actual lead time by lane | answers Q4
