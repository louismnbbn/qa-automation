# Test Cases — Telco Billing Data Validation

Dataset: `telco_billing.db` (customers, usage_records, invoices)
Business Rule: `total_amount = (total_data_mb × Rp100) + (total_call_minutes × Rp250)`

---

## TC-01: Verifikasi semua catatan penggunaan memiliki Invoice yang sesuai.

| Field | Detail |
|---|---|
| Test Case ID | TC-01 |
| Objective | Memastikan setiap customer yang memiliki data usage juga memiliki invoice pada periode yang sama |
| Precondition | Tabel `usage_records` dan `invoices` sudah terisi untuk periode yang sama |
| Steps | 1. Ambil seluruh `customer_id` unik dari `usage_records`<br>2. Lakukan LEFT JOIN ke tabel `invoices`<br>3. Filter baris di mana tidak ditemukan pasangan invoice |
| Expected Result | Tidak ada `customer_id` yang muncul (0 baris) — semua usage record memiliki invoice |
| Actual Result | 5 `customer_id` ditemukan: 7, 22, 35 (invoice benar-benar hilang), serta NULL dan 9999 (terdeteksi karena masalah data quality lain, dijelaskan pada TC-02 dan TC-03) |
| Status | **Failed** |

---

## TC-02: Verifikasi tidak ada kolom wajib (customer_id) yang bernilai Null.

| Field | Detail |
|---|---|
| Test Case ID | TC-02 |
| Objective | Memastikan kolom `customer_id` pada `usage_records`, sebagai field wajib, tidak memiliki nilai NULL |
| Precondition | Tabel `usage_records` sudah terisi |
| Steps | 1. Query seluruh baris di `usage_records`<br>2. Filter baris dengan `customer_id IS NULL` |
| Expected Result | 0 baris ditemukan |
| Actual Result | 1 baris ditemukan dengan `customer_id` kosong (usage_date: 2026-07-10, data_mb: 800.0) |
| Status | **Failed** |

---

## TC-03: Verifikasi Integritas antara Catatan Penggunaan dan Pelanggan.

| Field | Detail |
|---|---|
| Test Case ID | TC-03 |
| Objective | Memastikan setiap `customer_id` pada `usage_records` merujuk ke customer yang benar-benar terdaftar di tabel `customers` |
| Precondition | Tabel `customers` dan `usage_records` sudah terisi |
| Steps | 1. LEFT JOIN `usage_records` ke `customers` berdasarkan `customer_id`<br>2. Filter baris yang tidak ditemukan pasangannya di `customers`<br>3. Kecualikan baris dengan `customer_id` NULL |
| Expected Result | 0 baris ditemukan |
| Actual Result | 1 baris ditemukan: `customer_id = 9999`, tidak terdaftar di tabel `customers` |
| Status | **Failed** |

---

## TC-04: Verifikasi tidak ada catatan yang Duplikat.

| Field | Detail |
|---|---|
| Test Case ID | TC-04 |
| Objective | Memastikan tidak ada duplikat pada data usage dengan kombinasi customer, tanggal, dan jumlah pemakaian yang identik |
| Precondition | Tabel `usage_records` sudah terisi |
| Steps | 1. Kelompokkan data berdasarkan `customer_id`, `usage_date`, `data_mb`, `call_minutes`<br>2. Hitung jumlah anggota tiap kelompok<br>3. Filter kelompok dengan jumlah anggota lebih dari 1 |
| Expected Result | 0 kelompok ditemukan (tidak ada data duplikat) |
| Actual Result | 1 kelompok ditemukan: customer_id 3, tanggal 2026-07-15, data_mb 1200.0, call_minutes 45.0 — tercatat 2 kali |
| Status | **Failed** |

---

## TC-05: Verifikasi Jumlah Tagihan Sesuai dengan Perhitungan Penggunaan

| Field | Detail |
|---|---|
| Test Case ID | TC-05 |
| Objective | Memverifikasi bahwa `total_amount` pada tabel `invoices` sesuai dengan hasil kalkulasi total pemakaian pada tabel `usage_records`, berdasarkan business rule tarif yang berlaku |
| Precondition | Data usage dan invoice untuk periode yang sama sudah tersedia |
| Steps | 1. Hitung total `data_mb` dan `call_minutes` per customer dari `usage_records`<br>2. Hitung `amount_seharusnya` berdasarkan business rule<br>3. Bandingkan dengan `total_amount` tercatat di `invoices`<br>4. Beri toleransi floating point (selisih ≤ Rp1 dianggap sama) untuk menghindari false positive akibat presisi desimal |
| Expected Result | 0 baris ditemukan (seluruh invoice sesuai hasil kalkulasi dengan toleransi selisih Rp1) |
| Actual Result | 3 baris ditemukan dengan selisih signifikan:<br>• Customer 3: selisih -Rp17.216<br>• Customer 15: selisih -Rp7.692<br>• Customer 40: selisih -Rp15.752 |
| Status | **Failed** |

---

**Total Test Case: 5 | Passed: 0 | Failed: 5**

> Catatan: Seluruh test case gagal karena dataset ini sengaja dirancang dengan data anomali untuk keperluan portofolio QA. Setiap kegagalan didokumentasikan lebih lanjut sebagai defect report terpisah (lihat `defect_reports.md`).
