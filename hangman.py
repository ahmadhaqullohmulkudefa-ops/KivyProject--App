import asyncio
import base64
import random

import flet as ft

from database import DatabaseManager
from common import BgScreen, DARKBTN, ORANGE, TopBar, ModernButton, info_popup, CYAN, MUTED

WORDS = (
    'BUKU', 'MEJA', 'KURSI', 'PENSIL', 'TAS', 'JAM', 'KAMERA', 'KOMPUTER',
    'TELEPON', 'LAYAR', 'MOUSE', 'KABEL', 'KUCING', 'KELINCI', 'BURUNG',
    'IKAN', 'KUDA', 'GAJAH', 'NASI', 'ROTI', 'SOTO', 'BAKSO', 'APEL',
    'PISANG', 'GULA', 'SEKOLAH', 'RUMAH', 'PASAR', 'TAMAN', 'KANTOR',
    'KELAS', 'PANTAI', 'GUNUNG', 'SUNGAI', 'PELANGI', 'HUJAN', 'POHON',
    'BUNGA', 'MATAHARI', 'PAGI', 'MALAM', 'BELAJAR', 'MEMBACA', 'MENULIS',
    'BERMAIN', 'MEMASAK', 'DOKTER', 'GURU', 'PETANI', 'POLISI', 'SOPIR',
    'KERETA', 'MOBIL', 'SEPEDA', 'BUS', 'KAPAL', 'PESAWAT', 'PETUALANGAN',
)
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class Gallows(ft.Image):
    def __init__(self, game, **kwargs):
        self.game = game
        self.reveal = 0
        super().__init__(
            src="",
            width=280,
            height=205,
            fit=ft.BoxFit.CONTAIN,
            anti_alias=True,
            **kwargs,
        )
        self.draw()

    def animate_new_part(self):
        target = self.game.wrong
        self.reveal = max(0, target - 1)
        self.draw()
        if self.game.app_page:
            self.game.app_page.run_task(self._reveal_parts, target)
        else:
            self.reveal = target
            self.draw()

    async def _reveal_parts(self, target):
        while self.reveal < target:
            await asyncio.sleep(0.04)
            self.reveal += 1
            self.draw()
            if self.page:
                self.update()

    def draw(self, *_args):
        parts = [
            '<circle cx="165" cy="62" r="18"/>',
            '<path d="M165 80 V132"/>',
            '<path d="M165 91 L132 112"/>',
            '<path d="M165 91 L198 112"/>',
            '<path d="M165 132 L137 171"/>',
            '<path d="M165 132 L193 171"/>',
        ]
        body = "".join(parts[:self.reveal])
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 210">'
            '<g fill="none" stroke="#EBC979" stroke-width="6" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M45 188 H235 M64 188 V24 H165 V42"/></g>'
            f'<g fill="none" stroke="#F25347" stroke-width="5" stroke-linecap="round" '
            f'stroke-linejoin="round">{body}</g></svg>'
        )
        self.src = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode("ascii")


class HangmanScreen(BgScreen):
    def __init__(self, page, **kwargs):
        self.app_page = page
        self.db = DatabaseManager()
        self.word = ""
        self.guessed = set()
        self.wrong = 0
        self.finished = False
        self.used_words = set()
        self.stats = self.db.get_hangman_stats()

        self.progress = ft.Text("", color=CYAN, weight=ft.FontWeight.BOLD, size=22)
        self.hint = ft.Text("Tebak kata sebelum enam kesalahan.", color=MUTED, size=13)
        self.streak_label = ft.Text(
            "WIN STREAK: 0\nBEST: 0",
            color="#FFFFFF",
            weight=ft.FontWeight.BOLD,
            size=14,
            text_align=ft.TextAlign.CENTER,
        )
        self.gallows = Gallows(self)
        self.status = ft.Text(
            "Pilih sebuah huruf",
            color="#FFD16B",
            weight=ft.FontWeight.BOLD,
        )
        self.keys = {}
        key_controls = []
        viewport_width = getattr(page, "width", None) or 414
        key_width = min(54, max(42, (viewport_width - 54) / 7))
        for letter in LETTERS:
            key = ModernButton(
                text=letter,
                fill=DARKBTN,
                color="#FFFFFF",
                bold=True,
                font_size=17,
                height=44,
                on_click=lambda _event, value=letter: self.guess(value),
            )
            self.keys[letter] = key
            key_controls.append(key)
        self.keyboard = ft.GridView(
            controls=key_controls,
            runs_count=7,
            spacing=5,
            run_spacing=5,
            child_aspect_ratio=key_width / 44,
            height=191,
            on_size_change=self._fit_keyboard,
        )

        content = ft.Column(
            controls=[
                TopBar(page, "HANGMAN", on_refresh=self.new_game),
                self.progress,
                self.hint,
                self.streak_label,
                self.gallows,
                self.status,
                self.keyboard,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=7,
            scroll=ft.ScrollMode.AUTO,
        )
        super().__init__(bg="#121F38", content=content, padding=12, **kwargs)
        self._update_streak_label()
        self.new_game()

    def _fit_keyboard(self, event):
        key_width = min(54, max(42, (event.width - 30) / 7))
        aspect_ratio = key_width / 44
        if abs(self.keyboard.child_aspect_ratio - aspect_ratio) > 0.01:
            self.keyboard.child_aspect_ratio = aspect_ratio
            if self.keyboard.page:
                self.keyboard.update()

    def on_enter(self):
        self.stats = self.db.get_hangman_stats()
        self._update_streak_label()
        self.new_game()

    def _update_streak_label(self):
        self.streak_label.value = (
            f"WIN STREAK: {self.stats.get('current_streak', 0)}\n"
            f"BEST: {self.stats.get('best_streak', 0)}"
        )

    def new_game(self, *_args):
        available = [word for word in WORDS if word not in self.used_words]
        if not available:
            self.used_words.clear()
            available = list(WORDS)
        self.word = random.choice(available)
        self.used_words.add(self.word)
        self.guessed = set()
        unused = [letter for letter in LETTERS if letter not in self.word]
        self.auto_disabled = set(random.sample(unused, min(random.randint(3, 7), len(unused))))
        self.guessed.update(self.auto_disabled)
        self.wrong = 0
        self.finished = False
        self.gallows.reveal = 0
        self.gallows.draw()
        for letter, key in self.keys.items():
            key.disabled = letter in self.auto_disabled
            key.set_fill("#1F2633" if key.disabled else DARKBTN)
        self.status.value = "Pilih sebuah huruf"
        self.refresh()

    def refresh(self):
        self.progress.value = " ".join(
            letter if letter in self.guessed else "_" for letter in self.word
        )
        self.gallows.draw()

    def guess(self, letter):
        if self.finished or letter in self.guessed:
            return
        self.guessed.add(letter)
        key = self.keys[letter]
        key.disabled = True
        if letter in self.word:
            key.set_fill("#208C57")
            self.status.value = "Tepat! Cari huruf berikutnya."
        else:
            self.wrong += 1
            key.set_fill("#A63336")
            self.status.value = f"Belum tepat. Kesalahan {self.wrong}/6."
        self.refresh()
        if letter not in self.word and self.wrong:
            self.gallows.animate_new_part()
        if all(letter in self.guessed for letter in self.word):
            self.finish(True)
        elif self.wrong >= 6:
            self.finish(False)

    def finish(self, won):
        self.finished = True
        for key in self.keys.values():
            key.disabled = True
        if won:
            self.db.record_hangman_win()
            self.status.value = "Kamu menang!"
            title, button = "MENANG!", "Kata baru"
        else:
            self.db.record_hangman_loss()
            self.status.value = "Kesempatan habis."
            title, button = "SELESAI", "Coba lagi"
        self.stats = self.db.get_hangman_stats()
        self._update_streak_label()
        info_popup(
            self.app_page,
            title,
            f"Kata yang benar: {self.word}",
            on_ok=self.new_game,
            btn=button,
        )
