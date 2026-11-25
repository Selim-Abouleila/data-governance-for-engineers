{% docs gross_revenue %}
**Gross revenue (EUR)** is the order total including VAT and shipping, before refunds.
Rule: `gross_revenue_eur = stg_orders.total_amount_eur`.
Example only: an order total of EUR 120.00 gives gross revenue of EUR 120.00.
Owner: Sara Martin (Head of Sales). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
The starter model uses order totals, including pending orders, so this is not a measure of captured cash.
{% enddocs %}

{% docs active_customer %}
**Active customer** is a customer account with at least one non-cancelled order in the last 12 calendar months as of the reporting date.
Rule: join fct_orders to stg_customers on customer_id. For reporting date D, count distinct registered customer_id where status <> 'cancelled' and order_date BETWEEN D - INTERVAL '12 months' AND D.
Both boundary dates are included. Missing dates and future dates do not qualify.
Example only: on 2026-11-25, an account with a non-cancelled order on 2026-04-10 is active for the company but outside the Sales 6-month window.
Owner: Paul Girard (Head of Finance). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
Sales uses the separate label **recently active customer (6 months)**, with the same order rules and a 6-month window.
In dim_customers, D is CURRENT_DATE when the table is built. Use last_order_date >= D - INTERVAL '12 months' after rebuilding for D.
{% enddocs %}

{% docs net_revenue %}
**Net revenue** is order revenue in euros after refunds and excluding VAT, with shipping included.
Formula per order: `ROUND((gross_revenue_eur - refunded_eur) / 1.20, 2)`.
Gross is orders.total_amount_eur. Refunds are the sum of payments.amount where payment_status = 'refunded', or zero when none exist.
Example only: for an order total of EUR 120.00 and refunds of EUR 24.00, net revenue = (120.00 - 24.00) / 1.20 = EUR 80.00.
Owner: Paul Girard (Head of Finance). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
The lab assumes 20% VAT for every order. Shipping is already in the order total and is not added again.
Sales uses **sales revenue including VAT** = gross_revenue_eur - refunded_eur.
The starter model uses order totals, not captured cash. Source errors and every order status remain in this lab calculation.
{% enddocs %}

{% docs churned_customer %}
**Churned customer** is a customer account that ordered before but has no non-cancelled order in the last 12 calendar months as of the reporting date.
Rule: for registered customer accounts and reporting date D, require at least one non-cancelled order dated on or before D, and none with order_date BETWEEN D - INTERVAL '12 months' AND D.
In dim_customers, this means last_order_date < D - INTERVAL '12 months' after rebuilding for D.
Accounts with no dated non-cancelled order are not labelled churned. The rule uses known dates, so undated orders need review.
Example only: on 2026-11-25, an account whose last non-cancelled order was on 2025-10-01 is churned. An account that never ordered is not churned.
Owner: Paul Girard (Head of Finance). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
Use the company 12-month window.
{% enddocs %}

{% docs customer %}
**Customer** is a registered ShopFast account identified by customer_id, whether or not it has placed an order.
Rule: count distinct customer_id in stg_customers after removing exact duplicate rows. Different account IDs remain different customers even if they share an email.
Example only: two copied rows with customer_id 10410 count as one customer. Two different customer IDs with the same email count as two accounts.
Owner: Sara Martin (Head of Sales). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
The dataset identifies accounts, not unique people. A shared email is not enough to merge accounts.
{% enddocs %}

{% docs order %}
**Order** is a purchase request identified by order_id, including pending, shipped, delivered, returned and cancelled requests.
Rule: count distinct order_id in stg_orders. Keep one row per order_id after sorting by order_date.
Include every status for an order count, then apply the separate non-cancelled rule for active customers.
Example only: two source rows with order_id 700001 count as one order. An order with status cancelled still counts as an order but does not make its customer active.
Owner: Sara Martin (Head of Sales). Steward: Karim Benali (Analytics Engineer).
Status: approved for this CTP3 exercise. Decision date: 2026-11-25.
An order is not the same as a captured payment. Payment records are stored separately in stg_payments.
{% enddocs %}
