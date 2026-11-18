"""Controller utama aplikasi Tkinter dan pengelola navigasi antar-halaman Heptamed Klinik."""

import tkinter as tk

from src.services.clinic_service import ClinicService
from src.utils.theme import COLORS
from src.views.antrean_frame import AntreanFrame
from src.views.data_frame import DataFrame
from src.views.detail_frame import DetailFrame
from src.views.laporan_frame import LaporanFrame
from src.views.login_frame import LoginFrame
from src.views.registrasi_frame import RegistrasiFrame


class App(tk.Tk):
    """Jendela utama aplikasi Heptamed Klinik yang mengatur navigasi dan state."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Heptamed Klinik — Sistem Antrean & Registrasi Pasien")
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        win_w = min(1120, max(980, sw - 80))
        win_h = min(760, max(660, sh - 60))
        self.geometry(f"{win_w}x{win_h}")
        self.minsize(980, 650)
        self.configure(bg=COLORS["bg_page"])

        self.service = ClinicService()

        container = tk.Frame(self, bg=COLORS["bg_page"])
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._frames: dict[str, tk.Frame] = {}
        frame_classes = {
            "login": LoginFrame,
            "registrasi": RegistrasiFrame,
            "antrean": AntreanFrame,
            "data": DataFrame,
            "detail": DetailFrame,
            "laporan": LaporanFrame,
        }

        for name, frame_cls in frame_classes.items():
            frame = frame_cls(parent=container, controller=self)
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("login")

    def show_frame(self, name: str) -> None:
        """Tampilkan halaman berdasarkan nama rute yang terdaftar."""
        route = "antrean" if name == "dashboard" else name
        frame = self._frames.get(route)
        if frame is None:
            raise KeyError(f"Frame '{name}' tidak ditemukan.")
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def open_patient_detail(self, no_rm: str) -> None:
        """Buka halaman Detail Pasien untuk nomor rekam medis tertentu."""
        detail_frame = self._frames.get("detail")
        if isinstance(detail_frame, DetailFrame):
            detail_frame.set_patient(no_rm)
        self.show_frame("detail")
