# Proyek Ujian Praktik PBTGM — Aplikasi Desktop GUI Python

> **Mata Pelajaran:** Pemrograman Berorientasi Teks, Grafis, dan Multimedia (PBTGM)  
> **Kelas:** XII RPL 1 — SMK Plus Pelita Nusantara  
> **Tahun Ajaran:** 2026–2027

## Identitas Kelompok

- **Kelompok:** `[Nomor/Nama Kelompok]`
- **Soal Praktik:** `[1 / 2 / 3]`
- **Domain Studi Kasus:** `[Nama Domain]`
- **Judul Aplikasi:** `[Judul Aplikasi GUI]`
- **Link Desain Figma:** `https://www.figma.com/...`

### Pembagian Peran Tim

| No | Nama Anggota | Peran | Tanggung Jawab Utama |
| :-: | :--- | :--- | :--- |
| 1 | `[Nama]` | Project Manager (PM) | Koordinasi tim, Sprint Backlog, manajemen GitHub & laporan |
| 2 | `[Nama]` | UI/UX Designer | Desain wireframe & frame Figma, konsistensi visual |
| 3 | `[Nama]` | Programmer | Implementasi GUI Python (Tkinter/ttk), OOP, Event Handling, Validasi |
| 4 | `[Nama]` | QA Tester | Test case (valid/invalid), code review, debugging log |

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

## Alur Kolaborasi Git

1. Tarik pembaruan terbaru sebelum bekerja: `git pull origin main`
2. Buat branch fitur sesuai tugas (misal: `feat/login-ui`, `fix/validasi-input`).
3. Commit perubahan dengan pesan yang jelas (misal: `feat: tambah form login`).
4. Push dan buat Pull Request ke `main` setelah diuji.
