-- 1
SELECT * FROM fund_master LIMIT 10;

-- 2
SELECT fund_house, COUNT(*) AS total_funds
FROM fund_master
GROUP BY fund_house
ORDER BY total_funds DESC;

-- 3
SELECT AVG(nav) AS average_nav
FROM nav_history;

-- 4
SELECT amfi_code, MAX(nav) AS highest_nav
FROM nav_history
GROUP BY amfi_code
ORDER BY highest_nav DESC
LIMIT 5;

-- 5
SELECT transaction_type,
COUNT(*) total_transactions
FROM investor_transactions
GROUP BY transaction_type;

-- 6
SELECT state,
SUM(amount_inr) total_amount
FROM investor_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 7
SELECT AVG(expense_ratio_pct)
FROM scheme_performance;

-- 8
SELECT *
FROM scheme_performance
WHERE expense_ratio_pct < 1;

-- 9
SELECT category,
COUNT(*) total_schemes
FROM fund_master
GROUP BY category;

-- 10
SELECT benchmark,
COUNT(*) total
FROM fund_master
GROUP BY benchmark;