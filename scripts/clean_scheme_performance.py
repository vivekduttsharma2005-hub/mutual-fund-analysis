import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

inp = ROOT / "data" / "raw" / "07_scheme_performance.csv"
out = ROOT / "data" / "processed" / "07_scheme_performance_clean.csv"

df = pd.read_csv(inp)

# Convert return columns to numeric
return_cols = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct"
]

for col in return_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Expense ratio
if "expense_ratio_pct" in df.columns:
    df["expense_ratio_pct"] = pd.to_numeric(
        df["expense_ratio_pct"],
        errors="coerce"
    )

    anomalies = df[
        (df["expense_ratio_pct"] < 0.1) |
        (df["expense_ratio_pct"] > 2.5)
    ]

    print("\nExpense Ratio Anomalies:", len(anomalies))

# Remove duplicates
df = df.drop_duplicates()

out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

print("="*50)
print("SCHEME PERFORMANCE CLEANED")
print("Rows:", len(df))
print("Saved:", out)
print("="*50)