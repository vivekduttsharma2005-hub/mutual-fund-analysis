"""
Day 1 - Data Ingestion Script
Mutual Fund Analysis Project

Loads all CSV files from data/raw and displays:
- Shape
- Data Types
- First 5 rows
- Missing Values
- Duplicate Rows

Also saves a dataset summary to reports/dataset_summary.csv
"""

from pathlib import Path
import pandas as pd


# -----------------------------
# Project Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports"


def analyze_dataset(file_path):
    """Analyze a single CSV dataset."""

    print("\n" + "=" * 80)
    print(f"Dataset : {file_path.name}")
    print("=" * 80)

    df = pd.read_csv(file_path)

    print(f"\nShape : {df.shape}")

    print("\nData Types")
    print(df.dtypes)

    print("\nFirst 5 Rows")
    print(df.head())

    print("\nMissing Values")
    print(df.isnull().sum())

    duplicates = df.duplicated().sum()
    print(f"\nDuplicate Rows : {duplicates}")

    return {
        "Dataset": file_path.name,
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Missing Values": int(df.isnull().sum().sum()),
        "Duplicate Rows": int(duplicates),
    }


def main():

    print("=" * 80)
    print("DAY 1 : DATA INGESTION")
    print("=" * 80)

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    print(f"\nFound {len(csv_files)} CSV files.\n")

    if len(csv_files) == 0:
        print("No CSV files found.")
        print(f"Expected path: {RAW_DATA_DIR}")
        return

    summary = []

    for file in csv_files:
        result = analyze_dataset(file)
        summary.append(result)

    REPORT_DIR.mkdir(exist_ok=True)

    summary_df = pd.DataFrame(summary)

    summary_df.to_csv(
        REPORT_DIR / "dataset_summary.csv",
        index=False
    )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(summary_df)

    print("\nDataset summary saved successfully.")


if __name__ == "__main__":
    main()