"""Palet warna, tipografi, dan primitif vektor Canvas untuk Heptamed Klinik."""

import ctypes
import math
import os
import tkinter as tk
from pathlib import Path
from typing import Iterable

COLORS = {
    "bg_page": "#F7F9F8",
    "bg_white": "#FFFFFF",
    "bg_soft_mint": "#F0F5F1",
    "bg_input_mint": "#EBF4EE",
    "bg_info_soft": "#F4F7F5",
    "bg_pink": "#F8E3EC",
    "bg_pink_row": "#FDF4F8",
    "bg_pink_bar": "#F7E4EA",
    "bg_badge_green": "#E7F4EE",
    "bg_badge_yellow": "#FFF0D9",
    "bg_badge_red": "#FCE8EE",
    "primary": "#176650",
    "primary_hover": "#125240",
    "primary_dark": "#163F34",
    "primary_disabled": "#D2E0D9",
    "primary_disabled_text": "#63857A",
    "dock_bg": "#17664F",
    "dock_active": "#349F7F",
    "login_green": "#18624E",
    "login_watermark": "#1E6B56",
    "logo_dark": "#17664F",
    "logo_light": "#2B8D71",
    "chart_bar": "#176650",
    "chart_bar_peak": "#2E9276",
    "chart_gigi": "#4E9A7D",
    "chart_anak": "#B06584",
    "chart_track": "#ECF1EE",
    "text_primary": "#1A372F",
    "text_heading": "#183B31",
    "text_body": "#324A43",
    "text_muted": "#7A8A84",
    "text_placeholder": "#9AA8A3",
    "text_pink_badge": "#8D3E5E",
    "text_yellow_badge": "#8F6522",
    "text_green_badge": "#1A6B54",
    "text_danger": "#B6425E",
    "border": "#E2E9E5",
    "border_strong": "#CDD8D2",
    "border_danger": "#BD6C7E",
    "border_pink": "#EED3DF",
    "border_selected": "#176650",
    "gridline": "#EBF0ED",
}

# Inisialisasi font Instrument Sans dari Google Fonts jika file ttf tersedia
_FONT_DIR = Path(__file__).resolve().parents[2] / "assets"
_TTF_PATH = _FONT_DIR / "InstrumentSans.ttf"
if _TTF_PATH.exists() and os.name == "nt":
    try:
        ctypes.windll.gdi32.AddFontResourceExW(str(_TTF_PATH), 0x10, 0)
    except Exception:
        pass

FONT_FAMILY = "Instrument Sans"


def font(size: int, weight: str = "normal") -> tuple[str, int, str]:
    """Kembalikan tuple font standar aplikasi menggunakan Instrument Sans."""
    if weight == "bold":
        return (FONT_FAMILY, size, "bold")
    return (FONT_FAMILY, size)


def rounded_rect_points(
    x1: float, y1: float, x2: float, y2: float, r: float, segments: int = 8
) -> list[float]:
    """Bangun koordinat poligon persegi panjang sudut membulat yang halus."""
    w = max(0.0, x2 - x1)
    h = max(0.0, y2 - y1)
    r = min(r, w / 2.0, h / 2.0)
    if r <= 0:
        return [x1, y1, x2, y1, x2, y2, x1, y2]

    pts: list[float] = []
    corners = [
        (x2 - r, y1 + r, -math.pi / 2, 0.0),
        (x2 - r, y2 - r, 0.0, math.pi / 2),
        (x1 + r, y2 - r, math.pi / 2, math.pi),
        (x1 + r, y1 + r, math.pi, 3 * math.pi / 2),
    ]
    for cx, cy, start, end in corners:
        for i in range(segments + 1):
            ang = start + (end - start) * (i / segments)
            pts.append(cx + r * math.cos(ang))
            pts.append(cy + r * math.sin(ang))
    return pts


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    r: float = 12,
    fill: str = "#FFFFFF",
    outline: str = "",
    width: int = 1,
    tags: str | tuple[str, ...] = "",
) -> int:
    """Gambar persegi panjang dengan sudut membulat pada tk.Canvas."""
    pts = rounded_rect_points(x1, y1, x2, y2, r)
    return canvas.create_polygon(
        pts,
        fill=fill,
        outline=outline if outline else fill,
        width=width if outline else 0,
        smooth=False,
        tags=tags,
    )


def draw_heptamed_logo(
    canvas: tk.Canvas,
    x: float,
    y: float,
    size: float,
    dark_color: str = COLORS["logo_dark"],
    light_color: str = COLORS["logo_light"],
    tags: str | tuple[str, ...] = "",
) -> None:
    """Gambar logo Heptamed Klinik persis 1:1 sesuai gambar (kotak bingkai + salib hijau tua + panah chevron teal atas-bawah)."""
    s = size
    # 1. Bingkai luar bujur sangkar dengan outline tipis
    # Bounding box frame di icon koordinat 4..38 dari 44 = ~ 0.09s .. 0.86s
    fx1 = x + 0.09 * s
    fy1 = y + 0.09 * s
    fx2 = x + 0.86 * s
    fy2 = y + 0.86 * s
    canvas.create_rectangle(
        fx1, fy1, fx2, fy2,
        outline=dark_color, width=max(1, int(0.068 * s)), fill="", tags=tags,
    )

    # 2. Palang silang hijau tua (dark_color)
    # Batang horizontal lebar
    canvas.create_rectangle(
        x + 0.00 * s, y + 0.27 * s, x + 0.98 * s, y + 0.70 * s,
        fill=dark_color, outline="", tags=tags,
    )
    # Batang vertikal
    canvas.create_rectangle(
        x + 0.27 * s, y + 0.00 * s, x + 0.70 * s, y + 0.98 * s,
        fill=dark_color, outline="", tags=tags,
    )

    # 3. Panah chevron teal / hijau muda atas (chevron mengarah ke atas di cabang atas silang)
    poly_top = [
        x + 0.49 * s, y + 0.07 * s,
        x + 0.70 * s, y + 0.27 * s,
        x + 0.61 * s, y + 0.27 * s,
        x + 0.49 * s, y + 0.16 * s,
        x + 0.36 * s, y + 0.27 * s,
        x + 0.27 * s, y + 0.27 * s,
    ]
    canvas.create_polygon(poly_top, fill=light_color, outline="", tags=tags)

    # 4. Panah besar teal / hijau muda bawah (chevron mengarah ke atas di batang bawah silang)
    poly_bottom = [
        x + 0.49 * s, y + 0.43 * s,
        x + 0.70 * s, y + 0.64 * s,
        x + 0.70 * s, y + 0.98 * s,
        x + 0.27 * s, y + 0.98 * s,
        x + 0.27 * s, y + 0.64 * s,
    ]
    canvas.create_polygon(poly_bottom, fill=light_color, outline="", tags=tags)


def draw_dock_icon(
    canvas: tk.Canvas,
    kind: str,
    cx: float,
    cy: float,
    color: str = "#FFFFFF",
    tags: str | tuple[str, ...] = "",
) -> None:
    """Gambar ikon garis minimalis untuk floating dock dan tombol logout."""
    if kind == "registrasi":
        # Kepala & bahu orang + tanda plus
        canvas.create_oval(cx - 6, cy - 8, cx + 2, cy, outline=color, width=1.6, tags=tags)
        canvas.create_arc(
            cx - 9, cy + 1, cx + 5, cy + 12,
            start=0, extent=180, style=tk.ARC, outline=color, width=1.6, tags=tags,
        )
        canvas.create_line(cx + 5, cy + 3, cx + 11, cy + 3, fill=color, width=1.6, tags=tags)
        canvas.create_line(cx + 8, cy, cx + 8, cy + 6, fill=color, width=1.6, tags=tags)
    elif kind == "antrean":
        # Tiga kartu/baris antrean
        canvas.create_rectangle(cx - 8, cy - 7, cx + 8, cy - 3, outline=color, width=1.5, tags=tags)
        canvas.create_line(cx - 8, cy + 1, cx + 8, cy + 1, fill=color, width=1.6, tags=tags)
        canvas.create_line(cx - 8, cy + 6, cx + 5, cy + 6, fill=color, width=1.6, tags=tags)
    elif kind == "data":
        # Folder arsip pasien
        pts = [
            cx - 9, cy - 6,
            cx - 2, cy - 6,
            cx + 0, cy - 3,
            cx + 9, cy - 3,
            cx + 9, cy + 7,
            cx - 9, cy + 7,
        ]
        canvas.create_polygon(pts, fill="", outline=color, width=1.6, joinstyle=tk.ROUND, tags=tags)
    elif kind == "laporan":
        # Clipboard laporan
        canvas.create_rectangle(cx - 7, cy - 6, cx + 7, cy + 8, outline=color, width=1.6, tags=tags)
        canvas.create_rectangle(cx - 3, cy - 8, cx + 3, cy - 5, fill=color, outline=color, tags=tags)
        canvas.create_line(cx - 4, cy - 1, cx + 4, cy - 1, fill=color, width=1.4, tags=tags)
        canvas.create_line(cx - 4, cy + 3, cx + 4, cy + 3, fill=color, width=1.4, tags=tags)
    elif kind == "logout":
        # Lingkaran terbuka + panah kiri keluar
        canvas.create_arc(
            cx - 8, cy - 8, cx + 8, cy + 8,
            start=215, extent=290, style=tk.ARC, outline=color, width=1.8, tags=tags,
        )
        canvas.create_line(cx + 3, cy, cx - 7, cy, fill=color, width=1.8, tags=tags)
        canvas.create_line(cx - 3, cy - 4, cx - 7, cy, cx - 3, cy + 4, fill=color, width=1.8, tags=tags)


def bind_tree_click(widget: tk.Widget, callback) -> None:
    """Bind klik kiri pada widget beserta seluruh child widget-nya."""
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        bind_tree_click(child, callback)
