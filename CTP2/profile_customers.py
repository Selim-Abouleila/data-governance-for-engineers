"""CTP 2 - Exercise 1: profile customers.csv with pandas.
Student: Selim Abouleila
Run from the CTP2 folder:  python profile_customers.py
"""
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE.parent / "shopfast-kit" / "data" / "customers.csv", dtype=str)
n = len(df)
print("Rows:", n)
print("\nEmpty values per column:\n", df.isna().sum())

scorecard = []


def add_rule(dimension, rule, column, how, failing, severity, owner):
    score_pct = round(100 * (1 - failing / n), 2)
    scorecard.append({
        "dimension": dimension,
        "rule_in_plain_words": rule,
        "column": column,
        "how_you_measured_it": how,
        "failing_rows": int(failing),
        "total_rows": n,
        "score_pct": score_pct,
        "severity_high_medium_low": severity,
        "who_should_fix_owner_steward_custodian": owner,
    })


# Completeness
add_rule("Completeness", "email is not empty", "email", "df['email'].isna().sum()",
         df["email"].isna().sum(), "High", "Steward (contact CRM) & Custodian (make required)")
add_rule("Completeness", "phone is not empty", "phone", "df['phone'].isna().sum()",
         df["phone"].isna().sum(), "Medium", "Steward")
add_rule("Completeness", "country is not empty", "country", "df['country'].isna().sum()",
         df["country"].isna().sum(), "Medium", "Custodian (make country dropdown mandatory)")

# Uniqueness
dup_ids = df["customer_id"].duplicated(keep=False).sum()
print("\nDuplicated customer_id rows:", dup_ids)
add_rule("Uniqueness", "customer_id is unique", "customer_id", "df['customer_id'].duplicated(keep=False).sum()",
         dup_ids, "High", "Custodian (primary key check)")

norm_email = df["email"].dropna().str.strip().str.lower()
dup_emails = norm_email.duplicated(keep=False).sum()
print("Duplicated normalised emails:", dup_emails)
add_rule("Uniqueness", "one account per email (lowercase + trimmed)", "email",
         "df['email'].dropna().str.strip().str.lower().duplicated(keep=False).sum()",
         dup_emails, "High", "Owner (CRM) & Custodian (unique index)")

# Validity
email_re = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"
bad_emails = (~df["email"].dropna().str.match(email_re)).sum()
print("Invalid email format:", bad_emails)
add_rule("Validity", "email has a valid format", "email",
         "(~df['email'].dropna().str.match(email_re)).sum()",
         bad_emails, "High", "Custodian (form validation) & Steward")

tiers = ["bronze", "silver", "gold", "platinum"]
bad_tiers = (~df["loyalty_tier"].isin(tiers)).sum()
print("Invalid loyalty_tier:", bad_tiers)
add_rule("Validity", "loyalty_tier is bronze, silver, gold or platinum", "loyalty_tier",
         "(~df['loyalty_tier'].isin(tiers)).sum()",
         bad_tiers, "Medium", "Steward (fix typos) & Custodian (dropdown/enum)")

is_fr = df["country"].fillna("").str.strip().str.lower().isin(["fr", "france", "fra"])
bad_zip = (is_fr & ~df["postal_code"].fillna("").str.match(r"^\d{5}$")).sum()
print("Bad French postal codes:", bad_zip)
add_rule("Validity", "French postal code has 5 digits", "postal_code",
         "(is_fr & ~df['postal_code'].str.match(r'^\\d{5}$')).sum()",
         bad_zip, "Medium", "Steward (add missing leading 0) & Custodian (store as text)")

# Consistency
print("\nCountry spellings:\n", df["country"].value_counts(dropna=False))
bad_country = (df["country"].notna() & ~df["country"].isin(["FR", "DE", "BE", "ES"])).sum()
add_rule("Consistency", "country uses standard 2-letter code (FR, DE, BE, ES)", "country",
         "(df['country'].notna() & ~df['country'].isin(['FR','DE','BE','ES'])).sum()",
         bad_country, "Medium", "Steward (country mapping) & Custodian")

iso_re = r"^\d{4}-\d{2}-\d{2}$"
bad_signup = (~df["signup_date"].fillna("").str.match(iso_re)).sum()
print("Non-ISO signup_date:", bad_signup)
add_rule("Consistency", "signup_date uses YYYY-MM-DD format", "signup_date",
         "(~df['signup_date'].str.match(r'^\\d{4}-\\d{2}-\\d{2}$')).sum()",
         bad_signup, "Medium", "Custodian (standardise date format)")

# Accuracy
bday = pd.to_datetime(df["birth_date"], format="%Y-%m-%d", errors="coerce")
bad_bday = ((bday < "1906-01-01") | (bday > "2026-11-24")).sum()
print("Unrealistic birth dates:", bad_bday)
add_rule("Accuracy", "birth_date is realistic (between 1906 and today)", "birth_date",
         "((bday < '1906-01-01') | (bday > '2026-11-24')).sum()",
         bad_bday, "Medium", "Steward (check or clear impossible dates)")

# Timeliness
signup_dt = pd.to_datetime(df["signup_date"], format="mixed", dayfirst=True, errors="coerce")
future_signup = (signup_dt.isna() | (signup_dt > "2026-11-24")).sum()
print("Future or unparseable signup_date:", future_signup)
add_rule("Timeliness", "signup_date is not in the future", "signup_date",
         "(signup_dt.isna() | (signup_dt > '2026-11-24')).sum()",
         future_signup, "Low", "Custodian (reject future signup dates)")

out = pd.DataFrame(scorecard)
out.to_csv(HERE / "quality_scorecard.csv", index=False)
print("\nSaved quality_scorecard.csv:")
print(out[["dimension", "column", "failing_rows", "score_pct", "severity_high_medium_low"]].to_string(index=False))
