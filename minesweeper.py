import random
from collections import deque

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from database import DatabaseManager
from common import BgScreen, DARKBTN, CYAN, MUTED, ORANGE, TopBar, ModernButton, info_popup


class MineCell(ModernButton):
    def __init__(self, game, row, col, **kwargs):
        super().__init__(fill=(0.12, 0.2, 0.3, 1), **kwargs)
        self.game = game
        self.row = row
        self.col = col
        self.font_size = dp(14)
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.bind(on_press=self._pressed)

    def _pressed(self, *_):
        if self.game.flag_mode:
            self.game.toggle_flag(self.row, self.col)
        else:
            self.game.reveal(self.row, self.col)


class MinesweeperScreen(BgScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(bg=(0.035, 0.05, 0.09, 1), **kwargs)
        self.sm = sm
        self.db = DatabaseManager()
        self.rows = 9
        self.mines = 10
        self.flag_mode = False
        self.finished = False
        self.cells = []
        self.board = []
        self.revealed = []
        self.flags = set()
        self.counts = []
        self.stats = self.db.get_minesweeper_stats()

        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(8)], spacing=dp(8))
        root.add_widget(TopBar(sm, 'MINESWEEPER', on_refresh=self.new_game))

        info = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.mine_label = Label(text='MINE: 10', color=CYAN, bold=True, font_size=dp(13))
        self.flag_label = Label(text='FLAG: 0', color=(1, 1, 1, 1), bold=True, font_size=dp(13))
        self.streak_label = Label(text='WIN STREAK: 0\nBEST: 0', color=(1, 1, 1, 1),
                                 bold=True, font_size=dp(12), size_hint_x=None)
        info.add_widget(self.mine_label)
        info.add_widget(self.flag_label)
        info.add_widget(self.streak_label)
        root.add_widget(info)

        self.status = Label(text='Buka semua cell yang aman', color=(0.95, 0.98, 1, 1), bold=True,
                            font_size=dp(12), size_hint_y=None, height=dp(24))
        root.add_widget(self.status)

        self.board_grid = GridLayout(cols=self.rows, spacing=dp(2), padding=dp(3),
                                     size_hint=(1, 1), minimum_size=(dp(250), dp(250)))
        root.add_widget(self.board_grid)

        controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.flag_button = ModernButton(text='TANDAI FLAG', fill=(0.1, 0.3, 0.42, 1),
                                        color=(1, 1, 1, 1), bold=True)
        self.flag_button.bind(on_press=lambda *_: self.toggle_flag_mode())
        restart = ModernButton(text='RESTART', fill=ORANGE, color=(0.08, 0.1, 0.15, 1), bold=True)
        restart.bind(on_press=lambda *_: self.new_game())
        controls.add_widget(self.flag_button)
        controls.add_widget(restart)
        root.add_widget(controls)
        self.add_widget(root)

    def _go_menu(self):
        self.sm.transition.direction = 'right'
        self.sm.current = 'menu'

    def on_enter(self):
        self.stats = self.db.get_minesweeper_stats()
        self._update_streak_label()
        self.new_game()

    def _update_streak_label(self):
        self.streak_label.text = f"WIN STREAK: {self.stats.get('current_streak', 0)}\nBEST: {self.stats.get('best_streak', 0)}"

    def new_game(self, *_):
        self.flag_mode = False
        self.flag_button.text = 'TANDAI FLAG'
        self.finished = False
        self.flags = set()
        self.revealed = [[False] * self.rows for _ in range(self.rows)]
        self.board = [[False] * self.rows for _ in range(self.rows)]
        for row, col in random.sample([(r, c) for r in range(self.rows) for c in range(self.rows)], self.mines):
            self.board[row][col] = True
        self.counts = [[self._nearby_mines(r, c) for c in range(self.rows)] for r in range(self.rows)]
        self._build_board()
        self._refresh()

    def _nearby_mines(self, row, col):
        return sum(self.board[nr][nc]
                   for nr in range(max(0, row - 1), min(self.rows, row + 2))
                   for nc in range(max(0, col - 1), min(self.rows, col + 2))
                   if (nr, nc) != (row, col))

    def _build_board(self):
        self.board_grid.clear_widgets()
        self.board_grid.cols = self.rows
        self.cells = []
        for row in range(self.rows):
            for col in range(self.rows):
                cell = MineCell(self, row, col, text='')
                self.cells.append(cell)
                self.board_grid.add_widget(cell)

    def _cell(self, row, col):
        return self.cells[row * self.rows + col]

    def _refresh(self):
        self.mine_label.text = f'MINE: {self.mines - len(self.flags)}'
        self.flag_label.text = f'FLAG: {len(self.flags)}'
        for row in range(self.rows):
            for col in range(self.rows):
                cell = self._cell(row, col)
                if (row, col) in self.flags:
                    cell.text = 'F'
                    cell.color = (1, 0.82, 0.25, 1)
                    cell.fill = (0.35, 0.22, 0.08, 1)
                elif self.revealed[row][col]:
                    cell.text = '*' if self.board[row][col] else (str(self.counts[row][col]) if self.counts[row][col] else '')
                    cell.color = (1, 0.35, 0.3, 1) if self.board[row][col] else (0.08, 0.12, 0.18, 1)
                    cell.fill = (0.55, 0.12, 0.14, 1) if self.board[row][col] else (0.52, 0.62, 0.7, 1)
                else:
                    cell.text = ''
                    cell.color = (1, 1, 1, 1)
                    cell.fill = (0.12, 0.2, 0.3, 1)
                cell._redraw()

    def reveal(self, row, col):
        if self.finished or (row, col) in self.flags or self.revealed[row][col]:
            return
        if self.board[row][col]:
            self.revealed[row][col] = True
            self._refresh()
            self._finish(False)
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
        if self.finished or self.revealed[row][col]:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        elif len(self.flags) < self.mines:
            self.flags.add((row, col))
        self._refresh()

    def toggle_flag_mode(self):
        if self.finished:
            return
        self.flag_mode = not self.flag_mode
        self.flag_button.text = 'BUKA CELL' if self.flag_mode else 'TANDAI FLAG'

    def _finish(self, won):
        self.finished = True
        if won:
            self.db.record_minesweeper_win()
            self.stats = self.db.get_minesweeper_stats()
            self._update_streak_label()
            self.status.text = 'MENANG! Semua mine berhasil dihindari.'
            info_popup('MENANG!', 'Papan berhasil diselesaikan.', on_ok=self.new_game, btn='Main lagi')
        else:
            self.db.record_minesweeper_loss()
            self.stats = self.db.get_minesweeper_stats()
            self._update_streak_label()
            for row in range(self.rows):
                for col in range(self.rows):
                    if self.board[row][col]:
                        self.revealed[row][col] = True
            self._refresh()
            self.status.text = 'GAME OVER'
            info_popup('GAME OVER', 'Kamu membuka cell berisi mine.', on_ok=self.new_game, btn='Coba lagi')
