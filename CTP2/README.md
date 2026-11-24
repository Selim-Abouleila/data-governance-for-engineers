# CTP 2 — Data Quality, OpenRefine & Great Expectations

**Student:** Selim Abouleila

## Files

- [`profile_customers.py`](./profile_customers.py) & [`quality_scorecard.csv`](./quality_scorecard.csv) — Profiles `customers.csv` with pandas and saves 12 quality rules across 6 dimensions (`Completeness`, `Uniqueness`, `Validity`, `Consistency`, `Accuracy`, `Timeliness`).
- [`openrefine_customers_recipe.json`](./openrefine_customers_recipe.json) & [`customers_clean.csv`](./customers_clean.csv) — Replayable OpenRefine recipe that fixes names, emails, countries, leading zeros in postal codes, loyalty tiers, date formats, impossible birth dates, and duplicate `customer_id` rows (`1241 -> 1233` rows).
- [`gx_orders.py`](./gx_orders.py) & [`gx_orders_data_docs.png`](./gx_orders_data_docs.png) — Completed Great Expectations suite with 12 expectations on `orders.csv` and screenshot of the Data Docs report.
- [`gx_payments.py`](./gx_payments.py) — Tests `payments.csv` (passes both `naive_payments` and `smart_payments`) and `payments_batch_2.csv` (passes `naive_payments` but fails `smart_payments` because of the 100x cents error).

## Which governance guard was missing at ShopFast?

> ShopFast had no automated data contract or quality gate checking payment amount ranges and averages (min/max, mean, median) before loading new files, so changing amounts from euros to cents (100x bigger) passed basic schema checks.
