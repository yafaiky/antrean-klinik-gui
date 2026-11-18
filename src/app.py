"""Controller utama aplikasi Tkinter dan pengelola navigasi antar-frame."""

import tkinter as tk
from tkinter import ttk

from src.views.dashboard_frame import DashboardFrame
from src.views.data_frame import DataFrame
from src.views.login_frame import LoginFrame


class App(tk.Tk):
    """Jendela utama aplikasi yang mengatur perpindahan antar-halaman (Frame)."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Aplikasi Desktop GUI - Ujian Praktik PBTGM")
        self.geometry("900x600")
        self.minsize(720, 480)

        self._configure_style()

        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._frames: dict[str, ttk.Frame] = {}
        frame_classes = {
            "login": LoginFrame,
            "dashboard": DashboardFrame,
            "data": DataFrame,
        }

        for name, frame_cls in frame_classes.items():
            frame = frame_cls(parent=container, controller=self)
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("login")

    def _configure_style(self) -> None:
        """Atur tema dasar ttk."""
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

    def show_frame(self, name: str) -> None:
        """Tampilkan frame berdasarkan nama rute yang terdaftar."""
        frame = self._frames.get(name)
        if frame is None:
            raise KeyError(f"Frame '{name}' tidak ditemukan.")
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
