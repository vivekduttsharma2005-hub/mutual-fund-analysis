import os
import pandas as pd
from sqlalchemy import create_engine, text

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")

# Create SQLite database
engine = create_engine(f"sqlite:///{DB_PATH}")

# Files to load
tables = {
    "nav_history": "02_nav_history_clean.csv",
    "transactions": "08_investor_transactions_clean.csv",
    "performance": "07_scheme_performance_clean.csv"
}

print("=" * 60)
print("LOADING DATA INTO SQLITE")
print("=" * 60)

for table, filename in tables.items():
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filename}")
        continue

    df = pd.read_csv(filepath)

    df.to_sql(
        table,
        engine,
        if_exists="replace",
        index=False
    )

    print(f"✅ Loaded {table} ({len(df)} rows)")

print("\n" + "=" * 60)
print("VERIFYING TABLES")
print("=" * 60)

with engine.connect() as conn:
    for table in tables.keys():
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        rows = result.scalar()
        print(f"{table:20} : {rows} rows")

print("\n" + "=" * 60)
print("DATABASE CREATED SUCCESSFULLY")
print(DB_PATH)
print("=" * 60)