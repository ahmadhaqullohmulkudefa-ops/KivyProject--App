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
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle

from common import BgScreen, GameCard, IconButton, ModernButton, MUTED, CYAN
from database import DatabaseManager
from tictactoe import TicScreen
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

        with root.canvas.before:
            Color(0.12, 0.18, 0.30, 0.22)
            root._bg_orb_a = Ellipse(pos=(dp(-18), root.height - dp(150)), size=(dp(220), dp(220)))
            Color(0.15, 0.27, 0.40, 0.12)
            root._bg_orb_b = Ellipse(pos=(root.width - dp(160), root.height - dp(110)), size=(dp(200), dp(200)))
            Color(0.18, 0.82, 0.88, 0.08)
            root._line = Line(points=[root.center_x - dp(90), root.height - dp(112), root.center_x + dp(90), root.height - dp(112)], width=dp(1.1))

        def _update_background(*_):
            root._bg_orb_a.pos = (dp(-18), root.height - dp(150))
            root._bg_orb_a.size = (dp(220), dp(220))
            root._bg_orb_b.pos = (root.width - dp(160), root.height - dp(110))
            root._bg_orb_b.size = (dp(200), dp(200))
            root._line.points = [root.center_x - dp(90), root.height - dp(112), root.center_x + dp(90), root.height - dp(112)]

        root.bind(size=_update_background, pos=_update_background)

        self.music_button = IconButton(
            sym='music_on' if music.enabled else 'music_off',
            bg=(0.10, 0.16, 0.28, 1), fg=(0.78, 0.92, 0.98, 1),
            size_hint=(None, None), size=(dp(42), dp(42)),
            pos_hint={'right': 0.98, 'top': 0.96})
        self.music_button.bind(on_press=self.open_music_menu)
        root.add_widget(self.music_button)

        header = BoxLayout(orientation='vertical', size_hint=(None, None),
                           size=(dp(260), dp(88)), pos_hint={'center_x': 0.5, 'top': 0.91})
        header.add_widget(Label(text='FiveGames', font_size=dp(34), bold=True,
                                color=(1, 1, 1, 1), halign='center', valign='middle',
                                size_hint=(1, None), height=dp(42)))
        header.add_widget(Label(text='5 GAMES', font_size=dp(11), bold=True,
                                color=(0.67, 0.8, 0.92, 1), halign='center', valign='middle',
                                size_hint=(1, None), height=dp(16)))
        root.add_widget(header)

        games = (
            ('TIC TAC TOE', 'ttt', (0.10, 0.32, 0.68, 1), 'X'),
            ('CHESS', 'chess', (0.28, 0.34, 0.46, 1), '♟'),
            ('HANGMAN', 'hangman', (0.08, 0.48, 0.38, 1), '?'),
            ('LABIRIN', 'maze', (0.58, 0.30, 0.12, 1), '+'),
            ('MINESWEEPER', 'minesweeper', (0.05, 0.48, 0.50, 1), '*'))
        game_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(0.85, None),
                             height=dp(5 * 70 + 4 * 10), pos_hint={'center_x': 0.5, 'top': 0.67})
        for title, name, color, icon in games:
            button = GameCard(title, accent=color, symbol=icon, size_hint=(1, None), height=dp(70))
            button.bind(on_press=lambda inst, nm=name: self.go(nm))
            game_box.add_widget(button)
        root.add_widget(game_box)

        footer = Label(text='SELECT A GAME TO START', font_size=dp(10), bold=True,
                       color=(0.58, 0.72, 0.88, 1), halign='center', valign='middle',
                       size_hint=(None, None), size=(dp(220), dp(18)), pos_hint={'center_x': 0.5, 'y': 0.055})
        root.add_widget(footer)

        self.add_widget(root)

    def go(self, nm):
        self.sm.transition.direction = 'left'
        self.sm.current = nm

    def open_music_menu(self, *args):
        content = BoxLayout(orientation='vertical', padding=[dp(12), dp(16)], spacing=dp(6), size_hint=(None, None),
                    size=(dp(220), dp(500)))
        with content.canvas.before:
            Color(0.06, 0.10, 0.17, 1)
            content._music_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(14)])
            Color(0.25, 0.82, 0.9, 0.35)
            content._music_border = Line(rounded_rectangle=(content.x, content.y, content.width, content.height, dp(14)), width=dp(1.2))
        content.bind(pos=self._update_music_popup_bg, size=self._update_music_popup_bg)
        content.add_widget(Label(text='FiveGames', color=(0.96, 0.98, 1, 1), bold=True,
                                 font_size=dp(30), halign='center', valign='middle',
                                 text_size=(dp(196), None), size_hint_y=1))
        content.add_widget(Label(text='BACKGROUND MUSIC', color=(1, 1, 1, 1), bold=True,
                                 font_size=dp(13), size_hint_y=None, height=dp(24)))
        for index, _ in enumerate(self.music.paths):
            active = self.music.enabled and self.music.current_index == index
            label = f'{"✓ " if active else ""}Ops  {index + 1}' if active else f'Ops  {index + 1}'
            button = ModernButton(text=label, fill=(0.10, 0.30, 0.42, 1) if active else (0.12, 0.18, 0.28, 1),
                                 color=(0.95, 0.98, 1, 1), bold=True, size_hint_y=None, height=dp(32))
            button.bind(on_press=lambda instance, choice=index: self.select_music(choice, popup))
            content.add_widget(button)
        off = ModernButton(text='Matikan Musik', fill=(0.38, 0.16, 0.2, 1),
                           color=(1, 0.95, 0.95, 1), bold=True, size_hint_y=None, height=dp(32))
        off.bind(on_press=lambda *button: self.mute_music(popup))
        content.add_widget(off)
        close = ModernButton(text='Tutup', fill=(0.12, 0.18, 0.28, 1),
                             color=(0.85, 0.92, 1, 1), bold=True, size_hint_y=None, height=dp(32))
        close.bind(on_press=lambda *button: popup.dismiss())
        popup = Popup(title='MUSIC', content=content, size_hint=(None, None), size=(dp(220), dp(500)),
                      pos_hint={'right': 0.98, 'top': 0.91}, background_color=(0, 0, 0, 0),
                      separator_height=0, title_color=(1, 1, 1, 1), title_size=dp(14))
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
        self.paths = []
        if os.path.isdir(music_dir):
            for index in range(1, 9):
                path = os.path.join(music_dir, f'opsi{index}.mp3')
                if os.path.isfile(path):
                    self.paths.append(path)
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
    title = 'FiveGames'

    def build(self):
        self.db = DatabaseManager()
        self.db.initialize_database()
        self.music = BackgroundMusic()
        sm = ScreenManager(transition=SlideTransition(duration=0.22))
        sm.add_widget(MenuScreen(sm, self.music, name='menu'))
        sm.add_widget(TicScreen(sm, name='ttt'))
        sm.add_widget(ChessScreen(sm, name='chess'))
        sm.add_widget(HangmanScreen(sm, name='hangman'))
        sm.add_widget(MazeScreen(sm, name='maze'))
        sm.add_widget(MinesweeperScreen(sm, name='minesweeper'))
        return sm


if __name__ == '__main__':
    if platform not in ('android', 'ios'):
        Window.size = (430, 780)
    FiveGamesApp().run()