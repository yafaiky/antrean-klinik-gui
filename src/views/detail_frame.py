"""Halaman Detail Pasien (1:1 sesuai desain referensi)."""

import os
import tkinter as tk
from typing import Any

from src.models.patient import Patient
from src.utils.theme import COLORS, draw_rounded_rect, font
from src.utils.validators import format_thousand
from src.views.base_frame import WorkspaceFrame
from src.views.components import (
    RoundedButton,
    RoundedDropdown,
    RoundedInput,
    draw_pill_badge,
)


class _SummaryCard(tk.Canvas):
    """Kartu ringkas 4-kolom pada halaman detail pasien."""

    def __init__(self, parent: tk.Widget, label: str, value: str) -> None:
        super().__init__(parent, height=72, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self._label = label
        self._value = value
        self._width = 180
        self.bind("<Configure>", self._on_resize)

    def set_data(self, value: str) -> None:
        self._value = value
        self._redraw()

    def _on_resize(self, event) -> None:
        self._width = max(110, event.width)
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        draw_rounded_rect(
            self, 1, 1, self._width - 1, 71, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1,
        )
        self.create_text(18, 20, text=self._label, anchor="w", fill=COLORS["text_muted"], font=font(9))
        self.create_text(18, 48, text=self._value, anchor="w", fill=COLORS["text_heading"], font=font(17, "bold"))


class DetailFrame(WorkspaceFrame):
    """Halaman detail profil pasien beserta riwayat kunjungan/rekam medis."""

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(
            parent,
            controller,
            active_route="data",
            breadcrumb_parts=[
                ("Ruang kerja", None),
                ("Data pasien", lambda: self.controller.show_frame("data")),
                ("Abdul Rijman", None),
            ],
        )
        self._patient_rm = "RM-00247"
        self._avatar_img: tk.PhotoImage | None = None
        self._build_ui()

    def set_patient(self, no_rm: str) -> None:
        self._patient_rm = no_rm

    def on_show(self) -> None:
        p = self.controller.service.get_patient_by_rm(self._patient_rm)
        if p is None and self.controller.service.patients:
            p = self.controller.service.patients[0]
        if p is not None:
            self._breadcrumb_parts = [
                ("Ruang kerja", None),
                ("Data pasien", lambda: self.controller.show_frame("data")),
                (p.nama, None),
            ]
        self._rebuild_topbar(self._breadcrumb_parts)
        self._refresh(p)

    def _build_ui(self) -> None:
        # Judul halaman
        tk.Label(
            self.body,
            text="Data pasien",
            bg=COLORS["bg_page"],
            fg=COLORS["text_heading"],
            font=font(20, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        # Hero Profil: Avatar bulat + Nama + NIK + Pasien sejak
        hero = tk.Frame(self.body, bg=COLORS["bg_page"])
        hero.pack(fill=tk.X, pady=(0, 12))

        self.avatar_canvas = tk.Canvas(hero, width=116, height=116, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.avatar_canvas.pack(side=tk.LEFT, padx=(0, 22))

        info_box = tk.Frame(hero, bg=COLORS["bg_page"])
        info_box.pack(side=tk.LEFT, pady=18)

        name_line = tk.Frame(info_box, bg=COLORS["bg_page"])
        name_line.pack(anchor="w")

        self.name_lbl = tk.Label(
            name_line, text="Abdul Rijman", bg=COLORS["bg_page"],
            fg=COLORS["text_heading"], font=font(22, "bold"),
        )
        self.name_lbl.pack(side=tk.LEFT)

        self.nik_lbl = tk.Label(
            name_line, text="327330210330", bg=COLORS["bg_page"],
            fg=COLORS["text_muted"], font=font(10),
        )
        self.nik_lbl.pack(side=tk.LEFT, padx=(14, 0), pady=(6, 0))

        self.since_lbl = tk.Label(
            info_box, text="Pasien sejak 2023", bg=COLORS["bg_page"],
            fg=COLORS["text_muted"], font=font(10),
        )
        self.since_lbl.pack(anchor="w", pady=(4, 0))

        # 4 Kartu Ringkas
        cards_row = tk.Frame(self.body, bg=COLORS["bg_page"])
        cards_row.pack(fill=tk.X, pady=(0, 12))
        for i in range(4):
            cards_row.grid_columnconfigure(i, weight=1, uniform="detc")

        self.card_gender = _SummaryCard(cards_row, "Kelamin", "Laki-laki")
        self.card_gender.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.card_age = _SummaryCard(cards_row, "Usia", "46")
        self.card_age.grid(row=0, column=1, sticky="ew", padx=(0, 14))

        self.card_penjamin = _SummaryCard(cards_row, "Penjamin", "BPJS")
        self.card_penjamin.grid(row=0, column=2, sticky="ew", padx=(0, 14))

        self.card_visits = _SummaryCard(cards_row, "Kunjungan", "67")
        self.card_visits.grid(row=0, column=3, sticky="ew")

        # Kartu Tabel Riwayat
        self.table_card = tk.Canvas(self.body, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.table_card.pack(fill=tk.BOTH, expand=True)

        self.card_inner = tk.Frame(self.table_card, bg=COLORS["bg_white"])
        self._card_win = self.table_card.create_window(2, 2, window=self.card_inner, anchor="nw")
        self.table_card.bind("<Configure>", self._on_card_resize)

        fbar = tk.Frame(self.card_inner, bg=COLORS["bg_white"])
        fbar.pack(fill=tk.X, padx=16, pady=12)

        self.search_input = RoundedInput(
            fbar,
            placeholder="Cari nama, NIK, atau nomor rekam medis...",
            width=320,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_white"],
            on_change=lambda _v: self._refresh_rows(),
        )
        self.search_input.pack(side=tk.LEFT, padx=(0, 10))

        self.penjamin_dd = RoundedDropdown(
            fbar,
            options=["Semua penjamin", "BPJS", "Umum"],
            initial="Semua penjamin",
            width=150,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_white"],
            bold_text=True,
            on_select=lambda _v: self._refresh_rows(),
        )
        self.penjamin_dd.pack(side=tk.LEFT, padx=(0, 10))

        self.gender_dd = RoundedDropdown(
            fbar,
            options=["Semua jenis kelamin", "Laki-laki", "Perempuan"],
            initial="Semua jenis kelamin",
            width=168,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_white"],
            bold_text=True,
            on_select=lambda _v: self._refresh_rows(),
        )
        self.gender_dd.pack(side=tk.LEFT)

        self.count_lbl = tk.Label(
            fbar, text="1.248 pasien", bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(8),
        )
        self.count_lbl.pack(side=tk.RIGHT, padx=(8, 4))

        self.rows_holder = tk.Frame(self.card_inner, bg=COLORS["bg_white"])
        self.rows_holder.pack(fill=tk.BOTH, expand=True)

    def _on_card_resize(self, event) -> None:
        w, h = event.width, event.height
        self.table_card.delete("cardbg")
        draw_rounded_rect(
            self.table_card, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1, tags="cardbg",
        )
        self.table_card.tag_lower("cardbg")
        self.table_card.itemconfigure(self._card_win, width=max(300, w - 4), height=max(160, h - 4))

    def _refresh(self, p: Patient | None) -> None:
        if p is None:
            return
        self.name_lbl.configure(text=p.nama)
        self.nik_lbl.configure(text=p.nik)
        self.since_lbl.configure(text=f"Pasien sejak {p.pasien_sejak}")
        self.card_gender.set_data(p.jenis_kelamin)
        self.card_age.set_data(str(p.usia))
        self.card_penjamin.set_data(p.penjamin)
        self.card_visits.set_data(str(p.jumlah_kunjungan))

        self._draw_avatar(p)
        kpis = self.controller.service.get_patient_kpis()
        self.count_lbl.configure(text=f"{format_thousand(int(kpis['total']))} pasien")
        self._refresh_rows()

    def _draw_avatar(self, p: Patient) -> None:
        c = self.avatar_canvas
        c.delete("all")
        if p.avatar_path and os.path.exists(p.avatar_path):
            try:
                self._avatar_img = tk.PhotoImage(file=p.avatar_path)
                c.create_image(58, 58, image=self._avatar_img)
                return
            except tk.TclError:
                pass
        # Fallback avatar inisial bulat rapi
        c.create_oval(4, 4, 112, 112, fill=COLORS["bg_badge_green"], outline=COLORS["border_strong"], width=1)
        initials = "".join(part[0].upper() for part in p.nama.split()[:2]) or "P"
        c.create_text(58, 58, text=initials, fill=COLORS["primary"], font=font(30, "bold"))

    def _refresh_rows(self) -> None:
        for w in self.rows_holder.winfo_children():
            w.destroy()

        hdr = tk.Frame(self.rows_holder, bg=COLORS["bg_soft_mint"], height=34)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        cols = [
            ("NO. RM", 12, "w", (20, 0)),
            ("NAMA PASIEN / NIK", 24, "w", (0, 0)),
            ("JENIS KELAMIN", 14, "w", (0, 0)),
            ("USIA", 11, "w", (0, 0)),
            ("PENJAMIN", 11, "w", (0, 0)),
            ("KUNJUNGAN TERAKHIR", 16, "w", (0, 0)),
            ("AKSI", 12, "center", (0, 14)),
        ]
        for idx, (title, wt, anc, px) in enumerate(cols):
            hdr.grid_columnconfigure(idx, weight=wt, uniform="detcol")
            tk.Label(
                hdr, text=title, bg=COLORS["bg_soft_mint"],
                fg=COLORS["text_muted"], font=font(8, "bold"), anchor=anc,
            ).grid(row=0, column=idx, sticky="ew", padx=px, pady=7)

        items = self.controller.service.filter_patients(
            query=self.search_input.get(),
            penjamin=self.penjamin_dd.get(),
            gender=self.gender_dd.get(),
        )[:4]

        for pat in items[:3]:
            row = tk.Frame(self.rows_holder, bg=COLORS["bg_white"], height=40)
            row.pack(fill=tk.X)
            row.pack_propagate(False)
            for idx, (_, wt, _, _) in enumerate(cols):
                row.grid_columnconfigure(idx, weight=wt, uniform="detcol")

            tk.Label(
                row, text=pat.no_rm, bg=COLORS["bg_white"],
                fg=COLORS["primary"], font=font(9, "bold"), anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=(20, 0))

            c1 = tk.Frame(row, bg=COLORS["bg_white"])
            c1.grid(row=0, column=1, sticky="w")
            tk.Label(c1, text=pat.nama, bg=COLORS["bg_white"], fg=COLORS["text_heading"], font=font(9, "bold"), anchor="w").pack(anchor="w")
            tk.Label(c1, text=pat.masked_nik(), bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(7), anchor="w").pack(anchor="w")

            tk.Label(row, text=pat.jenis_kelamin, bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=2, sticky="w")
            tk.Label(row, text=f"{pat.usia} tahun", bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=3, sticky="w")

            if pat.penjamin == "BPJS":
                pill = draw_pill_badge(row, "BPJS", COLORS["bg_badge_green"], COLORS["text_green_badge"], width=62, height=22)
            else:
                pill = draw_pill_badge(row, "Umum", COLORS["bg_pink"], COLORS["text_pink_badge"], width=62, height=22)
            pill.grid(row=0, column=4, sticky="w")

            tk.Label(row, text=pat.kunjungan_terakhir, bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=5, sticky="w")

            act = tk.Frame(row, bg=COLORS["bg_white"])
            act.grid(row=0, column=6, sticky="e", padx=(0, 18))
            RoundedButton(
                act, text="Detail  →",
                command=lambda rm=pat.no_rm: self.controller.open_patient_detail(rm),
                variant="secondary", width=82, height=28, radius=8,
                font_spec=font(8, "bold"), parent_bg=COLORS["bg_white"],
            ).pack()
            tk.Frame(self.rows_holder, bg=COLORS["gridline"], height=1).pack(fill=tk.X)
