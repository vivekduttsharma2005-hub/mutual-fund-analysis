"""
transform.py — Data Transformation & Cleaning Module
Cleans raw NAV, AUM, SIP data and computes derived metrics
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

AMC_META = {
    "SBI":    {"full_name": "SBI Mutual Fund",           "aum_crore": 1250000},
    "HDFC":   {"full_name": "HDFC Mutual Fund",          "aum_crore": 680000},
    "ICICI":  {"full_name": "ICICI Prudential MF",       "aum_crore": 890000},
    "Nippon": {"full_name": "Nippon India MF",           "aum_crore": 420000},
    "Kotak":  {"full_name": "Kotak Mahindra MF",         "aum_crore": 390000},
    "Axis":   {"full_name": "Axis Mutual Fund",          "aum_crore": 310000},
    "ABSL":   {"full_name": "Aditya Birla Sun Life MF",  "aum_crore": 350000},
    "UTI":    {"full_name": "UTI Mutual Fund",           "aum_crore": 280000},
    "Mirae":  {"full_name": "Mirae Asset MF",            "aum_crore": 195000},
    "DSP":    {"full_name": "DSP Mutual Fund",           "aum_crore": 145000},
}


def clean_nav_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich NAV dataframe"""
    logger.info("Cleaning NAV data...")
    df = df.copy()
    df["nav_date"] = pd.to_datetime(df["nav_date"], errors="coerce")
    df["nav_value"] = pd.to_numeric(df["nav_value"], errors="coerce")
    df = df.dropna(subset=["nav_date", "nav_value"])
    df = df[df["nav_value"] > 0]
    df = df.sort_values(["scheme_code", "nav_date"]).reset_index(drop=True)

    # NAV imputation — fill missing dates with forward fill
    df = _impute_missing_navs(df)

    # Derived columns
    df["day_change"] = df.groupby("scheme_code")["nav_value"].diff()
    df["day_change_pct"] = df.groupby("scheme_code")["nav_value"].pct_change() * 100
    df["rolling_7d_avg"] = df.groupby("scheme_code")["nav_value"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    df["rolling_30d_avg"] = df.groupby("scheme_code")["nav_value"].transform(
        lambda x: x.rolling(30, min_periods=1).mean()
    )
    df["rolling_7d_high"] = df.groupby("scheme_code")["nav_value"].transform(
        lambda x: x.rolling(7, min_periods=1).max()
    )
    df["rolling_7d_low"] = df.groupby("scheme_code")["nav_value"].transform(
        lambda x: x.rolling(7, min_periods=1).min()
    )

    out_path = PROCESSED_DIR / "nav_cleaned.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} cleaned NAV records to {out_path}")
    return df


def _impute_missing_navs(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill missing NAV values for non-trading days"""
    groups = []
    for code, grp in df.groupby("scheme_code"):
        grp = grp.set_index("nav_date").sort_index()
        full_range = pd.date_range(grp.index.min(), grp.index.max(), freq="D")
        grp = grp.reindex(full_range)
        grp["scheme_code"] = code
        grp["nav_value"] = grp["nav_value"].ffill()
        grp = grp.reset_index().rename(columns={"index": "nav_date"})
        groups.append(grp)
    return pd.concat(groups, ignore_index=True)


def generate_aum_data() -> pd.DataFrame:
    """Generate realistic monthly AUM data for 10 AMCs (2020–2025)"""
    logger.info("Generating AUM data...")
    records = []
    months = pd.date_range("2020-01-01", "2025-12-01", freq="MS")
    np.random.seed(42)

    for amc, meta in AMC_META.items():
        base_aum = meta["aum_crore"] * 0.45  # start at 45% of current AUM
        current_aum = base_aum
        for month in months:
            growth = np.random.normal(0.018, 0.03)  # avg 1.8% monthly growth
            current_aum *= (1 + growth)
            current_aum = max(current_aum, base_aum * 0.5)
            records.append({
                "amc_name": amc,
                "report_month": month.strftime("%Y-%m-%d"),
                "aum_crore": round(current_aum, 2),
                "folio_count": int(current_aum / 0.12 + np.random.randint(-5000, 5000)),
            })

    df = pd.DataFrame(records)
    df["aum_change_pct"] = df.groupby("amc_name")["aum_crore"].pct_change() * 100
    out_path = PROCESSED_DIR / "aum_monthly.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} AUM records to {out_path}")
    return df


def generate_sip_data() -> pd.DataFrame:
    """Generate realistic monthly SIP inflow data"""
    logger.info("Generating SIP data...")
    records = []
    months = pd.date_range("2020-01-01", "2025-12-01", freq="MS")
    np.random.seed(99)

    amc_sip_share = {
        "SBI": 0.22, "HDFC": 0.15, "ICICI": 0.18, "Nippon": 0.09,
        "Kotak": 0.08, "Axis": 0.07, "ABSL": 0.08, "UTI": 0.06,
        "Mirae": 0.04, "DSP": 0.03,
    }
    industry_sip_base = 8000  # ₹8000 Cr in Jan 2020

    for month in months:
        months_since_start = (month.year - 2020) * 12 + month.month - 1
        industry_sip = industry_sip_base * (1.025 ** (months_since_start / 12))
        industry_sip += np.random.normal(0, 200)

        for amc, share in amc_sip_share.items():
            sip_amount = industry_sip * share * np.random.uniform(0.9, 1.1)
            records.append({
                "amc_name": amc,
                "report_month": month.strftime("%Y-%m-%d"),
                "sip_amount_crore": round(sip_amount, 2),
                "sip_count": int(sip_amount * 420 + np.random.randint(-500, 500)),
                "new_sip_count": int(sip_amount * 18 + np.random.randint(-50, 50)),
                "stopped_sip_count": int(sip_amount * 6 + np.random.randint(-20, 20)),
                "avg_sip_amount": round(np.random.normal(3500, 800), 2),
            })

    df = pd.DataFrame(records)
    out_path = PROCESSED_DIR / "sip_monthly.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} SIP records to {out_path}")
    return df


def generate_transactions() -> pd.DataFrame:
    """Generate 32k realistic investor transactions"""
    logger.info("Generating 32,000 investor transactions...")
    np.random.seed(7)

    states = {
        "Maharashtra": 0.18, "Karnataka": 0.14, "Tamil Nadu": 0.12,
        "Delhi": 0.11, "Gujarat": 0.10, "West Bengal": 0.07,
        "Rajasthan": 0.06, "Telangana": 0.05, "Uttar Pradesh": 0.05,
        "Madhya Pradesh": 0.04, "Haryana": 0.04, "Punjab": 0.04,
    }
    txn_types = ["BUY", "SIP", "BUY", "SIP", "SIP", "REDEEM", "SWITCH_IN"]

    records = []
    amcs = list(AMC_META.keys())
    for i in range(32000):
        amc = np.random.choice(amcs)
        state = np.random.choice(list(states.keys()), p=list(states.values()))
        age = int(np.random.normal(38, 10))
        age = max(21, min(75, age))
        tier = "Tier 1" if state in ["Maharashtra", "Karnataka", "Delhi", "Tamil Nadu"] else \
               "Tier 2" if np.random.random() > 0.35 else "Tier 3"
        txn_type = np.random.choice(txn_types)
        amount = np.random.lognormal(10.2, 0.8) if txn_type != "SIP" else \
                 np.random.choice([500, 1000, 2000, 3000, 5000, 10000],
                                   p=[0.05, 0.15, 0.25, 0.20, 0.25, 0.10])
        records.append({
            "investor_id": f"INV{100000 + i}",
            "folio_number": f"FOLIO{200000 + i}",
            "amc_name": amc,
            "txn_date": pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(np.random.uniform(0, 2190))),
            "txn_type": txn_type,
            "txn_amount": round(float(amount), 2),
            "state": state,
            "city_tier": tier,
            "investor_age": age,
            "investor_gender": np.random.choice(["Male", "Female"], p=[0.62, 0.38]),
            "channel": np.random.choice(["App", "Online", "Distributor", "Branch"],
                                         p=[0.35, 0.30, 0.25, 0.10]),
        })

    df = pd.DataFrame(records)
    out_path = PROCESSED_DIR / "transactions.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} transaction records to {out_path}")
    return df


def generate_fund_master() -> pd.DataFrame:
    """Generate fund master dimension table"""
    funds = [
        {"scheme_code": "120503", "scheme_name": "SBI Bluechip Fund", "amc_name": "SBI", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 0.98},
        {"scheme_code": "125494", "scheme_name": "SBI Small Cap Fund", "amc_name": "SBI", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.53},
        {"scheme_code": "119598", "scheme_name": "SBI Magnum Midcap Fund", "amc_name": "SBI", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.21},
        {"scheme_code": "119551", "scheme_name": "SBI Equity Hybrid Fund", "amc_name": "SBI", "category": "Hybrid", "sub_category": "Aggressive Hybrid", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 1.15},
        {"scheme_code": "100033", "scheme_name": "HDFC Top 100 Fund", "amc_name": "HDFC", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 1.03},
        {"scheme_code": "100270", "scheme_name": "HDFC Mid-Cap Opportunities Fund", "amc_name": "HDFC", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.28},
        {"scheme_code": "100016", "scheme_name": "HDFC Small Cap Fund", "amc_name": "HDFC", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.58},
        {"scheme_code": "101206", "scheme_name": "HDFC Balanced Advantage Fund", "amc_name": "HDFC", "category": "Hybrid", "sub_category": "Balanced Advantage", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 0.88},
        {"scheme_code": "120586", "scheme_name": "ICICI Pru Bluechip Fund", "amc_name": "ICICI", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 0.95},
        {"scheme_code": "120839", "scheme_name": "ICICI Pru Midcap Fund", "amc_name": "ICICI", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.19},
        {"scheme_code": "120843", "scheme_name": "ICICI Pru Value Discovery Fund", "amc_name": "ICICI", "category": "Equity", "sub_category": "Value", "benchmark_index": "Nifty 500", "expense_ratio": 1.05},
        {"scheme_code": "120594", "scheme_name": "ICICI Pru Equity & Debt Fund", "amc_name": "ICICI", "category": "Hybrid", "sub_category": "Aggressive Hybrid", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 1.12},
        {"scheme_code": "118701", "scheme_name": "Nippon India Large Cap Fund", "amc_name": "Nippon", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 1.08},
        {"scheme_code": "118825", "scheme_name": "Nippon India Growth Fund", "amc_name": "Nippon", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.35},
        {"scheme_code": "118989", "scheme_name": "Nippon India Small Cap Fund", "amc_name": "Nippon", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.55},
        {"scheme_code": "118550", "scheme_name": "Nippon India Balanced Advantage Fund", "amc_name": "Nippon", "category": "Hybrid", "sub_category": "Balanced Advantage", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 0.92},
        {"scheme_code": "120163", "scheme_name": "Kotak Bluechip Fund", "amc_name": "Kotak", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 1.01},
        {"scheme_code": "120164", "scheme_name": "Kotak Emerging Equity Fund", "amc_name": "Kotak", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.31},
        {"scheme_code": "120165", "scheme_name": "Kotak Small Cap Fund", "amc_name": "Kotak", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.62},
        {"scheme_code": "120170", "scheme_name": "Kotak Balanced Advantage Fund", "amc_name": "Kotak", "category": "Hybrid", "sub_category": "Balanced Advantage", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 0.85},
        {"scheme_code": "125503", "scheme_name": "Axis Bluechip Fund", "amc_name": "Axis", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 0.55},
        {"scheme_code": "125354", "scheme_name": "Axis Midcap Fund", "amc_name": "Axis", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 0.62},
        {"scheme_code": "125356", "scheme_name": "Axis Small Cap Fund", "amc_name": "Axis", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 0.72},
        {"scheme_code": "125355", "scheme_name": "Axis Long Term Equity Fund", "amc_name": "Axis", "category": "Equity", "sub_category": "ELSS", "benchmark_index": "Nifty 500", "expense_ratio": 0.68},
        {"scheme_code": "119270", "scheme_name": "ABSL Frontline Equity Fund", "amc_name": "ABSL", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 0.98},
        {"scheme_code": "119271", "scheme_name": "ABSL Midcap Fund", "amc_name": "ABSL", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.25},
        {"scheme_code": "119272", "scheme_name": "ABSL Small Cap Fund", "amc_name": "ABSL", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.49},
        {"scheme_code": "119536", "scheme_name": "ABSL Balanced Advantage Fund", "amc_name": "ABSL", "category": "Hybrid", "sub_category": "Balanced Advantage", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 0.80},
        {"scheme_code": "120716", "scheme_name": "UTI Nifty 50 Index Fund", "amc_name": "UTI", "category": "Equity", "sub_category": "Index", "benchmark_index": "Nifty 50", "expense_ratio": 0.18},
        {"scheme_code": "120717", "scheme_name": "UTI Mid Cap Fund", "amc_name": "UTI", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.38},
        {"scheme_code": "120718", "scheme_name": "UTI Small Cap Fund", "amc_name": "UTI", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.51},
        {"scheme_code": "120719", "scheme_name": "UTI Flexi Cap Fund", "amc_name": "UTI", "category": "Equity", "sub_category": "Flexi Cap", "benchmark_index": "Nifty 500", "expense_ratio": 1.05},
        {"scheme_code": "118980", "scheme_name": "Mirae Asset Large Cap Fund", "amc_name": "Mirae", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 0.54},
        {"scheme_code": "118981", "scheme_name": "Mirae Asset Emerging Bluechip Fund", "amc_name": "Mirae", "category": "Equity", "sub_category": "Large & Mid Cap", "benchmark_index": "Nifty LargeMidcap 250", "expense_ratio": 0.58},
        {"scheme_code": "118982", "scheme_name": "Mirae Asset Midcap Fund", "amc_name": "Mirae", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 0.65},
        {"scheme_code": "119260", "scheme_name": "Mirae Asset Tax Saver Fund", "amc_name": "Mirae", "category": "Equity", "sub_category": "ELSS", "benchmark_index": "Nifty 500", "expense_ratio": 0.52},
        {"scheme_code": "119230", "scheme_name": "DSP Top 100 Equity Fund", "amc_name": "DSP", "category": "Equity", "sub_category": "Large Cap", "benchmark_index": "Nifty 100", "expense_ratio": 1.12},
        {"scheme_code": "119231", "scheme_name": "DSP Midcap Fund", "amc_name": "DSP", "category": "Equity", "sub_category": "Mid Cap", "benchmark_index": "Nifty Midcap 150", "expense_ratio": 1.29},
        {"scheme_code": "119232", "scheme_name": "DSP Small Cap Fund", "amc_name": "DSP", "category": "Equity", "sub_category": "Small Cap", "benchmark_index": "BSE SmallCap", "expense_ratio": 1.52},
        {"scheme_code": "119233", "scheme_name": "DSP Equity & Bond Fund", "amc_name": "DSP", "category": "Hybrid", "sub_category": "Aggressive Hybrid", "benchmark_index": "Nifty 50 Hybrid", "expense_ratio": 1.08},
    ]
    df = pd.DataFrame(funds)
    df["fund_type"] = "Open-ended"
    df["min_investment"] = 500.0
    out_path = PROCESSED_DIR / "fund_master.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} fund master records to {out_path}")
    return df


if __name__ == "__main__":
    generate_fund_master()
    generate_aum_data()
    generate_sip_data()
    generate_transactions()
    logger.info("All transformations complete.")
