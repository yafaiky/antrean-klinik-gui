"""Helper validasi input dan pemformatan data untuk form GUI Heptamed Klinik."""

from datetime import date

MONTHS_ID = {
    "januari": 1,
    "februari": 2,
    "maret": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "agustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "desember": 12,
}


def is_not_empty(value: str) -> bool:
    """Kembalikan True jika string tidak kosong setelah di-trim."""
    return bool(value.strip())


def parse_positive_int(value: str) -> int | None:
    """Parse string menjadi bilangan bulat positif (> 0), atau None jika tidak valid."""
    try:
        parsed = int(value.strip())
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def parse_positive_float(value: str) -> float | None:
    """Parse string menjadi bilangan desimal positif (> 0), atau None jika tidak valid."""
    try:
        parsed = float(value.strip())
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def validate_nik(nik: str) -> tuple[bool, str]:
    """Validasi NIK harus tepat 16 digit angka."""
    cleaned = nik.strip()
    if not cleaned:
        return False, "NIK wajib diisi (16 digit angka)."
    if not cleaned.isdigit():
        return False, "NIK hanya boleh berisi angka."
    if len(cleaned) != 16:
        return False, f"NIK harus 16 digit angka. Saat ini: {len(cleaned)} digit."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validasi nomor telepon minimal 9 digit angka."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 9:
        return False, "Nomor telepon minimal 9 digit."
    return True, ""


def calculate_age_from_indonesian_date(date_str: str, ref_date: date | None = None) -> int | None:
    """Hitung usia dalam tahun dari format tanggal '14 Maret 1996' atau 'DD-MM-YYYY'."""
    text = date_str.strip()
    if not text:
        return None
    today = ref_date or date(2026, 11, 18)

    parts = text.replace(",", "").split()
    if len(parts) == 3:
        try:
            day = int(parts[0])
            month = MONTHS_ID.get(parts[1].lower())
            year = int(parts[2])
            if month and 1900 <= year <= today.year and 1 <= day <= 31:
                age = today.year - year - ((today.month, today.day) < (month, day))
                return max(0, age)
        except ValueError:
            return None

    for sep in ("-", "/"):
        if sep in text:
            seg = text.split(sep)
            if len(seg) == 3:
                try:
                    if len(seg[0]) == 4:
                        year, month, day = int(seg[0]), int(seg[1]), int(seg[2])
                    else:
                        day, month, year = int(seg[0]), int(seg[1]), int(seg[2])
                    if 1900 <= year <= today.year and 1 <= month <= 12 and 1 <= day <= 31:
                        age = today.year - year - ((today.month, today.day) < (month, day))
                        return max(0, age)
                except ValueError:
                    return None
    return None


def format_thousand(value: int) -> str:
    """Format angka ribuan menggunakan titik ala Indonesia (mis. 1.248)."""
    return f"{value:,}".replace(",", ".")
