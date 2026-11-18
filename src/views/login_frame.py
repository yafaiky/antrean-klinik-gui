"""Halaman Login Heptamed Klinik (1:1 sesuai desain referensi)."""

import tkinter as tk
from tkinter import messagebox
from typing import Any

from src.utils.theme import (
    COLORS,
    draw_heptamed_logo,
    draw_rounded_rect,
    font,
)
from src.views.base_frame import BaseFrame
from src.views.components import RoundedButton, RoundedInput


def _cubic_bezier_pts(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 24,
) -> list[float]:
    pts: list[float] = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        x = (mt**3) * p0[0] + 3 * (mt**2) * t * p1[0] + 3 * mt * (t**2) * p2[0] + (t**3) * p3[0]
        y = (mt**3) * p0[1] + 3 * (mt**2) * t * p1[1] + 3 * mt * (t**2) * p2[1] + (t**3) * p3[1]
        pts.extend([x, y])
    return pts


class LoginFrame(BaseFrame):
    """Halaman masuk staf klinik dengan latar gelombang organik dan watermark logo."""

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent, controller)
        self.configure(bg=COLORS["bg_white"])

        self.canvas = tk.Canvas(self, bg=COLORS["bg_white"], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._remember = tk.BooleanVar(value=False)
        self._form_holder = tk.Frame(self.canvas, bg=COLORS["bg_white"])

        self._build_form()
        self._form_win = self.canvas.create_window(84, 150, window=self._form_holder, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)

    def _build_form(self) -> None:
        f = self._form_holder
        self._form_width = 348

        tk.Label(
            f,
            text="Selamat datang\nkembali.",
            bg=COLORS["bg_white"],
            fg=COLORS["text_heading"],
            font=font(25, "bold"),
            justify=tk.LEFT,
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            f,
            text="Masuk untuk memulai pelayanan hari ini.",
            bg=COLORS["bg_white"],
            fg=COLORS["text_muted"],
            font=font(10),
            anchor="w",
        ).pack(anchor="w", pady=(0, 26))

        # Email
        tk.Label(
            f, text="Email", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(9, "bold"), anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        self.email_input = RoundedInput(
            f,
            placeholder="nama@gmail.id",
            width=self._form_width,
            height=42,
            radius=10,
            parent_bg=COLORS["bg_white"],
        )
        self.email_input.pack(anchor="w", pady=(0, 16))

        # Kata sandi
        tk.Label(
            f, text="Kata sandi", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(9, "bold"), anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        self.password_input = RoundedInput(
            f,
            placeholder="Masukkan kata sandi",
            width=self._form_width,
            height=42,
            radius=10,
            is_password=True,
            parent_bg=COLORS["bg_white"],
        )
        self.password_input.pack(anchor="w", pady=(0, 14))
        self.password_input.entry.bind("<Return>", lambda _e: self._handle_login())
        self.email_input.entry.bind("<Return>", lambda _e: self._handle_login())

        # Baris Ingat saya & Lupa kata sandi?
        opts_row = tk.Frame(f, bg=COLORS["bg_white"], width=self._form_width, height=24)
        opts_row.pack(fill=tk.X, pady=(0, 18))
        opts_row.pack_propagate(False)

        self.chk_canvas = tk.Canvas(
            opts_row, width=105, height=22, bg=COLORS["bg_white"],
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self.chk_canvas.pack(side=tk.LEFT)
        self.chk_canvas.bind("<Button-1>", self._toggle_remember)
        self._draw_checkbox()

        forgot_lbl = tk.Label(
            opts_row,
            text="Lupa kata sandi?",
            bg=COLORS["bg_white"],
            fg=COLORS["primary"],
            font=font(9, "bold"),
            cursor="hand2",
        )
        forgot_lbl.pack(side=tk.RIGHT)
        forgot_lbl.bind("<Button-1>", self._on_forgot_password)

        # Pesan error validasi (tersembunyi bila valid)
        self.error_lbl = tk.Label(
            f, text="", bg=COLORS["bg_white"], fg=COLORS["text_danger"],
            font=font(9), anchor="w",
        )

        # Tombol Masuk ke Heptamed ->
        self.login_btn = RoundedButton(
            f,
            text="Masuk ke Heptamed",
            command=self._handle_login,
            variant="primary",
            width=self._form_width,
            height=44,
            radius=10,
            parent_bg=COLORS["bg_white"],
            right_arrow=True,
        )
        self.login_btn.pack(anchor="w", pady=(2, 22))

        # Kotak info "Belum punya akses?"
        info_card = tk.Canvas(
            f, width=self._form_width, height=62,
            bg=COLORS["bg_white"], highlightthickness=0, bd=0,
        )
        info_card.pack(anchor="w")
        draw_rounded_rect(
            info_card, 0, 0, self._form_width, 62,
            r=10, fill=COLORS["bg_info_soft"], outline=COLORS["bg_info_soft"],
        )
        info_card.create_text(
            16, 20, text="Belum punya akses?", anchor="w",
            fill=COLORS["text_body"], font=font(9, "bold"),
        )
        info_card.create_text(
            16, 41, text="Hubungi administrator klinik untuk akun staf.", anchor="w",
            fill=COLORS["text_muted"], font=font(8),
        )

    def _draw_checkbox(self) -> None:
        c = self.chk_canvas
        c.delete("all")
        checked = self._remember.get()
        fill = COLORS["primary"] if checked else COLORS["bg_white"]
        border = COLORS["primary"] if checked else COLORS["border_strong"]
        draw_rounded_rect(c, 1, 3, 16, 18, r=4, fill=fill, outline=border, width=1)
        if checked:
            c.create_line(4, 11, 7, 14, 13, 7, fill="#FFFFFF", width=1.8)
        c.create_text(
            24, 10, text="Ingat saya", anchor="w",
            fill=COLORS["text_muted"], font=font(9),
        )

    def _toggle_remember(self, _e=None) -> None:
        self._remember.set(not self._remember.get())
        self._draw_checkbox()

    def _on_forgot_password(self, _e=None) -> None:
        messagebox.showinfo(
            "Bantuan Kata Sandi",
            "Silakan hubungi Administrator Heptamed Klinik untuk reset kata sandi akun staf Anda.",
        )

    def _handle_login(self) -> None:
        email = self.email_input.get()
        pwd = self.password_input.get()
        ok, msg = self.controller.service.authenticate(email, pwd)
        if not ok:
            self.error_lbl.configure(text=msg)
            self.error_lbl.pack(anchor="w", pady=(0, 8), before=self.login_btn)
            if "email" in msg.lower():
                self.email_input.set_border(COLORS["border_danger"])
            else:
                self.password_input.set_border(COLORS["border_danger"])
            return
        self.error_lbl.pack_forget()
        self.email_input.set_border(COLORS["border_strong"])
        self.password_input.set_border(COLORS["border_strong"])
        self.controller.show_frame("antrean")

    def _on_resize(self, event) -> None:
        w, h = max(800, event.width), max(560, event.height)
        c = self.canvas
        c.delete("bg_art")

        # Kurva gelombang organik pembatas area putih dan hijau kanan (sesuai 36b9824a.jpg)
        c1 = _cubic_bezier_pts(
            (0.39 * w, 0),
            (0.55 * w, 0.08 * h),
            (0.49 * w, 0.22 * h),
            (0.51 * w, 0.34 * h),
            steps=28,
        )
        c2 = _cubic_bezier_pts(
            (0.51 * w, 0.34 * h),
            (0.53 * w, 0.45 * h),
            (0.58 * w, 0.50 * h),
            (0.57 * w, 0.62 * h),
            steps=28,
        )
        c3 = _cubic_bezier_pts(
            (0.57 * w, 0.62 * h),
            (0.56 * w, 0.72 * h),
            (0.73 * w, 0.80 * h),
            (0.71 * w, h),
            steps=28,
        )
        wave_poly = c1 + c2[2:] + c3[2:] + [w, h, w, 0]
        c.create_polygon(wave_poly, fill=COLORS["login_green"], outline="", tags="bg_art")

        # Watermark besar silang Heptamed di sisi kanan hijau (lebih terang halus dari latar)
        wm_size = h * 0.78
        wm_x = w * 0.54
        wm_y = h * 0.11
        draw_heptamed_logo(
            c,
            wm_x,
            wm_y,
            wm_size,
            dark_color="#1A6652",
            light_color="#21725B",
            tags="bg_art",
        )

        # Logo kiri atas
        lx = max(54, int(w * 0.082))
        ly = max(32, int(h * 0.062))
        draw_heptamed_logo(c, lx, ly, 34, tags="bg_art")
        c.create_text(
            lx + 44, ly + 9, text="Heptamed", anchor="w",
            fill=COLORS["text_heading"], font=font(12, "bold"), tags="bg_art",
        )
        c.create_text(
            lx + 44, ly + 27, text="Klinik", anchor="w",
            fill=COLORS["text_heading"], font=font(12, "bold"), tags="bg_art",
        )

        # Posisi blok form kiri
        form_y = max(96, int(h * 0.175))
        c.coords(self._form_win, lx, form_y)
        c.tag_lower("bg_art")
