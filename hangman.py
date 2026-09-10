import random

from kivy.graphics import Color, Line, Ellipse
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

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


class Gallows(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.clear()
        wrong = self.game.wrong
        if self.width <= 0 or self.height <= 0:
            return
        left = self.x + self.width * 0.22
        base = self.y + self.height * 0.16
        top = self.y + self.height * 0.82
        pole = self.x + self.width * 0.5
        with self.canvas:
            Color(0.92, 0.78, 0.48, 1)
            Line(points=[left, base, self.x + self.width * 0.78, base], width=dp(4))
            Line(points=[left + dp(12), base, left + dp(12), top], width=dp(4))
            Line(points=[left + dp(12), top, pole, top], width=dp(4))
            Line(points=[pole, top, pole, top - dp(28)], width=dp(3))
            Color(0.95, 0.32, 0.26, 1)
            if wrong >= 1:
                Ellipse(pos=(pole - dp(18), top - dp(64)), size=(dp(36), dp(36)))
            if wrong >= 2:
                Line(points=[pole, top - dp(64), pole, top - dp(132)], width=dp(4))
            if wrong >= 3:
                Line(points=[pole, top - dp(82), pole - dp(34), top - dp(108)], width=dp(4))
            if wrong >= 4:
                Line(points=[pole, top - dp(82), pole + dp(34), top - dp(108)], width=dp(4))
            if wrong >= 5:
                Line(points=[pole, top - dp(132), pole - dp(30), top - dp(178)], width=dp(4))
            if wrong >= 6:
                Line(points=[pole, top - dp(132), pole + dp(30), top - dp(178)], width=dp(4))


class HangmanScreen(BgScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(bg=(0.07, 0.12, 0.22, 1), **kwargs)
        self.sm = sm
        self.db = DatabaseManager()
        self.word = ''
        self.guessed = set()
        self.wrong = 0
        self.finished = False
        self.used_words = set()
        self.stats = self.db.get_hangman_stats()

        root = BoxLayout(orientation='vertical', padding=[dp(12), dp(8)], spacing=dp(7))
        root.add_widget(TopBar(sm, 'HANGMAN', on_refresh=self.new_game))
        self.progress = Label(text='', color=CYAN, bold=True, font_size=dp(22),
                              size_hint_y=None, height=dp(42))
        root.add_widget(self.progress)
        self.hint = Label(text='Tebak kata sebelum enam kesalahan.', color=MUTED,
                          font_size=dp(13), size_hint_y=None, height=dp(24))
        root.add_widget(self.hint)
        self.streak_label = Label(text='WIN STREAK: 0\nBEST: 0', color=(1, 1, 1, 1),
                                   bold=True, font_size=dp(14),
                                   size_hint_y=None, height=dp(42))
        root.add_widget(self.streak_label)
        self.gallows = Gallows(self)
        root.add_widget(self.gallows)
        self.status = Label(text='Pilih sebuah huruf', color=(1, 0.82, 0.42, 1), bold=True,
                            size_hint_y=None, height=dp(30))
        root.add_widget(self.status)

        self.keyboard = GridLayout(cols=7, spacing=dp(4), padding=[dp(4), dp(2)])
        self.keys = {}
        for letter in LETTERS:
            key = ModernButton(text=letter, fill=DARKBTN, color=(1, 1, 1, 1),
                               bold=True, font_size=dp(14))
            key.bind(on_press=lambda button, value=letter: self.guess(value))
            self.keys[letter] = key
            self.keyboard.add_widget(key)
        root.add_widget(self.keyboard)
        self.add_widget(root)

    def on_enter(self):
        self.stats = self.db.get_hangman_stats()
        self._update_streak_label()
        self.new_game()

    def _update_streak_label(self):
        self.streak_label.text = f"WIN STREAK: {self.stats.get('current_streak', 0)}\nBEST: {self.stats.get('best_streak', 0)}"

    def new_game(self, *args):
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
        for key in self.keys.values():
            key.disabled = key.text in self.auto_disabled
            key.fill = (0.12, 0.15, 0.2, 1) if key.disabled else DARKBTN
            key._redraw()
        self.status.text = 'Pilih sebuah huruf'
        self.refresh()

    def refresh(self):
        self.progress.text = ' '.join(letter if letter in self.guessed else '_' for letter in self.word)
        self.gallows.draw()

    def guess(self, letter):
        if self.finished or letter in self.guessed:
            return
        self.guessed.add(letter)
        key = self.keys[letter]
        key.disabled = True
        if letter in self.word:
            key.fill = (0.12, 0.55, 0.34, 1)
            self.status.text = 'Tepat! Cari huruf berikutnya.'
        else:
            self.wrong += 1
            key.fill = (0.65, 0.2, 0.2, 1)
            self.status.text = f'Belum tepat. Kesalahan {self.wrong}/6.'
        key._redraw()
        self.refresh()
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
            self.stats = self.db.get_hangman_stats()
            self._update_streak_label()
            self.status.text = 'Kamu menang!'
            info_popup('MENANG!', f'Kata yang benar: {self.word}', on_ok=self.new_game, btn='Kata baru')
        else:
            self.db.record_hangman_loss()
            self.stats = self.db.get_hangman_stats()
            self._update_streak_label()
            self.status.text = 'Kesempatan habis.'
            info_popup('SELESAI', f'Kata yang benar: {self.word}', on_ok=self.new_game, btn='Coba lagi')
