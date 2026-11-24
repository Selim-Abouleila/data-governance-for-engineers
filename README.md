# Data Governance for Engineers — Student Labs (CTPs)

These represent the CTPs of student **SELIM ABOULEILA** for the Data Governance for Engineers course on the **ShopFast** dataset.

## Folders

- [`01_CM2_Lab/`](./01_CM2_Lab) — **CTP 1 / CM 2**: Data inventory for the 7 ShopFast datasets ([`data_inventory_template.csv`](./01_CM2_Lab/data_inventory_template.csv)) and SQL checks ([`explore_shopfast.sql`](./01_CM2_Lab/explore_shopfast.sql)).
- [`CTP2/`](./CTP2) — **CTP 2**: Data quality scorecard, OpenRefine cleaning recipe, and Great Expectations tests:
  - [`quality_scorecard.csv`](./CTP2/quality_scorecard.csv) & [`profile_customers.py`](./CTP2/profile_customers.py) — 12 quality rules across 6 dimensions with severity and owner/steward/custodian.
  - [`customers_clean.csv`](./CTP2/customers_clean.csv) & [`openrefine_customers_recipe.json`](./CTP2/openrefine_customers_recipe.json) — cleaned customers file and replayable OpenRefine recipe.
  - [`gx_orders.py`](./CTP2/gx_orders.py) & [`gx_orders_data_docs.png`](./CTP2/gx_orders_data_docs.png) — completed 12-expectation suite for `orders.csv` and Data Docs screenshot.
  - [`gx_payments.py`](./CTP2/gx_payments.py) — replay of the "cents" bug (`payments.csv` passes, `payments_batch_2.csv` fails).
- [`shopfast-kit/`](./shopfast-kit) — Raw CSV files, Docker Compose setup for PostgreSQL, and `check_setup.py`.

## Which governance guard was missing at ShopFast?

> ShopFast had no automated data contract or quality gate checking payment amount ranges and averages (min/max, mean, median) before loading new files, so changing amounts from euros to cents (100x bigger) passed basic schema checks.
