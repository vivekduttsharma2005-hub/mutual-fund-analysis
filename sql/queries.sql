-- ============================================================
-- MF Analytics Platform — Analytical SQL Queries
-- Bluestock Fintech Capstone
-- ============================================================

-- ============================================================
-- 1. MARKET OVERVIEW
-- ============================================================

-- Total AUM by AMC (latest month)
SELECT
    amc_name,
    SUM(aum_crore) AS total_aum_crore,
    ROUND(SUM(aum_crore) * 100.0 / (SELECT SUM(aum_crore) FROM fact_aum WHERE report_month = (SELECT MAX(report_month) FROM fact_aum)), 2) AS market_share_pct
FROM fact_aum
WHERE report_month = (SELECT MAX(report_month) FROM fact_aum)
GROUP BY amc_name
ORDER BY total_aum_crore DESC;

-- Monthly SIP inflow trend (last 12 months)
SELECT
    strftime('%Y-%m', report_month) AS month,
    SUM(sip_amount_crore) AS total_sip_crore,
    SUM(sip_count) AS total_sip_count
FROM fact_sip
GROUP BY strftime('%Y-%m', report_month)
ORDER BY month DESC
LIMIT 12;

-- Category-wise AUM split
SELECT
    f.category,
    SUM(a.aum_crore) AS aum_crore,
    COUNT(DISTINCT f.fund_id) AS scheme_count
FROM fact_aum a
JOIN dim_fund f ON a.fund_id = f.fund_id
WHERE a.report_month = (SELECT MAX(report_month) FROM fact_aum)
GROUP BY f.category
ORDER BY aum_crore DESC;

-- ============================================================
-- 2. FUND PERFORMANCE
-- ============================================================

-- 1-Year return for each scheme
SELECT
    f.scheme_name,
    f.amc_name,
    f.category,
    MAX(n.nav_value) AS current_nav,
    MIN(CASE WHEN n.nav_date >= DATE('now', '-365 days') THEN n.nav_value END) AS nav_1y_ago,
    ROUND(
        (MAX(n.nav_value) - MIN(CASE WHEN n.nav_date >= DATE('now', '-365 days') THEN n.nav_value END))
        / MIN(CASE WHEN n.nav_date >= DATE('now', '-365 days') THEN n.nav_value END) * 100, 2
    ) AS return_1y_pct
FROM fact_nav n
JOIN dim_fund f ON n.fund_id = f.fund_id
GROUP BY f.fund_id
ORDER BY return_1y_pct DESC;

-- Rolling 3-year CAGR
SELECT
    f.scheme_name,
    f.category,
    f.sub_category,
    MAX(n.nav_value) AS current_nav,
    MIN(CASE WHEN n.nav_date >= DATE('now', '-1095 days') THEN n.nav_value END) AS nav_3y_ago,
    ROUND(
        (POWER(
            MAX(n.nav_value) / NULLIF(MIN(CASE WHEN n.nav_date >= DATE('now', '-1095 days') THEN n.nav_value END), 0),
            1.0/3
        ) - 1) * 100, 2
    ) AS cagr_3y_pct
FROM fact_nav n
JOIN dim_fund f ON n.fund_id = f.fund_id
GROUP BY f.fund_id
ORDER BY cagr_3y_pct DESC;

-- Top 10 schemes by latest NAV
SELECT
    f.scheme_name,
    f.amc_name,
    f.category,
    n.nav_value,
    n.nav_date,
    n.day_change_pct
FROM fact_nav n
JOIN dim_fund f ON n.fund_id = f.fund_id
WHERE n.nav_date = (SELECT MAX(nav_date) FROM fact_nav)
ORDER BY n.nav_value DESC
LIMIT 10;

-- ============================================================
-- 3. INVESTOR DEMOGRAPHICS
-- ============================================================

-- Investor count and transaction volume by state
SELECT
    state,
    COUNT(DISTINCT investor_id) AS investor_count,
    SUM(txn_amount) AS total_invested,
    ROUND(AVG(txn_amount), 2) AS avg_ticket_size,
    SUM(CASE WHEN txn_type = 'SIP' THEN txn_amount ELSE 0 END) AS sip_amount
FROM fact_transactions
WHERE txn_type IN ('BUY', 'SIP')
GROUP BY state
ORDER BY total_invested DESC;

-- Age group distribution
SELECT
    CASE
        WHEN investor_age < 25 THEN 'Under 25'
        WHEN investor_age BETWEEN 25 AND 30 THEN '25–30'
        WHEN investor_age BETWEEN 31 AND 40 THEN '31–40'
        WHEN investor_age BETWEEN 41 AND 50 THEN '41–50'
        ELSE 'Above 50'
    END AS age_group,
    COUNT(DISTINCT investor_id) AS investor_count,
    SUM(txn_amount) AS total_invested,
    ROUND(SUM(CASE WHEN txn_type = 'SIP' THEN txn_amount ELSE 0 END) * 100.0 / SUM(txn_amount), 2) AS sip_pct
FROM fact_transactions
GROUP BY age_group
ORDER BY investor_count DESC;

-- SIP vs Lumpsum split
SELECT
    CASE WHEN txn_type = 'SIP' THEN 'SIP' ELSE 'Lumpsum' END AS investment_mode,
    COUNT(*) AS txn_count,
    SUM(txn_amount) AS total_amount,
    ROUND(SUM(txn_amount) * 100.0 / (SELECT SUM(txn_amount) FROM fact_transactions WHERE txn_type IN ('BUY','SIP')), 2) AS share_pct
FROM fact_transactions
WHERE txn_type IN ('BUY', 'SIP')
GROUP BY investment_mode;

-- City tier analysis (Tier 2 growth proxy)
SELECT
    city_tier,
    COUNT(DISTINCT investor_id) AS investors,
    SUM(txn_amount) AS total_investment,
    ROUND(AVG(txn_amount), 2) AS avg_ticket
FROM fact_transactions
GROUP BY city_tier
ORDER BY investors DESC;

-- ============================================================
-- 4. BENCHMARK COMPARISON (O7)
-- ============================================================

-- Large-cap funds vs Nifty 50 benchmark (simulated tracking error)
SELECT
    f.scheme_name,
    f.benchmark_index,
    ROUND(AVG(n.day_change_pct), 4) AS avg_daily_return,
    ROUND(
        SQRT(AVG(n.day_change_pct * n.day_change_pct) - AVG(n.day_change_pct) * AVG(n.day_change_pct)),
        4
    ) AS tracking_error_proxy
FROM fact_nav n
JOIN dim_fund f ON n.fund_id = f.fund_id
WHERE f.benchmark_index LIKE '%Nifty%'
GROUP BY f.fund_id
ORDER BY tracking_error_proxy ASC;

-- Category alpha vs Nifty 50
SELECT
    f.category,
    f.sub_category,
    ROUND(AVG(n.day_change_pct) * 252, 2) AS annualised_return_pct
FROM fact_nav n
JOIN dim_fund f ON n.fund_id = f.fund_id
GROUP BY f.category, f.sub_category
ORDER BY annualised_return_pct DESC;
