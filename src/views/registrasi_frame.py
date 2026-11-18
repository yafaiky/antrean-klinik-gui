"""Halaman Registrasi Pasien (1:1 sesuai desain referensi)."""

import tkinter as tk
from tkinter import messagebox
from typing import Any

from src.utils.theme import COLORS, draw_rounded_rect, font
from src.utils.validators import (
    calculate_age_from_indonesian_date,
    is_not_empty,
    validate_nik,
    validate_phone,
)
from src.views.base_frame import WorkspaceFrame
from src.views.components import RoundedButton, RoundedDropdown, RoundedInput


class RegistrasiFrame(WorkspaceFrame):
    """Form pendaftaran pasien baru/lama sekaligus penerbitan nomor antrean."""

    POLI_OPTIONS = ["Poli Umum", "Poli Gigi", "Poli Anak"]

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(
            parent,
            controller,
            active_route="registrasi",
            breadcrumb_parts=[
                ("Ruang kerja", None),
                ("Registrasi pasien", None),
            ],
        )
        self._selected_poli = tk.StringVar(value="Poli Umum")
        self._computed_age = 30
        self._build_ui()
        self._load_showcase_defaults()

    def on_show(self) -> None:
        self._rebuild_topbar(self._breadcrumb_parts)
        self._refresh_validation()

    def _build_ui(self) -> None:
        # Baris judul + tombol Cari pasien lama
        hdr = tk.Frame(self.body, bg=COLORS["bg_page"])
        hdr.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            hdr,
            text="Registrasi pasien",
            bg=COLORS["bg_page"],
            fg=COLORS["text_heading"],
            font=font(19, "bold"),
        ).pack(side=tk.LEFT)

        RoundedButton(
            hdr,
            text="Cari pasien lama  ↗",
            command=self._open_existing_patient_picker,
            variant="secondary",
            width=150,
            height=32,
            radius=9,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.RIGHT)

        # Stepper bar (01 Data pasien -> 02 Pilih poli -> 03 Terbitkan antrean)
        self.stepper = tk.Canvas(self.body, height=30, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.stepper.pack(fill=tk.X, pady=(0, 8))
        self.stepper.bind("<Configure>", self._draw_stepper)

        # Grid 2 kolom utama (kiri form, kanan ringkasan + checklist)
        main_cols = tk.Frame(self.body, bg=COLORS["bg_page"])
        main_cols.pack(fill=tk.BOTH, expand=True)
        main_cols.grid_columnconfigure(0, weight=17, uniform="regcol")
        main_cols.grid_columnconfigure(1, weight=10, uniform="regcol")
        main_cols.grid_rowconfigure(0, weight=1)

        # Kartu kiri: Identitas pasien
        left_wrap = tk.Frame(main_cols, bg=COLORS["bg_page"])
        left_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self._build_form_card(left_wrap)

        # Kolom kanan: Ringkasan pasien (pink) + Periksa sebelum menyimpan (putih)
        right_wrap = tk.Frame(main_cols, bg=COLORS["bg_page"])
        right_wrap.grid(row=0, column=1, sticky="nsew")
        self._build_right_cards(right_wrap)

        # Baris aksi bawah (warning, Batal, info klinik, Simpan & ambil antrean ->)
        bottom_bar = tk.Frame(self.body, bg=COLORS["bg_page"])
        bottom_bar.pack(fill=tk.X, pady=(6, 0))

        left_act = tk.Frame(bottom_bar, bg=COLORS["bg_page"])
        left_act.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.bottom_warn_lbl = tk.Label(
            left_act,
            text="Perbaiki NIK untuk melanjutkan pendaftaran.",
            bg=COLORS["bg_page"],
            fg=COLORS["text_danger"],
            font=font(8, "bold"),
            anchor="w",
        )
        self.bottom_warn_lbl.pack(anchor="w", pady=(0, 2))

        btn_note_row = tk.Frame(left_act, bg=COLORS["bg_page"])
        btn_note_row.pack(anchor="w")

        RoundedButton(
            btn_note_row,
            text="Batal",
            command=self._reset_form,
            variant="secondary",
            width=78,
            height=34,
            radius=9,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(
            btn_note_row,
            text="Data pasien hanya untuk kebutuhan pelayanan klinik.",
            bg=COLORS["bg_page"],
            fg=COLORS["text_muted"],
            font=font(8),
        ).pack(side=tk.LEFT)

        self.submit_btn = RoundedButton(
            bottom_bar,
            text="Simpan & ambil antrean  →",
            command=self._submit,
            variant="disabled",
            width=210,
            height=36,
            radius=9,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        )
        self.submit_btn.pack(side=tk.RIGHT, anchor="s")

    def _draw_stepper(self, _e=None) -> None:
        c = self.stepper
        w = max(400, c.winfo_width())
        h = 30
        c.delete("all")
        draw_rounded_rect(c, 0, 0, w, h, r=10, fill=COLORS["bg_input_mint"], outline=COLORS["bg_input_mint"])

        x1 = 20
        c.create_text(x1, h / 2, text="01  Data pasien", anchor="w", fill=COLORS["primary"], font=font(9, "bold"))
        c.create_text(w * 0.28, h / 2, text="→", fill=COLORS["text_placeholder"], font=font(10))
        c.create_text(w * 0.34, h / 2, text="02  Pilih poli", anchor="w", fill=COLORS["text_body"], font=font(9, "bold"))
        c.create_text(w * 0.57, h / 2, text="→", fill=COLORS["text_placeholder"], font=font(10))
        c.create_text(w * 0.63, h / 2, text="03  Terbitkan antrean", anchor="w", fill=COLORS["text_muted"], font=font(9))

    def _build_form_card(self, parent: tk.Frame) -> None:
        card_canvas = tk.Canvas(parent, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        card_canvas.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(card_canvas, bg=COLORS["bg_white"])
        inner_win = card_canvas.create_window(18, 12, window=inner, anchor="nw")

        def _redraw_card(event) -> None:
            w, h = event.width, event.height
            card_canvas.delete("cardbg")
            draw_rounded_rect(
                card_canvas, 1, 1, w - 1, h - 1, r=12,
                fill=COLORS["bg_white"], outline=COLORS["border"], width=1, tags="cardbg",
            )
            card_canvas.tag_lower("cardbg")
            card_canvas.itemconfigure(inner_win, width=max(200, w - 36))

        card_canvas.bind("<Configure>", _redraw_card)

        # Header kartu
        hdr = tk.Frame(inner, bg=COLORS["bg_white"])
        hdr.pack(fill=tk.X, pady=(0, 8))

        left_h = tk.Frame(hdr, bg=COLORS["bg_white"])
        left_h.pack(side=tk.LEFT)
        tk.Label(
            left_h, text="Identitas pasien", bg=COLORS["bg_white"],
            fg=COLORS["text_heading"], font=font(11, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            left_h, text="Lengkapi kolom bertanda * sesuai identitas pasien.",
            bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(8), anchor="w",
        ).pack(anchor="w")

        tk.Label(
            hdr, text="* Wajib diisi", bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(8),
        ).pack(side=tk.RIGHT, anchor="n", pady=2)

        # Grid 2 kolom input
        grid = tk.Frame(inner, bg=COLORS["bg_white"])
        grid.pack(fill=tk.X)
        grid.grid_columnconfigure(0, weight=1, uniform="fcol")
        grid.grid_columnconfigure(1, weight=1, uniform="fcol")

        # Baris 1: NIK * | Nama lengkap *
        nik_box = tk.Frame(grid, bg=COLORS["bg_white"])
        nik_box.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 3))
        tk.Label(
            nik_box, text="NIK *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.nik_input = RoundedInput(
            nik_box, placeholder="16 digit NIK", height=32, radius=8,
            on_change=lambda _v: self._refresh_validation(),
        )
        self.nik_input.pack(fill=tk.X)
        self.nik_hint = tk.Label(
            nik_box, text="", bg=COLORS["bg_white"],
            fg=COLORS["text_danger"], font=font(7), anchor="w",
        )
        self.nik_hint.pack(anchor="w", pady=(1, 0))

        nama_box = tk.Frame(grid, bg=COLORS["bg_white"])
        nama_box.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 3))
        tk.Label(
            nama_box, text="Nama lengkap *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.nama_input = RoundedInput(
            nama_box, placeholder="Nama sesuai KTP", height=32, radius=8,
            on_change=lambda _v: self._refresh_validation(),
        )
        self.nama_input.pack(fill=tk.X)
        tk.Label(nama_box, text=" ", bg=COLORS["bg_white"], font=font(7)).pack(anchor="w", pady=(1, 0))

        # Baris 2: Tanggal lahir * | Usia
        tgl_box = tk.Frame(grid, bg=COLORS["bg_white"])
        tgl_box.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 3))
        tk.Label(
            tgl_box, text="Tanggal lahir *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.tgl_input = RoundedInput(
            tgl_box, placeholder="Contoh: 14 Maret 1996", height=32, radius=8,
            on_change=lambda _v: self._refresh_validation(),
        )
        self.tgl_input.pack(fill=tk.X)
        tk.Label(tgl_box, text=" ", bg=COLORS["bg_white"], font=font(7)).pack(anchor="w", pady=(1, 0))

        usia_box = tk.Frame(grid, bg=COLORS["bg_white"])
        usia_box.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 3))
        tk.Label(
            usia_box, text="Usia", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.usia_input = RoundedInput(
            usia_box,
            placeholder="-",
            height=32,
            radius=8,
            bg_fill=COLORS["bg_input_mint"],
            readonly=True,
            text_color=COLORS["primary"],
            font_spec=font(9, "bold"),
        )
        self.usia_input.pack(fill=tk.X)
        tk.Label(
            usia_box, text="Dihitung otomatis dari tanggal lahir.",
            bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(7), anchor="w",
        ).pack(anchor="w", pady=(1, 0))

        # Baris 3: Jenis kelamin * | Nomor telepon *
        jk_box = tk.Frame(grid, bg=COLORS["bg_white"])
        jk_box.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))
        tk.Label(
            jk_box, text="Jenis kelamin *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.gender_dd = RoundedDropdown(
            jk_box,
            options=["Perempuan", "Laki-laki"],
            initial="Perempuan",
            height=32,
            radius=8,
            on_select=lambda _v: self._refresh_validation(),
        )
        self.gender_dd.pack(fill=tk.X)

        telp_box = tk.Frame(grid, bg=COLORS["bg_white"])
        telp_box.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        tk.Label(
            telp_box, text="Nomor telepon *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.telp_input = RoundedInput(
            telp_box, placeholder="08xx xxxx xxxx", height=32, radius=8,
            on_change=lambda _v: self._refresh_validation(),
        )
        self.telp_input.pack(fill=tk.X)

        # Baris 4: Alamat (full width)
        addr_box = tk.Frame(inner, bg=COLORS["bg_white"])
        addr_box.pack(fill=tk.X, pady=(0, 5))
        tk.Label(
            addr_box, text="Alamat", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 2))
        self.alamat_input = RoundedInput(
            addr_box, placeholder="Alamat lengkap pasien", height=32, radius=8,
        )
        self.alamat_input.pack(fill=tk.X)

        # Baris 5: Poli tujuan * (3 kartu radio)
        poli_box = tk.Frame(inner, bg=COLORS["bg_white"])
        poli_box.pack(fill=tk.X, pady=(0, 2))
        tk.Label(
            poli_box, text="Poli tujuan *", bg=COLORS["bg_white"],
            fg=COLORS["text_body"], font=font(8, "bold"),
        ).pack(anchor="w", pady=(0, 3))

        radios_row = tk.Frame(poli_box, bg=COLORS["bg_white"])
        radios_row.pack(fill=tk.X)
        self._poli_cards: dict[str, tk.Canvas] = {}
        for idx, p in enumerate(self.POLI_OPTIONS):
            radios_row.grid_columnconfigure(idx, weight=1, uniform="pradio")
            c = tk.Canvas(
                radios_row, height=32, bg=COLORS["bg_white"],
                highlightthickness=0, bd=0, cursor="hand2",
            )
            padx = (0, 8) if idx < 2 else (0, 0)
            c.grid(row=0, column=idx, sticky="ew", padx=padx)
            c.bind("<Button-1>", lambda _e, val=p: self._select_poli(val))
            c.bind("<Configure>", lambda _e, val=p: self._draw_poli_radio(val))
            self._poli_cards[p] = c

    def _draw_poli_radio(self, poli: str) -> None:
        c = self._poli_cards[poli]
        w = max(90, c.winfo_width())
        h = 32
        c.delete("all")
        selected = self._selected_poli.get() == poli
        fill = COLORS["bg_input_mint"] if selected else COLORS["bg_white"]
        border = COLORS["primary"] if selected else COLORS["border_strong"]
        draw_rounded_rect(c, 1, 1, w - 1, h - 1, r=8, fill=fill, outline=border, width=1)

        cx, cy = 18, h / 2
        if selected:
            c.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=COLORS["primary"], outline=COLORS["primary"])
        else:
            c.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="", outline=COLORS["border_strong"], width=1.4)

        c.create_text(
            32, cy, text=poli, anchor="w",
            fill=COLORS["primary"] if selected else COLORS["text_muted"],
            font=font(9, "bold") if selected else font(9),
        )

    def _select_poli(self, poli: str) -> None:
        self._selected_poli.set(poli)
        for p in self.POLI_OPTIONS:
            self._draw_poli_radio(p)
        self._refresh_validation()

    def _build_right_cards(self, parent: tk.Frame) -> None:
        # Kartu Pink: Ringkasan pasien
        self.summary_canvas = tk.Canvas(parent, height=176, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.summary_canvas.pack(fill=tk.X, pady=(0, 10))
        self.summary_canvas.bind("<Configure>", lambda _e: self._draw_summary_card())

        # Kartu Putih: Periksa sebelum menyimpan
        self.check_canvas = tk.Canvas(parent, height=192, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.check_canvas.pack(fill=tk.BOTH, expand=True)
        self.check_canvas.bind("<Configure>", lambda _e: self._draw_checklist_card())

    def _draw_summary_card(self) -> None:
        c = self.summary_canvas
        w = max(220, c.winfo_width())
        h = max(180, c.winfo_height())
        c.delete("all")
        draw_rounded_rect(
            c, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_pink"], outline=COLORS["border_pink"], width=1,
        )
        c.create_text(
            20, 20, text="PENDAFTARAN BARU", anchor="w",
            fill=COLORS["text_pink_badge"], font=font(8, "bold"),
        )
        c.create_text(
            20, 44, text="Ringkasan pasien", anchor="w",
            fill=COLORS["text_heading"], font=font(13, "bold"),
        )
        nama = self.nama_input.get().strip() or "Pasien Baru"
        gender = self.gender_dd.get()
        age_str = f"{self._computed_age} tahun" if self._computed_age is not None else "Usia -"
        c.create_text(
            20, 72, text=nama, anchor="w",
            fill=COLORS["text_heading"], font=font(11, "bold"),
        )
        c.create_text(
            20, 90, text=f"{gender} · {age_str}", anchor="w",
            fill=COLORS["text_muted"], font=font(9),
        )
        c.create_line(20, 108, w - 20, 108, fill=COLORS["border_pink"], width=1)
        c.create_text(
            20, 124, text="Poli tujuan", anchor="w",
            fill=COLORS["text_muted"], font=font(9),
        )
        c.create_text(
            w - 20, 124, text=self._selected_poli.get(), anchor="e",
            fill=COLORS["text_heading"], font=font(9, "bold"),
        )
        c.create_text(
            20, 150,
            text="Nomor antrean diterbitkan setelah\ndata berhasil disimpan.",
            anchor="w", fill=COLORS["text_muted"], font=font(8),
        )

    def _draw_checklist_card(self) -> None:
        c = self.check_canvas
        w = max(220, c.winfo_width())
        h = max(200, c.winfo_height())
        c.delete("all")
        draw_rounded_rect(
            c, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1,
        )
        c.create_text(
            20, 26, text="Periksa sebelum menyimpan", anchor="w",
            fill=COLORS["text_heading"], font=font(11, "bold"),
        )

        nik_ok, _ = validate_nik(self.nik_input.get())
        age_ok = self._computed_age is not None
        poli = self._selected_poli.get()

        items = [
            (
                nik_ok,
                "NIK valid" if nik_ok else "NIK belum valid",
                "16 digit angka lengkap." if nik_ok else "Lengkapi menjadi 16 digit angka.",
            ),
            (
                age_ok,
                "Tanggal lahir sesuai" if age_ok else "Tanggal lahir belum valid",
                f"Usia {self._computed_age} tahun, dihitung otomatis." if age_ok else "Gunakan format contoh: 14 Maret 1996.",
            ),
            (
                True,
                "Poli sudah dipilih",
                f"Pasien diarahkan ke {poli}.",
            ),
        ]

        y = 68
        for ok, title, sub in items:
            bg_c = COLORS["bg_badge_green"] if ok else COLORS["bg_badge_red"]
            fg_c = COLORS["primary"] if ok else COLORS["text_danger"]
            c.create_oval(20, y - 12, 44, y + 12, fill=bg_c, outline="")
            c.create_text(
                32, y, text=("✓" if ok else "!"),
                fill=fg_c, font=font(10, "bold"),
            )
            c.create_text(
                56, y - 6, text=title, anchor="w",
                fill=COLORS["text_heading"] if ok else COLORS["text_danger"],
                font=font(9, "bold"),
            )
            c.create_text(
                56, y + 11, text=sub, anchor="w",
                fill=COLORS["text_muted"], font=font(8),
            )
            y += 52

    def _load_showcase_defaults(self) -> None:
        self.nik_input.set("327501540396001")  # 15 digit awal sesuai gambar 5
        self.nama_input.set("Salsabila Putri")
        self.tgl_input.set("14 Maret 1996")
        self.gender_dd.set("Perempuan")
        self.telp_input.set("0812 3456 7890")
        self.alamat_input.set("Jl. Melati No. 18, Bandung")
        self._select_poli("Poli Umum")
        self._refresh_validation()

    def _reset_form(self) -> None:
        self.nik_input.set("")
        self.nama_input.set("")
        self.tgl_input.set("")
        self.telp_input.set("")
        self.alamat_input.set("")
        self._select_poli("Poli Umum")
        self._refresh_validation()

    def _refresh_validation(self) -> None:
        age = calculate_age_from_indonesian_date(self.tgl_input.get())
        self._computed_age = age
        self.usia_input.set(f"{age} tahun" if age is not None else "-")

        nik_ok, nik_msg = validate_nik(self.nik_input.get())
        if nik_ok:
            self.nik_input.set_border(COLORS["border_strong"])
            self.nik_hint.configure(text="")
        else:
            self.nik_input.set_border(COLORS["border_danger"])
            self.nik_hint.configure(text=nik_msg)

        name_ok = is_not_empty(self.nama_input.get())
        telp_ok, telp_msg = validate_phone(self.telp_input.get())
        all_ok = nik_ok and name_ok and (age is not None) and telp_ok

        if not nik_ok:
            self.bottom_warn_lbl.configure(text="Perbaiki NIK untuk melanjutkan pendaftaran.")
        elif not name_ok:
            self.bottom_warn_lbl.configure(text="Lengkapi nama lengkap pasien.")
        elif age is None:
            self.bottom_warn_lbl.configure(text="Format tanggal lahir belum valid (mis. 14 Maret 1996).")
        elif not telp_ok:
            self.bottom_warn_lbl.configure(text=telp_msg)
        else:
            self.bottom_warn_lbl.configure(text="")

        self.submit_btn.set_variant("primary" if all_ok else "disabled")
        self._draw_summary_card()
        self._draw_checklist_card()

    def _submit(self) -> None:
        nik_ok, nik_msg = validate_nik(self.nik_input.get())
        if not nik_ok or self._computed_age is None or not is_not_empty(self.nama_input.get()):
            messagebox.showwarning("Data Belum Lengkap", nik_msg or "Lengkapi seluruh kolom wajib (*).")
            return

        patient, qitem = self.controller.service.register_patient(
            nik=self.nik_input.get(),
            nama=self.nama_input.get(),
            tanggal_lahir=self.tgl_input.get(),
            usia=self._computed_age,
            jenis_kelamin=self.gender_dd.get(),
            telepon=self.telp_input.get(),
            alamat=self.alamat_input.get(),
            poli=self._selected_poli.get(),
        )
        messagebox.showinfo(
            "Antrean Diterbitkan",
            f"Pasien {patient.nama} ({patient.no_rm}) berhasil terdaftar.\n"
            f"Nomor Antrean: {qitem.no_antrean} ({qitem.poli})",
        )
        self._reset_form()
        self.controller.show_frame("antrean")

    def _open_existing_patient_picker(self) -> None:
        modal = tk.Toplevel(self)
        modal.title("Pilih Pasien Lama")
        modal.geometry("460x380")
        modal.configure(bg=COLORS["bg_white"])
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        tk.Label(
            modal, text="Pilih pasien lama", bg=COLORS["bg_white"],
            fg=COLORS["text_heading"], font=font(13, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(
            modal, text="Klik pasien untuk mengisi otomatis form registrasi.",
            bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9),
        ).pack(anchor="w", padx=20, pady=(0, 12))

        lb = tk.Frame(modal, bg=COLORS["bg_white"])
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        for p in self.controller.service.patients[:7]:
            row = tk.Frame(lb, bg=COLORS["bg_page"], cursor="hand2")
            row.pack(fill=tk.X, pady=3)
            tk.Label(
                row, text=f"{p.no_rm} · {p.nama}", bg=COLORS["bg_page"],
                fg=COLORS["text_heading"], font=font(9, "bold"),
            ).pack(side=tk.LEFT, padx=10, pady=8)
            tk.Label(
                row, text=p.penjamin, bg=COLORS["bg_page"],
                fg=COLORS["primary"], font=font(8, "bold"),
            ).pack(side=tk.RIGHT, padx=10)

            def _pick(_e, pat=p) -> None:
                self.nik_input.set(pat.nik if len(pat.nik) == 16 else pat.nik.ljust(16, "0"))
                self.nama_input.set(pat.nama)
                self.tgl_input.set(pat.tanggal_lahir)
                self.gender_dd.set(pat.jenis_kelamin)
                self.telp_input.set(pat.telepon)
                self.alamat_input.set(pat.alamat)
                self._refresh_validation()
                modal.destroy()

            row.bind("<Button-1>", _pick)
            for ch in row.winfo_children():
                ch.bind("<Button-1>", _pick)
