"""
run_validation.py
-------------------
Automation script untuk menjalankan seluruh SQL validation query terhadap
database 'telco_billing.db' secara otomatis, dan menghasilkan laporan
PASS/FAIL untuk setiap test case.
"""

import sqlite3
from datetime import datetime

DB_NAME = "telco_billing.db"
REPORT_FILE = "validation_report.txt"


# Setiap test case didefinisikan sebagai dictionary:
# id, objective, query, dan defect_id (referensi ke defect_reports.md jika FAIL)
TEST_CASES = [
    {
        "id": "TC-01",
        "objective": "Verify all usage records have a corresponding invoice",
        "query": """
            SELECT DISTINCT u.customer_id
            FROM usage_records u
            LEFT JOIN invoices i ON u.customer_id = i.customer_id
            WHERE i.invoice_id IS NULL
        """,
        "defect_id": "DEF-01 (dan terkait DEF-02, DEF-03)"
    },
    {
        "id": "TC-02",
        "objective": "Verify no mandatory field (customer_id) is null",
        "query": """
            SELECT *
            FROM usage_records
            WHERE customer_id IS NULL
        """,
        "defect_id": "DEF-02"
    },
    {
        "id": "TC-03",
        "objective": "Verify referential integrity between usage_records and customers",
        "query": """
            SELECT DISTINCT u.customer_id
            FROM usage_records u
            LEFT JOIN customers c ON u.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
              AND u.customer_id IS NOT NULL
        """,
        "defect_id": "DEF-03"
    },
    {
        "id": "TC-04",
        "objective": "Verify no duplicate usage records",
        "query": """
            SELECT customer_id, usage_date, data_mb, call_minutes, COUNT(*) AS jumlah_duplikat
            FROM usage_records
            GROUP BY customer_id, usage_date, data_mb, call_minutes
            HAVING COUNT(*) > 1
        """,
        "defect_id": "DEF-04"
    },
    {
        "id": "TC-05",
        "objective": "Verify invoice amount matches usage calculation",
        "query": """
            SELECT
                i.customer_id,
                i.total_amount,
                (SUM(u.data_mb) * 100) + (SUM(u.call_minutes) * 250) AS amount_seharusnya,
                ROUND(i.total_amount - ((SUM(u.data_mb) * 100) + (SUM(u.call_minutes) * 250)), 2) AS selisih
            FROM invoices i
            JOIN usage_records u ON i.customer_id = u.customer_id
            GROUP BY i.customer_id, i.total_amount
            HAVING ABS(selisih) > 1
        """,
        "defect_id": "DEF-05"
    },
]


def run_test_case(conn, test_case):
    """
    Menjalankan query validasi.
    Jika query mengembalikan 0 baris -> PASSED (tidak ada masalah)
    Jika query mengembalikan >0 baris -> FAILED (ada data bermasalah)
    """
    cur = conn.cursor()
    cur.execute(test_case["query"])
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    status = "PASSED" if len(rows) == 0 else "FAILED"

    return {
        "id": test_case["id"],
        "objective": test_case["objective"],
        "status": status,
        "row_count": len(rows),
        "columns": columns,
        "sample_rows": rows[:5],  # tampilkan maksimal 5 baris contoh
        "defect_id": test_case["defect_id"] if status == "FAILED" else None
    }


def print_summary(results):
    """Cetak ringkasan hasil ke terminal"""
    print("=" * 70)
    print("QA DATA VALIDATION REPORT — Telco Billing Reconciliation")
    print("=" * 70)

    for r in results:
        print(f"\n [{r['id']}] {r['objective']}")
        print(f"   Status      : {r['status']}")
        print(f"   Data Ditemukan : {r['row_count']} baris bermasalah")
        if r["status"] == "FAILED":
            print(f"   Referensi   : {r['defect_id']}")
            print(f"   Contoh Data : {r['sample_rows'][:2]}")

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = total - passed

    print("\n" + "=" * 70)
    print(f"TOTAL TEST CASE : {total}")
    print(f"PASSED          : {passed}")
    print(f"FAILED          : {failed}")
    print("=" * 70)


def write_report_file(results):
    """Simpan laporan detail ke file teks"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("QA DATA VALIDATION REPORT — Telco Billing Reconciliation\n")
        f.write("=" * 70 + "\n\n")

        for r in results:
            f.write(f"[{r['id']}] {r['objective']}\n")
            f.write(f"Status          : {r['status']}\n")
            f.write(f"Baris Bermasalah: {r['row_count']}\n")
            if r["status"] == "FAILED":
                f.write(f"Referensi Defect: {r['defect_id']}\n")
                f.write(f"Kolom           : {r['columns']}\n")
                f.write("Contoh Data     :\n")
                for row in r["sample_rows"]:
                    f.write(f"    {row}\n")
            f.write("-" * 70 + "\n\n")

        total = len(results)
        passed = sum(1 for r in results if r["status"] == "PASSED")
        failed = total - passed

        f.write(f"TOTAL TEST CASE : {total}\n")
        f.write(f"PASSED          : {passed}\n")
        f.write(f"FAILED          : {failed}\n")

    print(f"\n📄 Laporan detail tersimpan di: {REPORT_FILE}")


def main():
    conn = sqlite3.connect(DB_NAME)

    results = []
    for tc in TEST_CASES:
        result = run_test_case(conn, tc)
        results.append(result)

    conn.close()

    print_summary(results)
    write_report_file(results)


if __name__ == "__main__":
    main()