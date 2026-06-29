# 12-Slide Presentation Deck — MF Analytics Platform
## Bluestock Fintech Individual Capstone

---

### Slide 1 — Title Slide
**MF Analytics Platform**
Full-Stack Mutual Fund Data Pipeline & Analytics
Bluestock Fintech · Individual Capstone · June 2025
*Vivek Dutt Sharma*

---

### Slide 2 — Project Overview & Scope
**What we built:**
- End-to-end data pipeline: Ingest → Clean → Store → Analyze → Visualize
- 10 real AMCs | 40 schemes | 46k+ NAV records | 32k transactions

**Data Sources:** mfapi.in REST API + AMFI India
**Stack:** Python · pandas · SQLAlchemy · SQLite · Power BI

---

### Slide 3 — Data Architecture (Star Schema)
**5-table star schema:**
- `dim_fund` → master for 40 schemes across 10 AMCs
- `fact_nav` → daily NAV history (46k+ records)
- `fact_aum` → monthly AUM by fund house
- `fact_sip` → monthly SIP inflow data
- `fact_transactions` → 32k investor transactions

*[Diagram: Star schema with dim_fund at center]*

---

### Slide 4 — ETL Pipeline Architecture
**Three-stage pipeline:**

Extract → Transform → Load

- **Extract:** mfapi.in REST calls + AMFI bulk download
- **Transform:** Date standardization, NAV imputation (forward-fill), derived metrics
- **Load:** SQLite via SQLAlchemy; PostgreSQL-ready

*[Diagram: Pipeline flow with icons]*

---

### Slide 5 — Market Overview (Dashboard Page 1)
**Industry Snapshot — Dec 2025:**
- Total AUM: ₹46L+ Crore
- SIP Inflow: **₹31,002 Crore** (Dec '25)
- Total SIP accounts: 10.2 Cr+

**SBI dominates:** ₹12.5L Cr AUM (25% market share)
SIP CAGR: ~25% annualized over 5 years

*[KPI cards + AUM bar chart]*

---

### Slide 6 — Fund Performance (Dashboard Page 2)
**Risk-Adjusted Returns:**

| Category | 3Y CAGR | Sharpe | Alpha |
|---|---|---|---|
| Small Cap | 18.5% | 0.82 | +4.5% |
| Mid Cap | 16.2% | 0.74 | +3.2% |
| Large Cap | 13.0% | 0.61 | +1.8% |

**Sharpe vs Sortino scatter highlights mid-cap sweet spot**

---

### Slide 7 — Key Insight: Mid-Cap Alpha
> **"Mid-cap funds outperformed large-cap by 3.2% alpha over 3 years"**

- Active mid-cap managers consistently beat Nifty Midcap 150 benchmark
- Higher tracking error (2.8–4.2%) justified by alpha generation
- Best Sharpe ratios in mid-cap category (0.74 vs 0.61 for large-cap)

*[Alpha bar chart by category]*

---

### Slide 8 — Risk Metrics Deep Dive
**VaR & Drawdown Summary:**

- Small-cap VaR 95%: -2.8% (single day)
- Large-cap VaR 95%: -1.4%
- Max Drawdown (COVID, 2020): Small-cap -42% | Large-cap -35%

**Risk-reward conclusion:** Mid-cap offers best balance for 3–5Y horizon

*[Risk heatmap]*

---

### Slide 9 — Investor Demographics (Dashboard Page 3)
**Who is investing in mutual funds?**

- **31% investors under 30** — highest SIP participation (72% prefer SIP mode)
- **Top 5 states** account for 65% of AUM: MH, KA, TN, DL, GJ
- **App/Online channels** dominate: 65% of transactions

*[Choropleth India map + age bar chart]*

---

### Slide 10 — Tier-2 City Growth Story
> **"Tier-2 cities growing 2.5x faster than Tier-1"**

- Tier-2 investor count: +19% YoY
- Average ticket size in Tier-2: ₹12,000 (vs ₹28,000 Tier-1)
- SIP preference in Tier-2: 68% (vs 61% in Tier-1)

**Implication:** Digital-first AMC strategies must prioritize vernacular UX

*[City tier comparison chart]*

---

### Slide 11 — Benchmark Comparison (O7)
**Active vs Passive:**

| Benchmark | Active Alpha | Tracking Error |
|---|---|---|
| Nifty 50 (Index) | -0.2% | 0.08% |
| Nifty 100 (Large-cap) | +1.8% | 1.5% avg |
| Nifty Midcap 150 | +3.2% | 3.5% avg |
| BSE SmallCap | +4.5% | 5.5% avg |

**Conclusion:** Active management adds value in mid/small cap; index funds win in large-cap

*[Benchmark comparison line chart with interactive tooltips]*

---

### Slide 12 — Conclusions & Deliverables
**Project Deliverables Completed:**
- ✅ Python ETL pipeline (automated, idempotent)
- ✅ Star schema SQL (5 tables, fully joinable)
- ✅ EDA notebook (15+ charts)
- ✅ Risk metrics (Sharpe, Sortino, Alpha, VaR, Drawdown, Beta, CAGR)
- ✅ Power BI dashboard (4 pages)
- ✅ Demographic insights
- ✅ Benchmark comparison
- ✅ Report + Slide deck

**Top Recommendations:**
1. Increase mid-cap allocation for 3–5Y horizon investors
2. Invest in Tier-2 city digital acquisition
3. Blend index + active for cost-efficient portfolios

*GitHub: github.com/vivekduttsharma2005-hub/mutual-fund-analysis*
