"""Kelas dasar untuk seluruh halaman ruang kerja Heptamed Klinik."""

import tkinter as tk
from typing import Any, Callable

from src.utils.theme import COLORS
from src.views.components import BottomDock, TopBar


class BaseFrame(tk.Frame):
    """Base class Frame dengan referensi controller untuk navigasi."""

    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent, bg=COLORS["bg_page"])
        self.controller = controller

    def on_show(self) -> None:
        """Hook yang dipanggil setiap kali frame ditampilkan."""


class WorkspaceFrame(BaseFrame):
    """Kerangka halaman dengan TopBar, area konten proporsional, dan BottomDock."""

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        active_route: str,
        breadcrumb_parts: list[tuple[str, Callable[[], None] | None]],
        serving_text: str = "",
    ) -> None:
        super().__init__(parent, controller)
        self.active_route = active_route
        self._breadcrumb_parts = breadcrumb_parts
        self._serving_text = serving_text

        self.topbar_holder = tk.Frame(self, bg=COLORS["bg_white"])
        self.topbar_holder.pack(fill=tk.X, side=tk.TOP)
        self._rebuild_topbar(breadcrumb_parts)

        # Bottom dock di bawah layar
        self.dock = BottomDock(
            self,
            active_route=active_route,
            on_navigate=self.controller.show_frame,
            on_logout=lambda: self.controller.show_frame("login"),
            serving_text=serving_text,
        )
        self.dock.pack(fill=tk.X, side=tk.BOTTOM, pady=(2, 8))

        # Area konten tengah dengan padding samping responsif (~10% dari lebar layar)
        self.outer_body = tk.Frame(self, bg=COLORS["bg_page"])
        self.outer_body.pack(fill=tk.BOTH, expand=True)

        self.body = tk.Frame(self.outer_body, bg=COLORS["bg_page"])
        self.body.pack(fill=tk.BOTH, expand=True, padx=96, pady=(10, 2))
        self.outer_body.bind("<Configure>", self._adjust_margins)

    def _adjust_margins(self, event) -> None:
        pad_x = max(36, int(event.width * 0.10))
        self.body.pack_configure(padx=pad_x)

    def _rebuild_topbar(
        self, breadcrumb_parts: list[tuple[str, Callable[[], None] | None]]
    ) -> None:
        for w in self.topbar_holder.winfo_children():
            w.destroy()
        svc = self.controller.service
        topbar = TopBar(
            self.topbar_holder,
            breadcrumb_parts=breadcrumb_parts,
            date_text=svc.current_date_label,
            staff_badge=svc.staff_badge,
            staff_name=svc.staff_name,
            staff_role=svc.staff_role,
        )
        topbar.pack(fill=tk.X)
