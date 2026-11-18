"""Halaman Data Pasien (1:1 sesuai desain referensi)."""

import math
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from src.models.patient import Patient
from src.utils.theme import COLORS, draw_rounded_rect, font
from src.utils.validators import format_thousand
from src.views.base_frame import WorkspaceFrame
from src.views.components import (
    KpiCard,
    RoundedButton,
    RoundedDropdown,
    RoundedInput,
    draw_pill_badge,
)


class DataFrame(WorkspaceFrame):
    """Halaman direktori pasien dengan KPI, filter, tabel, ekspor CSV, dan paginasi."""

    PAGE_SIZE = 6

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(
            parent,
            controller,
            active_route="data",
            breadcrumb_parts=[
                ("Ruang kerja", None),
                ("Data pasien", None),
            ],
        )
        self._page = 1
        self._build_ui()

    def on_show(self) -> None:
        self._rebuild_topbar(self._breadcrumb_parts)
        self._refresh()

    def _build_ui(self) -> None:
        # Header: Data pasien + Ekspor data + + Tambah pasien
        hdr = tk.Frame(self.body, bg=COLORS["bg_page"])
        hdr.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            hdr,
            text="Data pasien",
            bg=COLORS["bg_page"],
            fg=COLORS["text_heading"],
            font=font(20, "bold"),
        ).pack(side=tk.LEFT)

        btn_box = tk.Frame(hdr, bg=COLORS["bg_page"])
        btn_box.pack(side=tk.RIGHT)

        RoundedButton(
            btn_box,
            text="Ekspor data",
            command=self._export_csv,
            variant="secondary",
            width=112,
            height=34,
            radius=10,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT, padx=(0, 10))

        RoundedButton(
            btn_box,
            text="+  Tambah pasien",
            command=lambda: self.controller.show_frame("registrasi"),
            variant="primary",
            width=146,
            height=34,
            radius=10,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT)

        # 4 KPI cards
        kpi_row = tk.Frame(self.body, bg=COLORS["bg_page"])
        kpi_row.pack(fill=tk.X, pady=(0, 10))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="dkpi")

        self.kpi_total = KpiCard(kpi_row, "Total pasien", "1.248", "Pasien terdaftar", height=68)
        self.kpi_total.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.kpi_baru = KpiCard(kpi_row, "Pasien baru", "86", "Bulan November 2026", pink=True, height=68)
        self.kpi_baru.grid(row=0, column=1, sticky="ew", padx=(0, 14))

        self.kpi_bpjs = KpiCard(kpi_row, "Pasien BPJS", "986", "79% dari total pasien", height=68)
        self.kpi_bpjs.grid(row=0, column=2, sticky="ew", padx=(0, 14))

        self.kpi_umum = KpiCard(kpi_row, "Pasien umum", "262", "21% dari total pasien", height=68)
        self.kpi_umum.grid(row=0, column=3, sticky="ew")

        # Kartu tabel utama (filter di dalam kartu)
        self.table_card = tk.Canvas(self.body, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.table_card.pack(fill=tk.BOTH, expand=True)

        self.card_inner = tk.Frame(self.table_card, bg=COLORS["bg_white"])
        self._card_win = self.table_card.create_window(2, 2, window=self.card_inner, anchor="nw")
        self.table_card.bind("<Configure>", self._on_card_resize)

        # Baris filter di dalam kartu
        fbar = tk.Frame(self.card_inner, bg=COLORS["bg_white"])
        fbar.pack(fill=tk.X, padx=16, pady=10)

        self.search_input = RoundedInput(
            fbar,
            placeholder="Cari nama, NIK, atau nomor rekam medis...",
            width=330,
            height=36,
            radius=9,
            parent_bg=COLORS["bg_white"],
            on_change=lambda _v: self._on_filter_change(),
        )
        self.search_input.pack(side=tk.LEFT, padx=(0, 12))

        self.penjamin_dd = RoundedDropdown(
            fbar,
            options=["Semua penjamin", "BPJS", "Umum"],
            initial="Semua penjamin",
            width=154,
            height=36,
            radius=9,
            parent_bg=COLORS["bg_white"],
            bold_text=True,
            on_select=lambda _v: self._on_filter_change(),
        )
        self.penjamin_dd.pack(side=tk.LEFT, padx=(0, 12))

        self.gender_dd = RoundedDropdown(
            fbar,
            options=["Semua jenis kelamin", "Laki-laki", "Perempuan"],
            initial="Semua jenis kelamin",
            width=174,
            height=36,
            radius=9,
            parent_bg=COLORS["bg_white"],
            bold_text=True,
            on_select=lambda _v: self._on_filter_change(),
        )
        self.gender_dd.pack(side=tk.LEFT)

        self.count_lbl = tk.Label(
            fbar,
            text="1.248 pasien",
            bg=COLORS["bg_white"],
            fg=COLORS["text_muted"],
            font=font(8),
        )
        self.count_lbl.pack(side=tk.RIGHT, padx=(8, 4))

        self.rows_holder = tk.Frame(self.card_inner, bg=COLORS["bg_white"])
        self.rows_holder.pack(fill=tk.BOTH, expand=True)

        self._refresh()

    def _on_card_resize(self, event) -> None:
        w, h = event.width, event.height
        self.table_card.delete("cardbg")
        draw_rounded_rect(
            self.table_card, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1, tags="cardbg",
        )
        self.table_card.tag_lower("cardbg")
        self.table_card.itemconfigure(self._card_win, width=max(300, w - 4), height=max(200, h - 4))

    def _on_filter_change(self) -> None:
        self._page = 1
        self._refresh()

    def _refresh(self) -> None:
        svc = self.controller.service
        kpis = svc.get_patient_kpis()
        self.kpi_total.update_data(format_thousand(int(kpis["total"])))
        self.kpi_baru.update_data(format_thousand(int(kpis["baru"])))
        self.kpi_bpjs.update_data(format_thousand(int(kpis["bpjs"])), f"{kpis['bpjs_pct']}% dari total pasien")
        self.kpi_umum.update_data(format_thousand(int(kpis["umum"])), f"{kpis['umum_pct']}% dari total pasien")

        filtered = svc.filter_patients(
            query=self.search_input.get(),
            penjamin=self.penjamin_dd.get(),
            gender=self.gender_dd.get(),
        )
        is_unfiltered = (
            not self.search_input.get().strip()
            and self.penjamin_dd.get() == "Semua penjamin"
            and self.gender_dd.get() == "Semua jenis kelamin"
        )
        display_total = int(kpis["total"]) if is_unfiltered else len(filtered)
        self.count_lbl.configure(text=f"{format_thousand(display_total)} pasien")

        total_pages = max(1, math.ceil(len(filtered) / self.PAGE_SIZE))
        self._page = min(self._page, total_pages)
        start = (self._page - 1) * self.PAGE_SIZE
        page_rows = filtered[start : start + self.PAGE_SIZE]

        self._render_table(page_rows, start, display_total, total_pages)

    def _render_table(
        self, rows: list[Patient], start_idx: int, display_total: int, total_pages: int
    ) -> None:
        for w in self.rows_holder.winfo_children():
            w.destroy()

        # Header tabel
        hdr = tk.Frame(self.rows_holder, bg=COLORS["bg_soft_mint"], height=30)
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
            hdr.grid_columnconfigure(idx, weight=wt, uniform="pcol")
            tk.Label(
                hdr, text=title, bg=COLORS["bg_soft_mint"],
                fg=COLORS["text_muted"], font=font(8, "bold"), anchor=anc,
            ).grid(row=0, column=idx, sticky="ew", padx=px, pady=8)

        body = tk.Frame(self.rows_holder, bg=COLORS["bg_white"])
        body.pack(fill=tk.BOTH, expand=True)

        if not rows:
            tk.Label(
                body,
                text="Tidak ada data pasien yang sesuai filter.",
                bg=COLORS["bg_white"],
                fg=COLORS["text_muted"],
                font=font(10),
            ).pack(pady=40)
        else:
            for p in rows:
                self._render_patient_row(body, p)

        # Footer paginasi
        footer = tk.Frame(self.rows_holder, bg=COLORS["bg_white"], height=36)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        if rows:
            shown_from = start_idx + 1
            shown_to = start_idx + len(rows)
            info_txt = f"Menampilkan {shown_from}–{shown_to} dari {format_thousand(display_total)} pasien"
        else:
            info_txt = "Menampilkan 0 pasien"

        tk.Label(
            footer, text=info_txt, bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(8),
        ).pack(side=tk.LEFT, padx=20)

        pag = tk.Frame(footer, bg=COLORS["bg_white"])
        pag.pack(side=tk.RIGHT, padx=20)

        prev_lbl = tk.Label(
            pag, text="‹", bg=COLORS["bg_white"],
            fg=COLORS["text_muted"] if self._page > 1 else COLORS["text_placeholder"],
            font=font(10), cursor="hand2" if self._page > 1 else "arrow",
        )
        prev_lbl.pack(side=tk.LEFT, padx=8)
        if self._page > 1:
            prev_lbl.bind("<Button-1>", lambda _e: self._goto_page(self._page - 1))

        for pnum in range(1, max(3, total_pages) + 1):
            if pnum > total_pages and pnum > 3:
                break
            is_cur = pnum == self._page
            if is_cur:
                b = draw_pill_badge(
                    pag, str(pnum), COLORS["bg_badge_green"], COLORS["primary"], width=26, height=26
                )
                b.pack(side=tk.LEFT, padx=3)
            else:
                enabled = pnum <= total_pages
                pl = tk.Label(
                    pag, text=str(pnum), bg=COLORS["bg_white"],
                    fg=COLORS["text_body"] if enabled else COLORS["text_placeholder"],
                    font=font(9), width=2, cursor="hand2" if enabled else "arrow",
                )
                pl.pack(side=tk.LEFT, padx=3)
                if enabled:
                    pl.bind("<Button-1>", lambda _e, n=pnum: self._goto_page(n))

        tk.Label(pag, text="...", bg=COLORS["bg_white"], fg=COLORS["text_placeholder"], font=font(9)).pack(side=tk.LEFT, padx=4)

        next_lbl = tk.Label(
            pag, text="›", bg=COLORS["bg_white"],
            fg=COLORS["text_muted"] if self._page < total_pages else COLORS["text_placeholder"],
            font=font(10), cursor="hand2" if self._page < total_pages else "arrow",
        )
        next_lbl.pack(side=tk.LEFT, padx=8)
        if self._page < total_pages:
            next_lbl.bind("<Button-1>", lambda _e: self._goto_page(self._page + 1))

    def _render_patient_row(self, parent: tk.Frame, p: Patient) -> None:
        row = tk.Frame(parent, bg=COLORS["bg_white"], height=40)
        row.pack(fill=tk.X)
        row.pack_propagate(False)

        weights = [12, 24, 14, 11, 11, 16, 12]
        for idx, wt in enumerate(weights):
            row.grid_columnconfigure(idx, weight=wt, uniform="pcol")

        tk.Label(
            row, text=p.no_rm, bg=COLORS["bg_white"],
            fg=COLORS["primary"], font=font(9, "bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(20, 0))

        c1 = tk.Frame(row, bg=COLORS["bg_white"])
        c1.grid(row=0, column=1, sticky="w", pady=4)
        tk.Label(
            c1, text=p.nama, bg=COLORS["bg_white"],
            fg=COLORS["text_heading"], font=font(9, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            c1, text=p.masked_nik(), bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(7), anchor="w",
        ).pack(anchor="w")

        tk.Label(
            row, text=p.jenis_kelamin, bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(9), anchor="w",
        ).grid(row=0, column=2, sticky="w")

        tk.Label(
            row, text=f"{p.usia} tahun", bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(9), anchor="w",
        ).grid(row=0, column=3, sticky="w")

        if p.penjamin == "BPJS":
            pill = draw_pill_badge(row, "BPJS", COLORS["bg_badge_green"], COLORS["text_green_badge"], width=62, height=24)
        else:
            pill = draw_pill_badge(row, "Umum", COLORS["bg_pink"], COLORS["text_pink_badge"], width=62, height=24)
        pill.grid(row=0, column=4, sticky="w")

        tk.Label(
            row, text=p.kunjungan_terakhir, bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(9), anchor="w",
        ).grid(row=0, column=5, sticky="w")

        act = tk.Frame(row, bg=COLORS["bg_white"])
        act.grid(row=0, column=6, sticky="e", padx=(0, 18))
        RoundedButton(
            act,
            text="Detail  →",
            command=lambda rm=p.no_rm: self.controller.open_patient_detail(rm),
            variant="secondary",
            width=82,
            height=28,
            radius=8,
            font_spec=font(8, "bold"),
            parent_bg=COLORS["bg_white"],
        ).pack()

        tk.Frame(parent, bg=COLORS["gridline"], height=1).pack(fill=tk.X)

    def _goto_page(self, page: int) -> None:
        self._page = page
        self._refresh()

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Ekspor Data Pasien",
            defaultextension=".csv",
            initialfile="data_pasien_heptamed.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        self.controller.service.export_patients_csv(path)
        messagebox.showinfo("Ekspor Berhasil", f"Data pasien disimpan ke:\n{path}")
