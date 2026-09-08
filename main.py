import os
import random

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import platform
from kivy.graphics import Color, Line, RoundedRectangle

from common import BgScreen, GameCard, IconButton, ModernButton, MUTED, CYAN
from tictactoe import TicScreen
from connect4 import C4Screen
from chessgame import ChessScreen
from hangman import HangmanScreen
from mazegame import MazeScreen
from minesweeper import MinesweeperScreen


class MenuScreen(BgScreen):
    def __init__(self, sm, music, **kw):
        super().__init__(bg=(0.035, 0.05, 0.09, 1), **kw)
        self.sm = sm
        self.music = music
        root = FloatLayout()
        box = BoxLayout(orientation='vertical', padding=[dp(24), dp(28)], spacing=dp(10))
        box.add_widget(Label(text='FIVE\nARCADE', font_size=dp(38), bold=True,
                     color=(1, 1, 1, 1), size_hint_y=None, height=dp(82)))
        box.add_widget(Label(text='YOUR NEXT PLAY', font_size=dp(12), bold=True,
                     color=CYAN, size_hint_y=None, height=dp(22)))
        box.add_widget(Label(text='Enam tantangan singkat untuk dimainkan kapan saja', font_size=dp(13),
                             color=MUTED, size_hint_y=None, height=dp(28)))
        games = (('TIC TAC TOE', 'Strategi cepat melawan bot', 'ttt', (0.12, 0.3, 0.58, 1), 'X'),
                 ('CONNECT 4', 'Susun empat keping lebih dulu', 'c4', (0.58, 0.16, 0.18, 1), '4'),
                 ('CATUR', 'Pertarungan klasik di papan 8x8', 'chess', (0.24, 0.27, 0.34, 1), 'K'),
                 ('HANGMAN', 'Temukan kata rahasia', 'hangman', (0.1, 0.42, 0.34, 1), '?'),
                 ('LABIRIN', 'Temukan jalan keluar', 'maze', (0.5, 0.3, 0.15, 1), '+'),
                 ('MINESWEEPER', 'Classic Mine Puzzle', 'minesweeper', (0.08, 0.42, 0.42, 1), '*'))
        for t, desc, n, color, icon in games:
            b = GameCard(t, desc, accent=color, symbol=icon, size_hint_y=None, height=dp(64))
            b.bind(on_press=lambda inst, nm=n: self.go(nm))
            box.add_widget(b)
        box.add_widget(Label(text='MAIN • MENANG • ULANGI', font_size=dp(11),
                             color=MUTED, size_hint_y=None, height=dp(24)))
        root.add_widget(box)
        self.music_button = IconButton(
            sym='music_on' if music.enabled else 'music_off',
            bg=(0.12, 0.18, 0.28, 1), fg=(0.75, 0.9, 0.95, 1),
            size_hint=(None, None), size=(dp(42), dp(42)),
            pos_hint={'right': 0.96, 'top': 0.96})
        self.music_button.bind(on_press=self.open_music_menu)
        root.add_widget(self.music_button)
        self.add_widget(root)

    def go(self, nm):
        self.sm.transition.direction = 'left'
        self.sm.current = nm

    def open_music_menu(self, *args):
        box = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(7))
        with box.canvas.before:
            Color(0.075, 0.10, 0.16, 1)
            box._music_bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(14)])
            Color(0.25, 0.82, 0.9, 0.35)
            box._music_border = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, dp(14)), width=dp(1))
        box.bind(pos=self._update_music_popup_bg, size=self._update_music_popup_bg)
        box.add_widget(Label(text='BACKGROUND MUSIC', color=(1, 1, 1, 1), bold=True,
                             font_size=dp(15), size_hint_y=None, height=dp(30)))
        for index, _ in enumerate(self.music.paths, start=1):
            active = self.music.enabled and self.music.current_index == index - 1
            label = f'✓  Opsi {index}' if active else f'♪  Opsi {index}'
            button = ModernButton(text=label, fill=(0.1, 0.3, 0.42, 1) if active else (0.12, 0.18, 0.28, 1),
                                  color=(0.95, 0.98, 1, 1), bold=True, size_hint_y=None, height=dp(38))
            button.bind(on_press=lambda instance, choice=index - 1: self.select_music(choice, popup))
            box.add_widget(button)
        off = ModernButton(text='Matikan Musik', fill=(0.38, 0.16, 0.2, 1),
                           color=(1, 0.95, 0.95, 1), bold=True, size_hint_y=None, height=dp(38))
        off.bind(on_press=lambda *button: self.mute_music(popup))
        box.add_widget(off)
        close = ModernButton(text='Tutup', fill=(0.12, 0.18, 0.28, 1),
                             color=(0.85, 0.92, 1, 1), bold=True, size_hint_y=None, height=dp(38))
        close.bind(on_press=lambda *button: popup.dismiss())
        box.add_widget(close)
        popup = Popup(content=box, size_hint=(None, None), size=(dp(270), dp(410)),
                      pos_hint={'right': 0.98, 'top': 0.91}, background_color=(0, 0, 0, 0),
                      separator_height=0)
        popup.open()

    def _update_music_popup_bg(self, box, *args):
        box._music_bg.pos = box.pos
        box._music_bg.size = box.size
        box._music_border.rounded_rectangle = (box.x, box.y, box.width, box.height, dp(14))

    def select_music(self, index, popup):
        self.music.play(index)
        self.update_music_button()
        popup.dismiss()

    def mute_music(self, popup):
        self.music.mute()
        self.update_music_button()
        popup.dismiss()

    def update_music_button(self):
        self.music_button.sym = 'music_on' if self.music.enabled else 'music_off'
        self.music_button._draw()


class BackgroundMusic:
    def __init__(self):
        music_dir = os.path.join(os.path.dirname(__file__), 'assets', 'music')
        self.paths = [os.path.join(music_dir, f'opsi{index}.mp3')
                  for index in range(1, 7) if os.path.isfile(os.path.join(music_dir, f'opsi{index}.mp3'))]
        self.sounds = {}
        self.current_sound = None
        self.current_index = None
        self.enabled = False
        if self.paths:
            self.play(random.randrange(len(self.paths)))

    def _when_finished(self, sound):
        if sound is self.current_sound and self.enabled and len(self.paths) > 1:
            Clock.schedule_once(lambda dt: self.play(self._next_index()), 0)

    def _next_index(self):
        choices = [index for index in range(len(self.paths)) if index != self.current_index]
        return random.choice(choices) if choices else self.current_index

    def play(self, index):
        if not self.paths or not 0 <= index < len(self.paths):
            return
        if self.current_sound:
            old_sound = self.current_sound
            self.current_sound = None
            old_sound.stop()
        sound = self.sounds.get(index)
        if sound is None:
            sound = SoundLoader.load(self.paths[index])
            if sound is None:
                self.current_index = None
                self.enabled = False
                return
            sound.loop = False
            sound.bind(on_stop=lambda stopped_sound: self._when_finished(stopped_sound))
            self.sounds[index] = sound
        self.current_index = index
        self.current_sound = sound
        self.enabled = True
        sound.play()

    def mute(self):
        self.enabled = False
        if self.current_sound:
            sound = self.current_sound
            self.current_sound = None
            sound.stop()


class FiveGamesApp(App):
    def build(self):
        self.music = BackgroundMusic()
        sm = ScreenManager(transition=SlideTransition(duration=0.22))
        sm.add_widget(MenuScreen(sm, self.music, name='menu'))
        sm.add_widget(TicScreen(sm, name='ttt'))
        sm.add_widget(C4Screen(sm, name='c4'))
        sm.add_widget(ChessScreen(sm, name='chess'))
        sm.add_widget(HangmanScreen(sm, name='hangman'))
        sm.add_widget(MazeScreen(sm, name='maze'))
        sm.add_widget(MinesweeperScreen(sm, name='minesweeper'))
        return sm


if __name__ == '__main__':
    if platform not in ('android', 'ios'):
        Window.size = (430, 780)
    FiveGamesApp().run()