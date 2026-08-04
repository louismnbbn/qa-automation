"""
generate_data.py
"""

import sqlite3
import random
from datetime import date, timedelta

DB_NAME = "telco_billing.db"

# Tarif dummy (sebagai "business rule")
TARIF_PER_MB = 100        # Rp 100 per MB
TARIF_PER_MENIT = 250     # Rp 250 per menit telepon


def create_schema(conn):
    """Membuat 3 tabel: customers, usage_records, invoices"""
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            plan_type TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE usage_records (
            usage_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            usage_date TEXT,
            data_mb REAL,
            call_minutes REAL
        )
    """)

    cur.execute("""
        CREATE TABLE invoices (
            invoice_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            period TEXT,
            total_amount REAL,
            status TEXT
        )
    """)

    conn.commit()
    print(" Schema berhasil dibuat: customers, usage_records, invoices")


def generate_customers(conn, jumlah=50):
    """Generate data customer bersih (tidak ada masalah di tabel ini)"""
    cur = conn.cursor()
    plans = ["Prepaid", "Postpaid", "Unlimited"]
    statuses = ["Active", "Suspended", "Inactive"]

    for cid in range(1, jumlah + 1):
        cur.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?)",
            (cid, f"Customer_{cid}", random.choice(plans), random.choice(statuses))
        )

    conn.commit()
    print(f" {jumlah} data customer berhasil dibuat")


def generate_usage_records(conn, jumlah_customer=50):
    """
    Generate usage records. Masalah yg disisipkan:
    - Beberapa usage_id DUPLIKAT
    - Beberapa customer_id NULL (data wajib kosong)
    - Beberapa customer_id tidak terdaftar di tabel customers (orphan)
    """
    cur = conn.cursor()
    usage_id = 1
    start_date = date(2026, 7, 1)

    for cid in range(1, jumlah_customer + 1):
        # tiap customer punya 3-5 record usage per bulan
        for _ in range(random.randint(3, 5)):
            usage_date = start_date + timedelta(days=random.randint(0, 29))
            data_mb = round(random.uniform(100, 5000), 2)
            call_minutes = round(random.uniform(0, 300), 2)

            cur.execute(
                "INSERT INTO usage_records VALUES (?, ?, ?, ?, ?)",
                (usage_id, cid, usage_date.isoformat(), data_mb, call_minutes)
            )
            usage_id += 1

    # --- Masalah DATA KOTOR yang disisipkan ---

    # 1. Duplikat data usage (customer_id + tanggal + data_mb + call_minutes sama persis,
    #    tapi usage_id beda -> simulasi bug "data ke-insert dua kali oleh sistem")
    cur.execute(
        "INSERT INTO usage_records VALUES (?, ?, ?, ?, ?)",
        (usage_id, 3, "2026-07-15", 1200.0, 45.0)
    )
    usage_id += 1
    cur.execute(
        "INSERT INTO usage_records VALUES (?, ?, ?, ?, ?)",
        (usage_id, 3, "2026-07-15", 1200.0, 45.0)
    )
    usage_id += 1

    # 2. customer_id NULL (data wajib kosong)
    cur.execute(
        "INSERT INTO usage_records VALUES (?, ?, ?, ?, ?)",
        (usage_id, None, "2026-07-10", 800.0, 20.0)
    )
    usage_id += 1

    # 3. customer_id yang tidak ada di tabel customers (orphan record)
    cur.execute(
        "INSERT INTO usage_records VALUES (?, ?, ?, ?, ?)",
        (usage_id, 9999, "2026-07-12", 500.0, 10.0)
    )
    usage_id += 1

    conn.commit()
    print(" Usage records berhasil dibuat (termasuk data kotor: duplikat, null, orphan)")


def generate_invoices(conn, jumlah_customer=50):
    """
    Generate invoice berdasarkan total usage tiap customer.
    Masalah yang disisipkan:
    - Beberapa invoice total_amount TIDAK SESUAI hasil kalkulasi usage
    - Beberapa customer usage-nya TIDAK PUNYA invoice sama sekali (data hilang)
    """
    cur = conn.cursor()
    invoice_id = 1
    period = "2026-07"

    for cid in range(1, jumlah_customer + 1):
        # Lewati beberapa customer secara sengaja -> usage ada, invoice tidak ada
        if cid in (7, 22, 35):
            continue

        cur.execute(
            "SELECT SUM(data_mb), SUM(call_minutes) FROM usage_records WHERE customer_id = ?",
            (cid,)
        )
        total_mb, total_minutes = cur.fetchone()
        total_mb = total_mb or 0
        total_minutes = total_minutes or 0

        amount_seharusnya = (total_mb * TARIF_PER_MB) + (total_minutes * TARIF_PER_MENIT)

        # Sengaja bikin beberapa invoice amount-nya SALAH (selisih dari perhitungan asli)
        if cid in (3, 15, 40):
            amount_final = amount_seharusnya - random.randint(5000, 20000)  # kurang bayar
        else:
            amount_final = amount_seharusnya

        cur.execute(
            "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
            (invoice_id, cid, period, round(amount_final, 2), "Issued")
        )
        invoice_id += 1

    conn.commit()
    print(" Invoices telah dibuat (termasuk data kotor: amount mismatch, invoice hilang)")


def main():
    conn = sqlite3.connect(DB_NAME)
    create_schema(conn)
    generate_customers(conn)
    generate_usage_records(conn)
    generate_invoices(conn)
    conn.close()
    print(f"\n Selesai! Database '{DB_NAME}' siap dipakai untuk tahap validasi SQL.")


if __name__ == "__main__":
    main()