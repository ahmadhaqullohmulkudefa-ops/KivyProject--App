import random
from collections import deque
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse, Rectangle, InstructionGroup

from common import BgScreen, TopBar, IconButton, ModernButton, info_popup, Hearts, DARKBTN, CYAN, MUTED

# arah: 0=atas 1=kanan 2=bawah 3=kiri
DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIFFS = [('SEDANG', 11, 14), ('SULIT', 15, 18)]


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
                if nxt not in prev:
                    prev[nxt] = cur
                    q.append(nxt)
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path if path and path[0] == start else []


class MazeBoard(Widget):
    def __init__(self, screen, **kw):
        super().__init__(**kw)
        self.screen = screen
        self.hint_grp = None
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        self.hint_grp = None
        scr = self.screen
        if scr.walls is None:
            return
        rows, cols = scr.rows, scr.cols
        cell = min(self.width / cols, self.height / rows)
        if cell <= 0:
            return
        ox = self.x + (self.width - cell * cols) / 2
        oy = self.y + (self.height - cell * rows) / 2
        with self.canvas:
            Color(0.32, 0.55, 0.62, 1)
            for r in range(rows):
                for c in range(cols):
                    x = ox + c * cell
                    y = oy + (rows - 1 - r) * cell
                    ws = scr.walls[r][c]
                    if ws[0]:
                        Line(points=[x, y + cell, x + cell, y + cell], width=dp(1.6))
                    if ws[2]:
                        Line(points=[x, y, x + cell, y], width=dp(1.6))
                    if ws[3]:
                        Line(points=[x, y, x, y + cell], width=dp(1.6))
                    if ws[1]:
                        Line(points=[x + cell, y, x + cell, y + cell], width=dp(1.6))
            ex, ey = ox + (cols - 1) * cell, oy + (rows - 1) * cell
            Color(0.2, 0.85, 0.3, 1)
            Ellipse(pos=(ex + cell * 0.2, ey + cell * 0.2), size=(cell * 0.6, cell * 0.6))
            pr, pc = scr.pos_
            px = ox + pc * cell
            py = oy + (rows - 1 - pr) * cell
            Color(1, 0.6, 0.1, 1)
            Ellipse(pos=(px + cell * 0.25, py + cell * 0.25), size=(cell * 0.5, cell * 0.5))
            Color(1, 1, 1, 1)
            Ellipse(pos=(px + cell * 0.38, py + cell * 0.38), size=(cell * 0.24, cell * 0.24))

    def show_hint(self, path):
        cell = min(self.width / self.screen.cols, self.height / self.screen.rows)
        ox = self.x + (self.width - cell * self.screen.cols) / 2
        oy = self.y + (self.height - cell * self.screen.rows) / 2
        pts = []
        for (r, c) in path:
            pts += [ox + c * cell + cell / 2,
                    oy + (self.screen.rows - 1 - r) * cell + cell / 2]
        grp = InstructionGroup()
        grp.add(Color(1, 0.9, 0.2, 1))
        grp.add(Line(points=pts, width=dp(2.5), dash_length=dp(6), dash_offset=dp(3)))
        self.hint_grp = grp
        self.canvas.add(grp)
        Clock.schedule_once(self.hide_hint, 2.5)

    def hide_hint(self, *a):
        if self.hint_grp:
            self.canvas.remove(self.hint_grp)
            self.hint_grp = None


class MazeScreen(BgScreen):
    def __init__(self, sm, **kw):
        super().__init__(bg=(0.13, 0.12, 0.16, 1), **kw)
        self.sm = sm
        self.di = 1          # default: SULIT
        self.level = 1
        self.walls = None

        root = BoxLayout(orientation='vertical', padding=[dp(12), dp(8)], spacing=dp(7))
        root.add_widget(TopBar(sm, 'LABIRIN'))

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(8), dp(4)], spacing=dp(8))
        self.btn_d = ModernButton(text='SULIT', size_hint_x=None, width=dp(90), fill=DARKBTN,
                      color=(1, 1, 1, 1), bold=True)
        self.btn_d.bind(on_press=lambda *a: self.cycle_diff())
        self.lbl_l = Label(text='Level 1', color=CYAN, bold=True, font_size=dp(18))
        self.hearts = Hearts(size_hint_x=None, width=dp(110))
        hdr.add_widget(self.btn_d); hdr.add_widget(self.lbl_l); hdr.add_widget(self.hearts)
        root.add_widget(hdr)

        self.board = MazeBoard(self)
        root.add_widget(self.board)

        hint_row = BoxLayout(size_hint_y=None, height=dp(54), padding=[dp(8), dp(3)])
        self.hint_btn = IconButton(sym='bulb', bg=(1, 0.85, 0.25, 1), fg=(0.35, 0.25, 0.05, 1),
                                   size_hint=(None, None), size=(dp(52), dp(52)),
                       pos_hint={'right': 1})
        self.hint_btn.bind(on_press=lambda *a: self.hint())
        hint_row.add_widget(Widget())
        hint_row.add_widget(self.hint_btn)
        root.add_widget(hint_row)

        ctr = GridLayout(cols=3, size_hint_y=None, height=dp(82),
             spacing=dp(3), padding=[dp(84), dp(2)])
        up = IconButton(sym='up', size_hint=(1, None), height=dp(34))
        up.bind(on_press=lambda *a: self.move(0))
        ctr.add_widget(Widget()); ctr.add_widget(up); ctr.add_widget(Widget())
        for sym, di in (('left', 3), ('down', 2), ('right', 1)):
            b = IconButton(sym=sym, size_hint=(1, None), height=dp(34))
            b.bind(on_press=lambda inst, d=di: self.move(d))
            ctr.add_widget(b)
        root.add_widget(ctr)

        self.status = Label(text='Capai lingkaran hijau!', color=MUTED,
                    size_hint_y=None, height=dp(30), bold=True)
        root.add_widget(self.status)
        self.add_widget(root)

    def on_enter(self):
        Window.bind(on_key_down=self._key)
        self.level = 1
        self.start()

    def on_leave(self):
        Window.unbind(on_key_down=self._key)

    def _key(self, win, key, *a):
        m = {273: 0, 275: 1, 274: 2, 276: 3}   # panah keyboard (desktop)
        if key in m:
            self.move(m[key])
            return True
        return False

    def start(self):
        name, cols, rows = DIFFS[self.di]
        self.cols, self.rows = cols, rows
        self.walls = gen_maze(rows, cols)
        self.pos_ = (rows - 1, 0)              # kiri bawah
        self.hearts.n = 3
        self.lbl_l.text = f'Level {self.level}'
        self.btn_d.text = name
        self.board._draw()

    def cycle_diff(self):
        self.di = (self.di + 1) % 2
        self.level = 1
        self.start()

    def move(self, di):
        if self.walls is None:
            return
        r, c = self.pos_
        if self.walls[r][c][di]:
            return
        rr, cc = r + DIRS[di][0], c + DIRS[di][1]
        if 0 <= rr < self.rows and 0 <= cc < self.cols:
            self.pos_ = (rr, cc)
            self.board.hide_hint()
            self.board._draw()
            if self.pos_ == (0, self.cols - 1):     # pojok kanan atas = exit
                self.level += 1
                info_popup('SELESAI!', f'Level selesai! Lanjut ke level {self.level}.',
                           on_ok=self.start, btn='Lanjut')

    def hint(self):
        if self.walls is None:
            return
        if self.hearts.n <= 0:
            self.status.text = 'Petunjuk habis!'
            return
        self.hearts.n -= 1
        path = solve(self.walls, self.pos_, (0, self.cols - 1), self.rows, self.cols)
        self.board.show_hint(path)
        self.status.text = 'Ikuti garis kuning!'