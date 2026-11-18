"""Halaman Laporan Klinik (1:1 sesuai desain referensi)."""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from src.utils.theme import COLORS, draw_rounded_rect, font
from src.utils.validators import format_thousand
from src.views.base_frame import WorkspaceFrame
from src.views.components import KpiCard, RoundedButton, RoundedDropdown


def _draw_top_rounded_bar(
    canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, r: float, fill: str
) -> None:
    """Gambar batang grafik dengan sudut atas membulat dan alas rata."""
    r = min(r, (x2 - x1) / 2, max(0.0, (y2 - y1) / 2))
    if y2 - y1 < 2:
        return
    if r <= 1:
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")
        return
    canvas.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, fill=fill, outline="")
    canvas.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, fill=fill, outline="")
    canvas.create_rectangle(x1 + r, y1, x2 - r, y1 + r, fill=fill, outline="")
    canvas.create_rectangle(x1, y1 + r, x2, y2, fill=fill, outline="")


class LaporanFrame(WorkspaceFrame):
    """Halaman analitik kunjungan poli dengan grafik batang, distribusi poli, dan ekspor."""

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(
            parent,
            controller,
            active_route="laporan",
            breadcrumb_parts=[
                ("Ruang kerja", None),
                ("Laporan klinik", None),
            ],
        )
        self._report_data: dict = {}
        self._build_ui()

    def on_show(self) -> None:
        self._rebuild_topbar(self._breadcrumb_parts)
        self._apply_filter()

    def _build_ui(self) -> None:
        # Header: Laporan Klinik + Cetak laporan + Unduh laporan
        hdr = tk.Frame(self.body, bg=COLORS["bg_page"])
        hdr.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            hdr,
            text="Laporan Klinik",
            bg=COLORS["bg_page"],
            fg=COLORS["text_heading"],
            font=font(20, "bold"),
        ).pack(side=tk.LEFT)

        btns = tk.Frame(hdr, bg=COLORS["bg_page"])
        btns.pack(side=tk.RIGHT)

        RoundedButton(
            btns,
            text="Cetak laporan",
            command=self._print_report,
            variant="secondary",
            width=116,
            height=34,
            radius=10,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT, padx=(0, 10))

        RoundedButton(
            btns,
            text="Unduh laporan",
            command=self._download_report,
            variant="primary",
            width=126,
            height=34,
            radius=10,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT)

        # 4 KPI cards
        kpi_row = tk.Frame(self.body, bg=COLORS["bg_page"])
        kpi_row.pack(fill=tk.X, pady=(0, 8))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="lkpi")

        self.kpi_total = KpiCard(kpi_row, "Total kunjungan", "642", "1–18 November 2026", height=66)
        self.kpi_total.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.kpi_baru = KpiCard(kpi_row, "Pasien baru", "86", "13,4% dari kunjungan", pink=True, height=66)
        self.kpi_baru.grid(row=0, column=1, sticky="ew", padx=(0, 14))

        self.kpi_lama = KpiCard(kpi_row, "Pasien lama", "556", "86,6% dari kunjungan", height=66)
        self.kpi_lama.grid(row=0, column=2, sticky="ew", padx=(0, 14))

        self.kpi_avg = KpiCard(kpi_row, "Rata-rata / hari", "36", "Kunjungan per hari", height=66)
        self.kpi_avg.grid(row=0, column=3, sticky="ew")

        # Filter bar
        fbar = tk.Frame(self.body, bg=COLORS["bg_page"])
        fbar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            fbar, text="Periode laporan", bg=COLORS["bg_page"],
            fg=COLORS["text_muted"], font=font(9),
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.period_dd = RoundedDropdown(
            fbar,
            options=["1–18 November 2026", "1–30 Oktober 2026", "Hari ini (18 Nov 2026)"],
            initial="1–18 November 2026",
            width=190,
            height=36,
            radius=9,
            parent_bg=COLORS["bg_page"],
            bold_text=True,
        )
        self.period_dd.pack(side=tk.LEFT, padx=(0, 10))

        self.poli_dd = RoundedDropdown(
            fbar,
            options=["Semua poli", "Poli Umum", "Poli Gigi", "Poli Anak"],
            initial="Semua poli",
            width=136,
            height=36,
            radius=9,
            parent_bg=COLORS["bg_page"],
            bold_text=True,
        )
        self.poli_dd.pack(side=tk.LEFT, padx=(0, 10))

        RoundedButton(
            fbar,
            text="Terapkan",
            command=self._apply_filter,
            variant="primary",
            width=96,
            height=36,
            radius=9,
            font_spec=font(9, "bold"),
            parent_bg=COLORS["bg_page"],
        ).pack(side=tk.LEFT)

        tk.Label(
            fbar,
            text="Diperbarui 18 Nov 2026, 16.00",
            bg=COLORS["bg_page"],
            fg=COLORS["text_muted"],
            font=font(8),
        ).pack(side=tk.RIGHT)

        # Baris tengah 2 kartu grafik
        charts = tk.Frame(self.body, bg=COLORS["bg_page"])
        charts.pack(fill=tk.X, pady=(0, 8))
        charts.grid_columnconfigure(0, weight=14, uniform="lchart")
        charts.grid_columnconfigure(1, weight=10, uniform="lchart")

        self.trend_canvas = tk.Canvas(charts, height=168, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.trend_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.trend_canvas.bind("<Configure>", lambda _e: self._draw_trend_chart())

        self.poli_canvas = tk.Canvas(charts, height=168, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.poli_canvas.grid(row=0, column=1, sticky="nsew")
        self.poli_canvas.bind("<Configure>", lambda _e: self._draw_poli_chart())

        # Kartu bawah: Rekap pelayanan per poli
        self.recap_card = tk.Canvas(self.body, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self.recap_card.pack(fill=tk.BOTH, expand=True)

        self.recap_inner = tk.Frame(self.recap_card, bg=COLORS["bg_white"])
        self._recap_win = self.recap_card.create_window(2, 2, window=self.recap_inner, anchor="nw")
        self.recap_card.bind("<Configure>", self._on_recap_resize)

        self._apply_filter()

    def _on_recap_resize(self, event) -> None:
        w, h = event.width, event.height
        self.recap_card.delete("cardbg")
        draw_rounded_rect(
            self.recap_card, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1, tags="cardbg",
        )
        self.recap_card.tag_lower("cardbg")
        self.recap_card.itemconfigure(self._recap_win, width=max(300, w - 4), height=max(120, h - 4))

    def _apply_filter(self) -> None:
        period = self.period_dd.get()
        poli = self.poli_dd.get()
        data = self.controller.service.get_report_data(period, poli)
        self._report_data = data

        self.kpi_total.update_data(format_thousand(data["total_kunjungan"]), period)
        baru_pct = f"{data['pasien_baru_pct']:.1f}%".replace(".", ",")
        lama_pct = f"{data['pasien_lama_pct']:.1f}%".replace(".", ",")
        self.kpi_baru.update_data(format_thousand(data["pasien_baru"]), f"{baru_pct} dari kunjungan")
        self.kpi_lama.update_data(format_thousand(data["pasien_lama"]), f"{lama_pct} dari kunjungan")
        self.kpi_avg.update_data(format_thousand(data["rata_rata"]), "Kunjungan per hari")

        self._draw_trend_chart()
        self._draw_poli_chart()
        self._render_recap_table()

    def _draw_trend_chart(self) -> None:
        c = self.trend_canvas
        w = max(320, c.winfo_width())
        h = max(140, c.winfo_height())
        c.delete("all")
        draw_rounded_rect(
            c, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1,
        )

        c.create_text(20, 20, text="Tren kunjungan", anchor="w", fill=COLORS["text_heading"], font=font(11, "bold"))
        c.create_text(20, 38, text="Jumlah kunjungan per 3 hari", anchor="w", fill=COLORS["text_muted"], font=font(8))

        # Legend
        draw_rounded_rect(c, w - 104, 18, w - 94, 28, r=2, fill=COLORS["primary"], outline=COLORS["primary"])
        c.create_text(w - 88, 23, text="Kunjungan", anchor="w", fill=COLORS["text_muted"], font=font(8))

        vals: list[int] = self._report_data.get("trend_vals", [96, 104, 112, 88, 126, 116])
        labels: list[str] = self._report_data.get("trend_labels", ["1–3 Nov", "4–6 Nov", "7–9 Nov", "10–12 Nov", "13–15 Nov", "16–18 Nov"])
        max_val = max(150, max(vals) if vals else 150)
        if max_val <= 20:
            ticks = [0, 5, 10, 15, 20]
            y_cap = 20
        elif max_val <= 150:
            ticks = [0, 50, 100, 150]
            y_cap = 150
        else:
            y_cap = ((max_val + 49) // 50) * 50
            step = y_cap // 3
            ticks = [0, step, step * 2, y_cap]

        plot_x1 = 52
        plot_x2 = w - 24
        plot_y1 = 68
        plot_y2 = h - 32

        for t in ticks:
            y = plot_y2 - (t / y_cap) * (plot_y2 - plot_y1)
            c.create_line(plot_x1, y, plot_x2, y, fill=COLORS["gridline"], width=1)
            c.create_text(plot_x1 - 10, y, text=str(t), anchor="e", fill=COLORS["text_placeholder"], font=font(7))

        n = len(vals)
        if n == 0:
            return
        peak_val = max(vals)
        slot_w = (plot_x2 - plot_x1) / n
        bar_w = min(40, slot_w * 0.54)

        for idx, (lbl, val) in enumerate(zip(labels, vals)):
            cx = plot_x1 + slot_w * (idx + 0.5)
            bar_h = (val / y_cap) * (plot_y2 - plot_y1)
            by1 = plot_y2 - bar_h
            color = COLORS["chart_bar_peak"] if val == peak_val else COLORS["chart_bar"]
            _draw_top_rounded_bar(c, cx - bar_w / 2, by1, cx + bar_w / 2, plot_y2, r=5, fill=color)
            c.create_text(cx, by1 - 10, text=str(val), fill=COLORS["text_heading"], font=font(8, "bold"))
            c.create_text(cx, plot_y2 + 14, text=lbl, fill=COLORS["text_muted"], font=font(7))

    def _draw_poli_chart(self) -> None:
        c = self.poli_canvas
        w = max(240, c.winfo_width())
        h = max(140, c.winfo_height())
        c.delete("all")
        draw_rounded_rect(
            c, 1, 1, w - 1, h - 1, r=12,
            fill=COLORS["bg_white"], outline=COLORS["border"], width=1,
        )

        recap = self._report_data.get("recap", [])
        total = self._report_data.get("total_kunjungan", 642)
        c.create_text(20, 22, text="Kunjungan per poli", anchor="w", fill=COLORS["text_heading"], font=font(11, "bold"))
        c.create_text(
            20, 40, text=f"{format_thousand(total)} kunjungan dari {len(recap)} poli",
            anchor="w", fill=COLORS["text_muted"], font=font(8),
        )

        y = 70
        bar_x1 = 20
        bar_x2 = w - 20
        track_w = max(60, bar_x2 - bar_x1)

        for r in recap:
            pct = r["kontribusi"]
            pct_str = f"{pct:.1f}%".replace(".", ",")
            c.create_text(bar_x1, y, text=r["poli"], anchor="w", fill=COLORS["text_heading"], font=font(9, "bold"))
            c.create_text(
                bar_x2, y, text=f"{r['kunjungan']} · {pct_str}",
                anchor="e", fill=COLORS["text_muted"], font=font(8),
            )
            ty1 = y + 10
            ty2 = ty1 + 8
            draw_rounded_rect(c, bar_x1, ty1, bar_x2, ty2, r=4, fill=COLORS["chart_track"], outline=COLORS["chart_track"])
            fill_w = max(10, track_w * (pct / 100.0))
            draw_rounded_rect(c, bar_x1, ty1, bar_x1 + fill_w, ty2, r=4, fill=r["color"], outline=r["color"])
            y += 35

    def _render_recap_table(self) -> None:
        for w in self.recap_inner.winfo_children():
            w.destroy()

        top = tk.Frame(self.recap_inner, bg=COLORS["bg_white"], height=30)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(
            top, text="Rekap pelayanan per poli", bg=COLORS["bg_white"],
            fg=COLORS["text_heading"], font=font(10, "bold"),
        ).pack(side=tk.LEFT, padx=18)
        tk.Label(
            top, text=self._report_data.get("period", ""), bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(8),
        ).pack(side=tk.RIGHT, padx=18)

        hdr = tk.Frame(self.recap_inner, bg=COLORS["bg_soft_mint"], height=26)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        cols = [
            ("POLI", 28, "w", (18, 0)),
            ("KUNJUNGAN", 18, "w", (0, 0)),
            ("PASIEN BARU", 18, "w", (0, 0)),
            ("PASIEN LAMA", 18, "w", (0, 0)),
            ("KONTRIBUSI", 18, "w", (0, 0)),
        ]
        for idx, (title, wt, anc, px) in enumerate(cols):
            hdr.grid_columnconfigure(idx, weight=wt, uniform="rcol")
            tk.Label(
                hdr, text=title, bg=COLORS["bg_soft_mint"],
                fg=COLORS["text_muted"], font=font(8, "bold"), anchor=anc,
            ).grid(row=0, column=idx, sticky="ew", padx=px, pady=4)

        for r in self._report_data.get("recap", []):
            row = tk.Frame(self.recap_inner, bg=COLORS["bg_white"], height=26)
            row.pack(fill=tk.X)
            row.pack_propagate(False)
            for idx, (_, wt, _, _) in enumerate(cols):
                row.grid_columnconfigure(idx, weight=wt, uniform="rcol")

            tk.Label(row, text=r["poli"], bg=COLORS["bg_white"], fg=COLORS["text_heading"], font=font(9, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=(18, 0))
            tk.Label(row, text=str(r["kunjungan"]), bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=1, sticky="w")
            tk.Label(row, text=str(r["baru"]), bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=2, sticky="w")
            tk.Label(row, text=str(r["lama"]), bg=COLORS["bg_white"], fg=COLORS["text_muted"], font=font(9), anchor="w").grid(row=0, column=3, sticky="w")
            pct_str = f"{r['kontribusi']:.1f}%".replace(".", ",")
            tk.Label(row, text=pct_str, bg=COLORS["bg_white"], fg=COLORS["text_heading"], font=font(9, "bold"), anchor="w").grid(row=0, column=4, sticky="w")
            tk.Frame(self.recap_inner, bg=COLORS["gridline"], height=1).pack(fill=tk.X)

    def _print_report(self) -> None:
        data = self._report_data
        messagebox.showinfo(
            "Pratinjau Cetak Laporan",
            f"Laporan Heptamed Klinik ({data.get('period')})\n"
            f"Total Kunjungan: {data.get('total_kunjungan')}\n"
            f"Pasien Baru: {data.get('pasien_baru')} | Pasien Lama: {data.get('pasien_lama')}\n\n"
            "Siap dikirim ke printer default.",
        )

    def _download_report(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Unduh Laporan Klinik",
            defaultextension=".csv",
            initialfile="laporan_klinik_heptamed.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        self.controller.service.export_report_csv(
            path, self.period_dd.get(), self.poli_dd.get()
        )
        messagebox.showinfo("Unduh Berhasil", f"Laporan berhasil disimpan ke:\n{path}")
