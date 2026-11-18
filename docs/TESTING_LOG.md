# Dokumentasi Pengujian (Test Case) & Debugging Log

## 1. Tabel Hasil Pengujian (Test Case)

> Uji minimal mencakup skenario **input valid** dan **input tidak valid** (kolom kosong, tipe angka salah/negatif, dll.).

| ID | Fitur / Form | Skenario Uji | Input Uji | Hasil Diharapkan | Hasil Aktual | Status |
| :-: | :--- | :--- | :--- | :--- | :--- | :-: |
| TC-01 | Login | Input kosong | Username/Password kosong | Muncul `messagebox` peringatan | `[Isi hasil]` | `[Pass/Fail]` |
| TC-02 | Form Input | Input angka negatif/huruf | Jumlah = `-1` / `abc` | Ditolak dengan `messagebox` | `[Isi hasil]` | `[Pass/Fail]` |
| TC-03 | Form Input | Input data valid | Data lengkap & benar | Data tersimpan & tampil di Treeview | `[Isi hasil]` | `[Pass/Fail]` |

## 2. Catatan Perbaikan Bug (Debugging Log)

> Dokumentasikan minimal **3 temuan bug** beserta perbaikannya.

| No | Tanggal | Deskripsi Bug | Penyebab | Solusi / Perbaikan | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
| 1 | `[YYYY-MM-DD]` | `[Contoh: Error saat input kosong]` | `[Penyebab]` | `[Perbaikan]` | `[Fixed]` |
| 2 | `[YYYY-MM-DD]` | `[Temuan 2]` | `[Penyebab]` | `[Perbaikan]` | `[Fixed]` |
| 3 | `[YYYY-MM-DD]` | `[Temuan 3]` | `[Penyebab]` | `[Perbaikan]` | `[Fixed]` |
