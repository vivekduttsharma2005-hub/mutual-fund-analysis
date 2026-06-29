# MF Analytics Platform — Bluestock Fintech Capstone

A full-stack Mutual Fund Analytics Platform built with publicly available Indian mutual fund data from AMFI India and mfapi.in.

## Project Stats
- **10 AMCs**: SBI, HDFC, ICICI, Nippon, Kotak, Axis, ABSL, UTI, Mirae, DSP
- **40 Schemes** across equity, debt, and hybrid categories
- **46k+ Daily NAV** records
- **32k Transactions** simulated
- **₹31,002 Cr SIP Inflow** (Dec 2025)
- **5k Investors** across 12 states

---

## Project Structure

```
mf-analytics/
├── data/
│   ├── raw/                    # Raw CSVs (01–10 datasets)
│   └── processed/              # Cleaned & enriched data
├── etl/
│   ├── etl_pipeline.py         # Main ETL pipeline (Extract → Transform → Load)
│   ├── ingest.py               # Data ingestion from mfapi.in & AMFI
│   └── transform.py            # Cleaning, imputation, derived metrics
├── sql/
│   ├── schema.sql              # Star schema DDL (5 tables)
│   └── queries.sql             # Analytical SQL queries
├── analysis/
│   ├── 01_eda_notebook.ipynb   # Exploratory Data Analysis (15+ charts)
│   └── 02_performance_metrics.ipynb  # Risk & performance metrics
├── metrics/
│   ├── risk_metrics.py         # Sharpe, Sortino, VaR, Drawdown, Beta
│   ├── fund_sharpe_ranks.csv   # Output: Sharpe ratio rankings
│   └── var_drawdown_summary.csv # Output: VaR & max drawdown
├── dashboard/
│   ├── dashboard_data.py       # Prepares data for BI dashboard
│   └── README_dashboard.md     # Power BI / Tableau setup guide
├── docs/
│   ├── report.md               # Full PDF report (markdown source)
│   └── presentation_outline.md # 12-slide deck outline
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the ETL pipeline (ingest → clean → load)
python etl/etl_pipeline.py

# 3. Run EDA notebook
jupyter notebook analysis/01_eda_notebook.ipynb

# 4. Compute risk metrics
python metrics/risk_metrics.py

# 5. Prepare dashboard data
python dashboard/dashboard_data.py
```

---

## Data Pipeline

```
mfapi.in REST API  ──┐
AMFI India CSVs    ──┤──▶  ETL Pipeline  ──▶  SQLite / PostgreSQL  ──▶  BI Dashboard
10 Raw CSV files   ──┘       (pandas)           (Star Schema)           (Power BI / Tableau)
```

### Star Schema (5 Tables)
| Table | Description |
|---|---|
| `dim_fund` | Fund master — AMC, scheme, category |
| `fact_nav` | Daily NAV history |
| `fact_aum` | Monthly AUM by fund house |
| `fact_sip` | Monthly SIP inflow data |
| `fact_transactions` | Investor transaction ledger |

---

## Risk & Performance Metrics

| Metric | Description |
|---|---|
| **Sharpe Ratio** | Risk-adjusted return vs risk-free rate |
| **Sortino Ratio** | Downside-deviation adjusted return |
| **Alpha** | Excess return vs benchmark (Nifty 50) |
| **Beta** | Market sensitivity |
| **VaR 95%** | Value at Risk at 95% confidence |
| **Max Drawdown** | Peak-to-trough decline |
| **Rolling CAGR** | 1Y / 3Y / 5Y compounded annual growth |

---

## Key Insights

- **Mid-cap funds outperformed large-cap by 3.2% alpha (3Y)**
- **31% of investors are under 30** — highest SIP participation
- **Tier-2 cities growing 2.5x faster** than Tier-1 (+19% YoY)
- **Top 5 states**: Maharashtra, Karnataka, Tamil Nadu, Delhi, Gujarat
- **SBI dominates AUM** at ₹12.5L Cr (25%+ market share)

---

## BI Dashboard (4 Pages)

1. **Market Overview** — KPI cards, AUM trend, SIP inflow forecast
2. **Fund Performance & Risk** — Sharpe vs Sortino scatter, rolling CAGR
3. **Investor Demographics** — Choropleth map, age distribution, SIP/Lumpsum pie
4. **Portfolio Holdings** — Sunburst sector concentration, benchmark comparison

---

## Deliverables Checklist

- [x] O1 · Python ETL pipeline (`etl/etl_pipeline.py`)
- [x] O2 · SQL schema (`sql/schema.sql`)
- [x] O3 · EDA notebook with 15+ charts (`analysis/01_eda_notebook.ipynb`)
- [x] O4 · Risk metrics notebook + CSVs (`analysis/02_performance_metrics.ipynb`)
- [x] O5 · Dashboard data prep (`dashboard/dashboard_data.py`)
- [x] O6 · Demographic insights (in EDA notebook)
- [x] O7 · Benchmark comparison (in metrics notebook)
- [x] O8 · Report + slide deck (`docs/`)

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Data Ingestion | `requests`, `mfapi.in` REST |
| Transformation | `pandas`, `numpy` |
| Database | SQLite (dev) / PostgreSQL (prod) via `SQLAlchemy` |
| Analysis | `jupyter`, `matplotlib`, `seaborn`, `scipy` |
| Metrics | `numpy`, `pandas` |
| Visualization | Power BI / Tableau |

---

## Data Sources

- **[mfapi.in](https://mfapi.in)** — Free REST API for NAV history
- **[AMFI India](https://www.amfiindia.com)** — Official AUM and SIP data
- Simulated transaction and investor demographic data (realistic distributions)

---

*Capstone project for Bluestock Fintech · June 2025*
