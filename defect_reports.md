# Defect Reports — Telco Billing Data Validation

Dataset: `telco_billing.db` (customers, usage_records, invoices)

---

## DEF-01: Missing Invoice for Customers with Valid Usage

| Field | Detail |
|---|---|
| Defect ID | DEF-01 |
| Title | Invoice tidak ter-generate untuk customer yang memiliki data usage valid |
| Severity/Priority | **High** — customer terpakai layanan tapi tidak pernah ditagih, berdampak langsung pada pendapatan yang tidak tertagih (revenue leakage) |
| Steps to Reproduce | Jalankan query:<br>`SELECT DISTINCT u.customer_id FROM usage_records u LEFT JOIN invoices i ON u.customer_id = i.customer_id WHERE i.invoice_id IS NULL AND u.customer_id IS NOT NULL;` |
| Expected Result | Semua customer dengan usage memiliki invoice yang sesuai |
| Actual Result | 3 customer (ID 7, 22, 35) memiliki data usage tetapi tidak memiliki invoice sama sekali untuk periode 2026-07 |

---

## DEF-02: Null Value Found in Mandatory Field (customer_id)

| Field | Detail |
|---|---|
| Defect ID | DEF-02 |
| Title | Ditemukan record usage dengan `customer_id` kosong (NULL) |
| Severity/Priority | **Medium** — data tidak bisa diatribusikan ke customer manapun sehingga tidak bisa ditagihkan, namun dampaknya terbatas pada 1 record |
| Priority | Medium |
| Steps to Reproduce | Jalankan query:<br>`SELECT * FROM usage_records WHERE customer_id IS NULL;` |
| Expected Result | 0 baris — seluruh record usage memiliki customer_id yang valid |
| Actual Result | 1 baris ditemukan dengan `customer_id` NULL (usage_date: 2026-07-10, data_mb: 800.0, call_minutes: 20.0) |

---

## DEF-03: Orphan Usage Record Referencing Non-Existent Customer

| Field | Detail |
|---|---|
| Defect ID | DEF-03 |
| Title | Ditemukan record usage dengan `customer_id` yang tidak terdaftar di tabel customers |
| Severity/Priority | **Medium** — menunjukkan potensi masalah data integrity antar sistem, meskipun dampak langsung ke billing masih terbatas |
| Priority | Medium |
| Steps to Reproduce | Jalankan query:<br>`SELECT DISTINCT u.customer_id FROM usage_records u LEFT JOIN customers c ON u.customer_id = c.customer_id WHERE c.customer_id IS NULL AND u.customer_id IS NOT NULL;` |
| Expected Result | 0 baris — seluruh customer_id pada usage_records terdaftar di tabel customers |
| Actual Result | 1 baris ditemukan: `customer_id = 9999`, tidak ada di tabel customers |

---

## DEF-04: Duplicate Usage Record Detected

| Field | Detail |
|---|---|
| Defect ID | DEF-04 |
| Title | Ditemukan pencatatan ganda (duplikat) pada data usage customer |
| Severity/Priority | **High** — jika tidak terdeteksi, duplikat ini akan membuat customer over-billed (ditagih dua kali untuk pemakaian yang sama), berpotensi menimbulkan komplain dan masalah kepercayaan pelanggan |
| Priority | High |
| Steps to Reproduce | Jalankan query:<br>`SELECT customer_id, usage_date, data_mb, call_minutes, COUNT(*) AS jumlah_duplikat FROM usage_records GROUP BY customer_id, usage_date, data_mb, call_minutes HAVING COUNT(*) > 1;` |
| Expected Result | 0 kelompok data terduplikasi |
| Actual Result | 1 kelompok ditemukan: customer_id 3, tanggal 2026-07-15, data_mb 1200.0, call_minutes 45.0 — tercatat sebanyak 2 kali dengan usage_id berbeda |

---

## DEF-05: Invoice Amount Mismatch with Usage Calculation (Underbilling)

| Field | Detail |
|---|---|
| Defect ID | DEF-05 |
| Title | Invoice `total_amount` tidak sesuai dengan hasil kalkulasi usage (underbilling) |
| Severity/Priority | **Critical** — berdampak langsung pada pendapatan perusahaan (revenue leakage), customer ditagih lebih rendah dari yang seharusnya |
| Priority | High | 
| Steps to Reproduce | Jalankan query:<br>`SELECT i.customer_id, i.total_amount, (SUM(u.data_mb)*100)+(SUM(u.call_minutes)*250) AS amount_seharusnya, ROUND(i.total_amount-((SUM(u.data_mb)*100)+(SUM(u.call_minutes)*250)),2) AS selisih FROM invoices i JOIN usage_records u ON i.customer_id=u.customer_id GROUP BY i.customer_id, i.total_amount HAVING ABS(selisih) > 1;` |
| Expected Result | Selisih antara `total_amount` tercatat dan hasil kalkulasi = Rp0 (dalam toleransi Rp1 untuk floating point) |
| Actual Result | 3 customer dengan selisih signifikan (underbilling):<br>• Customer 3: selisih -Rp17.216<br>• Customer 15: selisih -Rp7.692<br>• Customer 40: selisih -Rp15.752 |

---

## Ringkasan Defect

| Defect ID | Title | Severity/Priority | Priority |
|---|---|---|---|
| DEF-01 | Missing invoice | High | High |
| DEF-02 | Null customer_id | Medium | Medium |
| DEF-03 | Orphan usage record | Medium | Medium |
| DEF-04 | Duplicate usage record | High | High |
| DEF-05 | Invoice amount mismatch | Critical | High |

**Total Defect: 5 | Critical: 1 | High: 2 | Medium: 2 | Low: 0**
