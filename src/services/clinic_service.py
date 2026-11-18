"""Layanan bisnis, data seed, antrean poli, pasien, dan laporan Heptamed Klinik."""

import csv
from datetime import datetime
from pathlib import Path

from src.models.patient import Patient
from src.models.queue_item import QueueItem


class ClinicService:
    """Mengelola state pasien, antrean poli, autentikasi, dan statistik laporan."""

    # Offset baseline historis agar tampilan awal 1:1 dengan rekap klinik (1.248 pasien, dst.)
    _HIST_TOTAL_OFFSET = 1236
    _HIST_NEW_OFFSET = 74
    _HIST_BPJS_OFFSET = 978
    _HIST_UMUM_OFFSET = 258

    def __init__(self) -> None:
        self.staff_name = "Nadia Rahma"
        self.staff_role = "Petugas pendaftaran"
        self.staff_badge = "STAF"
        self.current_date_label = "Rabu, 18 November 2026"

        assets_dir = Path(__file__).resolve().parents[2] / "assets"
        abdul_avatar = str(assets_dir / "avatar_abdul.png")

        self.patients: list[Patient] = [
            Patient(
                no_rm="RM-00241",
                nik="3273010101840001",
                nama="Budi Santoso",
                tanggal_lahir="10 Mei 1984",
                usia=42,
                jenis_kelamin="Laki-laki",
                telepon="0812 1111 0001",
                alamat="Jl. Dago No. 12, Bandung",
                penjamin="BPJS",
                pasien_sejak="2024",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=12,
            ),
            Patient(
                no_rm="RM-00242",
                nik="3273010202980002",
                nama="Dewi Lestari",
                tanggal_lahir="02 Februari 1998",
                usia=28,
                jenis_kelamin="Perempuan",
                telepon="0812 1111 0002",
                alamat="Jl. Riau No. 45, Bandung",
                penjamin="Umum",
                pasien_sejak="2025",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=5,
            ),
            Patient(
                no_rm="RM-00243",
                nik="3273010303910003",
                nama="Andi Pratama",
                tanggal_lahir="03 Maret 1991",
                usia=35,
                jenis_kelamin="Laki-laki",
                telepon="0812 1111 0003",
                alamat="Jl. Braga No. 8, Bandung",
                penjamin="BPJS",
                pasien_sejak="2023",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=18,
            ),
            Patient(
                no_rm="RM-00244",
                nik="3273010404950004",
                nama="Rina Wulandari",
                tanggal_lahir="04 April 1995",
                usia=31,
                jenis_kelamin="Perempuan",
                telepon="0812 1111 0004",
                alamat="Jl. Cihampelas No. 21, Bandung",
                penjamin="BPJS",
                pasien_sejak="2024",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=9,
            ),
            Patient(
                no_rm="RM-00245",
                nik="3273010505700005",
                nama="Siti Aminah",
                tanggal_lahir="05 Mei 1970",
                usia=56,
                jenis_kelamin="Perempuan",
                telepon="0812 1111 0005",
                alamat="Jl. Setiabudi No. 67, Bandung",
                penjamin="Umum",
                pasien_sejak="2022",
                kunjungan_terakhir="17 Nov 2026",
                jumlah_kunjungan=24,
            ),
            Patient(
                no_rm="RM-00246",
                nik="3273010606020006",
                nama="Ahmad Fauzi",
                tanggal_lahir="06 Juni 2002",
                usia=24,
                jenis_kelamin="Laki-laki",
                telepon="0812 1111 0006",
                alamat="Jl. Sukajadi No. 19, Bandung",
                penjamin="BPJS",
                pasien_sejak="2025",
                kunjungan_terakhir="17 Nov 2026",
                jumlah_kunjungan=4,
            ),
            # Halaman 2 & 3 (termasuk Abdul Rijman sesuai detail screen)
            Patient(
                no_rm="RM-00247",
                nik="327330210330",
                nama="Abdul Rijman",
                tanggal_lahir="21 Maret 1980",
                usia=46,
                jenis_kelamin="Laki-laki",
                telepon="0813 2200 1046",
                alamat="Jl. Dipatiukur No. 33, Bandung",
                penjamin="BPJS",
                pasien_sejak="2023",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=67,
                avatar_path=abdul_avatar,
            ),
            Patient(
                no_rm="RM-00248",
                nik="3273010808920008",
                nama="Nadia Putri",
                tanggal_lahir="08 Agustus 1992",
                usia=34,
                jenis_kelamin="Perempuan",
                telepon="0812 3344 0008",
                alamat="Jl. Pasirkaliki No. 10, Bandung",
                penjamin="BPJS",
                pasien_sejak="2024",
                kunjungan_terakhir="16 Nov 2026",
                jumlah_kunjungan=7,
            ),
            Patient(
                no_rm="RM-00249",
                nik="3273010909880009",
                nama="Hendra Wijaya",
                tanggal_lahir="09 September 1988",
                usia=38,
                jenis_kelamin="Laki-laki",
                telepon="0812 3344 0009",
                alamat="Jl. Buah Batu No. 90, Bandung",
                penjamin="Umum",
                pasien_sejak="2025",
                kunjungan_terakhir="16 Nov 2026",
                jumlah_kunjungan=3,
            ),
            Patient(
                no_rm="RM-00250",
                nik="3273011010990010",
                nama="Maya Kusuma",
                tanggal_lahir="10 Oktober 1999",
                usia=27,
                jenis_kelamin="Perempuan",
                telepon="0812 3344 0010",
                alamat="Jl. Antapani No. 14, Bandung",
                penjamin="BPJS",
                pasien_sejak="2024",
                kunjungan_terakhir="15 Nov 2026",
                jumlah_kunjungan=6,
            ),
            Patient(
                no_rm="RM-00251",
                nik="3273011111790011",
                nama="Rizky Ramadhan",
                tanggal_lahir="11 November 1979",
                usia=47,
                jenis_kelamin="Laki-laki",
                telepon="0812 3344 0011",
                alamat="Jl. Soekarno Hatta No. 102, Bandung",
                penjamin="BPJS",
                pasien_sejak="2023",
                kunjungan_terakhir="15 Nov 2026",
                jumlah_kunjungan=15,
            ),
            Patient(
                no_rm="RM-00252",
                nik="3273011212010012",
                nama="Lina Marlina",
                tanggal_lahir="12 Desember 2001",
                usia=25,
                jenis_kelamin="Perempuan",
                telepon="0812 3344 0012",
                alamat="Jl. Cibaduyut No. 5, Bandung",
                penjamin="Umum",
                pasien_sejak="2026",
                kunjungan_terakhir="14 Nov 2026",
                jumlah_kunjungan=2,
            ),
        ]

        self.queue_items: list[QueueItem] = [
            QueueItem("A-001", "RM-00241", "Budi Santoso", 42, "Poli Umum", "08.02", "Diperiksa"),
            QueueItem("A-002", "RM-00242", "Dewi Lestari", 28, "Poli Umum", "08.10", "Menunggu"),
            QueueItem("A-003", "RM-00243", "Andi Pratama", 35, "Poli Umum", "08.14", "Selesai"),
            QueueItem("G-001", "RM-00244", "Rina Wulandari", 31, "Poli Gigi", "08.20", "Menunggu"),
            QueueItem("K-001", "RM-00245", "Siti Aminah", 56, "Poli Anak", "08.25", "Menunggu"),
            QueueItem("K-002", "RM-00246", "Ahmad Fauzi", 24, "Poli Anak", "08.32", "Menunggu"),
        ]

        self._new_registrations_count = 0

    def authenticate(self, email: str, password: str) -> tuple[bool, str]:
        """Validasi login staf klinik."""
        clean_email = email.strip()
        if clean_email and "@" not in clean_email:
            return False, "Format email tidak valid."
        if clean_email and not password.strip():
            return False, "Masukkan kata sandi terlebih dahulu."
        return True, "Berhasil masuk."

    def get_patient_kpis(self) -> dict[str, int | str]:
        """Hitung metrik KPI untuk halaman Data Pasien."""
        total = self._HIST_TOTAL_OFFSET + len(self.patients)
        baru = self._HIST_NEW_OFFSET + len(self.patients)
        bpjs_count = self._HIST_BPJS_OFFSET + sum(1 for p in self.patients if p.penjamin == "BPJS")
        umum_count = self._HIST_UMUM_OFFSET + sum(1 for p in self.patients if p.penjamin == "Umum")
        bpjs_pct = round((bpjs_count / total) * 100) if total else 0
        umum_pct = 100 - bpjs_pct if total else 0
        return {
            "total": total,
            "baru": baru,
            "bpjs": bpjs_count,
            "bpjs_pct": bpjs_pct,
            "umum": umum_count,
            "umum_pct": umum_pct,
        }

    def filter_patients(
        self, query: str = "", penjamin: str = "Semua penjamin", gender: str = "Semua jenis kelamin"
    ) -> list[Patient]:
        """Filter daftar pasien berdasarkan teks pencarian, penjamin, dan jenis kelamin."""
        q = query.strip().lower()
        result: list[Patient] = []
        for p in self.patients:
            if penjamin != "Semua penjamin" and p.penjamin != penjamin:
                continue
            if gender != "Semua jenis kelamin" and p.jenis_kelamin != gender:
                continue
            if q and not (
                q in p.nama.lower() or q in p.nik.lower() or q in p.no_rm.lower()
            ):
                continue
            result.append(p)
        return result

    def get_patient_by_rm(self, no_rm: str) -> Patient | None:
        """Cari pasien berdasarkan nomor rekam medis."""
        for p in self.patients:
            if p.no_rm == no_rm:
                return p
        return None

    def get_queue_kpis(self) -> dict[str, int]:
        """Hitung ringkasan antrean hari ini."""
        return {
            "total": len(self.queue_items),
            "menunggu": sum(1 for q in self.queue_items if q.status == "Menunggu"),
            "diperiksa": sum(1 for q in self.queue_items if q.status == "Diperiksa"),
            "selesai": sum(1 for q in self.queue_items if q.status == "Selesai"),
        }

    def get_active_serving(self) -> QueueItem | None:
        """Kembalikan antrean yang sedang berstatus Diperiksa."""
        for q in self.queue_items:
            if q.status == "Diperiksa":
                return q
        return None

    def filter_queue(
        self, query: str = "", poli: str = "Semua poli", status: str = "Semua status"
    ) -> list[QueueItem]:
        """Filter antrean poli."""
        q = query.strip().lower()
        result: list[QueueItem] = []
        for item in self.queue_items:
            if poli != "Semua poli" and item.poli != poli:
                continue
            if status != "Semua status" and item.status != status:
                continue
            if q and not (
                q in item.nama_pasien.lower()
                or q in item.no_antrean.lower()
                or q in item.no_rm.lower()
            ):
                continue
            result.append(item)
        return result

    def call_queue_item(self, no_antrean: str) -> None:
        """Panggil pasien untuk diperiksa (status menjadi Diperiksa)."""
        target = next((q for q in self.queue_items if q.no_antrean == no_antrean), None)
        if not target:
            return
        for q in self.queue_items:
            if q.poli == target.poli and q.status == "Diperiksa":
                q.status = "Selesai"
        target.status = "Diperiksa"

    def complete_queue_item(self, no_antrean: str) -> None:
        """Tandai pelayanan antrean selesai."""
        for q in self.queue_items:
            if q.no_antrean == no_antrean:
                q.status = "Selesai"
                break

    def _next_rm(self) -> str:
        max_num = 240
        for p in self.patients:
            if p.no_rm.startswith("RM-"):
                try:
                    max_num = max(max_num, int(p.no_rm.split("-")[1]))
                except ValueError:
                    pass
        return f"RM-{max_num + 1:05d}"

    def _next_queue_no(self, poli: str) -> str:
        prefix = {"Poli Umum": "A", "Poli Gigi": "G", "Poli Anak": "K"}.get(poli, "A")
        max_num = 0
        for q in self.queue_items:
            if q.no_antrean.startswith(f"{prefix}-"):
                try:
                    max_num = max(max_num, int(q.no_antrean.split("-")[1]))
                except ValueError:
                    pass
        return f"{prefix}-{max_num + 1:03d}"

    def register_patient(
        self,
        nik: str,
        nama: str,
        tanggal_lahir: str,
        usia: int,
        jenis_kelamin: str,
        telepon: str,
        alamat: str,
        poli: str,
        penjamin: str = "BPJS",
    ) -> tuple[Patient, QueueItem]:
        """Simpan pasien baru (atau pakai pasien lama jika NIK sama) dan terbitkan antrean."""
        existing = next((p for p in self.patients if p.nik == nik.strip()), None)
        if existing is None:
            patient = Patient(
                no_rm=self._next_rm(),
                nik=nik.strip(),
                nama=nama.strip(),
                tanggal_lahir=tanggal_lahir.strip(),
                usia=usia,
                jenis_kelamin=jenis_kelamin,
                telepon=telepon.strip(),
                alamat=alamat.strip(),
                penjamin=penjamin,
                pasien_sejak="2026",
                kunjungan_terakhir="18 Nov 2026",
                jumlah_kunjungan=1,
            )
            self.patients.insert(0, patient)
        else:
            patient = existing
            patient.jumlah_kunjungan += 1
            patient.kunjungan_terakhir = "18 Nov 2026"

        now_str = datetime.now().strftime("%H.%M")
        queue_item = QueueItem(
            no_antrean=self._next_queue_no(poli),
            no_rm=patient.no_rm,
            nama_pasien=patient.nama,
            usia=patient.usia,
            poli=poli,
            terdaftar=now_str,
            status="Menunggu",
        )
        self.queue_items.append(queue_item)
        self._new_registrations_count += 1
        return patient, queue_item

    def get_report_data(
        self, period: str = "1–18 November 2026", poli_filter: str = "Semua poli"
    ) -> dict:
        """Hasilkan data statistik Laporan Klinik sesuai periode dan poli."""
        extra = self._new_registrations_count

        base_recap = [
            {"poli": "Poli Umum", "kunjungan": 346 + extra, "baru": 44 + extra, "lama": 302, "color": "#176650"},
            {"poli": "Poli Gigi", "kunjungan": 180, "baru": 26, "lama": 154, "color": "#4E9A7D"},
            {"poli": "Poli Anak", "kunjungan": 116, "baru": 16, "lama": 100, "color": "#B36A88"},
        ]

        scale = 1.0
        if period == "1–30 Oktober 2026":
            scale = 1.35
            trend_labels = ["1–5 Okt", "6–10 Okt", "11–15 Okt", "16–20 Okt", "21–25 Okt", "26–30 Okt"]
            trend_vals = [122, 138, 145, 130, 158, 149]
            days = 30
        elif period == "Hari ini (18 Nov 2026)":
            scale = 0.08
            trend_labels = ["08.00", "09.00", "10.00", "11.00", "13.00", "14.00"]
            trend_vals = [8, 11, 14, 9, 12, 6]
            days = 1
        else:
            trend_labels = ["1–3 Nov", "4–6 Nov", "7–9 Nov", "10–12 Nov", "13–15 Nov", "16–18 Nov"]
            trend_vals = [96, 104, 112, 88, 126, 116 + extra]
            days = 18

        recap = []
        for r in base_recap:
            if poli_filter != "Semua poli" and r["poli"] != poli_filter:
                continue
            k = round(r["kunjungan"] * scale) if scale != 1.0 else r["kunjungan"]
            b = round(r["baru"] * scale) if scale != 1.0 else r["baru"]
            l_val = max(0, k - b)
            recap.append({
                "poli": r["poli"],
                "kunjungan": k,
                "baru": b,
                "lama": l_val,
                "color": r["color"],
            })

        total_kunjungan = sum(r["kunjungan"] for r in recap)
        total_baru = sum(r["baru"] for r in recap)
        total_lama = sum(r["lama"] for r in recap)
        avg_day = round(total_kunjungan / days) if days else total_kunjungan

        if poli_filter != "Semua poli" and scale == 1.0:
            ratio = total_kunjungan / max(1, 642 + extra)
            trend_vals = [max(1, round(v * ratio)) for v in trend_vals]

        for r in recap:
            r["kontribusi"] = (r["kunjungan"] / total_kunjungan * 100.0) if total_kunjungan else 0.0

        baru_pct = (total_baru / total_kunjungan * 100.0) if total_kunjungan else 0.0
        lama_pct = (total_lama / total_kunjungan * 100.0) if total_kunjungan else 0.0

        return {
            "period": period,
            "total_kunjungan": total_kunjungan,
            "pasien_baru": total_baru,
            "pasien_baru_pct": baru_pct,
            "pasien_lama": total_lama,
            "pasien_lama_pct": lama_pct,
            "rata_rata": avg_day,
            "trend_labels": trend_labels,
            "trend_vals": trend_vals,
            "recap": recap,
        }

    def export_patients_csv(self, filepath: str) -> None:
        """Ekspor daftar pasien ke file CSV."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["No RM", "Nama", "NIK", "Jenis Kelamin", "Usia", "Penjamin", "Kunjungan Terakhir"])
            for p in self.patients:
                writer.writerow([p.no_rm, p.nama, p.nik, p.jenis_kelamin, f"{p.usia} tahun", p.penjamin, p.kunjungan_terakhir])

    def export_report_csv(self, filepath: str, period: str, poli_filter: str) -> None:
        """Ekspor rekap laporan klinik ke file CSV."""
        data = self.get_report_data(period, poli_filter)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Periode", period])
            writer.writerow(["Total Kunjungan", data["total_kunjungan"]])
            writer.writerow(["Pasien Baru", data["pasien_baru"]])
            writer.writerow(["Pasien Lama", data["pasien_lama"]])
            writer.writerow([])
            writer.writerow(["Poli", "Kunjungan", "Pasien Baru", "Pasien Lama", "Kontribusi"])
            for r in data["recap"]:
                writer.writerow([r["poli"], r["kunjungan"], r["baru"], r["lama"], f"{r['kontribusi']:.1f}%".replace(".", ",")])
