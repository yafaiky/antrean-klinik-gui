"""Kelas dasar untuk semua halaman (Frame) pada aplikasi."""

from tkinter import ttk
from typing import Any


class BaseFrame(ttk.Frame):
    """Base class Frame dengan referensi controller untuk navigasi."""

    def __init__(self, parent: ttk.Frame, controller: Any) -> None:
        super().__init__(parent, padding=16)
        self.controller = controller

    def on_show(self) -> None:
        """Hook yang dipanggil setiap kali frame ditampilkan."""
