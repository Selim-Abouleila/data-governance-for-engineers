"""CTP 2 - Exercise 4: Replay the 'cents' incident with Great Expectations.
Author: Selim Abouleila

One sentence — which governance guard was missing at ShopFast?
ShopFast was missing an automated data contract and ingestion quality gate with semantic value-range and distribution assertions (mean/median/bounds on EUR amounts) between the payment producer and the analytics landing zone, allowing a schema-compatible unit change from euros to cents (100x inflation) to silently pass structural checks.
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"
files = {
    "payments (history)": KIT + "payments.csv",
    "payments_batch_2 (new)": "payments_batch_2.csv",
}

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast_payments")
asset = source.add_dataframe_asset(name="payments")
batch_def = asset.add_batch_definition_whole_dataframe("whole")
E = gx.expectations

naive = [
    E.ExpectColumnValuesToNotBeNull(column="payment_id"),
    E.ExpectColumnValuesToBeUnique(column="payment_id"),
    E.ExpectColumnValuesToNotBeNull(column="amount"),
    E.ExpectColumnValuesToBeInSet(column="currency", value_set=["EUR"]),
    E.ExpectColumnValuesToBeInSet(
        column="method",
        value_set=["card", "paypal", "apple_pay", "bank_transfer"],
    ),
]

smart = naive + [
    # 1. Row-level value range: a normal ShopFast consumer order payment in EUR is between 0.01 and 5,000 EUR
    E.ExpectColumnValuesToBeBetween(column="amount", min_value=0.01, max_value=5000.0),
    # 2. Batch distribution guard (mean): historical mean is ~154.54 EUR; cents batch shifts mean to ~15,548.88
    E.ExpectColumnMeanToBeBetween(column="amount", min_value=20.0, max_value=500.0),
    # 3. Batch distribution guard (median): historical median is ~119.30 EUR; cents batch shifts median to ~12,322.50
    E.ExpectColumnMedianToBeBetween(column="amount", min_value=20.0, max_value=400.0),
    # 4. Lexical/format guard on raw text: EUR amounts have at most 4 integer digits (and optional .XX decimals)
    E.ExpectColumnValuesToMatchRegex(column="amount_txt", regex=r"^\d{1,4}(\.\d{1,2})?$"),
]


def run(name, expectations, df):
    suite = context.suites.add_or_update(gx.ExpectationSuite(name=name))
    for e in expectations:
        suite.add_expectation(e.copy() if hasattr(e, "copy") else e)
    suite.save()
    return batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)


for label, path in files.items():
    df = pd.read_csv(path, dtype=str)
    df["amount_txt"] = df["amount"]
    df["amount"] = pd.to_numeric(df["amount"])
    for suite_name, exps in [("naive_payments", naive), ("smart_payments", smart)]:
        res = run(suite_name, exps, df)
        failed = [r.expectation_config.type for r in res.results if not r.success]
        print(f"{label:<24} {suite_name:<15} success={str(res.success):<5}  failed={failed}")

print(
    "\nMissing governance guard (one sentence):\n"
    "ShopFast was missing an automated data contract and pre-ingestion quality gate enforcing semantic "
    "value-range and distribution checks (min/max bounds and batch mean/median in EUR) on the payments feed, "
    "which allowed a breaking unit change from euros to cents (100x) to pass naive schema/null checks undetected."
)
