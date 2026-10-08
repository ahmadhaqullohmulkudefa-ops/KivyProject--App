# ==================================================
# IMPORT LIBRARY DAN WARNA
# Bagian ini menyiapkan Flet serta warna bersama untuk semua layar.
# ==================================================
import flet as ft

ORANGE = "#FF8C1F"
DARKBTN = "#383843"
BG = "#090D17"
SURFACE = "#131A29"
MUTED = "#C2D0E6"
CYAN = "#40D1E6"


# ==================================================
# HELPER WARNA
# Fungsi ini mengubah nilai warna ke format yang dapat dipakai Flet.
# ==================================================
def color_value(value):
    if isinstance(value, str):
        return value
    channels = [round(max(0, min(1, channel)) * 255) for channel in value[:3]]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


# ==================================================
# KOMPONEN TAMPILAN BERSAMA
# Class berikut menyediakan latar, tombol, ikon, dan bilah judul.
# ==================================================
class BgScreen(ft.Container):
    """Full-page Flet surface shared by game screens."""
    def __init__(self, bg=BG, content=None, **kwargs):
        kwargs.setdefault("padding", 0)
        kwargs.setdefault("expand", True)
        super().__init__(
            content=content,
            bgcolor=color_value(bg),
            **kwargs,
        )


# Tombol ini menjaga bentuk dan warna tetap seragam serta dapat diubah.
class ModernButton(ft.Button):
    def __init__(self, text="", fill=DARKBTN, color="#FFFFFF", bold=False,
                 font_size=16, on_click=None, button_padding=12, **kwargs):
        self._fill = color_value(fill)
        self._button_color = color_value(color)
        self._button_padding = button_padding
        self.text = text
        super().__init__(
            content=ft.Text(text, weight=ft.FontWeight.BOLD if bold else None,
                            size=font_size),
            style=self._button_style(),
            on_click=on_click,
            **kwargs,
        )
        self._button_ready = True

    @property
    def fill(self):
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = color_value(value)
        if getattr(self, "_button_ready", False):
            self.style = self._button_style()

    def _button_style(self):
        return ft.ButtonStyle(
            bgcolor=self._fill,
            color=self._button_color,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=self._button_padding,
        )

    def set_fill(self, fill):
        self.fill = fill


# Ikon dan kartu ini dipakai untuk mewakili pilihan game di menu.
class GameIcon(ft.Container):
    def __init__(self, kind="ttt", accent=CYAN, **kwargs):
        symbols = {"ttt": "X", "chess": "♟", "hangman": "?",
                   "maze": "+", "minesweeper": "*"}
        super().__init__(
            content=ft.Text(symbols.get(kind, "•"), size=22,
                            weight=ft.FontWeight.BOLD, color="#F5FAFF"),
            bgcolor=color_value(accent),
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            width=34,
            height=34,
            **kwargs,
        )


class ModernGameCard(ft.Button):
    def __init__(self, title, accent=CYAN, icon="ttt", **kwargs):
        self.title = title
        self.accent = color_value(accent)
        self.icon_kind = icon
        super().__init__(
            content=ft.Row(
                controls=[GameIcon(kind=icon, accent=accent),
                          ft.Text(title, size=16, weight=ft.FontWeight.BOLD,
                                  color="#F5FAFF", expand=True)],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=self.accent,
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=12,
            ),
            **kwargs,
        )


class GameCard(ModernGameCard):
    def __init__(self, title, subtitle=None, accent="#1F4D93", symbol=">", **kwargs):
        icon_map = {"X": "ttt", "♟": "chess", "?": "hangman",
                    "+": "maze", "*": "minesweeper"}
        kind = icon_map.get(symbol, symbol if symbol in icon_map.values() else "ttt")
        super().__init__(title=title, accent=accent, icon=kind, **kwargs)


# Tombol ikon ini menyatukan simbol, warna, dan petunjuk tombol.
class IconButton(ft.IconButton):
    def __init__(self, sym="back", bg="#1F2E47", fg="#C7EAF2",
                 on_click=None, **kwargs):
        icons = {
            "back": ft.Icons.ARROW_BACK,
            "refresh": ft.Icons.REFRESH,
            "bulb": ft.Icons.LIGHTBULB_OUTLINE,
            "music_on": ft.Icons.MUSIC_NOTE,
            "music_off": ft.Icons.MUSIC_OFF,
            "up": ft.Icons.KEYBOARD_ARROW_UP,
            "down": ft.Icons.KEYBOARD_ARROW_DOWN,
            "left": ft.Icons.KEYBOARD_ARROW_LEFT,
            "right": ft.Icons.KEYBOARD_ARROW_RIGHT,
        }
        self.sym = sym
        self.bgc = color_value(bg)
        self.fgc = color_value(fg)
        super().__init__(
            icon=icons.get(sym, ft.Icons.CIRCLE),
            icon_color=self.fgc,
            bgcolor=self.bgc,
            on_click=on_click,
            tooltip=sym.replace("_", " ").title(),
            **kwargs,
        )


# Bilah atas menampilkan judul serta tombol kembali atau muat ulang.
class TopBar(ft.Row):
    """Flet game header with back and optional reset controls."""
    def __init__(self, page, title="", on_refresh=None, on_back=None, **kwargs):
        self.app_page = page
        self.on_back = on_back
        controls = [
            IconButton(sym="back", on_click=lambda _event: self.go_menu()),
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF",
                    expand=True, text_align=ft.TextAlign.CENTER),
        ]
        if on_refresh:
            controls.append(IconButton(sym="refresh", on_click=on_refresh))
        else:
            controls.append(ft.Container(width=40))
        super().__init__(
            controls=controls,
            height=54,
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            **kwargs,
        )

    def go_menu(self):
        if self.on_back:
            self.on_back()
        elif hasattr(self.app_page, "navigate"):
            self.app_page.navigate("/")


# Komponen hati disediakan untuk game yang masih memakai nyawa.
class Hearts(ft.Row):
    """Row of heart icons for game screens that still use life counts."""
    def __init__(self, n=3, total=3, **kwargs):
        self._n = n
        self._total = total
        super().__init__(spacing=2, controls=self._hearts(), **kwargs)

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        self._n = value
        self.refresh()

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value
        self.refresh()

    def _hearts(self):
        return [
            ft.Icon(ft.Icons.FAVORITE, size=22,
                    color="#E62D46" if index < self.n else "#595D67")
            for index in range(self.total)
        ]

    def refresh(self):
        self.controls = self._hearts()
        try:
            page = self.page
        except RuntimeError:
            page = None
        if page:
            self.update()


# ==================================================
# DIALOG INFORMASI
# Helper ini menampilkan pesan dan menjalankan aksi setelah dialog ditutup.
# ==================================================
def info_popup(page, title, msg, on_ok=None, btn="OK"):
    """Display a Flet dialog and run its action after dismissal."""
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        content=ft.Text(msg, color="#EAF1FA"),
        bgcolor="#141B2A",
        actions=[
            ft.TextButton(
                content=btn,
                on_click=lambda _event: _close_dialog(page, on_ok),
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialog)
    return dialog


def _close_dialog(page, on_ok):
    page.pop_dialog()
    if on_ok:
        on_ok()