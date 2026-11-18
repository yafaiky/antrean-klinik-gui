"""Helper validasi input dasar untuk form GUI."""


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
