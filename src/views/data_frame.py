"""Halaman Pengelolaan Data & Tabel Treeview (template awal)."""

from tkinter import ttk
from typing import Any

from src.views.base_frame import BaseFrame


class DataFrame(BaseFrame):
    """Kerangka halaman form input dan tabel Treeview (CRUD/Rekap)."""

    def __init__(self, parent: ttk.Frame, controller: Any) -> None:
        super().__init__(parent, controller)

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text="Pengelolaan Data",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")

        ttk.Button(
            header,
            text="Kembali ke Dashboard",
            command=lambda: self.controller.show_frame("dashboard"),
        ).pack(side="right")

        columns = ("id", "nama", "keterangan")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.heading("nama", text="Nama")
        tree.heading("keterangan", text="Keterangan")
        tree.column("id", width=80, anchor="center")
        tree.column("nama", width=220)
        tree.column("keterangan", width=360)
        tree.pack(fill="both", expand=True)
