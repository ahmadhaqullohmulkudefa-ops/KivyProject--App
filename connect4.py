import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse, RoundedRectangle

from common import BgScreen, TopBar, info_popup, CYAN, MUTED

ROWS, COLS = 6, 7
ORDER = [3, 2, 4, 1, 5, 0, 6]


def c4_winner(b):
    for r in range(ROWS):
        for c in range(COLS):
            p = b[r][c]
            if p:
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    if all(0 <= r + dr * i < ROWS and 0 <= c + dc * i < COLS
                           and b[r + dr * i][c + dc * i] == p for i in range(4)):
                        return p
    return None


def windows(b):
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells, ok = [], True
                for i in range(4):
                    rr, cc = r + dr * i, c + dc * i
                    if 0 <= rr < ROWS and 0 <= cc < COLS:
                        cells.append(b[rr][cc])
                    else:
                        ok = False; break
                if ok:
                    yield cells


def c4_eval(b):
    s = 0
    for wc in windows(b):
        r_ = sum(1 for x in wc if x == 'R')
        y_ = sum(1 for x in wc if x == 'Y')
        if r_ and not y_:
            s += [0, 1, 8, 50][r_]
        elif y_ and not r_:
            s -= [0, 1, 8, 50][y_]
    return s


def valid_cols(b):
    return [c for c in range(COLS) if b[0][c] is None]


def drop(b, c, p):
    for r in range(ROWS - 1, -1, -1):
        if b[r][c] is None:
            b[r][c] = p
            return r
    return None


def mm(b, depth, alpha, beta, maxim):
    """Minimax + alpha-beta. 'R' = pemain (maksimum), 'Y' = bot."""
    w = c4_winner(b)
    if w == 'R':
        return 1e7 + depth, None
    if w == 'Y':
        return -1e7 - depth, None
    vc = valid_cols(b)
    if not vc or depth == 0:
        return c4_eval(b), None
    best = None
    if maxim:
        val = -1e18
        for c in ORDER:
            if c not in vc:
                continue
            nb = [row[:] for row in b]
            drop(nb, c, 'R')
            v, _ = mm(nb, depth - 1, alpha, beta, False)
            if v > val:
                val, best = v, c
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return val, best
    else:
        val = 1e18
        for c in ORDER:
            if c not in vc:
                continue
            nb = [row[:] for row in b]
            drop(nb, c, 'Y')
            v, _ = mm(nb, depth - 1, alpha, beta, True)
            if v < val:
                val, best = v, c
            beta = min(beta, val)
            if alpha >= beta:
                break
        return val, best


class C4Board(Widget):
    def __init__(self, game, **kw):
        super().__init__(**kw)
        self.game = game
        self._g = None
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        g = self.game
        pad = dp(6)
        strip = self.height * 0.12
        cell = min((self.width - pad * 2) / COLS, (self.height - strip - pad * 2) / ROWS)
        bw, bh = cell * COLS, cell * ROWS
        ox = self.x + (self.width - bw) / 2
        oy = self.y + pad + (self.height - pad * 2 - strip - bh) / 2
        self._g = (ox, oy, cell)
        with self.canvas:
            Color(0.07, 0.1, 0.16, 1)
            RoundedRectangle(pos=(ox - dp(10), oy - dp(10)),
                             size=(bw + dp(20), bh + dp(20)), radius=[dp(14)])
            Color(0.25, 0.38, 0.5, 1)
            Line(rounded_rectangle=(ox - dp(10), oy - dp(10), bw + dp(20), bh + dp(20), dp(14)), width=dp(2))
            for r in range(ROWS):
                for c in range(COLS):
                    cx = ox + c * cell + cell / 2
                    cy = oy + (ROWS - 1 - r) * cell + cell / 2
                    rad = cell * 0.38
                    p = g.b[r][c]
                    if p == 'R':
                        Color(0.91, 0.16, 0.16, 1)
                    elif p == 'Y':
                        Color(1, 0.84, 0.15, 1)
                    else:
                        Color(0.16, 0.22, 0.3, 1)
                    Ellipse(pos=(cx - rad, cy - rad), size=(2 * rad, 2 * rad))
                    if p is None:
                        Color(0.3, 0.4, 0.5, 1)
                        Line(circle=(cx, cy, rad), width=dp(1))
            # indikator giliran (lingkaran di atas papan)
            icx = ox + bw / 2
            icy = oy + bh + strip * 0.55
            irad = strip * 0.32
            if g.my_turn:
                Color(0.91, 0.16, 0.16, 1)
            else:
                Color(1, 0.84, 0.15, 1)
            Ellipse(pos=(icx - irad, icy - irad), size=(2 * irad, 2 * irad))

    def on_touch_down(self, t):
        if not self.collide_point(*t.pos) or self._g is None:
            return False
        ox, oy, cell = self._g
        c = int((t.x - ox) // cell)
        if 0 <= c < COLS:
            self.game.player_drop(c)
        return True


class C4Screen(BgScreen):
    def __init__(self, sm, **kw):
        super().__init__(**kw)
        self.sm = sm
        self.b = [[None] * COLS for _ in range(ROWS)]
        self.my_turn = True
        self.over = False
        self.sk = 0; self.sb = 0
        self.gen = 0

        root = BoxLayout(orientation='vertical', padding=[dp(12), dp(8)], spacing=dp(8))
        root.add_widget(TopBar(sm, 'CONNECT 4', on_refresh=lambda *a: self.new_game()))
        self.lbl_s = Label(text='KAMU 0   VS   BOT 0', color=CYAN,
                   bold=True, size_hint_y=None, height=dp(42), font_size=dp(16))
        root.add_widget(self.lbl_s)
        self.board = C4Board(self)
        root.add_widget(self.board)
        self.status = Label(text='Giliranmu (merah)', color=MUTED,
                    size_hint_y=None, height=dp(34), bold=True)
        root.add_widget(self.status)
        self.add_widget(root)

    def on_enter(self):
        self.new_game()

    def new_game(self):
        self.gen += 1
        self.b = [[None] * COLS for _ in range(ROWS)]
        self.my_turn = True
        self.over = False
        self.status.text = 'Giliranmu (merah)'
        self.board._draw()

    def player_drop(self, c):
        if self.over or not self.my_turn:
            return
        if self.b[0][c] is not None:
            self.status.text = 'Kolom penuh!'
            return
        drop(self.b, c, 'R')
        self.board._draw()
        self.check_end()
        if not self.over:
            self.my_turn = False
            self.status.text = 'Bot berpikir...'
            Clock.schedule_once(lambda dt, g=self.gen: self.bot_move(g), 0.7)

    def bot_move(self, g):
        if self.over or g != self.gen:
            return
        vc = valid_cols(self.b)
        if not vc:
            self.finish(None)
            return
        _, c = mm(self.b, 4, -1e18, 1e18, False)   # kedalaman 4
        if c is None or c not in vc:
            c = random.choice(vc)
        drop(self.b, c, 'Y')
        self.board._draw()
        self.check_end()
        if not self.over:
            self.my_turn = True
            self.status.text = 'Giliranmu (merah)'

    def check_end(self):
        w = c4_winner(self.b)
        if w or not valid_cols(self.b):
            self.finish(w)

    def finish(self, w):
        self.over = True
        if w == 'R':
            self.sk += 1
            info_popup('MENANG!', 'Empat berbaris! Kamu menang.', on_ok=self.new_game, btn='Main lagi')
        elif w == 'Y':
            self.sb += 1
            info_popup('KALAH', 'Bot membuat empat berbaris.', on_ok=self.new_game, btn='Coba lagi')
        else:
            info_popup('SERI', 'Papan penuh — seri.', on_ok=self.new_game, btn='Main lagi')
        self.lbl_s.text = f'KAMU {self.sk}   VS   BOT {self.sb}'
        self.status.text = ''