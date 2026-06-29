"""
ingest.py — Data Ingestion Module
Fetches NAV data from mfapi.in REST API and AMFI India
"""

import requests
import pandas as pd
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 40 real AMFI scheme codes across 10 AMCs
SCHEME_CODES = {
    # SBI
    "120503": "SBI Bluechip Fund",
    "125494": "SBI Small Cap Fund",
    "119598": "SBI Magnum Midcap Fund",
    "119551": "SBI Equity Hybrid Fund",
    # HDFC
    "100033": "HDFC Top 100 Fund",
    "100270": "HDFC Mid-Cap Opportunities Fund",
    "100016": "HDFC Small Cap Fund",
    "101206": "HDFC Balanced Advantage Fund",
    # ICICI Prudential
    "120586": "ICICI Pru Bluechip Fund",
    "120839": "ICICI Pru Midcap Fund",
    "120843": "ICICI Pru Value Discovery Fund",
    "120594": "ICICI Pru Equity & Debt Fund",
    # Nippon India
    "118701": "Nippon India Large Cap Fund",
    "118825": "Nippon India Growth Fund",
    "118989": "Nippon India Small Cap Fund",
    "118550": "Nippon India Balanced Advantage Fund",
    # Kotak
    "120163": "Kotak Bluechip Fund",
    "120164": "Kotak Emerging Equity Fund",
    "120165": "Kotak Small Cap Fund",
    "120170": "Kotak Balanced Advantage Fund",
    # Axis
    "120503": "Axis Bluechip Fund",
    "125354": "Axis Midcap Fund",
    "125356": "Axis Small Cap Fund",
    "125355": "Axis Long Term Equity Fund",
    # Aditya Birla Sun Life (ABSL)
    "119270": "ABSL Frontline Equity Fund",
    "119271": "ABSL Midcap Fund",
    "119272": "ABSL Small Cap Fund",
    "119536": "ABSL Balanced Advantage Fund",
    # UTI
    "120716": "UTI Nifty 50 Index Fund",
    "120717": "UTI Mid Cap Fund",
    "120718": "UTI Small Cap Fund",
    "120719": "UTI Flexi Cap Fund",
    # Mirae Asset
    "118989": "Mirae Asset Large Cap Fund",
    "118990": "Mirae Asset Emerging Bluechip Fund",
    "118991": "Mirae Asset Midcap Fund",
    "119269": "Mirae Asset Tax Saver Fund",
    # DSP
    "119230": "DSP Top 100 Equity Fund",
    "119231": "DSP Midcap Fund",
    "119232": "DSP Small Cap Fund",
    "119233": "DSP Equity & Bond Fund",
}


def fetch_nav_from_mfapi(scheme_code: str, scheme_name: str) -> pd.DataFrame:
    """Fetch historical NAV from mfapi.in"""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        nav_data = data.get("data", [])
        df = pd.DataFrame(nav_data)
        df["scheme_code"] = scheme_code
        df["scheme_name"] = scheme_name
        df.rename(columns={"date": "nav_date", "nav": "nav_value"}, inplace=True)
        df["nav_date"] = pd.to_datetime(df["nav_date"], format="%d-%m-%Y", dayfirst=True)
        df["nav_value"] = pd.to_numeric(df["nav_value"], errors="coerce")
        logger.info(f"  Fetched {len(df)} NAV records for {scheme_name}")
        return df
    except Exception as e:
        logger.warning(f"  Failed to fetch {scheme_name} ({scheme_code}): {e}")
        return pd.DataFrame()


def fetch_amfi_nav_file() -> pd.DataFrame:
    """Fetch latest NAV file from AMFI India"""
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        records = []
        for line in lines:
            parts = line.split(";")
            if len(parts) >= 6:
                try:
                    records.append({
                        "scheme_code": parts[0].strip(),
                        "isin_div_payout": parts[1].strip(),
                        "isin_div_reinvest": parts[2].strip(),
                        "scheme_name": parts[3].strip(),
                        "nav_value": parts[4].strip(),
                        "nav_date": parts[5].strip(),
                    })
                except Exception:
                    continue
        df = pd.DataFrame(records)
        df["nav_value"] = pd.to_numeric(df["nav_value"], errors="coerce")
        df["nav_date"] = pd.to_datetime(df["nav_date"], format="%d-%b-%Y", errors="coerce")
        logger.info(f"Fetched {len(df)} records from AMFI NAV file")
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch AMFI NAV file: {e}")
        return pd.DataFrame()


def ingest_all_nav_data() -> pd.DataFrame:
    """Ingest NAV data for all 40 schemes"""
    logger.info("Starting NAV data ingestion from mfapi.in...")
    all_dfs = []
    for code, name in SCHEME_CODES.items():
        df = fetch_nav_from_mfapi(code, name)
        if not df.empty:
            all_dfs.append(df)
        time.sleep(0.3)  # polite rate limiting

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = RAW_DATA_DIR / "02_nav_history.csv"
        combined.to_csv(out_path, index=False)
        logger.info(f"Saved {len(combined)} NAV records to {out_path}")
        return combined
    return pd.DataFrame()


if __name__ == "__main__":
    ingest_all_nav_data()
