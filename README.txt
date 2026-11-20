Analysis of the public Olist dataset (Kaggle) to assess delivery service quality and impact of late deliveries on customer satisfaction.


DELIVERABLES
- 📄 RESULTS.pdf: a quick overview of the results of the researcg
- 📊 Dashboard.xlsx
- 🎞️ Research process.pdf


RESULTs
- 93.2% of delivered orders arrived on or before the promised date. 6.8% (6,534 orders) were late.
- Typical delivery takes 10.2 days (mean 12.6); one order in ten takes more than 23.1 days.
- Where the parcel goes matters more than the purchased product: late rates run from 2.8% to 21.4% across customer states, but only 0% to 13.5% across product categories.
- Most lateness happens after the seller hands over the parcel: the carrier alone is behind 77.7% of classified late order-seller pairs, the seller alone 12.6%, both 9.7%.
- 13.4% of active sellers account for four fifths of late pairs. Much of this reflects order volume.
- Late deliveries go with much lower reviews: 4.29 stars on time, 3.29 one to three days late, 1.85 more than three days late. This is an association, not proof of cause.


METHOD
- Q1 how good is delivery, Q2 where and why it fails, Q3 the effect on review scores, Q4 what to fix first.
- 11 steps: clean the data, link orders to sellers, lanes and categories, compute headline figures, late rates, the seller/carrier split, Pareto concentration, review analysis, promised against actual time, tables and charts, recommendations, findings.
- Every number was produced by code. Each step was reviewed by an independent Verifier. All 7 critical steps were recomputed blind by a second worker with a different method, and the numbers agreed.


DATA SOURCES
- Olist Brazilian E-Commerce Public Dataset (9 CSV files, from Kaggle, supplied by the owner, Tier 2): customers, geolocation, order items, payments, orders, reviews, products, sellers, product category name translation.
- Covers Brazil, 2016 to 2018. Each file was sealed with a fingerprint and checked for changes at every step. No other data and no external benchmarks were used.


LIMITATIONS
- Review scores show an association with lateness, not a cause. Most reviews of late orders were written before the parcel arrived, so low scores partly reflect the wait.
- The data does not name the carrier, so carrier delay cannot be traced to a specific carrier.
- Lateness is measured against Olist's own promised date. Promises are generous (24.4 days promised against 12.5 delivered).
- Sellers, lanes and categories with fewer than 30 orders are not ranked. Months with fewer than 500 delivered orders are left out of the monthly chart.
- The seller and lane concentration mostly reflects where the orders are. Olist is a parcel e-commerce network, not full-truckload trucking.
- Not examined: freight cost, payments, profitability, forecasting.


REPRODUCIBILITY
Sources and code necessary to reproduce the project's findings are available in dedicated folder.


ABOUT ME
Mina Khella. BSc Statistics & Economics, Università degli studi di Milano-Bicocca. 
Linkedin -> https://www.linkedin.com/in/mina-khella-812113182/
e-mail   -> mina.khellas@gmail.com
