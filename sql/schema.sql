-- ============================================================
-- MF Analytics Platform — Star Schema
-- Bluestock Fintech Capstone
-- ============================================================

-- ============================================================
-- DIMENSION TABLE: dim_fund
-- Master fund registry across 10 AMCs and 40 schemes
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     VARCHAR(20)  NOT NULL UNIQUE,
    scheme_name     VARCHAR(255) NOT NULL,
    amc_name        VARCHAR(100) NOT NULL,
    category        VARCHAR(50)  NOT NULL,   -- Equity / Debt / Hybrid / Solution
    sub_category    VARCHAR(100),            -- Large Cap / Mid Cap / ELSS etc.
    fund_type       VARCHAR(20)  NOT NULL,   -- Open-ended / Close-ended
    launch_date     DATE,
    benchmark_index VARCHAR(100),            -- Nifty 50 / Nifty 100 / BSE SmallCap
    fund_manager    VARCHAR(100),
    expense_ratio   DECIMAL(5,2),
    min_investment  DECIMAL(12,2),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FACT TABLE: fact_nav
-- Daily Net Asset Value history for each scheme
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         INTEGER NOT NULL REFERENCES dim_fund(fund_id),
    nav_date        DATE    NOT NULL,
    nav_value       DECIMAL(15,4) NOT NULL,
    day_change      DECIMAL(10,4),           -- Absolute change from previous day
    day_change_pct  DECIMAL(8,4),            -- % change from previous day
    week_high       DECIMAL(15,4),
    week_low        DECIMAL(15,4),
    month_high      DECIMAL(15,4),
    month_low       DECIMAL(15,4),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_id, nav_date)
);

-- ============================================================
-- FACT TABLE: fact_aum
-- Monthly Assets Under Management by fund house
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         INTEGER NOT NULL REFERENCES dim_fund(fund_id),
    amc_name        VARCHAR(100) NOT NULL,
    report_month    DATE    NOT NULL,        -- First day of the month
    aum_crore       DECIMAL(15,2) NOT NULL, -- AUM in ₹ Crore
    aum_change_pct  DECIMAL(8,2),           -- MoM % change
    folio_count     INTEGER,                -- Number of folios
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_id, report_month)
);

-- ============================================================
-- FACT TABLE: fact_sip
-- Monthly SIP inflow data
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_sip (
    sip_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         INTEGER NOT NULL REFERENCES dim_fund(fund_id),
    report_month    DATE    NOT NULL,
    sip_amount_crore  DECIMAL(15,2) NOT NULL,  -- SIP inflow in ₹ Crore
    sip_count         INTEGER,                  -- Number of SIP registrations
    new_sip_count     INTEGER,                  -- New SIPs registered this month
    stopped_sip_count INTEGER,                  -- SIPs stopped this month
    avg_sip_amount    DECIMAL(10,2),            -- Average SIP ticket size
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_id, report_month)
);

-- ============================================================
-- FACT TABLE: fact_transactions
-- Investor transaction ledger (buy / sell / switch / redeem)
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         INTEGER NOT NULL REFERENCES dim_fund(fund_id),
    investor_id     VARCHAR(20) NOT NULL,
    folio_number    VARCHAR(30) NOT NULL,
    txn_date        DATE    NOT NULL,
    txn_type        VARCHAR(20) NOT NULL,     -- BUY / REDEEM / SWITCH_IN / SWITCH_OUT / SIP
    txn_amount      DECIMAL(15,2) NOT NULL,   -- Transaction amount in ₹
    nav_at_txn      DECIMAL(15,4) NOT NULL,   -- NAV on transaction date
    units           DECIMAL(15,4) NOT NULL,   -- Units purchased/redeemed
    state           VARCHAR(50),              -- Investor state
    city_tier       VARCHAR(10),              -- Tier 1 / Tier 2 / Tier 3
    investor_age    INTEGER,
    investor_gender VARCHAR(10),
    channel         VARCHAR(30),              -- Online / Offline / App / Distributor
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES for query performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_nav_fund_date   ON fact_nav(fund_id, nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_date        ON fact_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_aum_month       ON fact_aum(report_month);
CREATE INDEX IF NOT EXISTS idx_sip_month       ON fact_sip(report_month);
CREATE INDEX IF NOT EXISTS idx_txn_date        ON fact_transactions(txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_fund        ON fact_transactions(fund_id);
CREATE INDEX IF NOT EXISTS idx_txn_investor    ON fact_transactions(investor_id);
CREATE INDEX IF NOT EXISTS idx_fund_category   ON dim_fund(category, sub_category);
CREATE INDEX IF NOT EXISTS idx_fund_amc        ON dim_fund(amc_name);
