# Data Governance for Engineers — CTP Portfolio (ShopFast Case Study)

**Student:** **SELIM ABOULEILA**  
**Course:** Data Governance for Engineers (EFREI 2026)  
**Case Study:** ShopFast (French E-Commerce Platform)

---

## Overview

This repository contains the practical Data Governance engineering labs (**CTPs**) completed by **Selim Abouleila** on the **ShopFast** e-commerce dataset.

## Repository Structure

| Folder | Lab / Session | Key Deliverables |
| :--- | :--- | :--- |
| [`01_CM2_Lab/`](./01_CM2_Lab) | **CM 2 / CTP 1 — Data Inventory & Governance Roles** | • [`data_inventory_template.csv`](./01_CM2_Lab/data_inventory_template.csv) — Complete inventory of all 7 ShopFast datasets with business descriptions, Owner/Steward/Custodian assignments, Personal Data (GDPR) flags, sensitivity classification, exact row counts, and data quality findings.<br>• [`explore_shopfast.sql`](./01_CM2_Lab/explore_shopfast.sql) — PostgreSQL diagnostic queries on `raw.*`. |
| [`CTP2/`](./CTP2) | **CTP 2 — Data Quality Profiling, OpenRefine Cleansing & Great Expectations** | • [`quality_scorecard.csv`](./CTP2/quality_scorecard.csv) — 13 measured data quality rules across all 6 dimensions (`Completeness`, `Uniqueness`, `Validity`, `Consistency`, `Accuracy`, `Timeliness`), with severity ratings and Owner/Steward/Custodian remediation responsibility.<br>• [`profile_customers.py`](./CTP2/profile_customers.py) — Pandas profiling script computing the exact scorecard metrics.<br>• [`customers_clean.csv`](./CTP2/customers_clean.csv) & [`openrefine_customers_recipe.json`](./CTP2/openrefine_customers_recipe.json) — Cleaned customer dataset and replayable OpenRefine GREL operations recipe.<br>• [`gx_orders.py`](./CTP2/gx_orders.py) & [`gx_orders_data_docs.png`](./CTP2/gx_orders_data_docs.png) — Completed 12-expectation Great Expectations suite for `orders.csv` + Data Docs report screenshot.<br>• [`gx_payments.py`](./CTP2/gx_payments.py) — Great Expectations replay of the "cents" incident (`payments.csv` passes; `payments_batch_2.csv` fails `smart_payments`). |
| [`shopfast-kit/`](./shopfast-kit) | **ShopFast Training Kit** | Raw e-commerce CSV datasets (`data/`), PostgreSQL 16 Docker Compose configuration (`docker-compose.yml`, `init/01_load_shopfast.sql`), and environment self-test (`check_setup.py`). |

---

## CTP 2 — Key Highlight: Which Governance Guard Was Missing at ShopFast?

> **One-sentence answer:**  
> **ShopFast was missing an automated data contract and pre-ingestion quality gate enforcing semantic value-range and distribution assertions (min/max EUR bounds and batch mean/median checks) between the payments producer and the landing zone, allowing a schema-compatible unit change from euros to cents (100× inflation) to silently pass structural checks.**

---

*Author: **Selim Abouleila** — EFREI Paris (2026)*
