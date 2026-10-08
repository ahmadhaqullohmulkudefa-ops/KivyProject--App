# ==================================================
# IMPORT LIBRARY
# Bagian ini memuat library untuk navigasi, file, dan audio.
# ==================================================
import asyncio
import os
from pathlib import Path

import flet as ft
try:
    import flet_audio as fta
except ImportError:
    fta = None

from common import CYAN, MUTED, TopBar

# ==================================================
# MEMUAT LAYAR GAME
# Bagian ini menghubungkan setiap game dengan halaman utamanya.
# ==================================================
chess_import_error = None
try:
    from chessgame import ChessScreen
except ImportError as error:
    ChessScreen = None
    chess_import_error = error

hangman_import_error = None
try:
    from hangman import HangmanScreen
except ImportError as error:
    HangmanScreen = None
    hangman_import_error = error

minesweeper_import_error = None
try:
    from minesweeper import MinesweeperScreen
except ImportError as error:
    MinesweeperScreen = None
    minesweeper_import_error = error

maze_import_error = None
try:
    from mazegame import MazeScreen
except ImportError as error:
    MazeScreen = None
    maze_import_error = error

tictactoe_import_error = None
try:
    from tictactoe import TicScreen
except ImportError as error:
    TicScreen = None
    tictactoe_import_error = error


# ==================================================
# DAFTAR GAME
# Data ini dipakai untuk menampilkan dan membuka game dari menu.
# ==================================================
GAMES = (
    {
        "key": "chess",
        "title": "Chess",
        "symbol": "chess",
        "accent": "#39485D",
        "screen": ChessScreen,
        "error": chess_import_error,
    },
    {
        "key": "hangman",
        "title": "Hangman",
        "symbol": "hangman",
        "accent": "#246044",
        "screen": HangmanScreen,
        "error": hangman_import_error,
    },
    {
        "key": "minesweeper",
        "title": "Minesweeper",
        "symbol": "minesweeper",
        "accent": "#176A70",
        "screen": MinesweeperScreen,
        "error": minesweeper_import_error,
    },
    {
        "key": "maze",
        "title": "Maze",
        "symbol": "maze",
        "accent": "#70462D",
        "screen": MazeScreen,
        "error": maze_import_error,
    },
    {
        "key": "tictactoe",
        "title": "Tic Tac Toe",
        "symbol": "ttt",
        "accent": "#285CA8",
        "screen": TicScreen,
        "error": tictactoe_import_error,
    },
)


# ==================================================
# NAVIGASI APLIKASI
# Class ini mengatur perpindahan halaman dan menyimpan layar game.
# ==================================================
class FiveGamesRouter:
    def __init__(self, page):
        self.page = page
        self.screens = {}
        self.active_key = None
        self.active_screen = None
        self.games_by_key = {game["key"]: game for game in GAMES}
        assets_dir = Path(
            os.environ.get("FLET_ASSETS_DIR") or Path(__file__).parent / "assets"
        )
        music_dir = assets_dir / "music"
        self.music_paths = sorted(
            (path for path in music_dir.glob("opsi*.mp3") if path.stem[4:].isdigit()),
            key=lambda path: int(path.stem[4:]),
        )
        self.current_music = None
        self.music_muted = False
        self.music_error = None
        self.audio_state = None
        self.audio_loaded = False
        self.audio_load_event = None
        self.music_button = None
        self.audio = None

    def start(self):
        # Atur tampilan awal aplikasi dan siapkan layanan musik.
        self.page.title = "Five Games"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#090D17"
        self.page.padding = 0
        self.page.on_route_change = self._route_changed
        if fta is not None and self.music_paths:
            try:
                self.audio = fta.Audio(
                    src=f"music/{self.music_paths[0].name}",
                    release_mode=fta.ReleaseMode.LOOP,
                    on_loaded=self._on_audio_loaded,
                    on_state_change=self._on_audio_state_change,
                )
                self.page.services.append(self.audio)
            except Exception:
                self.audio = None
        self._show_route(self.page.route or "/")

    def navigate(self, route):
        self.page.navigate(route)

    def _route_changed(self, _event):
        self._show_route(self.page.route or "/")

    def _leave_active_screen(self):
        if self.active_screen is not None:
            on_leave = getattr(self.active_screen, "on_leave", None)
            if on_leave:
                on_leave()
        self.active_screen = None

    def _show_route(self, route):
        # Tampilkan menu atau game sesuai alamat halaman yang dipilih.
        key = route.strip("/")
        if not key:
            self._leave_active_screen()
            self.active_key = None
            self.page.clean()
            self.page.add(ft.SafeArea(content=self._build_menu(), expand=True))
            return

        game = self.games_by_key.get(key)
        if game is None:
            self.navigate("/")
            return
        if self.active_key == key and self.active_screen is not None:
            return

        self._leave_active_screen()
        self.page.clean()
        self.active_key = key

        screen = self.screens.get(key)
        if screen is None:
            if game["screen"] is None:
                self.page.add(
                    ft.SafeArea(content=self._build_import_error(game), expand=True)
                )
                return
            screen = game["screen"](self.page)
            self.screens[key] = screen
        else:
            on_enter = getattr(screen, "on_pre_enter", None)
            if on_enter is None:
                on_enter = getattr(screen, "on_enter", None)
            if on_enter:
                on_enter()
            if key == "maze":
                self.page.on_keyboard_event = screen._key

        self.active_screen = screen
        self.page.add(ft.SafeArea(content=screen, expand=True))

    def _build_menu(self):
        # Susun tombol game dan komponen utama pada halaman menu.
        icon_by_key = {
            "tictactoe": ft.Icons.GRID_3X3,
            "chess": None,
            "hangman": ft.Icons.PERSON_OUTLINE,
            "maze": ft.Icons.ALT_ROUTE,
            "minesweeper": ft.Icons.WARNING_AMBER,
        }
        cards = []
        game_order = ("tictactoe", "chess", "hangman", "maze", "minesweeper")
        for game in sorted(GAMES, key=lambda item: game_order.index(item["key"])):
            icon = icon_by_key[game["key"]]
            icon_control = (
                ft.Text("♟", size=29, color="#F5FAFF")
                if icon is None
                else ft.Icon(icon, size=27, color="#F5FAFF")
            )
            cards.append(
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=icon_control,
                                width=42,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(
                                game["title"].upper(),
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color="#F5FAFF",
                                expand=True,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(width=42),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=game["accent"],
                        color="#F5FAFF",
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=ft.Padding(14, 10, 14, 10),
                    ),
                    height=68,
                    on_click=lambda _event, key=game["key"]: self.navigate(f"/{key}"),
                )
            )

        self.music_button = ft.IconButton(
            icon=ft.Icons.MUSIC_OFF if self.music_muted else ft.Icons.MUSIC_NOTE,
            icon_color="#EAF5FF",
            bgcolor="#1A263A",
            icon_size=21,
            width=48,
            height=48,
            tooltip="Music",
            style=ft.ButtonStyle(shape=ft.CircleBorder()),
            on_click=self._show_music_menu,
        )
        menu = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        self.music_button,
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    height=52,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "FiveGames",
                            size=36,
                            weight=ft.FontWeight.BOLD,
                            color="#F4F8FF",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "5 GAMES",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=CYAN,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                ft.Container(height=20),
                ft.Column(controls=cards, spacing=10),
                ft.Container(expand=True),
                ft.Text(
                    "SELECT A GAME TO START",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        )
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        width=280,
                        height=280,
                        left=82,
                        top=-160,
                        shape=ft.BoxShape.CIRCLE,
                        border=ft.Border.all(1, "#17243A"),
                        ignore_interactions=True,
                    ),
                    ft.Container(
                        width=190,
                        height=190,
                        left=-116,
                        top=-108,
                        shape=ft.BoxShape.CIRCLE,
                        border=ft.Border.all(1, "#121E32"),
                        ignore_interactions=True,
                    ),
                    menu,
                ],
                expand=True,
            ),
            bgcolor="#090D17",
            padding=ft.Padding(20, 8, 20, 12),
            expand=True,
        )

    def _show_music_menu(self, _event=None):
        # Tampilkan pilihan lagu dan status audio dalam dialog.
        playlist = []
        for path in self.music_paths:
            number = int(path.stem[4:])
            selected = path == self.current_music
            playlist.append(
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if selected else ft.Icons.MUSIC_NOTE,
                                size=20,
                            ),
                            ft.Text(f"Opsi {number}", expand=True),
                        ],
                        spacing=12,
                    ),
                    height=44,
                    on_click=self._music_option_handler(path),
                )
            )

        if not playlist:
            playlist.append(ft.Text("Tidak ada playlist di assets/music/"))

        selected_number = (
            f"Opsi {int(self.current_music.stem[4:])}"
            if self.current_music is not None
            else "Belum ada lagu dipilih"
        )
        if (
            self.current_music is not None
            and fta is not None
            and self.audio_state == fta.AudioState.PLAYING
        ):
            selected_number += " sedang diputar"
        elif self.current_music is not None and self.audio_loaded:
            selected_number += " siap diputar"
        status_text = self.music_error or selected_number
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("BACKGROUND MUSIC", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text(status_text, color="#FF8B82" if self.music_error else MUTED),
                    ft.Column(
                        controls=playlist,
                        spacing=5,
                        height=min(430, max(44, len(playlist) * 49)),
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=10,
                tight=True,
            ),
            bgcolor="#111A29",
            actions=[
                ft.TextButton(
                    content="Unmute" if self.music_muted else "Mute",
                    on_click=self._toggle_music_mute,
                ),
                ft.TextButton(content="Close", on_click=self._close_music_menu),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)

    def _on_audio_loaded(self, _event=None):
        self.audio_loaded = True
        self.music_error = None
        if self.audio_load_event is not None:
            self.audio_load_event.set()

    def _on_audio_state_change(self, event):
        self.audio_state = event.state
        if event.state == fta.AudioState.PLAYING:
            self.music_error = None

    def _music_option_handler(self, path):
        # Buat handler async agar pemilihan lagu menunggu proses audio.
        async def select(_event):
            await self._select_music(path)

        return select

    async def _select_music(self, path):
        # Muat lagu pilihan, lalu mulai pemutaran dengan penanganan error.
        self.current_music = path
        self.music_muted = False
        self.music_error = None
        self._update_music_button()
        self._close_music_menu()
        self.page.update()
        if self.audio is not None:
            source = f"music/{path.name}"
            source_changed = self.audio.src != source
            if source_changed and self.audio_loaded:
                try:
                    await self.audio.pause()
                    await self.audio.release()
                except Exception:
                    pass
            if source_changed or not self.audio_loaded:
                self.audio_loaded = False
                self.audio_load_event = asyncio.Event()
            try:
                self.audio.src = source
                self.audio.volume = 1
                self.page.update(self.audio)
                if not self.audio_loaded and self.audio_load_event is not None:
                    await asyncio.wait_for(self.audio_load_event.wait(), timeout=30)
                await self.audio.play()
            except Exception as error:
                self.music_error = f"Audio gagal diputar: {error}"
                self.music_muted = True
                self._update_music_button()
                self._show_music_menu()
                self.page.update()

    async def _toggle_music_mute(self, _event=None):
        # Ubah status mute dan jalankan perintah audio yang sesuai.
        self.music_muted = not self.music_muted
        self._update_music_button()
        self._close_music_menu()
        self._show_music_menu()
        self.page.update()
        if self.audio is not None:
            try:
                if self.music_muted:
                    await self.audio.pause()
                elif self.current_music is not None:
                    await self.audio.resume()
            except Exception as error:
                self.music_error = f"Audio gagal diputar: {error}"
                self.page.update()

    def _close_music_menu(self, _event=None):
        self.page.pop_dialog()

    def _update_music_button(self):
        if self.music_button is not None:
            self.music_button.icon = (
                ft.Icons.MUSIC_OFF if self.music_muted else ft.Icons.MUSIC_NOTE
            )

    def _build_import_error(self, game):
        # Beri pesan jika suatu layar game gagal dimuat.
        return ft.Container(
            content=ft.Column(
                controls=[
                    TopBar(self.page, game["title"]),
                    ft.Text(
                        f"{game['title']} gagal dimuat.",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    ft.Text(str(game["error"]), color="#FF8B82", selectable=True),
                ],
                spacing=16,
                expand=True,
            ),
            bgcolor="#090D17",
            padding=20,
            expand=True,
        )


# ==================================================
# TITIK MASUK APLIKASI
# Fungsi ini mengatur ukuran jendela desktop dan memulai router.
# ==================================================
def main(page: ft.Page):
    if page.platform in (ft.PagePlatform.WINDOWS, ft.PagePlatform.LINUX, ft.PagePlatform.MACOS):
        page.window.width = 414
        page.window.height = 768
    FiveGamesRouter(page).start()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")