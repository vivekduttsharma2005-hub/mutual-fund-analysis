"""
risk_metrics.py — Risk & Performance Metrics
Computes Sharpe, Sortino, Alpha, Beta, VaR, Max Drawdown, Rolling CAGR
Bluestock Fintech Capstone
"""

import logging
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "mf_analytics.db"
METRICS_DIR = Path(__file__).parent
RISK_FREE_RATE_ANNUAL = 0.065  # 6.5% p.a. (10-yr G-Sec)
RISK_FREE_DAILY = RISK_FREE_RATE_ANNUAL / 252

# Nifty 50 synthetic daily returns (proxy benchmark)
np.random.seed(0)
NIFTY_DAILY_RETURNS = np.random.normal(0.00042, 0.011, 1380)  # ~5.5 years of trading days


def load_nav_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT f.fund_id, f.scheme_name, f.amc_name, f.category, f.sub_category,
               n.nav_date, n.nav_value, n.day_change_pct
        FROM fact_nav n
        JOIN dim_fund f ON n.fund_id = f.fund_id
        ORDER BY f.fund_id, n.nav_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["nav_date"] = pd.to_datetime(df["nav_date"])
    df["day_change_pct"] = pd.to_numeric(df["day_change_pct"], errors="coerce") / 100
    return df


def compute_sharpe(returns: pd.Series, rf_daily: float = RISK_FREE_DAILY) -> float:
    excess = returns - rf_daily
    if excess.std() == 0:
        return np.nan
    return round(float(excess.mean() / excess.std() * np.sqrt(252)), 4)


def compute_sortino(returns: pd.Series, rf_daily: float = RISK_FREE_DAILY) -> float:
    excess = returns - rf_daily
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return np.nan
    return round(float(excess.mean() / downside.std() * np.sqrt(252)), 4)


def compute_max_drawdown(nav_series: pd.Series) -> float:
    roll_max = nav_series.cummax()
    drawdown = (nav_series - roll_max) / roll_max
    return round(float(drawdown.min() * 100), 4)


def compute_var_95(returns: pd.Series) -> float:
    return round(float(np.percentile(returns.dropna(), 5) * 100), 4)


def compute_beta(fund_returns: pd.Series, benchmark_returns: np.ndarray) -> float:
    n = min(len(fund_returns), len(benchmark_returns))
    f = fund_returns.dropna().values[:n]
    b = benchmark_returns[:n]
    if np.std(b) == 0:
        return np.nan
    cov = np.cov(f, b)[0][1]
    var_b = np.var(b)
    return round(float(cov / var_b), 4)


def compute_alpha(fund_returns: pd.Series, benchmark_returns: np.ndarray,
                  beta: float, rf_daily: float = RISK_FREE_DAILY) -> float:
    n = min(len(fund_returns), len(benchmark_returns))
    avg_fund = fund_returns.dropna().values[:n].mean()
    avg_bm = benchmark_returns[:n].mean()
    alpha_daily = avg_fund - (rf_daily + beta * (avg_bm - rf_daily))
    return round(float(alpha_daily * 252 * 100), 4)  # annualised %


def compute_cagr(nav_series: pd.Series, years: int) -> float:
    if len(nav_series) < years * 252:
        return np.nan
    start_nav = nav_series.iloc[-years * 252]
    end_nav = nav_series.iloc[-1]
    if start_nav <= 0:
        return np.nan
    return round(float(((end_nav / start_nav) ** (1 / years) - 1) * 100), 4)


def compute_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for fund_id, grp in df.groupby("fund_id"):
        grp = grp.sort_values("nav_date").dropna(subset=["day_change_pct"])
        if len(grp) < 252:
            continue

        returns = grp["day_change_pct"]
        nav = grp["nav_value"]

        sharpe  = compute_sharpe(returns)
        sortino = compute_sortino(returns)
        mdd     = compute_max_drawdown(nav)
        var95   = compute_var_95(returns)
        beta    = compute_beta(returns, NIFTY_DAILY_RETURNS)
        alpha   = compute_alpha(returns, NIFTY_DAILY_RETURNS, beta)
        cagr1   = compute_cagr(nav, 1)
        cagr3   = compute_cagr(nav, 3)
        cagr5   = compute_cagr(nav, 5)

        records.append({
            "fund_id":      fund_id,
            "scheme_name":  grp["scheme_name"].iloc[0],
            "amc_name":     grp["amc_name"].iloc[0],
            "category":     grp["category"].iloc[0],
            "sub_category": grp["sub_category"].iloc[0],
            "sharpe_ratio": sharpe,
            "sortino_ratio":sortino,
            "alpha_pct":    alpha,
            "beta":         beta,
            "var_95_pct":   var95,
            "max_drawdown_pct": mdd,
            "cagr_1y_pct":  cagr1,
            "cagr_3y_pct":  cagr3,
            "cagr_5y_pct":  cagr5,
        })

    return pd.DataFrame(records)


def save_outputs(metrics: pd.DataFrame):
    sharpe_ranks = metrics[["scheme_name", "amc_name", "category", "sub_category",
                              "sharpe_ratio", "sortino_ratio", "alpha_pct", "beta",
                              "cagr_1y_pct", "cagr_3y_pct", "cagr_5y_pct"]].copy()
    sharpe_ranks = sharpe_ranks.sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)
    sharpe_ranks.index += 1
    sharpe_ranks.index.name = "rank"
    out1 = METRICS_DIR / "fund_sharpe_ranks.csv"
    sharpe_ranks.to_csv(out1)
    logger.info(f"Saved Sharpe rankings to {out1}")

    var_summary = metrics[["scheme_name", "amc_name", "category", "sub_category",
                             "var_95_pct", "max_drawdown_pct", "beta"]].copy()
    var_summary = var_summary.sort_values("var_95_pct").reset_index(drop=True)
    out2 = METRICS_DIR / "var_drawdown_summary.csv"
    var_summary.to_csv(out2, index=False)
    logger.info(f"Saved VaR & Drawdown summary to {out2}")

    return sharpe_ranks, var_summary


def print_summary(metrics: pd.DataFrame):
    print("\n" + "=" * 70)
    print("RISK & PERFORMANCE METRICS SUMMARY")
    print("=" * 70)
    print(f"\nTop 5 by Sharpe Ratio:")
    print(metrics.nlargest(5, "sharpe_ratio")[
        ["scheme_name", "sharpe_ratio", "sortino_ratio", "alpha_pct", "cagr_3y_pct"]
    ].to_string(index=False))

    print(f"\nTop 5 by 3Y CAGR:")
    print(metrics.nlargest(5, "cagr_3y_pct")[
        ["scheme_name", "cagr_3y_pct", "sharpe_ratio", "max_drawdown_pct"]
    ].to_string(index=False))

    print(f"\nLowest Risk (Max Drawdown) — Best 5:")
    print(metrics.nsmallest(5, "max_drawdown_pct")[
        ["scheme_name", "max_drawdown_pct", "var_95_pct", "beta"]
    ].to_string(index=False))

    sub = metrics.groupby("sub_category").agg(
        avg_sharpe=("sharpe_ratio", "mean"),
        avg_cagr_3y=("cagr_3y_pct", "mean"),
        avg_alpha=("alpha_pct", "mean"),
    ).round(4)
    print(f"\nCategory-Level Averages:")
    print(sub.to_string())
    print("=" * 70)


if __name__ == "__main__":
    logger.info("Loading NAV data from DB...")
    df = load_nav_data()
    logger.info(f"Computing metrics for {df['fund_id'].nunique()} funds...")
    metrics = compute_all_metrics(df)
    save_outputs(metrics)
    print_summary(metrics)
    logger.info("Risk metrics computation complete.")
