"""Model data entitas Pasien untuk aplikasi Heptamed Klinik."""

from dataclasses import dataclass, field


@dataclass
class Patient:
    """Representasi data pasien terdaftar di Heptamed Klinik."""

    no_rm: str
    nik: str
    nama: str
    tanggal_lahir: str
    usia: int
    jenis_kelamin: str
    telepon: str
    alamat: str
    penjamin: str = "BPJS"
    pasien_sejak: str = "2026"
    kunjungan_terakhir: str = "18 Nov 2026"
    jumlah_kunjungan: int = 1
    avatar_path: str = ""
    riwayat_poli: list[str] = field(default_factory=list)

    def masked_nik(self) -> str:
        """Format NIK tersamar seperti '3273 ···· ···· 0001'."""
        digits = "".join(ch for ch in self.nik if ch.isdigit())
        if len(digits) >= 8:
            return f"{digits[:4]} ···· ···· {digits[-4:]}"
        return self.nik
