# Dashboard Setup Guide — Power BI / Tableau
## MF Analytics Platform · Bluestock Fintech Capstone

---

## Data Sources (exported CSVs)

All dashboard data is in `dashboard/exports/`. Run `python dashboard/dashboard_data.py` first.

| File | Dashboard Page | Description |
|---|---|---|
| `p1_aum_by_amc.csv` | Page 1 — Market Overview | AUM by AMC with market share |
| `p1_aum_trend.csv` | Page 1 | Monthly industry AUM trend |
| `p1_sip_trend.csv` | Page 1 | Monthly SIP inflow trend |
| `p1_category_aum.csv` | Page 1 | AUM split by category |
| `p2_sharpe_sortino.csv` | Page 2 — Fund Performance | Sharpe, Sortino, Alpha, CAGR |
| `p2_var_drawdown.csv` | Page 2 | VaR 95%, Max Drawdown, Beta |
| `p2_nav_snapshot.csv` | Page 2 | Latest NAV per fund |
| `p3_state_investors.csv` | Page 3 — Demographics | State-wise investor count & flows |
| `p3_age_distribution.csv` | Page 3 | Age group breakdown |
| `p3_sip_vs_lumpsum.csv` | Page 3 | SIP vs Lumpsum split |
| `p3_city_tier.csv` | Page 3 | Tier 1 / 2 / 3 city analysis |
| `p3_gender_split.csv` | Page 3 | Gender distribution |
| `p4_sunburst_holdings.csv` | Page 4 — Portfolio | Category/Sector concentration |
| `p4_benchmark_comparison.csv` | Page 4 | Fund vs benchmark returns |

---

## Page 1 — Market Overview

**Visuals:**
- KPI Cards: Total AUM, Total SIP Inflow (Dec '25), Total Folios, Active Schemes
- Bar Chart: AUM by AMC (sorted descending)
- Line Chart: Monthly industry AUM trend (2020–2025)
- Area Chart: Monthly SIP inflow with forecast trend line
- Donut Chart: Category-wise AUM split (Equity / Debt / Hybrid)

**Key KPIs:**
- Total AUM: ₹46L+ Crore (industry)
- SIP Inflow Dec '25: ₹31,002 Crore
- SBI Market Share: ~25%

---

## Page 2 — Fund Performance & Risk

**Visuals:**
- Scatter Plot: Sharpe Ratio vs Sortino Ratio (bubble size = AUM)
- Bar Chart: Top 10 funds by 3Y CAGR
- Waterfall / Column: Alpha by sub-category
- Heatmap: Risk metrics matrix (Sharpe, Beta, VaR, Drawdown)
- Line: Rolling NAV trend for top 5 funds

**Insight callout:** "Mid-cap funds outperformed large-cap by 3.2% alpha (3Y)"

---

## Page 3 — Investor Demographics

**Visuals:**
- Choropleth Map: Investor count by Indian state (use India state GeoJSON)
- Bar Chart: Age group distribution with SIP % overlay
- Pie Chart: SIP vs Lumpsum split
- Column Chart: City Tier investment comparison
- KPI: "31% investors under 30 · Tier-2 cities +19% YoY"

**State GeoJSON:** Use India state boundaries from naturalearthdata or GADM.

---

## Page 4 — Portfolio Holdings & Benchmark

**Visuals:**
- Sunburst Chart: AMC → Category → Sub-Category → AUM
- Line Chart: Fund return vs Nifty 50 / Nifty 100 / BSE SmallCap
- Table: Benchmark comparison with tracking error
- Bar: Annualised return by benchmark index group

---

## Power BI Setup Steps

1. Open Power BI Desktop
2. Get Data → Text/CSV → import each CSV file
3. Use Power Query to set correct data types (date columns, numerics)
4. Create relationships between tables using `amc_name` as the common key
5. Build each page using the visual suggestions above
6. Add slicers: AMC, Category, Date Range, State

## Tableau Setup Steps

1. Connect to Folder → select `dashboard/exports/`
2. Create a data source for each CSV
3. Blend on `amc_name` field across sources
4. Use Tableau Maps with custom India GeoJSON for the choropleth
