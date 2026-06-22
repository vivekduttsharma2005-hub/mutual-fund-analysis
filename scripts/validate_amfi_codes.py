import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

fund_master = pd.read_csv(PROJECT_ROOT/"data/raw/01_fund_master.csv")
nav_history = pd.read_csv(PROJECT_ROOT/"data/raw/02_nav_history.csv")

master_codes = set(fund_master["amfi_code"])
nav_codes = set(nav_history["amfi_code"])

missing = master_codes - nav_codes

print("="*60)
print("AMFI CODE VALIDATION")
print("="*60)

print("Fund Master Codes :", len(master_codes))
print("NAV History Codes :", len(nav_codes))
print("Missing Codes :", len(missing))

if missing:
    print("\nMissing Codes:")
    print(sorted(missing))
else:
    print("\nAll AMFI codes are present.")