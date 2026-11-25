1. Changing payment amounts from euros to cents without conversion makes stg_payments.amount 100 times too large.
2. In fct_orders, refunds become too large and net revenue becomes wrong; dim_customers.lifetime_net_revenue_eur is then wrong too.
3. The affected consumers are sales_dashboard, finance_monthly_revenue_report and churn_prediction_model; order counts and last-order dates do not change.
4. Warn Sara Martin (Sales), Paul Girard (Finance) and Karim Benali (steward); test amounts at 0.01-5000 EUR, mean at 20-500 EUR and median at 20-400 EUR, as in CTP2.
5. Paul Girard must approve the unit change with Sara Martin; Karim updates the contract, converts cents to euros with amount / 100 and reruns the tests before release.
