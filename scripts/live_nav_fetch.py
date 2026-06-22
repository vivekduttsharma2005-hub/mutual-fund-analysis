"""
Day 1 - Live NAV Fetch
"""

import requests
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA = PROJECT_ROOT / "data" / "raw"

SCHEMES = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841
}


def fetch_nav(amfi_code, scheme_name):

    url = f"https://api.mfapi.in/mf/{amfi_code}"

    print(f"\nFetching {scheme_name}...")

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        print("Failed.")
        return

    data = response.json()

    nav_df = pd.DataFrame(data["data"])

    filename = scheme_name.lower().replace(" ", "_") + "_nav.csv"

    nav_df.to_csv(RAW_DATA / filename, index=False)

    print(f"Saved -> {filename}")


def main():

    for name, code in SCHEMES.items():
        fetch_nav(code, name)


if __name__ == "__main__":
    main()