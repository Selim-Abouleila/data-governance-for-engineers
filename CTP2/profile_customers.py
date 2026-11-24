"""CTP 2 - Exercise 1: profile customers.csv with pandas and generate quality_scorecard.csv.
Author: Selim Abouleila
Run from the CTP2 folder:  python profile_customers.py
"""
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
KIT_DATA = HERE.parent / "shopfast-kit" / "data"

df = pd.read_csv(KIT_DATA / "customers.csv", dtype=str)
n = len(df)
print(f"Total rows in customers.csv: {n}")

# 1. Completeness: email is filled
missing_email = int(df["email"].isna().sum())

# 2. Completeness: phone is filled
missing_phone = int(df["phone"].isna().sum())

# 3. Completeness: country is filled
missing_country = int(df["country"].isna().sum())

# 4. Uniqueness: customer_id is unique
dup_customer_id_rows = int(df["customer_id"].duplicated(keep=False).sum())

# 5. Uniqueness (TODO 1): normalised email (strip + lower case) is unique across non-null emails
norm_email = df["email"].dropna().str.strip().str.lower()
dup_norm_email_rows = int(norm_email.duplicated(keep=False).sum())

# 6. Validity (TODO 2): email matches ^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$ (among non-null emails)
email_regex = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"
invalid_email_rows = int((~df["email"].dropna().str.match(email_regex)).sum())

# 7. Consistency (TODO 3): country uses standard ISO-2 code in {FR, DE, BE, ES}
print("\nDistinct country spellings (value_counts):")
print(df["country"].value_counts(dropna=False))
num_country_spellings = int(df["country"].nunique(dropna=True))
non_standard_country_rows = int((df["country"].notna() & (~df["country"].isin(["FR", "DE", "BE", "ES"]))).sum())

# 8. Consistency (TODO 4): signup_date is in ISO format YYYY-MM-DD
iso_date_regex = r"^\d{4}-\d{2}-\d{2}$"
bad_signup_format_rows = int((~df["signup_date"].fillna("").str.match(iso_date_regex)).sum())

# 9. Consistency: birth_date is in ISO format YYYY-MM-DD
bad_bday_format_rows = int((~df["birth_date"].fillna("").str.match(iso_date_regex)).sum())

# 10. Validity (TODO 5): loyalty_tier in {bronze, silver, gold, platinum}
valid_tiers = {"bronze", "silver", "gold", "platinum"}
invalid_loyalty_tier_rows = int((~df["loyalty_tier"].fillna("").isin(valid_tiers)).sum())

# 11. Accuracy (TODO 6): birth_date is realistic (not in the future and not before 1906-01-01)
bday_dt = pd.to_datetime(df["birth_date"], format="%Y-%m-%d", errors="coerce")
unrealistic_bday_rows = int(((bday_dt < "1906-01-01") | (bday_dt > "2026-11-24")).sum())
print("\nUnrealistic ISO birth dates (<1906 or >2026-11-24):", df.loc[(bday_dt < "1906-01-01") | (bday_dt > "2026-11-24"), ["customer_id", "birth_date"]].to_dict(orient="records"))

# 12. Validity (TODO 7): French postal codes have exactly 5 digits
is_france = df["country"].fillna("").str.strip().str.lower().isin({"fr", "france", "fra"})
bad_fr_postal_rows = int((is_france & (~df["postal_code"].fillna("").str.match(r"^\d{5}$"))).sum())
bad_all_postal_rows = int((~df["postal_code"].fillna("").str.match(r"^\d{5}$")).sum())
print(f"Bad French postal codes: {bad_fr_postal_rows} (All rows non-5-digit postal_code: {bad_all_postal_rows})")

# 13. Timeliness: signup_date is not in the future (<= 2026-11-24) and chronologically valid
signup_dt = pd.to_datetime(df["signup_date"], format="%Y-%m-%d", errors="coerce")
future_signup_rows = int((signup_dt > "2026-11-24").sum())
print(f"Future signup_date (>2026-11-24): {future_signup_rows}")

rules = [
    ("Completeness", "email is filled (not null)", "email", "df['email'].isna().sum()", missing_email, n, "High", "Steward (CRM Data Steward) & Custodian (enforce NOT NULL at signup)"),
    ("Completeness", "phone is filled (not null)", "phone", "df['phone'].isna().sum()", missing_phone, n, "Medium", "Steward (CRM Data Steward)"),
    ("Completeness", "country is filled (not null)", "country", "df['country'].isna().sum()", missing_country, n, "Medium", "Steward (CRM Data Steward) & Custodian (mandatory dropdown in UI)"),
    ("Uniqueness", "customer_id is unique across all rows", "customer_id", "df['customer_id'].duplicated(keep=False).sum()", dup_customer_id_rows, n, "High", "Custodian (Data Platform Team - primary key constraint & ingestion dedup)"),
    ("Uniqueness", "normalised email (strip + lowercase) belongs to a single customer", "email", "df['email'].dropna().str.strip().str.lower().duplicated(keep=False).sum()", dup_norm_email_rows, n, "High", "Owner (Head of CRM) & Custodian (unique index on lower(trim(email)))"),
    ("Validity", "email matches standard email syntax ^[^@\\s]+@[^@\\s]+\\.[a-zA-Z]{2,}$", "email", "(~df['email'].dropna().str.match(r'^[^@\\s]+@[^@\\s]+\\.[a-zA-Z]{2,}$')).sum()", invalid_email_rows, n, "High", "Custodian (frontend/API email validation) & Steward (quarantine invalid emails)"),
    ("Validity", "loyalty_tier is in allowed set {bronze, silver, gold, platinum}", "loyalty_tier", "(~df['loyalty_tier'].isin(['bronze','silver','gold','platinum'])).sum()", invalid_loyalty_tier_rows, n, "Medium", "Steward (normalise casing/typos like 'Platinium') & Custodian (ENUM/CHECK constraint)"),
    ("Validity", "French postal_code has exactly 5 digits (^\\d{5}$)", "postal_code", "(is_france & ~df['postal_code'].str.match(r'^\\d{5}$')).sum()", bad_fr_postal_rows, n, "Medium", "Steward (restore leading zeros / fix truncated codes) & Custodian (store as TEXT(5))"),
    ("Consistency", "country uses canonical ISO-2 code in {FR, DE, BE, ES} (17 distinct spellings found)", "country", "(df['country'].notna() & ~df['country'].isin(['FR','DE','BE','ES'])).sum()", non_standard_country_rows, n, "Medium", "Steward (define ISO-2 mapping reference table) & Custodian (enforce country lookup)"),
    ("Consistency", "signup_date is formatted as ISO-8601 YYYY-MM-DD", "signup_date", "(~df['signup_date'].str.match(r'^\\d{4}-\\d{2}-\\d{2}$')).sum()", bad_signup_format_rows, n, "Medium", "Custodian (parse & store as DATE type in Silver layer)"),
    ("Consistency", "birth_date is formatted as ISO-8601 YYYY-MM-DD", "birth_date", "(~df['birth_date'].str.match(r'^\\d{4}-\\d{2}-\\d{2}$')).sum()", bad_bday_format_rows, n, "Medium", "Custodian (parse & store as DATE type in Silver layer)"),
    ("Accuracy", "birth_date is plausible (between 1906-01-01 and current date)", "birth_date", "((bday_dt < '1906-01-01') | (bday_dt > '2026-11-24')).sum()", unrealistic_bday_rows, n, "Medium", "Steward (nullify or verify impossible dates like 1890 or future 2028)"),
    ("Timeliness", "signup_date is a parseable current/historical ISO date (not unparseable or future)", "signup_date", "(pd.to_datetime(df['signup_date'], format='%Y-%m-%d', errors='coerce').isna() | (signup_dt > '2026-11-24')).sum()", int((signup_dt.isna() | (signup_dt > "2026-11-24")).sum()), n, "Low", "Custodian (standardise ingestion timestamp & reject future dates)"),
]

scorecard_rows = []
for dim, rule, col, how, fail, total, sev, fixer in rules:
    score_pct = round(100.0 * (1.0 - fail / total), 2)
    scorecard_rows.append({
        "dimension": dim,
        "rule_in_plain_words": rule,
        "column": col,
        "how_you_measured_it": how,
        "failing_rows": fail,
        "total_rows": total,
        "score_pct": score_pct,
        "severity_high_medium_low": sev,
        "who_should_fix_owner_steward_custodian": fixer,
    })

scorecard_df = pd.DataFrame(scorecard_rows)
scorecard_df.to_csv(HERE / "quality_scorecard.csv", index=False)
scorecard_df.to_csv(HERE / "quality_scorecard_template.csv", index=False)
print("\nGenerated quality_scorecard.csv with", len(scorecard_df), "rules across", scorecard_df["dimension"].nunique(), "dimensions:")
print(scorecard_df[["dimension", "column", "failing_rows", "total_rows", "score_pct", "severity_high_medium_low"]].to_string(index=False))
