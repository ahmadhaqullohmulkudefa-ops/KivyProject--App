import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Line, RoundedRectangle

from common import BgScreen, TopBar, ModernButton, info_popup, DARKBTN, SURFACE, MUTED, CYAN

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


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


class TTTBoard(Widget):
    def __init__(self, game, **kw):
        super().__init__(**kw)
        self.game = game
        self._g = None
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        g = self.game
        s = min(self.width, self.height)
        if s <= 0:
            return
        ox = self.x + (self.width - s) / 2
        oy = self.y + (self.height - s) / 2
        cell = s / 3
        self._g = (ox, oy, cell)
        with self.canvas:
            Color(0.07, 0.1, 0.16, 1)
            RoundedRectangle(pos=(ox - dp(8), oy - dp(8)), size=(s + dp(16), s + dp(16)), radius=[dp(18)])
            Color(0.28, 0.38, 0.5, 1)
            for i in range(4):
                Line(points=[ox + i * cell, oy, ox + i * cell, oy + s], width=dp(2.5))
                Line(points=[ox, oy + i * cell, ox + s, oy + i * cell], width=dp(2.5))
            for idx, p in enumerate(g.b):
                if p is None:
                    continue
                r, c = divmod(idx, 3)
                cx = ox + c * cell + cell / 2
                cy = oy + (2 - r) * cell + cell / 2
                m = cell * 0.27
                if p == 'X':
                    Color(0.25, 0.82, 0.9, 1)
                    Line(points=[cx - m, cy - m, cx + m, cy + m], width=dp(3.5))
                    Line(points=[cx - m, cy + m, cx + m, cy - m], width=dp(3.5))
                else:
                    Color(1, 0.42, 0.38, 1)
                    Line(circle=(cx, cy, m), width=dp(3.5))

    def on_touch_down(self, t):
        if not self.collide_point(*t.pos) or self._g is None:
            return False
        ox, oy, cell = self._g
        c = int((t.x - ox) // cell)
        rb = int((t.y - oy) // cell)
        if 0 <= c < 3 and 0 <= rb < 3:
            self.game.player_move((2 - rb) * 3 + c)
        return True


class TicScreen(BgScreen):
    def __init__(self, sm, **kw):
        super().__init__(**kw)
        self.sm = sm
        self.b = [None] * 9
        self.sk = 0; self.sb = 0
        self.difficulty = 1
        self.locked = False
        self.gen = 0

        root = BoxLayout(orientation='vertical', padding=[dp(12), dp(8)], spacing=dp(8))
        root.add_widget(TopBar(sm, 'TIC TAC TOE', on_refresh=lambda *a: self.new_game()))

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(8), dp(4)], spacing=dp(6))
        self.lbl_k = Label(text='KAMU 0', bold=True, color=CYAN, font_size=dp(16))
        self.btn_d = ModernButton(text='SULIT', size_hint_x=None, width=dp(84), fill=DARKBTN,
                      color=(1, 1, 1, 1), bold=True)
        self.btn_d.bind(on_press=lambda *a: self.toggle())
        self.lbl_v = Label(text='VS', bold=True, color=MUTED)
        self.lbl_b = Label(text='BOT 0', bold=True, color=(1, 0.42, 0.38, 1), font_size=dp(16))
        for w in (self.lbl_k, self.btn_d, self.lbl_v, self.lbl_b):
            hdr.add_widget(w)
        root.add_widget(hdr)

        self.board = TTTBoard(self)
        root.add_widget(self.board)
        self.status = Label(text='Giliranmu (X)', color=(1, 1, 1, 1),
                    size_hint_y=None, height=dp(34), font_size=dp(16), bold=True)
        root.add_widget(self.status)
        self.add_widget(root)

    def on_enter(self):
        self.new_game()

    def new_game(self):
        self.gen += 1
        self.b = [None] * 9
        self.locked = False
        self.status.text = 'Giliranmu (X)'
        self.board._draw()

    def toggle(self):
        self.difficulty = 1 - self.difficulty
        self.sulit = self.difficulty == 1
        self.btn_d.text = ('SEDANG', 'SULIT')[self.difficulty]
        self.new_game()

    def player_move(self, i):
        if self.locked or self.b[i] is not None:
            return
        self.b[i] = 'X'
        self.board._draw()
        w = winner(self.b)
        if w:
            self._end(w)
            return
        self.locked = True
        self.status.text = 'Bot berpikir...'
        Clock.schedule_once(lambda dt, g=self.gen: self.bot_move(g), 0.55)

    def bot_move(self, g):
        if g != self.gen:
            return
        empty = [i for i in range(9) if self.b[i] is None]
        if not empty:
            return
        if self.difficulty == 0 and random.random() < 0.35:
            i = random.choice(empty)
        else:
            _, i = minimax(self.b, True)
        if i is None or self.b[i] is not None:
            i = random.choice(empty)
        self.b[i] = 'O'
        self.board._draw()
        w = winner(self.b)
        if w:
            self._end(w)
            return
        self.locked = False
        self.status.text = 'Giliranmu (X)'

    def _end(self, w):
        self.locked = True
        if w == 'X':
            self.sk += 1; t, m, btn, st = 'MENANG!', 'Selamat, kamu menang!', 'Main lagi', 'Kamu menang!'
        elif w == 'O':
            self.sb += 1; t, m, btn, st = 'KALAH', 'Bot menang.', 'Coba lagi', 'Bot menang.'
        else:
            t, m, btn, st = 'SERI', 'Permainan seri.', 'Main lagi', 'Seri.'
        self.status.text = st
        self.lbl_k.text = f'KAMU {self.sk}'
        self.lbl_b.text = f'BOT {self.sb}'
        info_popup(t, m, on_ok=self.new_game, btn=btn)