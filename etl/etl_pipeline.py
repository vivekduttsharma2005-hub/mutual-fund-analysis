"""
etl_pipeline.py — Main ETL Pipeline
Extract → Transform → Load for MF Analytics Platform
Bluestock Fintech Capstone
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from transform import (
    clean_nav_data,
    generate_aum_data,
    generate_fund_master,
    generate_sip_data,
    generate_transactions,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "mf_analytics.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# LOAD
# ============================================================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_schema(conn: sqlite3.Connection):
    schema_path = BASE_DIR / "sql" / "schema.sql"
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()
    logger.info("Schema initialized.")


def load_fund_master(conn: sqlite3.Connection, df: pd.DataFrame):
    df_load = df[[
        "scheme_code", "scheme_name", "amc_name", "category",
        "sub_category", "fund_type", "benchmark_index", "expense_ratio", "min_investment",
    ]].copy()
    df_load.to_sql("dim_fund", conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_load)} rows into dim_fund")


def load_nav_data(conn: sqlite3.Connection, nav_df: pd.DataFrame, fund_master: pd.DataFrame):
    fund_id_map = dict(zip(fund_master["scheme_code"].astype(str), range(1, len(fund_master) + 1)))
    nav_df["fund_id"] = nav_df["scheme_code"].astype(str).map(fund_id_map)
    nav_df = nav_df.dropna(subset=["fund_id"])
    nav_df["fund_id"] = nav_df["fund_id"].astype(int)

    df_load = nav_df[[
        "fund_id", "nav_date", "nav_value", "day_change", "day_change_pct",
        "rolling_7d_high", "rolling_7d_low", "rolling_30d_avg",
    ]].rename(columns={
        "rolling_7d_high": "week_high",
        "rolling_7d_low": "week_low",
        "rolling_30d_avg": "month_high",
    }).copy()
    df_load["nav_date"] = df_load["nav_date"].astype(str)
    df_load.to_sql("fact_nav", conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_load)} rows into fact_nav")


def load_aum_data(conn: sqlite3.Connection, aum_df: pd.DataFrame, fund_master: pd.DataFrame):
    fund_rows = fund_master.copy()
    amc_first_fund = fund_rows.drop_duplicates("amc_name")[["amc_name", "scheme_code"]]
    amc_first_fund["fund_id"] = range(1, len(amc_first_fund) + 1)
    merged = aum_df.merge(amc_first_fund[["amc_name", "fund_id"]], on="amc_name", how="left")
    merged = merged.dropna(subset=["fund_id"])
    merged["fund_id"] = merged["fund_id"].astype(int)
    df_load = merged[["fund_id", "amc_name", "report_month", "aum_crore", "aum_change_pct", "folio_count"]]
    df_load.to_sql("fact_aum", conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_load)} rows into fact_aum")


def load_sip_data(conn: sqlite3.Connection, sip_df: pd.DataFrame, fund_master: pd.DataFrame):
    amc_first_fund = fund_master.drop_duplicates("amc_name")[["amc_name"]].copy()
    amc_first_fund["fund_id"] = range(1, len(amc_first_fund) + 1)
    merged = sip_df.merge(amc_first_fund, on="amc_name", how="left")
    merged = merged.dropna(subset=["fund_id"])
    merged["fund_id"] = merged["fund_id"].astype(int)
    df_load = merged[[
        "fund_id", "report_month", "sip_amount_crore", "sip_count",
        "new_sip_count", "stopped_sip_count", "avg_sip_amount",
    ]]
    df_load.to_sql("fact_sip", conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_load)} rows into fact_sip")


def load_transactions(conn: sqlite3.Connection, txn_df: pd.DataFrame, fund_master: pd.DataFrame):
    amc_first_fund = fund_master.drop_duplicates("amc_name")[["amc_name"]].copy()
    amc_first_fund["fund_id"] = range(1, len(amc_first_fund) + 1)
    merged = txn_df.merge(amc_first_fund, on="amc_name", how="left")
    merged = merged.dropna(subset=["fund_id"])
    merged["fund_id"] = merged["fund_id"].astype(int)
    merged["nav_at_txn"] = 50.0  # placeholder — would join from fact_nav by date
    merged["units"] = merged["txn_amount"] / merged["nav_at_txn"]
    merged["txn_date"] = merged["txn_date"].astype(str)
    df_load = merged[[
        "fund_id", "investor_id", "folio_number", "txn_date", "txn_type",
        "txn_amount", "nav_at_txn", "units", "state", "city_tier",
        "investor_age", "investor_gender", "channel",
    ]]
    df_load.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_load)} rows into fact_transactions")


# ============================================================
# PIPELINE ORCHESTRATOR
# ============================================================

def run_pipeline():
    logger.info("=" * 60)
    logger.info("MF Analytics ETL Pipeline — Starting")
    logger.info("=" * 60)

    # --- EXTRACT & TRANSFORM ---
    logger.info("[Step 1] Generating Fund Master...")
    fund_master = generate_fund_master()

    logger.info("[Step 2] Generating AUM data...")
    aum_df = generate_aum_data()

    logger.info("[Step 3] Generating SIP data...")
    sip_df = generate_sip_data()

    logger.info("[Step 4] Generating Transactions...")
    txn_df = generate_transactions()

    logger.info("[Step 5] Building synthetic NAV data...")
    nav_df = _build_synthetic_nav(fund_master)

    logger.info("[Step 6] Cleaning NAV data...")
    nav_cleaned = clean_nav_data(nav_df)

    # --- LOAD ---
    logger.info("[Step 7] Loading into SQLite database...")
    conn = get_connection()
    init_schema(conn)
    load_fund_master(conn, fund_master)
    load_nav_data(conn, nav_cleaned, fund_master)
    load_aum_data(conn, aum_df, fund_master)
    load_sip_data(conn, sip_df, fund_master)
    load_transactions(conn, txn_df, fund_master)
    conn.close()

    logger.info("=" * 60)
    logger.info(f"Pipeline complete. DB saved to: {DB_PATH}")
    logger.info("=" * 60)


def _build_synthetic_nav(fund_master: pd.DataFrame) -> pd.DataFrame:
    """Build 5-year synthetic NAV history with realistic returns per category"""
    import numpy as np
    np.random.seed(42)

    category_params = {
        "Large Cap":         {"mu": 0.00045, "sigma": 0.012, "base_nav": 45.0},
        "Mid Cap":           {"mu": 0.00060, "sigma": 0.016, "base_nav": 32.0},
        "Small Cap":         {"mu": 0.00075, "sigma": 0.022, "base_nav": 28.0},
        "Aggressive Hybrid": {"mu": 0.00040, "sigma": 0.009, "base_nav": 55.0},
        "Balanced Advantage":{"mu": 0.00035, "sigma": 0.007, "base_nav": 38.0},
        "ELSS":              {"mu": 0.00055, "sigma": 0.014, "base_nav": 60.0},
        "Flexi Cap":         {"mu": 0.00050, "sigma": 0.013, "base_nav": 42.0},
        "Index":             {"mu": 0.00042, "sigma": 0.011, "base_nav": 140.0},
        "Value":             {"mu": 0.00048, "sigma": 0.013, "base_nav": 35.0},
        "Large & Mid Cap":   {"mu": 0.00052, "sigma": 0.014, "base_nav": 50.0},
    }

    dates = pd.date_range("2020-01-01", "2025-06-30", freq="B")
    all_navs = []

    for _, fund in fund_master.iterrows():
        sub_cat = fund["sub_category"]
        params = category_params.get(sub_cat, {"mu": 0.00045, "sigma": 0.012, "base_nav": 40.0})
        returns = np.random.normal(params["mu"], params["sigma"], len(dates))
        nav_series = params["base_nav"] * (1 + pd.Series(returns)).cumprod().values

        for i, (date, nav) in enumerate(zip(dates, nav_series)):
            all_navs.append({
                "scheme_code": fund["scheme_code"],
                "scheme_name": fund["scheme_name"],
                "nav_date": date,
                "nav_value": round(float(nav), 4),
            })

    return pd.DataFrame(all_navs)


if __name__ == "__main__":
    run_pipeline()
