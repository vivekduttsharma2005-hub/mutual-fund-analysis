"""
dashboard_data.py — Dashboard Data Preparation
Exports clean CSVs for Power BI / Tableau dashboard
Bluestock Fintech Capstone
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "mf_analytics.db"
DASHBOARD_DIR = Path(__file__).parent / "exports"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


def get_conn():
    return sqlite3.connect(DB_PATH)


# ============================================================
# PAGE 1: Market Overview
# ============================================================

def export_market_overview():
    conn = get_conn()

    # AUM by AMC (latest month)
    aum_latest = pd.read_sql_query("""
        SELECT a.amc_name, SUM(a.aum_crore) as aum_crore,
               SUM(a.folio_count) as folio_count, MAX(a.report_month) as as_of
        FROM fact_aum a
        WHERE a.report_month = (SELECT MAX(report_month) FROM fact_aum)
        GROUP BY a.amc_name ORDER BY aum_crore DESC
    """, conn)
    aum_latest["market_share_pct"] = (aum_latest["aum_crore"] / aum_latest["aum_crore"].sum() * 100).round(2)
    aum_latest.to_csv(DASHBOARD_DIR / "p1_aum_by_amc.csv", index=False)
    logger.info(f"Exported p1_aum_by_amc.csv ({len(aum_latest)} rows)")

    # Monthly AUM trend
    aum_trend = pd.read_sql_query("""
        SELECT report_month, SUM(aum_crore) as total_aum_crore,
               SUM(folio_count) as total_folios
        FROM fact_aum GROUP BY report_month ORDER BY report_month
    """, conn)
    aum_trend.to_csv(DASHBOARD_DIR / "p1_aum_trend.csv", index=False)
    logger.info(f"Exported p1_aum_trend.csv ({len(aum_trend)} rows)")

    # Monthly SIP trend
    sip_trend = pd.read_sql_query("""
        SELECT report_month, SUM(sip_amount_crore) as sip_crore,
               SUM(sip_count) as sip_count
        FROM fact_sip GROUP BY report_month ORDER BY report_month
    """, conn)
    sip_trend.to_csv(DASHBOARD_DIR / "p1_sip_trend.csv", index=False)
    logger.info(f"Exported p1_sip_trend.csv ({len(sip_trend)} rows)")

    # Category-wise AUM
    cat_aum = pd.read_sql_query("""
        SELECT f.category, SUM(a.aum_crore) as aum_crore
        FROM fact_aum a JOIN dim_fund f ON a.fund_id = f.fund_id
        WHERE a.report_month = (SELECT MAX(report_month) FROM fact_aum)
        GROUP BY f.category ORDER BY aum_crore DESC
    """, conn)
    cat_aum.to_csv(DASHBOARD_DIR / "p1_category_aum.csv", index=False)
    logger.info(f"Exported p1_category_aum.csv")

    conn.close()


# ============================================================
# PAGE 2: Fund Performance & Risk
# ============================================================

def export_fund_performance():
    metrics_path = BASE_DIR / "metrics" / "fund_sharpe_ranks.csv"
    var_path = BASE_DIR / "metrics" / "var_drawdown_summary.csv"

    if metrics_path.exists():
        sharpe_df = pd.read_csv(metrics_path)
        sharpe_df.to_csv(DASHBOARD_DIR / "p2_sharpe_sortino.csv", index=False)
        logger.info(f"Exported p2_sharpe_sortino.csv ({len(sharpe_df)} rows)")

    if var_path.exists():
        var_df = pd.read_csv(var_path)
        var_df.to_csv(DASHBOARD_DIR / "p2_var_drawdown.csv", index=False)
        logger.info(f"Exported p2_var_drawdown.csv ({len(var_df)} rows)")

    conn = get_conn()
    # Latest NAV snapshot per fund
    nav_snapshot = pd.read_sql_query("""
        SELECT f.scheme_name, f.amc_name, f.category, f.sub_category,
               n.nav_value, n.nav_date, n.day_change_pct
        FROM fact_nav n
        JOIN dim_fund f ON n.fund_id = f.fund_id
        WHERE n.nav_date = (SELECT MAX(nav_date) FROM fact_nav)
        ORDER BY f.category, n.nav_value DESC
    """, conn)
    nav_snapshot.to_csv(DASHBOARD_DIR / "p2_nav_snapshot.csv", index=False)
    logger.info(f"Exported p2_nav_snapshot.csv ({len(nav_snapshot)} rows)")
    conn.close()


# ============================================================
# PAGE 3: Investor Demographics
# ============================================================

def export_investor_demographics():
    conn = get_conn()

    # State-wise investor summary
    state_data = pd.read_sql_query("""
        SELECT state,
               COUNT(DISTINCT investor_id) as investors,
               SUM(txn_amount) as total_invested,
               AVG(txn_amount) as avg_ticket,
               SUM(CASE WHEN txn_type='SIP' THEN txn_amount ELSE 0 END) as sip_amount,
               SUM(CASE WHEN txn_type!='SIP' THEN txn_amount ELSE 0 END) as lumpsum_amount
        FROM fact_transactions
        WHERE txn_type IN ('BUY','SIP')
        GROUP BY state ORDER BY investors DESC
    """, conn)
    state_data.to_csv(DASHBOARD_DIR / "p3_state_investors.csv", index=False)
    logger.info(f"Exported p3_state_investors.csv ({len(state_data)} rows)")

    # Age group distribution
    age_data = pd.read_sql_query("""
        SELECT
            CASE
                WHEN investor_age < 25 THEN 'Under 25'
                WHEN investor_age BETWEEN 25 AND 30 THEN '25-30'
                WHEN investor_age BETWEEN 31 AND 40 THEN '31-40'
                WHEN investor_age BETWEEN 41 AND 50 THEN '41-50'
                ELSE 'Above 50'
            END as age_group,
            COUNT(DISTINCT investor_id) as investor_count,
            SUM(txn_amount) as total_invested,
            SUM(CASE WHEN txn_type='SIP' THEN txn_amount ELSE 0 END) as sip_total
        FROM fact_transactions GROUP BY age_group
    """, conn)
    age_data["sip_pct"] = (age_data["sip_total"] / age_data["total_invested"] * 100).round(2)
    age_data.to_csv(DASHBOARD_DIR / "p3_age_distribution.csv", index=False)
    logger.info(f"Exported p3_age_distribution.csv")

    # SIP vs Lumpsum pie
    sip_lump = pd.read_sql_query("""
        SELECT
            CASE WHEN txn_type='SIP' THEN 'SIP' ELSE 'Lumpsum' END as mode,
            COUNT(*) as count, SUM(txn_amount) as amount
        FROM fact_transactions WHERE txn_type IN ('BUY','SIP')
        GROUP BY mode
    """, conn)
    sip_lump.to_csv(DASHBOARD_DIR / "p3_sip_vs_lumpsum.csv", index=False)
    logger.info(f"Exported p3_sip_vs_lumpsum.csv")

    # City tier analysis
    tier_data = pd.read_sql_query("""
        SELECT city_tier, COUNT(DISTINCT investor_id) as investors,
               SUM(txn_amount) as total_invested, AVG(txn_amount) as avg_ticket
        FROM fact_transactions GROUP BY city_tier ORDER BY investors DESC
    """, conn)
    tier_data.to_csv(DASHBOARD_DIR / "p3_city_tier.csv", index=False)
    logger.info(f"Exported p3_city_tier.csv")

    # Gender split
    gender_data = pd.read_sql_query("""
        SELECT investor_gender, COUNT(DISTINCT investor_id) as investors,
               SUM(txn_amount) as total_invested
        FROM fact_transactions GROUP BY investor_gender
    """, conn)
    gender_data.to_csv(DASHBOARD_DIR / "p3_gender_split.csv", index=False)
    logger.info(f"Exported p3_gender_split.csv")

    conn.close()


# ============================================================
# PAGE 4: Portfolio Holdings & Benchmark
# ============================================================

def export_portfolio_and_benchmark():
    conn = get_conn()

    # Sector/Category concentration (sunburst data)
    sunburst = pd.read_sql_query("""
        SELECT f.category, f.sub_category, f.amc_name,
               SUM(a.aum_crore) as aum_crore
        FROM fact_aum a JOIN dim_fund f ON a.fund_id = f.fund_id
        WHERE a.report_month = (SELECT MAX(report_month) FROM fact_aum)
        GROUP BY f.category, f.sub_category, f.amc_name
        ORDER BY f.category, aum_crore DESC
    """, conn)
    sunburst.to_csv(DASHBOARD_DIR / "p4_sunburst_holdings.csv", index=False)
    logger.info(f"Exported p4_sunburst_holdings.csv ({len(sunburst)} rows)")

    # Benchmark comparison — tracking error proxy
    benchmark = pd.read_sql_query("""
        SELECT f.scheme_name, f.benchmark_index, f.sub_category,
               AVG(n.day_change_pct) as avg_daily_return,
               SUM(n.day_change_pct * n.day_change_pct) / COUNT(*) -
                   (AVG(n.day_change_pct) * AVG(n.day_change_pct)) as return_variance
        FROM fact_nav n JOIN dim_fund f ON n.fund_id = f.fund_id
        GROUP BY f.fund_id
        ORDER BY f.benchmark_index, avg_daily_return DESC
    """, conn)
    benchmark["annualised_return_pct"] = (benchmark["avg_daily_return"] * 252 * 100).round(4)
    benchmark["tracking_error_proxy"] = (np.sqrt(benchmark["return_variance"].abs()) * np.sqrt(252) * 100).round(4)
    benchmark.to_csv(DASHBOARD_DIR / "p4_benchmark_comparison.csv", index=False)
    logger.info(f"Exported p4_benchmark_comparison.csv ({len(benchmark)} rows)")

    conn.close()


if __name__ == "__main__":
    logger.info("Preparing dashboard data exports...")
    export_market_overview()
    export_fund_performance()
    export_investor_demographics()
    export_portfolio_and_benchmark()
    logger.info(f"All exports saved to {DASHBOARD_DIR}")
