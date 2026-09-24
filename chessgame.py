import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse, Rectangle, Triangle, RoundedRectangle

from common import BgScreen, TopBar, ModernButton, info_popup, DARKBTN, CYAN, MUTED

DIRS_B = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
DIRS_R = [(1, 0), (-1, 0), (0, 1), (0, -1)]
KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
VAL = {'P': 1, 'N': 3, 'B': 3.2, 'R': 5, 'Q': 9, 'K': 0}
CENTER = [[0, 1, 2, 3, 3, 2, 1, 0], [1, 2, 3, 4, 4, 3, 2, 1],
          [2, 3, 4, 5, 5, 4, 3, 2], [3, 4, 5, 6, 6, 5, 4, 3],
          [3, 4, 5, 6, 6, 5, 4, 3], [2, 3, 4, 5, 5, 4, 3, 2],
          [1, 2, 3, 4, 4, 3, 2, 1], [0, 1, 2, 3, 3, 2, 1, 0]]


def inb(r, c):
    return 0 <= r < 8 and 0 <= c < 8


class Engine:
    """Engine catur murni Python: semua gerakan sah, skakmat, rokade,
    en passant, promosi (otomatis jadi ratu), dan AI minimax."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.b = [list('rnbqkbnr'), list('pppppppp')] + \
                 [[None] * 8 for _ in range(4)] + \
                 [list('PPPPPPPP'), list('RNBQKBNR')]
        self.turn = 'w'
        self.ep = None            # target en passant
        self.rights = set('KQkq')  # hak rokade
        self.last = None

    def own(self, p, color):
        return p is not None and (p.isupper() == (color == 'w'))

    def attacked(self, r, c, by):
        b = self.b
        d = 1 if by == 'w' else -1
        for dc in (-1, 1):
            rr, cc = r + d, c + dc
            if inb(rr, cc) and self.own(b[rr][cc], by) and b[rr][cc].upper() == 'P':
                return True
        for dr, dc in KN:
            rr, cc = r + dr, c + dc
            if inb(rr, cc) and self.own(b[rr][cc], by) and b[rr][cc].upper() == 'N':
                return True
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    rr, cc = r + dr, c + dc
                    if inb(rr, cc) and self.own(b[rr][cc], by) and b[rr][cc].upper() == 'K':
                        return True
        for dirs, ks in ((DIRS_B, 'BQ'), (DIRS_R, 'RQ')):
            for dr, dc in dirs:
                rr, cc = r + dr, c + dc
                while inb(rr, cc):
                    p = b[rr][cc]
                    if p is not None:
                        if p.upper() in ks and self.own(p, by):
                            return True
                        break
                    rr += dr; cc += dc
        return False

    def pseudo(self, color):
        b, mv = self.b, []
        for r in range(8):
            for c in range(8):
                p = b[r][c]
                if not self.own(p, color):
                    continue
                u = p.upper()
                if u == 'P':
                    d = -1 if color == 'w' else 1
                    st = 6 if color == 'w' else 1
                    if inb(r + d, c) and b[r + d][c] is None:
                        mv.append((r, c, r + d, c))
                        if r == st and b[r + 2 * d][c] is None:
                            mv.append((r, c, r + 2 * d, c))
                    for dc in (-1, 1):
                        rr, cc = r + d, c + dc
                        if inb(rr, cc):
                            if b[rr][cc] is not None and not self.own(b[rr][cc], color):
                                mv.append((r, c, rr, cc))
                            elif self.ep == (rr, cc):
                                mv.append((r, c, rr, cc))
                elif u == 'N':
                    for dr, dc in KN:
                        rr, cc = r + dr, c + dc
                        if inb(rr, cc) and not self.own(b[rr][cc], color):
                            mv.append((r, c, rr, cc))
                elif u == 'K':
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr, cc = r + dr, c + dc
                            if inb(rr, cc) and not self.own(b[rr][cc], color):
                                mv.append((r, c, rr, cc))
                    hr = 7 if color == 'w' else 0
                    opp = 'b' if color == 'w' else 'w'
                    R_ = 'R' if color == 'w' else 'r'
                    if r == hr and c == 4 and not self.attacked(hr, 4, opp):
                        if ('K' if color == 'w' else 'k') in self.rights and \
                           b[hr][7] == R_ and b[hr][5] is None and b[hr][6] is None and \
                           not self.attacked(hr, 5, opp) and not self.attacked(hr, 6, opp):
                            mv.append((r, c, hr, 6))
                        if ('Q' if color == 'w' else 'q') in self.rights and \
                           b[hr][0] == R_ and b[hr][1] is None and b[hr][2] is None and b[hr][3] is None and \
                           not self.attacked(hr, 3, opp) and not self.attacked(hr, 2, opp):
                            mv.append((r, c, hr, 2))
                else:
                    dirs = DIRS_B if u == 'B' else DIRS_R if u == 'R' else DIRS_B + DIRS_R
                    for dr, dc in dirs:
                        rr, cc = r + dr, c + dc
                        while inb(rr, cc):
                            q = b[rr][cc]
                            if q is None:
                                mv.append((r, c, rr, cc))
                            else:
                                if not self.own(q, color):
                                    mv.append((r, c, rr, cc))
                                break
                            rr += dr; cc += dc
        return mv

    def make(self, m):
        r1, c1, r2, c2 = m
        b = self.b
        piece = b[r1][c1]; cap = b[r2][c2]; flags = ''
        ep_old = self.ep; rights_old = set(self.rights)
        self.ep = None
        if piece.upper() == 'P':
            if (r2, c2) == ep_old and cap is None and c1 != c2:
                cap = b[r1][c2]; b[r1][c2] = None; flags = 'ep'
            elif abs(r2 - r1) == 2:
                self.ep = ((r1 + r2) // 2, c1)
        if piece == 'K':
            self.rights -= {'K', 'Q'}
        elif piece == 'k':
            self.rights -= {'k', 'q'}
        for rr, cc, rg in ((7, 0, 'Q'), (7, 7, 'K'), (0, 0, 'q'), (0, 7, 'k')):
            if (r1, c1) == (rr, cc) or (r2, c2) == (rr, cc):
                self.rights.discard(rg)
        if piece.upper() == 'K' and abs(c2 - c1) == 2:
            flags = 'ck' if c2 == 6 else 'cq'
            if c2 == 6:
                b[r1][5] = b[r1][7]; b[r1][7] = None
            else:
                b[r1][3] = b[r1][0]; b[r1][0] = None
        if piece == 'P' and r2 == 0:
            b[r2][c2] = 'Q'
        elif piece == 'p' and r2 == 7:
            b[r2][c2] = 'q'
        else:
            b[r2][c2] = piece
        b[r1][c1] = None
        self.turn = 'b' if self.turn == 'w' else 'w'
        return (piece, cap, ep_old, rights_old, flags)

    def unmake(self, m, info):
        r1, c1, r2, c2 = m
        b = self.b
        piece, cap, ep_old, rights_old, flags = info
        b[r1][c1] = piece
        b[r2][c2] = cap
        if flags == 'ep':
            b[r2][c2] = None; b[r1][c2] = cap
        elif flags == 'ck':
            b[r1][7] = b[r1][5]; b[r1][5] = None
        elif flags == 'cq':
            b[r1][0] = b[r1][3]; b[r1][3] = None
        self.ep = ep_old; self.rights = rights_old
        self.turn = 'b' if self.turn == 'w' else 'w'

    def king_pos(self, color):
        k = 'K' if color == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.b[r][c] == k:
                    return (r, c)
        return None

    def in_check(self, color):
        kp = self.king_pos(color)
        return kp is not None and self.attacked(kp[0], kp[1], 'b' if color == 'w' else 'w')

    def legal(self, color=None):
        color = color or self.turn
        out = []
        for m in self.pseudo(color):
            info = self.make(m)
            if not self.in_check(color):
                out.append(m)
            self.unmake(m, info)
        return out

    def evaluate(self):
        s = 0.0
        for r in range(8):
            for c in range(8):
                p = self.b[r][c]
                if p is None:
                    continue
                v = VAL[p.upper()] + CENTER[r][c] * 0.04
                s += v if p.isupper() else -v
        return s

    def search(self, depth, alpha, beta, color):
        moves = self.legal(color)
        if not moves:
            if self.in_check(color):
                return (-1000 if color == 'w' else 1000), None
            return 0, None
        if depth == 0:
            return self.evaluate(), None
        moves.sort(key=lambda m: self.b[m[2]][m[3]] is not None, reverse=True)
        best = None
        if color == 'w':
            val = -1e9
            for m in moves:
                info = self.make(m)
                v, _ = self.search(depth - 1, alpha, beta, 'b')
                self.unmake(m, info)
                if v > val:
                    val, best = v, m
                alpha = max(alpha, val)
                if alpha >= beta:
                    break
            return val, best
        else:
            val = 1e9
            for m in moves:
                info = self.make(m)
                v, _ = self.search(depth - 1, alpha, beta, 'w')
                self.unmake(m, info)
                if v < val:
                    val, best = v, m
                beta = min(beta, val)
                if alpha >= beta:
                    break
            return val, best


def add_piece(inst, p, x, y, s):
    """Draw a recognizable chess-piece silhouette without font glyphs."""
    white = p.isupper()
    fill = (0.96, 0.98, 1, 1) if white else (0.08, 0.1, 0.15, 1)
    edge = (0.05, 0.08, 0.12, 1) if white else (0.85, 0.92, 1, 1)
    cx, cy = x + s / 2, y + s / 2
    base_y = y + s * 0.12
    body_y = y + s * 0.28
    piece = p.upper()
    inst.add(Color(*edge))
    inst.add(Ellipse(pos=(x + s * 0.16, base_y), size=(s * 0.68, s * 0.16)))
    inst.add(RoundedRectangle(pos=(x + s * 0.24, base_y + s * 0.06),
                              size=(s * 0.52, s * 0.1), radius=[s * 0.04]))
    inst.add(Color(*fill))
    inst.add(Ellipse(pos=(x + s * 0.22, y + s * 0.2), size=(s * 0.56, s * 0.15)))
    if piece == 'P':
        inst.add(Ellipse(pos=(cx - s * 0.15, y + s * 0.55), size=(s * 0.3, s * 0.28)))
        inst.add(Triangle(points=[cx - s * 0.2, body_y, cx + s * 0.2, body_y,
                                  cx, y + s * 0.6]))
    elif piece == 'N':
        inst.add(Rectangle(pos=(x + s * 0.32, body_y), size=(s * 0.32, s * 0.38)))
        inst.add(Triangle(points=[x + s * 0.38, y + s * 0.55, x + s * 0.4, y + s * 0.86,
                                  x + s * 0.7, y + s * 0.55]))
        inst.add(Triangle(points=[x + s * 0.55, y + s * 0.55, x + s * 0.7, y + s * 0.55,
                                  x + s * 0.73, y + s * 0.7]))
        inst.add(Ellipse(pos=(x + s * 0.55, y + s * 0.65), size=(s * 0.07, s * 0.07)))
    elif piece == 'R':
        inst.add(Rectangle(pos=(x + s * 0.3, body_y), size=(s * 0.4, s * 0.4)))
        for offset in (0.3, 0.43, 0.56):
            inst.add(Rectangle(pos=(x + s * offset, y + s * 0.66), size=(s * 0.1, s * 0.18)))
        inst.add(Rectangle(pos=(x + s * 0.26, y + s * 0.63), size=(s * 0.48, s * 0.08)))
    elif piece == 'B':
        inst.add(Triangle(points=[cx, y + s * 0.88, x + s * 0.32, body_y,
                                  x + s * 0.68, body_y]))
        inst.add(Ellipse(pos=(cx - s * 0.13, y + s * 0.72), size=(s * 0.26, s * 0.2)))
        inst.add(Line(points=[cx - s * 0.04, y + s * 0.76, cx + s * 0.05, y + s * 0.86], width=dp(1.5)))
    elif piece == 'Q':
        inst.add(Ellipse(pos=(cx - s * 0.18, y + s * 0.68), size=(s * 0.36, s * 0.2)))
        inst.add(Triangle(points=[x + s * 0.28, y + s * 0.71, x + s * 0.36, y + s * 0.9,
                                  cx, y + s * 0.74]))
        inst.add(Triangle(points=[cx, y + s * 0.74, x + s * 0.64, y + s * 0.9,
                                  x + s * 0.72, y + s * 0.71]))
    else:
        inst.add(Rectangle(pos=(x + s * 0.43, y + s * 0.58), size=(s * 0.14, s * 0.27)))
        inst.add(Rectangle(pos=(x + s * 0.32, y + s * 0.8), size=(s * 0.36, s * 0.1)))
        inst.add(Rectangle(pos=(x + s * 0.45, y + s * 0.89), size=(s * 0.1, s * 0.08)))


class ChessBoard(Widget):
    def __init__(self, screen, **kw):
        super().__init__(**kw)
        self.screen = screen
        self._g = None
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        scr = self.screen
        eng = scr.eng
        s = min(self.width, self.height)
        if s <= 0:
            return
        ox = self.x + (self.width - s) / 2
        oy = self.y + (self.height - s) / 2
        cs = s / 8
        self._g = (ox, oy, cs)
        targets = {(m[2], m[3]) for m in scr.targets}
        with self.canvas:
            for r in range(8):
                for c in range(8):
                    Color(*(0.2, 0.29, 0.36, 1) if (r + c) % 2 == 0 else (0.1, 0.16, 0.22, 1))
                    Rectangle(pos=(ox + c * cs, oy + r * cs), size=(cs, cs))
            if eng.last:
                Color(0.35, 0.8, 0.35, 0.45)
                for (r, c) in (eng.last[0:2], eng.last[2:4]):
                    Rectangle(pos=(ox + c * cs, oy + r * cs), size=(cs, cs))
            if scr.sel:
                Color(1, 0.9, 0.2, 0.6)
                Rectangle(pos=(ox + scr.sel[1] * cs, oy + scr.sel[0] * cs), size=(cs, cs))
                Color(0.1, 0.1, 0.1, 0.5)
                for (r, c) in targets:
                    if eng.b[r][c] is None:
                        Ellipse(pos=(ox + c * cs + cs * .42, oy + r * cs + cs * .42),
                                size=(cs * .16, cs * .16))
                    else:
                        Line(circle=(ox + c * cs + cs / 2, oy + r * cs + cs / 2, cs * .44), width=dp(2))
            for r in range(8):
                for c in range(8):
                    p = eng.b[r][c]
                    if p:
                        add_piece(self.canvas, p, ox + c * cs, oy + r * cs, cs)

    def on_touch_down(self, t):
        if not self.collide_point(*t.pos) or self._g is None or not self.screen.my_turn:
            return False
        ox, oy, cs = self._g
        c = int((t.x - ox) // cs)
        r = int((t.y - oy) // cs)
        if 0 <= r < 8 and 0 <= c < 8:
            self.screen.tap(r, c)
        return True


class ChessScreen(BgScreen):
    def __init__(self, sm, **kw):
        super().__init__(**kw)
        self.sm = sm
        self.eng = Engine()
        self.sel = None
        self.targets = []
        self.my_turn = True
        self.over = False
        self.sulit = True
        self.gen = 0
        self.replay_record = None
        self.player2_mode = None

        root = BoxLayout(orientation='vertical', padding=[dp(12), dp(8)], spacing=dp(8))
        root.add_widget(TopBar(sm, 'CATUR', on_refresh=self.reset_game))

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(8), dp(4)], spacing=dp(8))
        self.lbl_k = Label(text='KAMU 16', bold=True, color=CYAN, font_size=dp(16))
        self.lbl_v = Label(text='VS', bold=True, color=MUTED)
        self.lbl_b = Label(text='BOT 16', bold=True, color=(1, 0.42, 0.38, 1), font_size=dp(16))
        for w in (self.lbl_k, self.lbl_v, self.lbl_b):
            hdr.add_widget(w)
        root.add_widget(hdr)

        self.board = ChessBoard(self)
        root.add_widget(self.board)
        self.status = Label(text='Pilih mode permainan', color=MUTED,
                    size_hint_y=None, height=dp(34), bold=True)
        root.add_widget(self.status)
        self.replay_btn = ModernButton(text='Ulangi Gerakan', size_hint_y=None, height=dp(46),
                 fill=(0.6, 0.16, 0.18, 1),
                     color=(1, 1, 1, 1), bold=True)
        self.replay_btn.bind(on_press=lambda *a: self.replay_move())
        root.add_widget(self.replay_btn)
        self.add_widget(root)

    def on_pre_enter(self):
        self.reset_session()
        self._show_mode_prompt()

    def on_leave(self):
        self.reset_session()

    def reset_session(self):
        """Clear the active mode and board before the next Chess session."""
        self.gen += 1
        self.eng.reset()
        self.sel = None
        self.targets = []
        self.my_turn = True
        self.over = False
        self.replay_record = None
        self.player2_mode = None
        self.status.text = 'Pilih mode permainan'
        self.update_labels()
        self.update_replay_button()
        self.board._draw()

    def _show_mode_prompt(self):
        box = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10), size_hint=(None, None), size=(dp(260), dp(180)))
        with box.canvas.before:
            Color(0.06, 0.09, 0.15, 1)
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(16)])
            Color(0.25, 0.82, 0.9, 0.35)
            box._border = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, dp(16)), width=dp(1.2))
        box.bind(pos=lambda *_: self._sync_mode_popup_bg(box), size=lambda *_: self._sync_mode_popup_bg(box))
        box.add_widget(Label(text='Pilih Player 2', color=(1, 1, 1, 1), bold=True, font_size=dp(18),
                            size_hint_y=None, height=dp(28)))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        bot_btn = ModernButton(text='BOT', fill=(0.12, 0.22, 0.35, 1), color=(1, 1, 1, 1), bold=True)
        bot_btn.bind(on_press=lambda *a: self._set_mode(False, popup))
        row.add_widget(bot_btn)
        local_btn = ModernButton(text='PLAYER 2', fill=(0.20, 0.34, 0.42, 1), color=(1, 1, 1, 1), bold=True)
        local_btn.bind(on_press=lambda *a: self._set_mode(True, popup))
        row.add_widget(local_btn)
        box.add_widget(row)
        popup = Popup(title='CHESS', content=box, size_hint=(None, None), size=(dp(260), dp(180)),
                      background_color=(0, 0, 0, 0), separator_height=0, title_color=(1, 1, 1, 1),
                      title_size=dp(16))
        self._mode_popup = popup
        popup.open()

    def _sync_mode_popup_bg(self, box):
        if hasattr(box, '_bg'):
            box._bg.pos = box.pos
            box._bg.size = box.size
        if hasattr(box, '_border'):
            box._border.rounded_rectangle = (box.x, box.y, box.width, box.height, dp(16))

    def _set_mode(self, is_local, popup):
        self.player2_mode = is_local
        popup.dismiss()
        self.new_game()

    def new_game(self):
        self.gen += 1
        self.eng.reset()
        self.sel = None
        self.targets = []
        self.my_turn = True
        self.over = False
        self.replay_record = None
        self.status.text = 'Giliranmu (putih)' if not self.player2_mode else 'Giliran putih'
        self.update_labels()
        self.update_replay_button()
        self.board._draw()

    def reset_game(self, *args):
        """Reset the board and invalidate any bot move already scheduled."""
        self.new_game()

    def update_labels(self):
        w = sum(1 for row in self.eng.b for p in row if p and p.isupper())
        b_ = sum(1 for row in self.eng.b for p in row if p and not p.isupper())
        self.lbl_k.text = f'KAMU {w}'
        self.lbl_b.text = f'BOT {b_}' if not self.player2_mode else f'P2 {b_}'

    def tap(self, r, c):
        if self.over or not self.my_turn:
            return
        if (r, c) in {(m[2], m[3]) for m in self.targets}:
            self.do_move((self.sel[0], self.sel[1], r, c))
            return
        p = self.eng.b[r][c]
        turn = self.eng.turn
        if self.player2_mode:
            if p and ((turn == 'w' and p.isupper()) or (turn == 'b' and p.islower())):
                self.sel = (r, c)
                self.targets = [m for m in self.eng.legal(turn) if (m[0], m[1]) == (r, c)]
                self.board._draw()
            else:
                self.sel = None
                self.targets = []
                self.board._draw()
            return
        if p and p.isupper():
            self.sel = (r, c)
            self.targets = [m for m in self.eng.legal('w') if (m[0], m[1]) == (r, c)]
            self.board._draw()
        else:
            self.sel = None
            self.targets = []
            self.board._draw()

    def do_move(self, m):
        before = self._snapshot()
        turn = self.eng.turn
        self.eng.make(m)
        self.eng.last = m
        self.replay_record = (before, self._snapshot(), m, turn)
        self.sel = None
        self.targets = []
        self.update_labels()
        self.update_replay_button()
        self.board._draw()
        self.after_move(turn)

    def _snapshot(self):
        return ([row[:] for row in self.eng.b], self.eng.turn,
                self.eng.ep, set(self.eng.rights))

    def _restore(self, snapshot):
        board, turn, ep, rights = snapshot
        self.eng.b = [row[:] for row in board]
        self.eng.turn = turn
        self.eng.ep = ep
        self.eng.rights = set(rights)

    def _same_state(self, left, right):
        return (left[0] == right[0] and left[1:] == right[1:])

    def update_replay_button(self):
        self.replay_btn.disabled = self.over or self.replay_record is None

    def replay_move(self):
        record = self.replay_record
        if self.over or record is None:
            self.update_replay_button()
            return
        before, after, move, moved = record
        cur = self._snapshot()
        if self._same_state(cur, after):
            self._restore(before)
            self.sel = None
            self.targets = []
            self.update_labels()
            self.board._draw()
            self.status.text = 'Gerakan terakhir dibatalkan'
            self.replay_record = (before, after, move, moved)
            self.update_replay_button()
            return
        if self._same_state(cur, before):
            self.eng.make(move)
            self.eng.last = move
            self.sel = None
            self.targets = []
            self.update_labels()
            self.board._draw()
            self.status.text = 'Gerakan terakhir diputar ulang'
            self.replay_record = (before, after, move, moved)
            self.update_replay_button()
            return
        self.update_replay_button()

    def after_move(self, moved):
        eng = self.eng
        nxt = 'b' if moved == 'w' else 'w'
        moves = eng.legal(nxt)
        chk = eng.in_check(nxt)
        if not moves:
            self.over = True
            self.update_replay_button()
            if chk:
                self.status.text = 'Skakmat!'
                msg = 'Skakmat! ' + ('Kamu menang!' if moved == 'w' else 'Bot menang.')
                info_popup('PERMAINAN SELESAI', msg, on_ok=self.new_game, btn='Main lagi')
            else:
                self.status.text = 'Remis'
                info_popup('REMIS', 'Remis (stalemate) — tidak ada langkah sah.',
                           on_ok=self.new_game, btn='Main lagi')
            return
        if self.player2_mode:
            self.my_turn = True
            side = 'Putih' if eng.turn == 'w' else 'Hitam'
            self.status.text = ('SKAK! ' if chk else '') + f'Giliran {side}'
            return
        if moved == 'w':
            self.my_turn = False
            self.status.text = ('SKAK! ' if chk else '') + 'Bot berpikir...'
            Clock.schedule_once(lambda dt, g=self.gen: self.bot_move(g), 0.7)
        else:
            self.my_turn = True
            self.status.text = ('SKAK! ' if chk else '') + 'Giliranmu'

    def bot_move(self, g):
        if self.over or g != self.gen or self.player2_mode:
            return
        eng = self.eng
        moves = eng.legal('b')
        if not moves:
            return
        _, m = eng.search(3, -1e9, 1e9, 'b')
        if m is None:
            m = random.choice(moves)
        before = self._snapshot()
        eng.make(m)
        eng.last = m
        self.replay_record = (before, self._snapshot(), m, 'b')
        self.update_labels()
        self.update_replay_button()
        self.board._draw()
        self.after_move('b')

