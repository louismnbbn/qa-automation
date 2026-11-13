# QA Automation with CI/CD Security Pipeline

[![CI & Security Scan](https://github.com/louismnbbn/qa-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/louismnbbn/qa-automation/actions/workflows/ci.yml)

A portfolio project simulating a real-world QA workflow for a telco billing system, backed by a GitHub Actions pipeline that runs automated data validation and security scans on every push and pull request.

## What This Project Covers

1. **Test case design**: objective, precondition, steps, expected vs actual result (`test_cases.md`)
2. **SQL data validation**: LEFT JOIN for missing records, referential integrity checks, duplicate detection via GROUP BY/HAVING, and financial reconciliation with floating-point tolerance handling
3. **Defect documentation**: formal defect reports with severity/priority, root cause hypothesis, business impact, and suggested next steps (`defect_reports.md`)
4. **Test automation**: a Python script that executes all validation queries and generates a PASS/FAIL summary report (`run_validation.py`)
5. **CI/CD security pipeline**: automated SAST, SCA, and secrets scanning with GitHub Actions (`.github/workflows/ci.yml`)

> **Note:** All test cases are designed to fail against this intentionally corrupted dataset, in order to demonstrate detection capability across different data quality issue categories.

## CI/CD Pipeline

The workflow **CI & Security Scan** runs on every `push` and `pull_request` and has two jobs:

| Job | Step | Tool | Purpose |
|---|---|---|---|
| `validate` | Generate data and run validation | Python, SQLite | Rebuilds the database, runs all validation queries, uploads `validation_report.txt` as an artifact |
| `security` | SAST | [Bandit](https://github.com/PyCQA/bandit) | Static analysis of Python code (medium severity and above) |
| `security` | SCA | [pip-audit](https://github.com/pypa/pip-audit) | Checks Python dependencies for known vulnerabilities |
| `security` | Secrets scan | [Gitleaks](https://github.com/gitleaks/gitleaks-action) | Scans the full commit history for leaked credentials |

The `security` job fails the pipeline if any scan reports a finding. Permissions are limited to `contents: read`.

### Why `run_validation.py || true`?

The dataset is intentionally corrupted, so the validation script is expected to report FAIL results. `|| true` keeps the `validate` job from failing for that expected reason, so the report is always generated and uploaded as an artifact. The security scans are **not** configured to ignore errors.

## Troubleshooting Log

**Problem:** The first pipeline run failed in the `validate` job:

```
sqlite3.OperationalError: table customers already exists
```

**Root cause:** The generated database `telco_billing.db` had been committed to the repository. After checkout, the file already existed, so `CREATE TABLE` in `generate_data.py` failed.

**Fix:**
1. Added `rm -f telco_billing.db` before data generation in the workflow so the database is always rebuilt from scratch.
2. Removed `telco_billing.db` from the repository and added it to `.gitignore`, since it is a generated artifact and not source code.

## Run Locally

```bash
# 1. Generate the (intentionally corrupted) dataset
python generate_data.py

# 2. Run all validation queries and produce the PASS/FAIL report
python run_validation.py
```

If you run it again, delete the old database first to avoid the `table already exists` error:

```bash
rm -f telco_billing.db
```

Optional: run the security scans locally.

```bash
pip install bandit pip-audit
bandit -r . -ll
pip-audit
```

## Repository Structure

```
.
├── .github/workflows/ci.yml   # CI & security pipeline
├── generate_data.py           # Generates the corrupted telco billing dataset
├── run_validation.py          # Runs validation queries, writes the report
├── test_cases.md              # Test case design
├── defect_reports.md          # Formal defect reports
├── validation_report.txt      # Sample PASS/FAIL output
└── README.md
```

## Tech Stack

- **Python 3**: data generation and automation
- **SQLite**: relational database
- **SQL**: validation queries (JOIN, GROUP BY/HAVING, aggregation, NULL handling)
- **GitHub Actions**: CI/CD
- **Bandit, pip-audit, Gitleaks**: SAST, SCA, and secrets scanning
- **DB Browser for SQLite**: manual data inspection during development
