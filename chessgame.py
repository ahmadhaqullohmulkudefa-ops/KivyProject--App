import asyncio
import base64
import random

import flet as ft

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


def _piece_image(piece):
    white = piece.isupper()
    fill = "#F4F7FA" if white else "#111722"
    edge = "#101722" if white else "#E7EEF5"
    shapes = {
        "P": '<circle cx="50" cy="31" r="15"/><path d="M35 50 Q50 42 65 50 L74 79 H26 Z"/>',
        "N": '<path d="M26 79 L31 49 Q39 39 37 25 L57 18 L53 34 Q70 38 76 57 L70 79 Z"/><circle cx="58" cy="39" r="2" fill="{edge}"/>',
        "B": '<path d="M50 17 Q71 36 62 49 Q74 58 72 79 H28 Q26 58 38 49 Q29 36 50 17 Z"/><path d="M45 31 L56 42" fill="none" stroke="{edge}" stroke-width="4"/>',
        "R": '<path d="M27 20 H39 V33 H45 V20 H56 V33 H62 V20 H74 V43 L68 49 V78 H32 V49 L27 43 Z"/>',
        "Q": '<path d="M27 27 L41 42 L50 19 L59 42 L73 27 L68 53 H32 Z M34 59 H66 L72 79 H28 Z"/><circle cx="27" cy="23" r="5"/><circle cx="50" cy="15" r="5"/><circle cx="73" cy="23" r="5"/>',
        "K": '<path d="M46 15 H54 V27 H66 V35 H54 V46 Q69 53 68 62 H32 Q31 53 46 46 V35 H34 V27 H46 Z M34 67 H66 L72 80 H28 Z"/>',
    }
    piece_shape = shapes[piece.upper()].format(edge=edge)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        f'<g fill="{fill}" stroke="{edge}" stroke-width="3" '
        f'stroke-linejoin="round">{piece_shape}</g></svg>'
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


class ChessBoard(ft.GridView):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(
            runs_count=8,
            spacing=0,
            run_spacing=0,
            child_aspect_ratio=1,
            controls=self._squares(),
        )

    def _squares(self):
        screen = self.screen
        legal_targets = {(move[2], move[3]) for move in screen.targets}
        last_squares = set()
        if screen.eng.last:
            last_squares = {screen.eng.last[:2], screen.eng.last[2:]}
        squares = []
        for row in range(8):
            for column in range(8):
                piece = screen.eng.b[row][column]
                selected = screen.sel == (row, column)
                is_target = (row, column) in legal_targets
                color = "#405D70" if (row + column) % 2 == 0 else "#192936"
                if (row, column) in last_squares:
                    color = "#587D4A"
                if selected:
                    color = "#B28B29"
                content = None
                if piece:
                    content = ft.Image(
                        src=_piece_image(piece),
                        width=40,
                        height=40,
                        fit=ft.BoxFit.CONTAIN,
                        anti_alias=True,
                    )
                elif is_target:
                    content = ft.Container(
                        width=12,
                        height=12,
                        bgcolor="#A9BEC8",
                        border_radius=20,
                    )
                square = ft.Container(
                    content=content,
                    bgcolor=color,
                    alignment=ft.Alignment(0, 0),
                    padding=0,
                    border=ft.Border.all(2, "#D4B45E") if is_target and piece else None,
                    on_click=lambda _event, r=row, c=column: screen.tap(r, c),
                    tooltip=f"{chr(97 + column)}{8 - row}",
                )
                squares.append(square)
        return squares

    def redraw(self):
        self.controls = self._squares()


class ChessScreen(BgScreen):
    PLAYER_TURN = "player"
    BOT_TURN = "bot"

    def __init__(self, page, **kwargs):
        self.app_page = page
        self.eng = Engine()
        self.sel = None
        self.targets = []
        self.my_turn = True
        self.turn_state = self.PLAYER_TURN
        self.bot_thinking = False
        self.is_replaying = False
        self.over = False
        self.sulit = True
        self.gen = 0
        self.pending_turn = None
        self.last_complete_turn = None
        self.player2_mode = None

        self.lbl_k = ft.Text("KAMU 16", weight=ft.FontWeight.BOLD, color=CYAN)
        self.lbl_v = ft.Text("VS", weight=ft.FontWeight.BOLD, color=MUTED)
        self.lbl_b = ft.Text("BOT 16", weight=ft.FontWeight.BOLD, color="#FF6B63")
        self.status = ft.Text("Pilih mode permainan", color=MUTED, weight=ft.FontWeight.BOLD)
        self.board = ChessBoard(self)
        board_size = min(max((getattr(page, "width", None) or 430) - 32, 280), 520)
        self.replay_btn = ModernButton(
            text="Ulangi Gerakan",
            fill="#992E35",
            color="#FFFFFF",
            bold=True,
            height=46,
            disabled=True,
            on_click=lambda _event: self.replay_move(),
        )
        content = ft.Column(
            controls=[
                TopBar(page, "CATUR", on_refresh=self.reset_game),
                ft.Row(
                    controls=[self.lbl_k, self.lbl_v, self.lbl_b],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    height=42,
                ),
                ft.Container(
                    content=self.board,
                    width=board_size,
                    height=board_size,
                    border_radius=6,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                self.status,
                self.replay_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        super().__init__(bg="#111E2D", content=content, **kwargs)
        if self.app_page:
            self._show_mode_prompt()

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
        self.turn_state = self.PLAYER_TURN
        self.bot_thinking = False
        self.is_replaying = False
        self.over = False
        self.pending_turn = None
        self.last_complete_turn = None
        self.player2_mode = None
        self.status.value = "Pilih mode permainan"
        self.update_labels()
        self.update_replay_button()
        self.board.redraw()

    def _show_mode_prompt(self):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Pilih Player 2", color="#FFFFFF",
                          weight=ft.FontWeight.BOLD),
            content=ft.Text("Main melawan bot atau bergantian di perangkat ini?",
                            color=MUTED),
            bgcolor="#111A29",
            actions=[
                ft.Button(
                    content="BOT",
                    on_click=lambda _event: self._set_mode(False),
                    bgcolor="#203859",
                    color="#FFFFFF",
                ),
                ft.Button(
                    content="PLAYER 2",
                    on_click=lambda _event: self._set_mode(True),
                    bgcolor="#315260",
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.app_page.show_dialog(dialog)

    def _set_mode(self, is_local):
        self.app_page.pop_dialog()
        self.player2_mode = is_local
        self.new_game()

    def new_game(self):
        self.gen += 1
        self.eng.reset()
        self.sel = None
        self.targets = []
        self.my_turn = True
        self.turn_state = self.PLAYER_TURN
        self.bot_thinking = False
        self.is_replaying = False
        self.over = False
        self.pending_turn = None
        self.last_complete_turn = None
        self.status.value = "Giliranmu (putih)" if not self.player2_mode else "Giliran putih"
        self.update_labels()
        self.update_replay_button()
        self.board.redraw()

    def reset_game(self, *_args):
        """Reset the board and invalidate any bot move already scheduled."""
        self.new_game()

    def update_labels(self):
        white_count = sum(1 for row in self.eng.b for piece in row if piece and piece.isupper())
        black_count = sum(1 for row in self.eng.b for piece in row if piece and not piece.isupper())
        self.lbl_k.value = f"KAMU {white_count}"
        self.lbl_b.value = f"BOT {black_count}" if not self.player2_mode else f"P2 {black_count}"

    def tap(self, row, column):
        if (
            self.over
            or not self.my_turn
            or (not self.player2_mode and self.turn_state != self.PLAYER_TURN)
        ):
            return
        if (row, column) in {(move[2], move[3]) for move in self.targets}:
            self.do_move((self.sel[0], self.sel[1], row, column))
            return
        piece = self.eng.b[row][column]
        turn = self.eng.turn
        if self.player2_mode:
            if piece and ((turn == "w" and piece.isupper()) or (turn == "b" and piece.islower())):
                self.sel = (row, column)
                self.targets = [move for move in self.eng.legal(turn)
                                if (move[0], move[1]) == (row, column)]
            else:
                self.sel = None
                self.targets = []
            self.board.redraw()
            return
        if piece and piece.isupper():
            self.sel = (row, column)
            self.targets = [move for move in self.eng.legal("w")
                            if (move[0], move[1]) == (row, column)]
        else:
            self.sel = None
            self.targets = []
        self.board.redraw()

    def do_move(self, move):
        turn = self._apply_move(move)
        self.sel = None
        self.targets = []
        self.update_labels()
        self.board.redraw()
        self.after_move(turn)

    def _apply_move(self, move):
        before = self._snapshot()
        moved = self.eng.turn
        self.eng.make(move)
        self.eng.last = move
        if moved == "w":
            self.pending_turn = {"before": before, "player_move": move}
            self.last_complete_turn = None
        elif self.pending_turn is not None:
            self.last_complete_turn = {
                **self.pending_turn,
                "bot_move": move,
                "after": self._snapshot(),
            }
            self.pending_turn = None
        self.update_replay_button()
        return moved

    def _snapshot(self):
        return ([row[:] for row in self.eng.b], self.eng.turn,
                self.eng.ep, set(self.eng.rights), self.eng.last)

    def _restore(self, snapshot):
        board, turn, ep, rights, last = snapshot
        self.eng.b = [row[:] for row in board]
        self.eng.turn = turn
        self.eng.ep = ep
        self.eng.rights = set(rights)
        self.eng.last = last

    def _same_state(self, left, right):
        return left[0] == right[0] and left[1:] == right[1:]

    def update_replay_button(self):
        self.replay_btn.disabled = (
            self.over
            or self.is_replaying
            or self.bot_thinking
            or self.pending_turn is not None
            or self.last_complete_turn is None
        )

    async def replay_move(self):
        record = self.last_complete_turn
        if (
            self.over
            or self.is_replaying
            or self.bot_thinking
            or self.pending_turn is not None
            or record is None
        ):
            self.update_replay_button()
            return
        current = self._snapshot()
        if not self._same_state(current, record["after"]):
            self.update_replay_button()
            return

        self.is_replaying = True
        self.my_turn = False
        self.status.value = "Mengulang giliran..."
        self.update_replay_button()
        try:
            self._restore(record["before"])
            self.sel = None
            self.targets = []
            self.update_labels()
            self.board.redraw()
            if self.app_page:
                self.app_page.update()
            await asyncio.sleep(0.18)

            if record["player_move"] not in self.eng.legal("w"):
                self._restore(current)
                return
            self.eng.make(record["player_move"])
            self.eng.last = record["player_move"]
            self.turn_state = self.BOT_TURN
            self.update_labels()
            self.board.redraw()
            self.status.value = "Langkah player diputar ulang"
            if self.app_page:
                self.app_page.update()
            await asyncio.sleep(0.18)

            if record["bot_move"] not in self.eng.legal("b"):
                self._restore(current)
                return
            self.eng.make(record["bot_move"])
            self.eng.last = record["bot_move"]
        finally:
            self.is_replaying = False
        self.pending_turn = None
        self.my_turn = True
        self.turn_state = self.PLAYER_TURN
        self.bot_thinking = False
        self.over = False
        self.sel = None
        self.targets = []
        self.update_labels()
        self.board.redraw()
        self.status.value = "Gerakan player dan bot diputar ulang"
        self.after_move("b")
        if self.app_page:
            self.app_page.update()

    def after_move(self, moved):
        if self.is_replaying:
            return
        next_turn = "b" if moved == "w" else "w"
        moves = self.eng.legal(next_turn)
        check = self.eng.in_check(next_turn)
        if not moves:
            self.over = True
            self.bot_thinking = False
            self.update_replay_button()
            if check:
                self.status.value = "Skakmat!"
                message = "Skakmat! " + ("Kamu menang!" if moved == "w" else "Bot menang.")
                info_popup(self.app_page, "PERMAINAN SELESAI", message,
                           on_ok=self.new_game, btn="Main lagi")
            else:
                self.status.value = "Remis"
                info_popup(self.app_page, "REMIS", "Remis (stalemate) — tidak ada langkah sah.",
                           on_ok=self.new_game, btn="Main lagi")
            return
        if self.player2_mode:
            self.turn_state = self.PLAYER_TURN
            self.bot_thinking = False
            self.my_turn = True
            side = "Putih" if self.eng.turn == "w" else "Hitam"
            self.status.value = ("SKAK! " if check else "") + f"Giliran {side}"
            return
        if moved == "w":
            if (
                self.turn_state == self.BOT_TURN
                or self.bot_thinking
                or self.pending_turn is None
                or self.eng.turn != "b"
            ):
                return
            self.turn_state = self.BOT_TURN
            self.bot_thinking = True
            self.my_turn = False
            self.status.value = ("SKAK! " if check else "") + "Bot berpikir..."
            if self.app_page:
                self.app_page.run_task(self._delayed_bot_move, self.gen)
        else:
            self.turn_state = self.PLAYER_TURN
            self.bot_thinking = False
            self.my_turn = True
            self.status.value = ("SKAK! " if check else "") + "Giliranmu"
            self.update_replay_button()

    async def _delayed_bot_move(self, generation):
        await asyncio.sleep(0.7)
        if (
            self.over
            or generation != self.gen
            or self.player2_mode
            or self.turn_state != self.BOT_TURN
            or not self.bot_thinking
        ):
            return
        self.bot_move(generation)
        if self.app_page:
            self.app_page.update()

    def bot_move(self, generation):
        if (
            self.over
            or generation != self.gen
            or self.player2_mode
            or self.eng.turn != "b"
            or self.turn_state != self.BOT_TURN
            or not self.bot_thinking
        ):
            return
        moves = self.eng.legal("b")
        if not moves:
            return
        _, move = self.eng.search(3, -1e9, 1e9, "b")
        if move is None:
            move = random.choice(moves)
        self._apply_move(move)
        self.update_labels()
        self.board.redraw()
        self.after_move("b")

