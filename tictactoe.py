# ==================================================
# IMPORT LIBRARY DAN ATURAN PERMAINAN
# Bagian ini menyiapkan pilihan acak, jeda animasi, dan aturan papan.
# ==================================================
import random

import asyncio
import flet as ft

from common import BgScreen, TopBar, ModernButton, info_popup, DARKBTN, SURFACE, MUTED, CYAN

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


# ==================================================
# PEMERIKSA HASIL DAN STRATEGI BOT
# Fungsi ini memeriksa pemenang dan mencari langkah terbaik bot.
# ==================================================
def winner(b):
    for x, y, z in LINES:
        if b[x] and b[x] == b[y] == b[z]:
            return b[x]
    if all(v is not None for v in b):
        return 'D'
    return None


def minimax(b, ai):
    w = winner(b)
    if w == 'O':
        return 1, None
    if w == 'X':
        return -1, None
    if w == 'D':
        return 0, None
    best = -2 if ai else 2
    bm = None
    for i in range(9):
        if b[i] is None:
            b[i] = 'O' if ai else 'X'
            s, _ = minimax(b, not ai)
            b[i] = None
            if (ai and s > best) or (not ai and s < best):
                best, bm = s, i
    return best, bm


class TTTBoard(ft.GridView):
    # Papan ini menggambar sembilan kotak dan meneruskan aksi sentuh.
    def __init__(self, game):
        self.game = game
        self.selected = -1
        self.pulse = 0
        self.scales = [1] * 9
        super().__init__(
            controls=self._cells(),
            runs_count=3,
            spacing=8,
            run_spacing=8,
            child_aspect_ratio=1,
        )

    def _cells(self):
        cells = []
        for index, mark in enumerate(self.game.b):
            selected = index == self.selected
            fill = "#183746" if selected else "#111B29"
            border_color = "#41BFD1" if selected else "#35485E"
            mark_color = CYAN if mark == "X" else "#FF7168"
            cells.append(
                ft.Container(
                    content=ft.Text(
                        mark or "",
                        size=self.game.cell_font_size,
                        weight=ft.FontWeight.BOLD,
                        color=mark_color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=fill,
                    border=ft.Border.all(2, border_color),
                    border_radius=14,
                    alignment=ft.Alignment(0, 0),
                    padding=0,
                    scale=ft.Scale(scale=self.scales[index]),
                    animate_scale=ft.Animation(
                        duration=200,
                        curve=ft.AnimationCurve.EASE_OUT_BACK,
                    ),
                    on_click=lambda _event, cell=index: self._tap(cell),
                    ink=True,
                )
            )
        return cells

    def _tap(self, index):
        if not self.game.locked and self.game.b[index] is None:
            self.selected = index
            self.pulse = 1
            self.redraw()
        self.game.player_move(index)

    def redraw(self):
        self.controls = self._cells()

    def animate_move(self, index):
        self.scales[index] = 0.72
        self.redraw()
        if self.game.app_page:
            self.game.app_page.run_task(self._restore_scale, index)
        else:
            self.scales[index] = 1
            self.redraw()

    async def _restore_scale(self, index):
        # Kembalikan ukuran kotak setelah animasi langkah selesai.
        await asyncio.sleep(0.03)
        self.scales[index] = 1
        self.redraw()
        self.game.app_page.update()

    def animate_winner(self, cells):
        self.selected = -1
        self.pulse = 0
        if self.game.app_page:
            self.game.app_page.run_task(self._pulse_winner, list(cells))

    async def _pulse_winner(self, cells):
        # Sorot kotak pemenang satu per satu dengan animasi singkat.
        for index in cells:
            self.selected = index
            self.pulse = 1
            self.redraw()
            self.game.app_page.update()
            await asyncio.sleep(0.16)
            self.pulse = 0
            self.redraw()
            self.game.app_page.update()
            await asyncio.sleep(0.12)
        self.selected = -1
        self.redraw()
        self.game.app_page.update()


class TicScreen(BgScreen):
    # Layar ini mengatur langkah player, giliran bot, dan skor permainan.
    def __init__(self, page, **kwargs):
        self.app_page = page
        self.b = [None] * 9
        self.sk = 0
        self.sb = 0
        self.locked = False
        self.gen = 0

        self.lbl_k = ft.Text("KAMU 0", weight=ft.FontWeight.BOLD, color=CYAN, size=16)
        self.lbl_v = ft.Text("VS", weight=ft.FontWeight.BOLD, color=MUTED)
        self.lbl_b = ft.Text("BOT 0", weight=ft.FontWeight.BOLD, color="#FF7168", size=16)
        self.cell_font_size = 58
        self.board = TTTBoard(self)
        self.status = ft.Text(
            "Giliranmu (X)",
            color="#FFFFFF",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        viewport_width = getattr(page, "width", None) or 430
        viewport_height = getattr(page, "height", None) or 768
        board_size = min(480, max(0, viewport_width - 40), max(0, viewport_height - 260))
        self.board_frame = ft.Container(
            content=self.board,
            width=board_size,
            height=board_size,
            padding=8,
            bgcolor="#0B111C",
            border_radius=18,
        )
        self.board_slot = ft.Container(
            content=self.board_frame,
            expand=True,
            alignment=ft.Alignment(0, 0),
            on_size_change=self._fit_board,
        )
        content = ft.Column(
            controls=[
                TopBar(page, "TIC TAC TOE", on_refresh=lambda _event: self.new_game()),
                ft.Row(
                    controls=[self.lbl_k, self.lbl_v, self.lbl_b],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    height=48,
                ),
                self.board_slot,
                self.status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            expand=True,
        )
        super().__init__(bg="#090D17", content=content, padding=12, **kwargs)

    def _fit_board(self, event):
        board_size = min(event.width, event.height, 480)
        if board_size <= 0:
            return
        if self.board_frame.width != board_size or self.board_frame.height != board_size:
            self.board_frame.width = board_size
            self.board_frame.height = board_size
            self.cell_font_size = max(36, min(58, (board_size - 16) * 0.16))
            self.board.redraw()
            try:
                board_page = self.board_frame.page
            except RuntimeError:
                board_page = None
            if board_page:
                self.board_frame.update()

    def on_enter(self):
        self.new_game()

    def new_game(self):
        # Bersihkan papan dan batalkan hasil dari giliran sebelumnya.
        self.gen += 1
        self.b = [None] * 9
        self.locked = False
        self.status.value = "Giliranmu (X)"
        self.board.selected = -1
        self.board.pulse = 0
        self.board.scales = [1] * 9
        self.board.redraw()
        if self.app_page:
            self.app_page.update()

    def player_move(self, i):
        # Catat pilihan player, periksa hasil, lalu jadwalkan giliran bot.
        if self.locked or self.b[i] is not None:
            return
        self.b[i] = 'X'
        self.board.animate_move(i)
        self.board.redraw()
        w = winner(self.b)
        if w:
            self._end(w)
            return
        self.locked = True
        self.status.value = "Bot berpikir..."
        if self.app_page:
            self.app_page.update()
            self.app_page.run_task(self._delayed_bot_move, self.gen)

    async def _delayed_bot_move(self, generation):
        # Beri jeda animasi sebelum bot memilih langkahnya.
        await asyncio.sleep(0.55)
        self.bot_move(generation)

    def bot_move(self, g):
        # Pilih langkah kosong dengan minimax dan perbarui papan permainan.
        if g != self.gen:
            return
        empty = [i for i in range(9) if self.b[i] is None]
        if not empty:
            return
        _, i = minimax(self.b, True)
        if i is None or self.b[i] is not None:
            i = random.choice(empty)
        self.b[i] = 'O'
        self.board.animate_move(i)
        self.board.redraw()
        w = winner(self.b)
        if w:
            self._end(w)
            return
        self.locked = False
        self.status.value = "Giliranmu (X)"
        if self.app_page:
            self.app_page.update()

    def _end(self, w):
        # Kunci papan, perbarui skor, dan jadwalkan dialog hasil.
        self.locked = True
        if w == 'X':
            self.sk += 1; title, message, button, status = 'MENANG!', 'Selamat, kamu menang!', 'Main lagi', 'Kamu menang!'
        elif w == 'O':
            self.sb += 1; title, message, button, status = 'KALAH', 'Bot menang.', 'Coba lagi', 'Bot menang.'
        else:
            title, message, button, status = 'SERI', 'Permainan seri.', 'Main lagi', 'Seri.'
        self.status.value = status
        self.lbl_k.value = f"KAMU {self.sk}"
        self.lbl_b.value = f"BOT {self.sb}"
        if w in ('X', 'O'):
            winning_cells = next(line for line in LINES if all(self.b[index] == w for index in line))
            self.board.animate_winner(winning_cells)
        if self.app_page:
            self.app_page.update()
            self.app_page.run_task(self._delayed_result_dialog, title, message, button)

    async def _delayed_result_dialog(self, title, message, button):
        # Tampilkan dialog setelah animasi hasil selesai.
        await asyncio.sleep(0.62)
        info_popup(
            self.app_page,
            title,
            message,
            on_ok=self.new_game,
            btn=button,
        )