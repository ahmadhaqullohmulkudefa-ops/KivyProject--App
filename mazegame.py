# ==================================================
# IMPORT LIBRARY DAN ARAH LABIRIN
# Bagian ini menyiapkan pembuatan gambar, timer petunjuk, dan arah gerak.
# ==================================================
import asyncio
import base64
import random
from collections import deque

import flet as ft

from database import DatabaseManager
from common import BgScreen, TopBar, IconButton, ModernButton, info_popup, CYAN, MUTED

# arah: 0=atas 1=kanan 2=bawah 3=kiri
DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIFFS = [('SULIT', 15, 18)]


# ==================================================
# PEMBUATAN DAN PENYELESAIAN LABIRIN
# Generator membuat jalur, sedangkan BFS mencari rute untuk petunjuk.
# ==================================================
def gen_maze(rows, cols):
    """Generator labirin: recursive backtracker."""
    walls = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    vis = [[False] * cols for _ in range(rows)]
    st = [(0, 0)]
    vis[0][0] = True
    while st:
        r, c = st[-1]
        nb = []
        for di, (dr, dc) in enumerate(DIRS):
            rr, cc = r + dr, c + dc
            if 0 <= rr < rows and 0 <= cc < cols and not vis[rr][cc]:
                nb.append((rr, cc, di))
        if nb:
            rr, cc, di = random.choice(nb)
            walls[r][c][di] = False
            walls[rr][cc][(di + 2) % 4] = False
            vis[rr][cc] = True
            st.append((rr, cc))
        else:
            st.pop()
    return walls


def solve(walls, start, goal, rows, cols):
    """BFS: jalur terpendek (untuk tombol petunjuk)."""
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return []
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return []
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        r, c = cur
        for di, (dr, dc) in enumerate(DIRS):
            if not walls[r][c][di]:
                nxt = (r + dr, c + dc)
                if (
                    0 <= nxt[0] < rows
                    and 0 <= nxt[1] < cols
                    and nxt not in prev
                ):
                    prev[nxt] = cur
                    q.append(nxt)
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path if path and path[0] == start else []


# ==================================================
# PAPAN DAN PETUNJUK LABIRIN
# Class ini menggambar labirin serta menampilkan petunjuk sementara.
# ==================================================
class MazeBoard(ft.Image):
    def __init__(self, screen, width, height):
        self.screen = screen
        self.hint_path = []
        self.hint_generation = 0
        super().__init__(
            src="",
            width=width,
            height=height,
            fit=ft.BoxFit.CONTAIN,
            anti_alias=True,
        )
        self.redraw()

    def redraw(self):
        screen = self.screen
        if screen.walls is None:
            return
        rows, cols = screen.rows, screen.cols
        unit = 100
        wall_segments = []
        for row in range(rows):
            for column in range(cols):
                x, y = column * unit, row * unit
                cell_walls = screen.walls[row][column]
                if cell_walls[0]:
                    wall_segments.append(f"M{x} {y}h{unit}")
                if cell_walls[1]:
                    wall_segments.append(f"M{x + unit} {y}v{unit}")
                if cell_walls[2]:
                    wall_segments.append(f"M{x} {y + unit}h{unit}")
                if cell_walls[3]:
                    wall_segments.append(f"M{x} {y}v{unit}")

        goal_x, goal_y = (cols - 0.5) * unit, unit / 2
        player_row, player_column = screen.pos_
        player_x = (player_column + 0.5) * unit
        player_y = (player_row + 0.5) * unit
        hint = ""
        if self.hint_path:
            points = " ".join(
                f"{(column + 0.5) * unit},{(row + 0.5) * unit}"
                for row, column in self.hint_path
            )
            hint = (
                f'<polyline points="{points}" fill="none" stroke="#FFD34E" '
                'stroke-width="12" stroke-linecap="round" stroke-linejoin="round" '
                'stroke-dasharray="18 18" opacity="0.9"/>'
            )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cols * unit} {rows * unit}">'
            f'<rect width="{cols * unit}" height="{rows * unit}" fill="#111B29"/>'
            f'<path d="{" ".join(wall_segments)}" fill="none" stroke="#68A5B4" '
            'stroke-width="8" stroke-linecap="square"/>'
            f'<circle cx="{goal_x}" cy="{goal_y}" r="29" fill="#41C879"/>'
            f'{hint}'
            f'<circle cx="{player_x}" cy="{player_y}" r="29" fill="#FF9638"/>'
            f'<circle cx="{player_x}" cy="{player_y}" r="11" fill="#FFF8EB"/>'
            '</svg>'
        )
        self.src = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode("ascii")

    def show_hint(self, path):
        self.hint_generation += 1
        generation = self.hint_generation
        self.hint_path = path
        self.redraw()
        if self.screen.app_page:
            self.screen.app_page.run_task(self._hide_hint_after, generation, 2.5)

    async def _hide_hint_after(self, generation, seconds):
        await asyncio.sleep(seconds)
        if generation == self.hint_generation:
            self.hide_hint()

    def hide_hint(self, *_args):
        self.hint_generation += 1
        if self.hint_path:
            self.hint_path = []
            self.redraw()


class MazeScreen(BgScreen):
    # Layar ini mengatur level, posisi player, kontrol, dan penyimpanan kemajuan.
    def __init__(self, page, **kwargs):
        self.app_page = page
        self.db = DatabaseManager()
        self.di = 0
        self.level = 1
        self.highest_level = 1
        self.finished = False
        self.walls = None
        self.progress = self.db.get_maze_progress()
        self.level = int(self.progress.get("current_level") or 1)
        self.highest_level = int(self.progress.get("highest_level") or self.level)

        self.lbl_l = ft.Text("Level 1", color=CYAN, size=18, weight=ft.FontWeight.BOLD)
        self.status = ft.Text("Capai lingkaran hijau!", color=MUTED, weight=ft.FontWeight.BOLD)
        _, maze_cols, maze_rows = DIFFS[self.di]
        viewport_width = getattr(page, "width", None) or 414
        viewport_height = getattr(page, "height", None) or 768
        available_width = max(1, viewport_width - 48)
        available_height = max(180, viewport_height - 360)
        board_width = min(available_width, available_height * maze_cols / maze_rows)
        board_height = board_width * maze_rows / maze_cols
        self.board = MazeBoard(self, board_width, board_height)
        self.hint_btn = IconButton(
            sym="bulb",
            bg="#FFD166",
            fg="#49320B",
            width=50,
            height=50,
            on_click=lambda _event: self.hint(),
        )
        self.controls_row = ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Container(width=52), self._direction_button("up", 0),
                              ft.Container(width=52)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                ft.Row(
                    controls=[
                        self._direction_button("left", 3),
                        self._direction_button("down", 2),
                        self._direction_button("right", 1),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
            ],
            spacing=5,
        )
        self.controls_area = ft.Row(
            controls=[
                ft.Container(width=58),
                ft.Container(
                    content=self.controls_row,
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=self.hint_btn,
                    width=58,
                    alignment=ft.Alignment(0, 1),
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )
        self.board_slot = ft.Container(
            content=self.board,
            expand=True,
            alignment=ft.Alignment(0, 0),
            on_size_change=self._fit_board,
        )
        content = ft.Column(
            controls=[
                TopBar(page, "LABIRIN"),
                ft.Row(
                    controls=[self.lbl_l],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=46,
                ),
                self.board_slot,
                self.controls_area,
                ft.Container(content=self.status, alignment=ft.Alignment(0, 0)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=5,
            expand=True,
        )
        super().__init__(bg="#211E29", content=content, padding=12, **kwargs)
        if self.app_page:
            self.app_page.on_keyboard_event = self._key
        self.start()

    def _direction_button(self, symbol, direction):
        return IconButton(
            sym=symbol,
            width=52,
            height=52,
            on_click=lambda _event: self.move(direction),
        )

    def _fit_board(self, event):
        # Sesuaikan ukuran papan dengan ruang yang tersedia di layar HP.
        available_width = max(0, event.width)
        available_height = max(0, event.height)
        board_width = min(available_width, available_height * self.cols / self.rows)
        board_height = board_width * self.rows / self.cols
        if board_width <= 0 or board_height <= 0:
            return
        if self.board.width != board_width or self.board.height != board_height:
            self.board.width = board_width
            self.board.height = board_height
            try:
                board_page = self.board.page
            except RuntimeError:
                board_page = None
            if board_page:
                self.board.update()

    def on_enter(self):
        # Muat kembali kemajuan saat halaman Maze dibuka.
        self.progress = self.db.get_maze_progress()
        self.level = int(self.progress.get('current_level') or 1)
        self.highest_level = int(self.progress.get('highest_level') or self.level)
        self.start()

    def on_leave(self):
        # Simpan level terakhir dan lepaskan handler tombol keyboard.
        self.db.save_maze_progress(self.level, self.highest_level)
        if self.app_page:
            self.app_page.on_keyboard_event = None

    def _key(self, event):
        # Terjemahkan tombol panah keyboard menjadi arah gerak player.
        key = event.key.lower()
        directions = {
            "arrow up": 0, "arrowup": 0,
            "arrow right": 1, "arrowright": 1,
            "arrow down": 2, "arrowdown": 2,
            "arrow left": 3, "arrowleft": 3,
        }
        if key in directions:
            self.move(directions[key])

    def start(self):
        # Buat labirin untuk level aktif dan kembalikan player ke titik awal.
        _, cols, rows = DIFFS[self.di]
        self.cols, self.rows = cols, rows
        self.walls = gen_maze(rows, cols)
        self.pos_ = (rows - 1, 0)
        self.finished = False
        self.lbl_l.value = f"Level {self.level}"
        self.status.value = "Capai lingkaran hijau!"
        self.board.hide_hint()
        self.board.redraw()
        self._update_ui()

    def _update_ui(self):
        try:
            screen_page = self.page
        except RuntimeError:
            screen_page = None
        if screen_page:
            screen_page.update()

    def move(self, di):
        # Pindahkan player hanya jika sisi cell tidak terhalang dinding.
        if self.walls is None or self.finished:
            return
        r, c = self.pos_
        if self.walls[r][c][di]:
            return
        rr, cc = r + DIRS[di][0], c + DIRS[di][1]
        if 0 <= rr < self.rows and 0 <= cc < self.cols:
            self.pos_ = (rr, cc)
            self.board.hide_hint()
            self.board.redraw()
            if self.pos_ == (0, self.cols - 1):
                self.finished = True
                self.highest_level = max(self.highest_level, self.level + 1)
                self.db.save_maze_progress(self.level + 1, self.highest_level)
                self.level += 1
                self.lbl_l.value = f"Level {self.level}"
                info_popup(
                    self.app_page,
                    "SELESAI!",
                    f"Level selesai! Lanjut ke level {self.level}.",
                    on_ok=self.start,
                    btn="Lanjut",
                )

    def hint(self):
        # Hitung jalur ke tujuan dan tampilkan sebagai garis petunjuk sementara.
        if self.walls is None:
            return
        path = solve(self.walls, self.pos_, (0, self.cols - 1), self.rows, self.cols)
        self.board.show_hint(path)
        self.status.value = "Ikuti garis kuning!"
        if self.app_page:
            self.app_page.update()