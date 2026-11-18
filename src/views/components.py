"""Komponen UI modular berbasis tk.Canvas untuk tampilan 1:1 Heptamed Klinik."""

import tkinter as tk
from typing import Callable

from src.utils.theme import (
    COLORS,
    draw_dock_icon,
    draw_heptamed_logo,
    draw_rounded_rect,
    font,
)


class RoundedButton(tk.Canvas):
    """Tombol sudut membulat dengan efek hover dan dukungan varian warna."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable[[], None] | None = None,
        variant: str = "primary",
        width: int = 150,
        height: int = 38,
        radius: int = 10,
        font_spec: tuple | None = None,
        parent_bg: str = COLORS["bg_page"],
        right_arrow: bool = False,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2" if variant != "disabled" else "arrow",
        )
        self._text = text
        self._command = command
        self._variant = variant
        self._width = width
        self._height = height
        self._radius = radius
        self._font = font_spec or font(10, "bold")
        self._right_arrow = right_arrow
        self._hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._redraw()

    def set_variant(self, variant: str) -> None:
        self._variant = variant
        self.configure(cursor="hand2" if variant != "disabled" else "arrow")
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        self._redraw()

    def _palette(self) -> tuple[str, str, str]:
        if self._variant == "primary":
            bg = COLORS["primary_hover"] if self._hovered else COLORS["primary"]
            return bg, bg, "#FFFFFF"
        if self._variant == "disabled":
            return COLORS["primary_disabled"], COLORS["primary_disabled"], COLORS["primary_disabled_text"]
        if self._variant == "pill_white":
            bg = "#F8FAF9" if self._hovered else COLORS["bg_white"]
            return bg, COLORS["border"], COLORS["text_primary"]
        # secondary / outlined
        bg = "#F3F7F5" if self._hovered else COLORS["bg_white"]
        return bg, COLORS["border_strong"], COLORS["text_primary"]

    def _redraw(self) -> None:
        self.delete("all")
        bg, border, fg = self._palette()
        draw_rounded_rect(
            self, 1, 1, self._width - 1, self._height - 1,
            r=self._radius, fill=bg, outline=border, width=1,
        )
        if self._right_arrow:
            self.create_text(
                self._width / 2 - 4,
                self._height / 2,
                text=self._text,
                fill=fg,
                font=self._font,
            )
            self.create_text(
                self._width - 20,
                self._height / 2,
                text="→",
                fill=fg,
                font=font(12, "bold"),
            )
        else:
            self.create_text(
                self._width / 2,
                self._height / 2,
                text=self._text,
                fill=fg,
                font=self._font,
            )

    def _on_enter(self, _e=None) -> None:
        if self._variant != "disabled":
            self._hovered = True
            self._redraw()

    def _on_leave(self, _e=None) -> None:
        self._hovered = False
        self._redraw()

    def _on_click(self, _e=None) -> None:
        if self._variant != "disabled" and self._command:
            self._command()


class RoundedInput(tk.Canvas):
    """Input teks sudut membulat dengan placeholder, border state, dan toggle sandi opsional."""

    def __init__(
        self,
        parent: tk.Widget,
        placeholder: str = "",
        width: int = 320,
        height: int = 42,
        radius: int = 10,
        is_password: bool = False,
        parent_bg: str = COLORS["bg_white"],
        bg_fill: str = COLORS["bg_white"],
        readonly: bool = False,
        text_color: str = COLORS["text_primary"],
        font_spec: tuple | None = None,
        on_change: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
        )
        self._width = width
        self._height = height
        self._radius = radius
        self._placeholder = placeholder
        self._is_password = is_password
        self._show_password = False
        self._bg_fill = bg_fill
        self._border_color = COLORS["border_strong"]
        self._readonly = readonly
        self._text_color = text_color
        self._on_change = on_change
        self._showing_placeholder = False

        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            bd=0,
            relief=tk.FLAT,
            bg=bg_fill,
            fg=text_color,
            insertbackground=COLORS["primary"],
            font=font_spec or font(10),
            highlightthickness=0,
            disabledbackground=bg_fill,
            disabledforeground=text_color,
            readonlybackground=bg_fill,
        )
        if readonly:
            self.entry.configure(state="readonly")

        right_pad = 78 if is_password else 14
        self._entry_win = self.create_window(
            14,
            height / 2,
            window=self.entry,
            anchor="w",
            width=max(60, width - 14 - right_pad),
            height=height - 12,
        )
        self._toggle_id: int | None = None

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", lambda _e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)

        self._apply_placeholder()
        self._redraw()

    def _on_resize(self, event) -> None:
        self._width = max(80, event.width)
        self._height = max(28, event.height)
        right_pad = 78 if self._is_password else 14
        self.coords(self._entry_win, 14, self._height / 2)
        self.itemconfigure(self._entry_win, width=max(50, self._width - 14 - right_pad))
        self._redraw()

    def _redraw(self) -> None:
        self.delete("bg")
        draw_rounded_rect(
            self, 1, 1, self._width - 1, self._height - 1,
            r=self._radius, fill=self._bg_fill, outline=self._border_color, width=1, tags="bg",
        )
        self.tag_lower("bg")

        if self._is_password:
            if self._toggle_id:
                self.delete(self._toggle_id)
            label = "Sembunyikan" if self._show_password else "Tampilkan"
            self._toggle_id = self.create_text(
                self._width - 14,
                self._height / 2,
                text=label,
                anchor="e",
                fill=COLORS["primary"],
                font=font(9, "bold"),
                tags="toggle",
            )
            self.tag_bind("toggle", "<Button-1>", self._toggle_password)

    def _toggle_password(self, _e=None) -> None:
        self._show_password = not self._show_password
        if not self._showing_placeholder:
            self.entry.configure(show="" if self._show_password else "•")
        self._redraw()

    def _apply_placeholder(self) -> None:
        if self._placeholder and not self.var.get():
            self._showing_placeholder = True
            self.entry.configure(fg=COLORS["text_placeholder"], show="")
            self.var.set(self._placeholder)

    def _on_focus_in(self, _e=None) -> None:
        if self._readonly:
            return
        if self._showing_placeholder:
            self._showing_placeholder = False
            self.var.set("")
            self.entry.configure(
                fg=self._text_color,
                show=("•" if self._is_password and not self._show_password else ""),
            )

    def _on_focus_out(self, _e=None) -> None:
        if self._readonly:
            return
        if not self.var.get():
            self._apply_placeholder()

    def _on_key_release(self, _e=None) -> None:
        if not self._showing_placeholder and self._on_change:
            self._on_change(self.get())

    def get(self) -> str:
        if self._showing_placeholder:
            return ""
        return self.var.get()

    def set(self, value: str) -> None:
        self._showing_placeholder = False
        if self._readonly:
            self.entry.configure(state="normal")
        self.var.set(value)
        self.entry.configure(
            fg=self._text_color,
            show=("•" if self._is_password and not self._show_password else ""),
        )
        if not value and self._placeholder and self.focus_get() != self.entry:
            self._apply_placeholder()
        if self._readonly:
            self.entry.configure(state="readonly")

    def set_border(self, color: str) -> None:
        self._border_color = color
        self._redraw()


class RoundedDropdown(tk.Canvas):
    """Dropdown pill bergaya modern dengan popup daftar pilihan."""

    def __init__(
        self,
        parent: tk.Widget,
        options: list[str],
        initial: str | None = None,
        width: int = 165,
        height: int = 38,
        radius: int = 10,
        parent_bg: str = COLORS["bg_white"],
        bold_text: bool = False,
        on_select: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._items = options
        self._value = initial if initial is not None else (options[0] if options else "")
        self._width = width
        self._height = height
        self._radius = radius
        self._bold_text = bold_text
        self._on_select = on_select
        self._hovered = False
        self._popup: tk.Toplevel | None = None

        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<Button-1>", self._toggle_popup)
        self.bind("<Configure>", self._on_resize)
        self._redraw()

    def _on_resize(self, event) -> None:
        self._width = max(80, event.width)
        self._height = max(28, event.height)
        self._redraw()

    def _set_hover(self, state: bool) -> None:
        self._hovered = state
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        fill = "#F8FAF9" if self._hovered else COLORS["bg_white"]
        draw_rounded_rect(
            self, 1, 1, self._width - 1, self._height - 1,
            r=self._radius, fill=fill, outline=COLORS["border_strong"], width=1,
        )
        fnt = font(10, "bold") if self._bold_text else font(10)
        self.create_text(
            14,
            self._height / 2,
            text=self._value,
            anchor="w",
            fill=COLORS["text_primary"],
            font=fnt,
        )
        # Chevron kecil ke bawah
        cx = self._width - 16
        cy = self._height / 2
        self.create_line(cx - 4, cy - 2, cx, cy + 2, cx + 4, cy - 2, fill=COLORS["text_muted"], width=1.5)

    def get(self) -> str:
        return self._value

    def set(self, value: str) -> None:
        self._value = value
        self._redraw()

    def _toggle_popup(self, _e=None) -> None:
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None
            return

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=COLORS["border_strong"], padx=1, pady=1)
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self._height + 4
        popup.geometry(f"{self._width}x{min(240, len(self._items) * 34 + 8)}+{x}+{y}")

        inner = tk.Frame(popup, bg=COLORS["bg_white"], pady=4)
        inner.pack(fill=tk.BOTH, expand=True)

        for opt in self._items:
            is_sel = opt == self._value
            lbl = tk.Label(
                inner,
                text=opt,
                anchor="w",
                padx=12,
                pady=6,
                bg=COLORS["bg_badge_green"] if is_sel else COLORS["bg_white"],
                fg=COLORS["primary"] if is_sel else COLORS["text_primary"],
                font=font(10, "bold") if is_sel else font(10),
                cursor="hand2",
            )
            lbl.pack(fill=tk.X)
            lbl.bind("<Enter>", lambda _e, w=lbl, sel=is_sel: w.configure(bg=COLORS["bg_soft_mint"] if not sel else COLORS["bg_badge_green"]))
            lbl.bind("<Leave>", lambda _e, w=lbl, sel=is_sel: w.configure(bg=COLORS["bg_badge_green"] if sel else COLORS["bg_white"]))
            lbl.bind("<Button-1>", lambda _e, v=opt: self._choose(v))

        popup.bind("<FocusOut>", lambda _e: self._close_popup())
        popup.focus_set()
        self._popup = popup

    def _close_popup(self) -> None:
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None

    def _choose(self, value: str) -> None:
        self._value = value
        self._close_popup()
        self._redraw()
        if self._on_select:
            self._on_select(value)


def draw_pill_badge(
    parent: tk.Widget,
    text: str,
    bg_color: str,
    fg_color: str,
    parent_bg: str = COLORS["bg_white"],
    width: int = 74,
    height: int = 24,
    radius: float | None = None,
) -> tk.Canvas:
    """Buat lencana pill sudut membulat untuk status/penjamin."""
    c = tk.Canvas(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, bd=0)
    r = radius if radius is not None else height / 2
    draw_rounded_rect(c, 0, 0, width, height, r=r, fill=bg_color, outline=bg_color)
    c.create_text(width / 2, height / 2, text=text, fill=fg_color, font=font(9, "bold"))
    return c


class KpiCard(tk.Canvas):
    """Kartu KPI ringkas dengan label atas, angka besar, dan keterangan samping."""

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: str,
        subtitle: str,
        pink: bool = False,
        height: int = 70,
        parent_bg: str = COLORS["bg_page"],
    ) -> None:
        super().__init__(parent, height=height, bg=parent_bg, highlightthickness=0, bd=0)
        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._pink = pink
        self._height = height
        self._width = 210
        self.bind("<Configure>", self._on_resize)

    def update_data(self, value: str, subtitle: str | None = None) -> None:
        self._value = value
        if subtitle is not None:
            self._subtitle = subtitle
        self._redraw()

    def _on_resize(self, event) -> None:
        self._width = max(120, event.width)
        self._height = max(60, event.height)
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        fill = COLORS["bg_pink"] if self._pink else COLORS["bg_white"]
        outline = COLORS["border_pink"] if self._pink else COLORS["border"]
        draw_rounded_rect(
            self, 1, 1, self._width - 1, self._height - 1,
            r=12, fill=fill, outline=outline, width=1,
        )
        self.create_text(
            16, 18,
            text=self._title,
            anchor="w",
            fill=COLORS["text_muted"],
            font=font(9),
        )
        val_id = self.create_text(
            16, self._height - 23,
            text=self._value,
            anchor="w",
            fill=COLORS["text_heading"],
            font=font(20, "bold"),
        )
        bbox = self.bbox(val_id)
        sub_x = (bbox[2] + 10) if bbox else 74
        self.create_text(
            sub_x, self._height - 20,
            text=self._subtitle,
            anchor="w",
            fill=COLORS["text_muted"],
            font=font(8),
        )


class TopBar(tk.Frame):
    """Header atas bersama dengan logo Heptamed, breadcrumb, tanggal, dan profil staf."""

    def __init__(
        self,
        parent: tk.Widget,
        breadcrumb_parts: list[tuple[str, Callable[[], None] | None]],
        date_text: str,
        staff_badge: str,
        staff_name: str,
        staff_role: str,
    ) -> None:
        super().__init__(parent, bg=COLORS["bg_white"], height=52)
        self.pack_propagate(False)

        inner = tk.Frame(self, bg=COLORS["bg_white"])
        inner.pack(fill=tk.BOTH, expand=True, padx=24)

        # Kiri: Logo + Heptamed Klinik
        logo_canvas = tk.Canvas(inner, width=136, height=38, bg=COLORS["bg_white"], highlightthickness=0, bd=0)
        logo_canvas.pack(side=tk.LEFT, pady=6)
        draw_heptamed_logo(logo_canvas, 2, 3, 30)
        logo_canvas.create_text(40, 10, text="Heptamed", anchor="w", fill=COLORS["text_heading"], font=font(10, "bold"))
        logo_canvas.create_text(40, 26, text="Klinik", anchor="w", fill=COLORS["text_heading"], font=font(10, "bold"))

        # Breadcrumb
        bc_frame = tk.Frame(inner, bg=COLORS["bg_white"])
        bc_frame.pack(side=tk.LEFT, padx=(18, 0))
        for idx, (label, cmd) in enumerate(breadcrumb_parts):
            if idx > 0:
                tk.Label(
                    bc_frame, text="/", bg=COLORS["bg_white"],
                    fg=COLORS["text_placeholder"], font=font(9),
                ).pack(side=tk.LEFT, padx=6)
            is_last = idx == len(breadcrumb_parts) - 1
            lbl = tk.Label(
                bc_frame,
                text=label,
                bg=COLORS["bg_white"],
                fg=COLORS["text_primary"] if is_last else COLORS["text_muted"],
                font=font(9, "bold") if is_last else font(9),
                cursor="hand2" if cmd else "arrow",
            )
            lbl.pack(side=tk.LEFT)
            if cmd:
                lbl.bind("<Button-1>", lambda _e, fn=cmd: fn())

        # Kanan: Tanggal | Badge STAF | Nama & Jabatan
        right_box = tk.Frame(inner, bg=COLORS["bg_white"])
        right_box.pack(side=tk.RIGHT, pady=8)

        tk.Label(
            right_box,
            text=date_text,
            bg=COLORS["bg_white"],
            fg=COLORS["text_muted"],
            font=font(9),
        ).pack(side=tk.LEFT, padx=(0, 18))

        tk.Frame(right_box, bg=COLORS["border"], width=1, height=26).pack(side=tk.LEFT, padx=(0, 18))

        staf_pill = draw_pill_badge(
            right_box, staff_badge, COLORS["bg_badge_green"], COLORS["primary"],
            parent_bg=COLORS["bg_white"], width=50, height=32, radius=8,
        )
        staf_pill.pack(side=tk.LEFT, padx=(0, 10))

        staff_text = tk.Frame(right_box, bg=COLORS["bg_white"])
        staff_text.pack(side=tk.LEFT)
        tk.Label(
            staff_text, text=staff_name, bg=COLORS["bg_white"],
            fg=COLORS["text_heading"], font=font(10, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            staff_text, text=staff_role, bg=COLORS["bg_white"],
            fg=COLORS["text_muted"], font=font(8), anchor="w",
        ).pack(anchor="w")

        # Garis batas bawah
        tk.Frame(self, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)


class BottomDock(tk.Canvas):
    """Dock navigasi mengambang berwarna hijau tua dan banner opsional SEDANG DILAYANI."""

    ITEMS = [
        ("registrasi", "Registrasi"),
        ("antrean", "Antrean"),
        ("data", "Data"),
        ("laporan", "Laporan"),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        active_route: str,
        on_navigate: Callable[[str], None],
        on_logout: Callable[[], None],
        serving_text: str = "",
    ) -> None:
        super().__init__(parent, height=62, bg=COLORS["bg_page"], highlightthickness=0, bd=0)
        self._active = active_route
        self._on_navigate = on_navigate
        self._on_logout = on_logout
        self._serving_text = serving_text
        self._width = 1024
        self._height = 62

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)
        self._hitboxes: list[tuple[float, float, float, float, str]] = []

    def set_serving_text(self, text: str) -> None:
        self._serving_text = text
        self._redraw()

    def _on_resize(self, event) -> None:
        self._width = max(400, event.width)
        self._height = max(58, event.height)
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        self._hitboxes.clear()
        w, h = self._width, self._height

        # Opsional banner pink "SEDANG DILAYANI" seperti di halaman Antrean poli
        if self._serving_text:
            mx = max(48, int(w * 0.10))
            draw_rounded_rect(
                self, mx, 4, w - mx, h - 4, r=12,
                fill=COLORS["bg_pink_bar"], outline=COLORS["border_pink"], width=1,
            )
            self.create_text(
                mx + 18, h / 2 - 9, text="SEDANG DILAYANI", anchor="w",
                fill=COLORS["text_pink_badge"], font=font(7, "bold"),
            )
            self.create_text(
                mx + 18, h / 2 + 8, text=self._serving_text, anchor="w",
                fill=COLORS["text_heading"], font=font(10, "bold"),
            )
            # Pill putih kanan
            pw, ph = 148, 28
            px2 = w - mx - 14
            px1 = px2 - pw
            py1 = h / 2 - ph / 2
            draw_rounded_rect(
                self, px1, py1, px2, py1 + ph, r=8,
                fill=COLORS["bg_white"], outline=COLORS["border_pink"], width=1,
            )
            self.create_text(
                (px1 + px2) / 2, h / 2,
                text="Pelayanan berlangsung",
                fill=COLORS["text_muted"],
                font=font(8),
            )

        # Dock pill utama + tombol logout bulat
        pill_w = 280
        pill_h = 46
        gap = 14
        logout_d = 46
        total_w = pill_w + gap + logout_d
        start_x = (w - total_w) / 2
        py = (h - pill_h) / 2

        draw_rounded_rect(
            self, start_x, py, start_x + pill_w, py + pill_h,
            r=pill_h / 2, fill=COLORS["dock_bg"], outline=COLORS["dock_bg"],
        )

        slot_w = (pill_w - 20) / 4
        for idx, (route, label) in enumerate(self.ITEMS):
            cx = start_x + 10 + slot_w * (idx + 0.5)
            cy = py + pill_h / 2
            if route == self._active:
                r_hi = 21
                self.create_oval(
                    cx - r_hi, cy - r_hi, cx + r_hi, cy + r_hi,
                    fill=COLORS["dock_active"], outline="",
                )
            draw_dock_icon(self, route, cx, cy - 8, color="#FFFFFF")
            self.create_text(
                cx, cy + 10, text=label, fill="#FFFFFF",
                font=font(7, "bold") if route == self._active else font(7),
            )
            self._hitboxes.append((cx - slot_w / 2, py, cx + slot_w / 2, py + pill_h, route))

        # Tombol bulat logout di kanan pill
        lx1 = start_x + pill_w + gap
        ly1 = py
        self.create_oval(
            lx1, ly1, lx1 + logout_d, ly1 + logout_d,
            fill=COLORS["dock_bg"], outline="",
        )
        draw_dock_icon(self, "logout", lx1 + logout_d / 2, ly1 + logout_d / 2, color="#FFFFFF")
        self._hitboxes.append((lx1, ly1, lx1 + logout_d, ly1 + logout_d, "__logout__"))

    def _on_click(self, event) -> None:
        for x1, y1, x2, y2, action in self._hitboxes:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if action == "__logout__":
                    self._on_logout()
                else:
                    self._on_navigate(action)
                return
