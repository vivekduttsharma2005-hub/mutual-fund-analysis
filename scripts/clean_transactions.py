import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

inp = ROOT / "data" / "raw" / "08_investor_transactions.csv"
out = ROOT / "data" / "processed" / "08_investor_transactions_clean.csv"

df = pd.read_csv(inp)

# ------------------------
# Standardize Transaction Type
# ------------------------
df["transaction_type"] = (
    df["transaction_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

mapping = {
    "Sip": "SIP",
    "Lumpsum": "Lumpsum",
    "Redemption": "Redemption"
}

df["transaction_type"] = df["transaction_type"].replace(mapping)

# ------------------------
# Date
# ------------------------
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)

# ------------------------
# Amount
# ------------------------
df["amount_inr"] = pd.to_numeric(
    df["amount_inr"],
    errors="coerce"
)

df = df[df["amount_inr"] > 0]

# ------------------------
# KYC Validation
# ------------------------
valid = ["Verified", "Pending"]

df = df[df["kyc_status"].isin(valid)]

# ------------------------
# Remove duplicates
# ------------------------
df = df.drop_duplicates()

out.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(out, index=False)

print("="*50)
print("INVESTOR TRANSACTIONS CLEANED")
print("Rows:", len(df))
print("Saved:", out)
print("="*50)