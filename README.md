# Proyek Ujian Praktik PBTGM — Aplikasi Desktop GUI Python

## Struktur Folder

```text
uprak-pbtgm/
├── assets/                 # Aset gambar/ikon (jika ada)
├── data/                   # Penyimpanan data lokal (JSON/CSV/SQLite)
├── docs/                   # Dokumentasi proyek, sprint backlog, testing & laporan
│   ├── AI_DECLARATION.md
│   ├── LAPORAN_PROYEK.md
│   ├── SPRINT_BACKLOG.md
│   └── TESTING_LOG.md
├── src/                    # Kode sumber utama aplikasi (GUI + OOP)
│   ├── app.py              # Controller utama aplikasi & navigasi antar-frame
│   ├── models/             # Model data / struktur entitas
│   ├── services/           # Logika bisnis, perhitungan, & penyimpanan data
│   ├── utils/              # Utilitas & fungsi validasi input
│   └── views/              # Komponen tampilan GUI (Tkinter / ttk.Frame)
├── tests/                  # Unit testing
├── main.py                 # Entry point aplikasi
├── requirements.txt        # Daftar dependensi proyek
└── README.md               # Dokumentasi utama repository
```

## Cara Menjalankan Proyek

1. Pastikan **Python 3.10+** sudah terpasang (beserta modul `tkinter`).
2. Jalankan aplikasi dari root folder proyek:

   ```bash
   python main.py
   ```

3. Jalankan unit test:

   ```bash
   python -m unittest discover -s tests -v
   ```
