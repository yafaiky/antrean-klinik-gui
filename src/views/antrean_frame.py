"""Halaman Antrean Poli (1:1 sesuai desain referensi)."""

import tkinter as tk
from typing import Any

from src.models.queue_item import QueueItem
from src.utils.theme import COLORS, draw_rounded_rect, font
from src.views.base_frame import WorkspaceFrame
from src.views.components import (
    KpiCard,
    RoundedButton,
    RoundedDropdown,
    RoundedInput,
    draw_pill_badge,
)


class AntreanFrame(WorkspaceFrame):
    """Halaman manajemen antrean pasien dikelompokkan per poli."""

    POLI_ORDER = ["Poli Umum", "Poli Gigi", "Poli Anak"]

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(
            parent,
            controller,
            active_route="antrean",
            breadcrumb_parts=[
                ("Ruang kerja", None),
                ("Antrean poli", None),
            ],
            serving_text="A-001 · Budi Santoso",
        )
        self._collapsed: dict[str, bool] = {
            "Poli Umum": False,
            "Poli Gigi": False,
            "Poli Anak": True,
        }
        self._page = 1
        self._build_ui()

    def on_show(self) -> None:
        self._rebuild_topbar(self._breadcrumb_parts)
        self._refresh()

    def _build_ui(self) -> None:
        # Header: Antrean poli + + Registrasi pasien
        hdr = tk.Frame(self.body, bg=COLORS["bg_page"])
        hdr.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            hdr,
            text="Antrean poli",
            bg=COLORS["bg_page"],
            fg=COLORS["text_heading"],
            font=font(20, "bold"),
        ).pack(side=tk.LEFT)

        RoundedButton(
            hdr,
            text="+  Registrasi pasien",
            command=lambda: self.controller.show_frame("registrasi"),
            variant="primary",
            width=162,
            height=34,
            radius=10,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.RIGHT)

        # 4 KPI cards
        kpi_row = tk.Frame(self.body, bg=COLORS["bg_page"])
        kpi_row.pack(fill=tk.X, pady=(0, 10))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="akpi")

        self.kpi_total = KpiCard(kpi_row, "Total pasien", "06", "Terdaftar hari ini", height=68)
        self.kpi_total.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.kpi_wait = KpiCard(kpi_row, "Menunggu", "04", "Siap untuk dipanggil", height=68)
        self.kpi_wait.grid(row=0, column=1, sticky="ew", padx=(0, 14))

        self.kpi_active = KpiCard(kpi_row, "Sedang diperiksa", "01", "Pelayanan berlangsung", pink=True, height=68)
        self.kpi_active.grid(row=0, column=2, sticky="ew", padx=(0, 14))

        self.kpi_done = KpiCard(kpi_row, "Selesai", "01", "Pelayanan tuntas", height=68)
        self.kpi_done.grid(row=0, column=3, sticky="ew")

        # Filter bar di atas kartu tabel
        filter_row = tk.Frame(self.body, bg=COLORS["bg_page"])
        filter_row.pack(fill=tk.X, pady=(0, 10))

        self.search_input = RoundedInput(
            filter_row,
            placeholder="Cari nama atau nomor antrean...",
            width=330,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_page"],
            bg_fill=COLORS["bg_white"],
            on_change=lambda _v: self._refresh(),
        )
        self.search_input.pack(side=tk.LEFT, padx=(0, 12))

        self.poli_dd = RoundedDropdown(
            filter_row,
            options=["Semua poli", "Poli Umum", "Poli Gigi", "Poli Anak"],
            initial="Semua poli",
            width=155,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_page"],
            bold_text=True,
            on_select=lambda _v: self._refresh(),
        )
        self.poli_dd.pack(side=tk.LEFT, padx=(0, 12))

        self.status_dd = RoundedDropdown(
            filter_row,
            options=["Semua status", "Menunggu", "Diperiksa", "Selesai"],
            initial="Semua status",
            width=165,
            height=34,
            radius=9,
            parent_bg=COLORS["bg_page"],
            bold_text=True,
            on_select=lambda _v: self._refresh(),
        )
        self.status_dd.pack(side=tk.LEFT)

        # Kartu tabel antrean
        self.table_card = tk.Canvas(self.body, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.table_card.pack(fill=tk.BOTH, expand=True)

        self.table_inner = tk.Frame(self.table_card, bg=COLORS["bg_white"])
        self._table_win = self.table_card.create_window(2, 2, window=self.table_inner, anchor="nw")
        self.table_card.bind("<Configure>", self._on_card_resize)

        self._refresh()

    def _on_card_resize(self, event) -> None:
        w, h = event.width, event.height
        self.table_card.delete("cardbg")
        draw_rounded_rect(
            self.table_card, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1, tags="cardbg",
        )
        self.table_card.tag_lower("cardbg")
        self.table_card.itemconfigure(self._table_win, width=max(300, w - 4), height=max(180, h - 4))

    def _refresh(self) -> None:
        svc = self.controller.service
        kpis = svc.get_queue_kpis()
        self.kpi_total.update_data(f"{kpis['total']:02d}")
        self.kpi_wait.update_data(f"{kpis['menunggu']:02d}")
        self.kpi_active.update_data(f"{kpis['diperiksa']:02d}")
        self.kpi_done.update_data(f"{kpis['selesai']:02d}")

        active = svc.get_active_serving()
        self.dock.set_serving_text(
            f"{active.no_antrean} · {active.nama_pasien}" if active else "Belum ada pasien dipanggil"
        )

        items = svc.filter_queue(
            query=self.search_input.get(),
            poli=self.poli_dd.get(),
            status=self.status_dd.get(),
        )
        self._render_table(items, len(svc.queue_items))

    def _render_table(self, items: list[QueueItem], total_all: int) -> None:
        for w in self.table_inner.winfo_children():
            w.destroy()

        # Header kolom
        hdr = tk.Frame(self.table_inner, bg=COLORS["bg_soft_mint"], height=30)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        cols = [
            ("NO. ANTREAN", 12, "w", (28, 0)),
            ("PASIEN", 26, "w", (0, 0)),
            ("USIA", 8, "w", (0, 0)),
            ("TERDAFTAR", 12, "w", (0, 0)),
            ("STATUS", 14, "w", (0, 0)),
            ("AKSI", 16, "center", (0, 14)),
        ]
        for idx, (title, wt, anc, px) in enumerate(cols):
            hdr.grid_columnconfigure(idx, weight=wt, uniform="qcol")
            tk.Label(
                hdr, text=title, bg=COLORS["bg_soft_mint"],
                fg=COLORS["text_muted"], font=font(8, "bold"), anchor=anc,
            ).grid(row=0, column=idx, sticky="ew", padx=px, pady=8)

        # Area isi tabel
        list_area = tk.Frame(self.table_inner, bg=COLORS["bg_white"])
        list_area.pack(fill=tk.BOTH, expand=True)

        shown_count = 0
        for poli in self.POLI_ORDER:
            grp = [q for q in items if q.poli == poli]
            if not grp:
                continue
            waiting_n = sum(1 for q in grp if q.status == "Menunggu")
            is_collapsed = self._collapsed.get(poli, False)
            # Bila sedang mencari/filter spesifik, otomatis buka semua grup
            if self.search_input.get().strip() or self.poli_dd.get() != "Semua poli" or self.status_dd.get() != "Semua status":
                is_collapsed = False

            grp_bar = tk.Frame(list_area, bg="#FAFBF9", height=30, cursor="hand2")
            grp_bar.pack(fill=tk.X)
            grp_bar.pack_propagate(False)

            chev = "›" if is_collapsed else "⌄"
            left_g = tk.Frame(grp_bar, bg="#FAFBF9")
            left_g.pack(side=tk.LEFT, padx=(16, 0))
            tk.Label(
                left_g, text=chev, bg="#FAFBF9", fg=COLORS["primary"],
                font=font(11, "bold"), width=2,
            ).pack(side=tk.LEFT)
            tk.Label(
                left_g, text=poli, bg="#FAFBF9", fg=COLORS["primary"],
                font=font(9, "bold"),
            ).pack(side=tk.LEFT, padx=(2, 10))
            tk.Label(
                left_g, text=f"{len(grp)} pasien · {waiting_n} menunggu",
                bg="#FAFBF9", fg=COLORS["text_muted"], font=font(8),
            ).pack(side=tk.LEFT)

            toggle_lbl = tk.Label(
                grp_bar,
                text="Tampilkan" if is_collapsed else "Ciutkan",
                bg="#FAFBF9",
                fg=COLORS["text_muted"],
                font=font(8),
                cursor="hand2",
            )
            toggle_lbl.pack(side=tk.RIGHT, padx=20)

            def _toggle(_e, p_name=poli) -> None:
                self._collapsed[p_name] = not self._collapsed.get(p_name, False)
                self._refresh()

            grp_bar.bind("<Button-1>", _toggle)
            toggle_lbl.bind("<Button-1>", _toggle)
            for ch in left_g.winfo_children():
                ch.bind("<Button-1>", _toggle)

            tk.Frame(list_area, bg=COLORS["gridline"], height=1).pack(fill=tk.X)

            if not is_collapsed:
                for q in grp:
                    self._render_queue_row(list_area, q)
                    shown_count += 1

        # Footer tabel
        tk.Frame(self.table_inner, bg=COLORS["gridline"], height=1).pack(fill=tk.X, side=tk.BOTTOM, before=None)
        footer = tk.Frame(self.table_inner, bg=COLORS["bg_white"], height=36)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text=f"Menampilkan {shown_count} dari {total_all} pasien · Dikelompokkan per poli",
            bg=COLORS["bg_white"],
            fg=COLORS["text_muted"],
            font=font(8),
        ).pack(side=tk.LEFT, padx=20)

        pag = tk.Frame(footer, bg=COLORS["bg_white"])
        pag.pack(side=tk.RIGHT, padx=20)
        tk.Label(pag, text="‹", bg=COLORS["bg_white"], fg=COLORS["text_placeholder"], font=font(10)).pack(side=tk.LEFT, padx=8)
        p1 = draw_pill_badge(pag, "1", COLORS["bg_badge_green"], COLORS["primary"], width=26, height=26)
        p1.pack(side=tk.LEFT, padx=2)
        tk.Label(pag, text="›", bg=COLORS["bg_white"], fg=COLORS["text_placeholder"], font=font(10)).pack(side=tk.LEFT, padx=8)

    def _render_queue_row(self, parent: tk.Frame, item: QueueItem) -> None:
        is_active = item.status == "Diperiksa"
        row_bg = COLORS["bg_pink_row"] if is_active else COLORS["bg_white"]

        row = tk.Frame(parent, bg=row_bg, height=40)
        row.pack(fill=tk.X)
        row.pack_propagate(False)

        weights = [12, 26, 8, 12, 14, 16]
        for idx, wt in enumerate(weights):
            row.grid_columnconfigure(idx, weight=wt, uniform="qcol")

        # Kolom 0: NO. ANTREAN (+ garis tipis kiri)
        c0 = tk.Frame(row, bg=row_bg)
        c0.grid(row=0, column=0, sticky="nsew", padx=(18, 0))
        tk.Frame(c0, bg=COLORS["border_pink"] if is_active else COLORS["border"], width=2, height=26).pack(side=tk.LEFT, pady=12)
        tk.Label(
            c0, text=item.no_antrean, bg=row_bg,
            fg=COLORS["text_heading"], font=font(10, "bold"),
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Kolom 1: PASIEN (Nama + No RM)
        c1 = tk.Frame(row, bg=row_bg)
        c1.grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(
            c1, text=item.nama_pasien, bg=row_bg,
            fg=COLORS["text_heading"], font=font(9, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            c1, text=item.no_rm, bg=row_bg,
            fg=COLORS["text_muted"], font=font(7), anchor="w",
        ).pack(anchor="w")

        # Kolom 2: USIA
        tk.Label(
            row, text=f"{item.usia} th", bg=row_bg,
            fg=COLORS["text_muted"], font=font(9), anchor="w",
        ).grid(row=0, column=2, sticky="w")

        # Kolom 3: TERDAFTAR
        tk.Label(
            row, text=item.terdaftar, bg=row_bg,
            fg=COLORS["text_muted"], font=font(9), anchor="w",
        ).grid(row=0, column=3, sticky="w")

        # Kolom 4: STATUS pill
        badge_map = {
            "Diperiksa": (COLORS["bg_pink"], COLORS["text_pink_badge"]),
            "Menunggu": (COLORS["bg_badge_yellow"], COLORS["text_yellow_badge"]),
            "Selesai": (COLORS["bg_badge_green"], COLORS["text_green_badge"]),
        }
        bg_b, fg_b = badge_map.get(item.status, (COLORS["bg_soft_mint"], COLORS["text_body"]))
        pill = draw_pill_badge(row, item.status, bg_b, fg_b, parent_bg=row_bg, width=78, height=24)
        pill.grid(row=0, column=4, sticky="w")

        # Kolom 5: AKSI button
        act_wrap = tk.Frame(row, bg=row_bg)
        act_wrap.grid(row=0, column=5, sticky="e", padx=(0, 18))

        if item.status == "Diperiksa":
            RoundedButton(
                act_wrap, text="Selesaikan",
                command=lambda n=item.no_antrean: self._complete_item(n),
                variant="secondary", width=108, height=30, radius=8,
                font_spec=font(8, "bold"), parent_bg=row_bg,
            ).pack()
        elif item.status == "Menunggu":
            RoundedButton(
                act_wrap, text="Panggil  →",
                command=lambda n=item.no_antrean: self._call_item(n),
                variant="primary", width=108, height=30, radius=8,
                font_spec=font(8, "bold"), parent_bg=row_bg,
            ).pack()
        else:
            RoundedButton(
                act_wrap, text="Detail",
                command=lambda rm=item.no_rm: self._open_detail(rm),
                variant="secondary", width=108, height=30, radius=8,
                font_spec=font(8, "bold"), parent_bg=row_bg,
            ).pack()

        tk.Frame(parent, bg=COLORS["gridline"], height=1).pack(fill=tk.X)

    def _call_item(self, no_antrean: str) -> None:
        self.controller.service.call_queue_item(no_antrean)
        self._refresh()

    def _complete_item(self, no_antrean: str) -> None:
        self.controller.service.complete_queue_item(no_antrean)
        self._refresh()

    def _open_detail(self, no_rm: str) -> None:
        self.controller.open_patient_detail(no_rm)
