"""Model data entitas Antrean Poli untuk aplikasi Heptamed Klinik."""

from dataclasses import dataclass


@dataclass
class QueueItem:
    """Representasi satu item antrean pasien pada poli tertentu."""

    no_antrean: str
    no_rm: str
    nama_pasien: str
    usia: int
    poli: str
    terdaftar: str
    status: str = "Menunggu"  # "Diperiksa" | "Menunggu" | "Selesai"
    tanggal: str = "18 Nov 2026"
