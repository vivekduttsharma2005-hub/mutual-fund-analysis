import pandas as pd
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load dataset
df = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "01_fund_master.csv")

print("=" * 60)
print("UNIQUE FUND HOUSES")
print("=" * 60)
print(df["fund_house"].unique())
print("\nTotal:", df["fund_house"].nunique())

print("\n" + "=" * 60)
print("CATEGORIES")
print("=" * 60)
print(df["category"].unique())
print("\nTotal:", df["category"].nunique())

print("\n" + "=" * 60)
print("SUB-CATEGORIES")
print("=" * 60)
print(df["sub_category"].unique())
print("\nTotal:", df["sub_category"].nunique())

print("\n" + "=" * 60)
print("RISK CATEGORIES")
print("=" * 60)
print(df["risk_category"].unique())
print("\nTotal:", df["risk_category"].nunique())

print("\n" + "=" * 60)
print("SEBI CATEGORY CODES")
print("=" * 60)
print(df["sebi_category_code"].unique())
print("\nTotal:", df["sebi_category_code"].nunique())