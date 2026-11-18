"""Entry point aplikasi desktop GUI Python (Tkinter & ttk)."""

from src.app import App


def main() -> None:
    """Inisialisasi dan jalankan loop utama aplikasi."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
