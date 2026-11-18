"""Halaman Login / Menu Awal (template awal)."""

from tkinter import ttk
from typing import Any

from src.views.base_frame import BaseFrame


class LoginFrame(BaseFrame):
    """Kerangka halaman login untuk dikembangkan sesuai desain Figma."""

    def __init__(self, parent: ttk.Frame, controller: Any) -> None:
        super().__init__(parent, controller)

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            wrapper,
            text="Halaman Login / Menu Utama",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 8))

        ttk.Label(
            wrapper,
            text="Template setup proyek GUI + OOP (Tkinter & ttk).",
        ).pack(pady=(0, 16))

        ttk.Button(
            wrapper,
            text="Masuk ke Dashboard",
            command=lambda: self.controller.show_frame("dashboard"),
        ).pack(fill="x")
