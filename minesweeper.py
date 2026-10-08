# ==================================================
# IMPORT LIBRARY DAN KOMPONEN CELL
# Bagian ini menyiapkan timer async, angka acak, dan kotak papan.
# ==================================================
import asyncio
import random
from collections import deque

import flet as ft

from database import DatabaseManager
from common import BgScreen, DARKBTN, CYAN, MUTED, ORANGE, TopBar, ModernButton, info_popup


# ==================================================
# TAMPILAN MINESWEEPER
# Class cell meneruskan klik ke aturan permainan dan memperbarui warnanya.
# ==================================================
class MineCell(ft.Container):
    def __init__(self, game, row, col):
        self.game = game
        self.row_index = row
        self.column_index = col
        self.label = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF",
            text_align=ft.TextAlign.CENTER,
        )
        super().__init__(
            content=self.label,
            bgcolor="#1F344D",
            alignment=ft.Alignment(0, 0),
            padding=0,
            border_radius=5,
            on_click=self._pressed,
            ink=True,
        )

    def _pressed(self, _event=None):
        if self.game.flag_mode:
            self.game.toggle_flag(self.row_index, self.column_index)
        else:
            self.game.reveal(self.row_index, self.column_index)

    def set_visual(self, text, color, fill):
        self.label.value = text
        self.label.color = color
        self.bgcolor = fill


# Layar ini menyimpan papan, ranjau, tanda, status, dan statistik permainan.
class MinesweeperScreen(BgScreen):
    def __init__(self, page, **kwargs):
        self.app_page = page
        self.db = DatabaseManager()
        self.rows = 9
        self.mines = 10
        self.flag_mode = False
        self.finished = False
        self.showing_mines = False
        self.loss_generation = 0
        self.cells = []
        self.board = []
        self.revealed = []
        self.flags = set()
        self.counts = []
        self.stats = self.db.get_minesweeper_stats()

        self.mine_label = ft.Text("MINE: 10", color=CYAN, size=13, weight=ft.FontWeight.BOLD)
        self.flag_label = ft.Text("FLAG: 0", color="#FFFFFF", size=13, weight=ft.FontWeight.BOLD)
        self.streak_label = ft.Text(
            "WIN STREAK: 0\nBEST: 0",
            color="#FFFFFF",
            size=12,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.RIGHT,
        )
        self.status = ft.Text(
            "Buka semua cell yang aman",
            color="#F2F7FC",
            size=13,
            weight=ft.FontWeight.BOLD,
        )
        self.board_grid = ft.GridView(
            controls=[],
            runs_count=self.rows,
            spacing=3,
            run_spacing=3,
            child_aspect_ratio=1,
            expand=True,
        )
        self.flag_button = ModernButton(
            text="TANDAI FLAG",
            fill="#194D6B",
            color="#FFFFFF",
            bold=True,
            expand=True,
            height=46,
            on_click=lambda _event: self.toggle_flag_mode(),
        )
        restart = ModernButton(
            text="RESTART",
            fill=ORANGE,
            color="#17130D",
            bold=True,
            expand=True,
            height=46,
            on_click=lambda _event: self.new_game(),
        )
        viewport_width = getattr(page, "width", None) or 430
        viewport_height = getattr(page, "height", None) or 768
        board_size = min(540, max(0, viewport_width - 20), max(0, viewport_height - 220))
        self.board_frame = ft.Container(
            content=self.board_grid,
            width=board_size,
            height=board_size,
        )
        self.board_slot = ft.Container(
            content=self.board_frame,
            expand=True,
            alignment=ft.Alignment(0, 0),
            on_size_change=self._fit_board,
        )
        content = ft.Column(
            controls=[
                TopBar(page, "MINESWEEPER", on_refresh=self.new_game),
                ft.Row(
                    controls=[self.mine_label, self.flag_label, self.streak_label],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=42,
                ),
                self.status,
                self.board_slot,
                ft.Row(controls=[self.flag_button, restart], spacing=8),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            expand=True,
        )
        super().__init__(bg="#090D17", content=content, padding=10, **kwargs)
        self.new_game()

    def _fit_board(self, event):
        board_size = min(event.width, event.height, 540)
        if board_size <= 0:
            return
        if self.board_frame.width != board_size or self.board_frame.height != board_size:
            self.board_frame.width = board_size
            self.board_frame.height = board_size
            try:
                board_page = self.board_frame.page
            except RuntimeError:
                board_page = None
            if board_page:
                self.board_frame.update()

    def _go_menu(self):
        if hasattr(self.app_page, "navigate"):
            self.app_page.navigate("/")

    def on_enter(self):
        self.stats = self.db.get_minesweeper_stats()
        self._update_streak_label()
        self.new_game()

    def _update_streak_label(self):
        self.streak_label.value = (
            f"WIN STREAK: {self.stats.get('current_streak', 0)}\n"
            f"BEST: {self.stats.get('best_streak', 0)}"
        )

    def new_game(self, *_):
        # Naikkan generasi timer, buat papan baru, lalu tampilkan semua cell tertutup.
        self.loss_generation += 1
        self.flag_mode = False
        self.flag_button.text = "TANDAI FLAG"
        self.flag_button.content.value = "TANDAI FLAG"
        self.finished = False
        self.showing_mines = False
        self.status.value = "Buka semua cell yang aman"
        self.flags = set()
        self.revealed = [[False] * self.rows for _ in range(self.rows)]
        self.board = [[False] * self.rows for _ in range(self.rows)]
        for row, col in random.sample([(r, c) for r in range(self.rows) for c in range(self.rows)], self.mines):
            self.board[row][col] = True
        self.counts = [[self._nearby_mines(r, c) for c in range(self.rows)] for r in range(self.rows)]
        self._build_board()
        self._refresh()
        try:
            game_page = self.page
        except RuntimeError:
            game_page = None
        if game_page:
            self.update()

    def _nearby_mines(self, row, col):
        return sum(self.board[nr][nc]
                   for nr in range(max(0, row - 1), min(self.rows, row + 2))
                   for nc in range(max(0, col - 1), min(self.rows, col + 2))
                   if (nr, nc) != (row, col))

    def _build_board(self):
        self.cells = []
        for row in range(self.rows):
            for col in range(self.rows):
                cell = MineCell(self, row, col)
                self.cells.append(cell)
        self.board_grid.controls = self.cells

    def _cell(self, row, col):
        return self.cells[row * self.rows + col]

    def _refresh(self):
        # Samakan tulisan dan warna setiap kotak dengan kondisi permainan saat ini.
        self.mine_label.value = f"MINE: {self.mines - len(self.flags)}"
        self.flag_label.value = f"FLAG: {len(self.flags)}"
        for row in range(self.rows):
            for col in range(self.rows):
                cell = self._cell(row, col)
                if self.showing_mines and self.board[row][col]:
                    cell.set_visual("*", "#FFFFFF", "#C62828")
                elif (row, col) in self.flags:
                    cell.set_visual("F", "#FFD166", "#593D14")
                elif self.revealed[row][col]:
                    text = "*" if self.board[row][col] else (
                        str(self.counts[row][col]) if self.counts[row][col] else ""
                    )
                    color = "#FF655C" if self.board[row][col] else "#13202D"
                    fill = "#8C2529" if self.board[row][col] else "#849EAF"
                    cell.set_visual(text, color, fill)
                else:
                    cell.set_visual("", "#FFFFFF", "#1F344D")

    def reveal(self, row, col):
        # Buka cell aman atau tampilkan semua ranjau sebelum memulai timer kalah.
        if self.finished or self.showing_mines or (row, col) in self.flags or self.revealed[row][col]:
            return
        if self.board[row][col]:
            self.showing_mines = True
            self._refresh()
            self.status.value = "RANJAU TERDETEKSI"
            generation = self.loss_generation
            if self.app_page:
                self.app_page.update()
                self.app_page.run_task(self._finish_loss_after_delay, generation)
            return
        queue = deque([(row, col)])
        while queue:
            current = queue.popleft()
            cr, cc = current
            if self.revealed[cr][cc] or current in self.flags:
                continue
            self.revealed[cr][cc] = True
            if self.counts[cr][cc] == 0:
                for nr in range(max(0, cr - 1), min(self.rows, cr + 2)):
                    for nc in range(max(0, cc - 1), min(self.rows, cc + 2)):
                        if not self.revealed[nr][nc] and not self.board[nr][nc]:
                            queue.append((nr, nc))
        self._refresh()
        if all(self.board[row][col] or self.revealed[row][col] for row in range(self.rows) for col in range(self.rows)):
            self._finish(True)

    def toggle_flag(self, row, col):
        if self.finished or self.showing_mines or self.revealed[row][col]:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        elif len(self.flags) < self.mines:
            self.flags.add((row, col))
        self._refresh()

    def toggle_flag_mode(self):
        if self.finished or self.showing_mines:
            return
        self.flag_mode = not self.flag_mode
        label = "BUKA CELL" if self.flag_mode else "TANDAI FLAG"
        self.flag_button.text = label
        self.flag_button.content.value = label

    async def _finish_loss_after_delay(self, generation):
        # Tunggu tanpa membekukan UI; abaikan timer dari ronde yang sudah di-reset.
        await asyncio.sleep(2)
        if generation != self.loss_generation or self.finished or not self.showing_mines:
            return
        self._finish(False)
        if self.app_page:
            self.app_page.update()

    def _finish(self, won):
        # Simpan hasil permainan dan tampilkan dialog kemenangan atau kekalahan.
        if self.finished:
            return
        self.finished = True
        if won:
            self.db.record_minesweeper_win()
            self.stats = self.db.get_minesweeper_stats()
            self._update_streak_label()
            self.status.value = "MENANG! Semua mine berhasil dihindari."
            info_popup(
                self.app_page,
                "MENANG!",
                "Papan berhasil diselesaikan.",
                on_ok=self.new_game,
                btn="Main lagi",
            )
        else:
            self.db.record_minesweeper_loss()
            self.stats = self.db.get_minesweeper_stats()
            self._update_streak_label()
            for row in range(self.rows):
                for col in range(self.rows):
                    if self.board[row][col]:
                        self.revealed[row][col] = True
            self._refresh()
            self.status.value = "GAME OVER"
            info_popup(
                self.app_page,
                "GAME OVER",
                "Kamu membuka cell berisi mine.",
                on_ok=self.new_game,
                btn="Coba lagi",
            )
