"""CTP 2 - Exercise 3: expectation suite for ShopFast orders (12 expectations, GX Core 1.x).
Student: Selim Abouleila
Run from the CTP2 folder:  python gx_orders.py
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"
orders = pd.read_csv(KIT + "orders.csv", dtype=str)
customers = pd.read_csv(KIT + "customers.csv", dtype=str)
orders["total_amount_eur"] = pd.to_numeric(orders["total_amount_eur"], errors="coerce")
orders["order_date_dt"] = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast")
asset = source.add_dataframe_asset(name="orders")
batch_def = asset.add_batch_definition_whole_dataframe("all_orders")

suite = context.suites.add_or_update(gx.ExpectationSuite(name="orders_suite"))
E = gx.expectations
for e in [
    E.ExpectTableRowCountToBeBetween(min_value=1000, max_value=100000),
    E.ExpectColumnValuesToNotBeNull(column="order_id"),
    E.ExpectColumnValuesToBeUnique(column="order_id"),
    # 4. customer_id must not be null
    E.ExpectColumnValuesToNotBeNull(column="customer_id"),
    # 5. customer_id must exist in customers.csv
    E.ExpectColumnValuesToBeInSet(column="customer_id", value_set=list(set(customers["customer_id"].dropna()))),
    # 6. order_date must not be null
    E.ExpectColumnValuesToNotBeNull(column="order_date"),
    # 7. order_date must look like YYYY-MM-DD
    E.ExpectColumnValuesToMatchRegex(column="order_date", regex=r"^\d{4}-\d{2}-\d{2}$"),
    # 8. no order in the future
    E.ExpectColumnValuesToBeBetween(column="order_date_dt", min_value=pd.Timestamp("2020-01-01"), max_value=pd.Timestamp("2026-11-24")),
    # 9. status only in allowed values
    E.ExpectColumnValuesToBeInSet(column="status", value_set=["pending", "shipped", "delivered", "cancelled", "returned"]),
    # 10. channel only in allowed values
    E.ExpectColumnValuesToBeInSet(column="channel", value_set=["web", "mobile_app", "marketplace"]),
    # 11. shipping_country only in allowed values
    E.ExpectColumnValuesToBeInSet(column="shipping_country", value_set=["FR", "BE", "DE", "ES"]),
    # 12. total_amount_eur strictly positive and below a sensible max
    E.ExpectColumnValuesToBeBetween(column="total_amount_eur", min_value=0.01, max_value=10000),
]:
    suite.add_expectation(e)
suite.save()

vd = context.validation_definitions.add_or_update(gx.ValidationDefinition(name="orders_validation", data=batch_def, suite=suite))
checkpoint = context.checkpoints.add_or_update(gx.Checkpoint(name="orders_checkpoint", validation_definitions=[vd],
                                                             actions=[gx.checkpoint.UpdateDataDocsAction(name="docs")]))
result = checkpoint.run(batch_parameters={"dataframe": orders})

print("\nTotal expectations:", len(suite.expectations))
print("Suite passed:", result.success)
for vr in result.run_results.values():
    for r in vr.results:
        cfg = r.expectation_config
        print(f"{'PASS' if r.success else 'FAIL'}  {cfg.type:<45} {cfg.kwargs.get('column', ''):<18} unexpected={r.result.get('unexpected_count', '-')}")
print("\nOpen the report: gx/uncommitted/data_docs/local_site/index.html")
