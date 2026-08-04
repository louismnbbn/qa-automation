# QA Data Validation - Telco Billing Reconciliation
A portfolio project simulating a real-world QA workflow for a telco billing system: 
1. Test case design — objective, precondition, steps, expected vs actual result
2. SQL data validation — LEFT JOIN for missing records, referential integrity checks, duplicate detection via GROUP BY/HAVING, and financial reconciliation with floating-point tolerance handling
3. Defect documentation — formal defect reports with severity/priority, root cause hypothesis, business impact, and suggested next steps
4. Test automation — a Python script that executes all validation queries and generates a PASS/FAIL summary report

Note:
All test cases are designed to fail against this intentionally corrupted dataset, in order to demonstrate detection capability across different data quality issue categories. 

🛠️ **Tech Stack**
Python 3 — data generation & automation
SQLite — relational database
SQL — data validation queries (JOIN, GROUP BY/HAVING, aggregation, NULL handling)
DB Browser for SQLite — manual data inspection during development

