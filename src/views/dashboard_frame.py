"""Halaman Dashboard Navigasi (template awal)."""

from tkinter import ttk
from typing import Any

from src.views.base_frame import BaseFrame


class DashboardFrame(BaseFrame):
    """Kerangka halaman dashboard utama untuk navigasi antar-form."""

    def __init__(self, parent: ttk.Frame, controller: Any) -> None:
        super().__init__(parent, controller)

        ttk.Label(
            self,
            text="Dashboard Aplikasi",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        nav_frame = ttk.Frame(self)
        nav_frame.pack(anchor="w", pady=(0, 16))

        ttk.Button(
            nav_frame,
            text="Buka Form & Data",
            command=lambda: self.controller.show_frame("data"),
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            nav_frame,
            text="Kembali ke Login",
            command=lambda: self.controller.show_frame("login"),
        ).pack(side="left")
