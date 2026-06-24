import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

inp = ROOT / "data" / "raw" / "02_nav_history.csv"
out = ROOT / "data" / "processed" / "02_nav_history_clean.csv"

df = pd.read_csv(inp)

# Date conversion
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove invalid dates
df = df.dropna(subset=["date"])

# Sort
df = df.sort_values(["amfi_code", "date"])

# Remove duplicates
df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")

# NAV numeric
df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

# Forward fill NAV per scheme
df["nav"] = df.groupby("amfi_code")["nav"].ffill()

# Keep only valid NAVs
df = df[df["nav"] > 0]

out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

print("=" * 50)
print("NAV HISTORY CLEANED")
print("Rows:", len(df))
print("Saved:", out)
print("=" * 50)