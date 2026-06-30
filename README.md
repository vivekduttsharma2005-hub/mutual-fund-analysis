# 📈 Mutual Fund Analytics Platform

### Bluestock Fintech Capstone Project

A comprehensive **Mutual Fund Analytics Platform** built using Python, SQL, and Power BI to analyze Indian mutual fund performance, investor behavior, risk metrics, and market trends.

The project combines an end-to-end **ETL pipeline**, **Exploratory Data Analysis (EDA)**, **financial risk analytics**, and an **interactive Power BI dashboard** using publicly available data from **AMFI India** and **mfapi.in** along with realistic simulated investor and transaction data.

---

# 🚀 Project Highlights

* 📊 Interactive Power BI Dashboard (4 Pages)
* 🐍 Automated Python ETL Pipeline
* 🗄️ Star Schema Database Design
* 📉 Risk & Performance Analytics
* 📈 15+ Exploratory Data Analysis Visualizations
* 💼 Industry-Style Capstone Project
* 📄 Professional PDF Report
* 📸 Dashboard Screenshots

---

# 📌 Project Statistics

| Metric                     |       Value |
| -------------------------- | ----------: |
| Asset Management Companies |          10 |
| Mutual Fund Schemes        |          40 |
| Daily NAV Records          |     46,000+ |
| Investor Transactions      |     32,000+ |
| Investors                  |       5,000 |
| States Covered             |          12 |
| Monthly SIP Inflow         |  ₹31,002 Cr |
| Total Industry AUM         | ₹81 Lakh Cr |

---

# 🏗️ Project Architecture

```text
                  +----------------------+
                  |   AMFI India Data    |
                  +----------+-----------+
                             |
                             |
                  +----------v-----------+
                  |     mfapi.in API     |
                  +----------+-----------+
                             |
                             |
                    Python ETL Pipeline
      (Extract → Transform → Clean → Feature Engineering)
                             |
                             |
                  SQLite / PostgreSQL Database
                             |
               +-------------+-------------+
               |                           |
       Exploratory Data Analysis     Risk Analytics
               |                           |
               +-------------+-------------+
                             |
                       Power BI Dashboard
                             |
                     PDF Report & Insights
```

---

# 📂 Project Structure

```text
mf-analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── etl/
│   ├── etl_pipeline.py
│   ├── ingest.py
│   └── transform.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── analysis/
│   ├── 01_eda_notebook.ipynb
│   └── 02_performance_metrics.ipynb
│
├── metrics/
│   ├── risk_metrics.py
│   ├── fund_sharpe_ranks.csv
│   └── var_drawdown_summary.csv
│
├── dashboard/
│   ├── dashboard_data.py
│   ├── Bluestock_MF_Dashboard.pbix
│   └── README_dashboard.md
│
├── docs/
│   ├── Bluestock_MF_Dashboard.pdf
│   ├── report.md
│   └── presentation_outline.md
│
├── screenshots/
│   ├── dashboard_1.png
│   ├── dashboard_2.png
│   ├── dashboard_3.png
│   └── dashboard_4.png
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/mf-analytics.git

cd mf-analytics
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

## 1. Run ETL Pipeline

```bash
python etl/etl_pipeline.py
```

---

## 2. Run Exploratory Data Analysis

```bash
jupyter notebook analysis/01_eda_notebook.ipynb
```

---

## 3. Generate Risk Metrics

```bash
python metrics/risk_metrics.py
```

---

## 4. Prepare Dashboard Dataset

```bash
python dashboard/dashboard_data.py
```

---

## 5. Open Power BI Dashboard

Open:

```text
dashboard/Bluestock_MF_Dashboard.pbix
```

---

# 🗄️ Database Schema

The project follows a **Star Schema** for efficient analytics.

### Dimension Table

| Table    | Description             |
| -------- | ----------------------- |
| dim_fund | Fund master information |

### Fact Tables

| Table             | Description           |
| ----------------- | --------------------- |
| fact_nav          | Daily NAV history     |
| fact_aum          | Monthly AUM           |
| fact_sip          | SIP inflows           |
| fact_transactions | Investor transactions |

---

# 📊 Dashboard Pages

## 1️⃣ Market Overview

* Industry KPIs
* Total AUM
* Monthly SIP Inflows
* Folios
* Industry Growth Trend
* AMC-wise AUM

---

## 2️⃣ Fund Performance

* Return vs Risk Scatter Plot
* Benchmark Comparison
* NAV Trend
* Fund Ranking
* CAGR Analysis

---

## 3️⃣ Investor Analytics

* State-wise Investment
* SIP vs Lumpsum Distribution
* Age Group Analysis
* Monthly Transactions
* Investor Demographics

---

## 4️⃣ Portfolio & Market Trends

* Category-wise Inflows
* Nifty vs SIP Trend
* Portfolio Holdings
* Sector Allocation
* Top Performing Categories

---

# 📈 Risk Metrics

The project calculates multiple financial metrics including:

* Sharpe Ratio
* Sortino Ratio
* Alpha
* Beta
* Rolling CAGR
* Value at Risk (95%)
* Maximum Drawdown

---

# 🔍 Exploratory Data Analysis

The notebook contains more than **15 visualizations**, including:

* NAV Trend Analysis
* AMC Comparison
* SIP Growth
* Category Distribution
* Rolling Returns
* Risk Distribution
* Transaction Trends
* Investor Demographics
* Monthly AUM Growth
* Portfolio Allocation

---

# 💡 Key Business Insights

* 📈 Mid-cap funds generated approximately **3.2% higher alpha** than large-cap funds over 3 years.
* 👥 Investors below 30 years account for **31% of total SIP participation**.
* 🌆 Tier-2 cities recorded **2.5× faster growth** than Tier-1 cities.
* 🌍 Maharashtra, Karnataka, Tamil Nadu, Delhi, and Gujarat contributed the highest investment volume.
* 🏦 SBI Mutual Fund holds nearly **25% market share** with around **₹12.5 lakh crore AUM**.

---

# 🛠️ Technology Stack

| Category        | Technologies                 |
| --------------- | ---------------------------- |
| Programming     | Python 3.11                  |
| Data Processing | Pandas, NumPy                |
| API             | mfapi.in                     |
| Database        | SQLite, PostgreSQL           |
| SQL             | SQLAlchemy                   |
| Analysis        | Jupyter Notebook             |
| Visualization   | Matplotlib, Plotly, Power BI |
| Dashboard       | Microsoft Power BI           |
| Version Control | Git & GitHub                 |

---

# 📦 Deliverables

* ✅ Python ETL Pipeline
* ✅ SQL Database Schema
* ✅ Exploratory Data Analysis Notebook
* ✅ Financial Risk Metrics
* ✅ Power BI Dashboard
* ✅ Dashboard PDF
* ✅ Project Documentation
* ✅ Presentation Outline

---

# 📸 Dashboard Preview

Add screenshots here after completing the dashboard.

```text
screenshots/dashboard_1.png

screenshots/dashboard_2.png

screenshots/dashboard_3.png

screenshots/dashboard_4.png
```

---

# 📚 Data Sources

* **AMFI India** – Mutual Fund Industry Statistics
* **mfapi.in** – Historical NAV API
* Simulated investor, transaction, and demographic datasets generated for analytical purposes.

---

# 👨‍💻 Author

**Vivek Dutt Sharma**

Aspiring Data Analyst | Python | SQL | Power BI | Excel


* LinkedIn: www.linkedin.com/in/vivekdutt-sharma-5317b2338
* GitHub: https://github.com/vivekduttsharma2005-hub 

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

Feedback, suggestions, and contributions are always welcome!

