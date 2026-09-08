from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, Rectangle, Triangle, RoundedRectangle
from kivy.properties import NumericProperty

ORANGE = (1, 0.55, 0.12, 1)
DARKBTN = (0.22, 0.22, 0.27, 1)
BG = (0.035, 0.05, 0.09, 1)
SURFACE = (0.075, 0.10, 0.16, 1)
MUTED = (0.76, 0.82, 0.9, 1)
CYAN = (0.25, 0.82, 0.9, 1)


class BgScreen(Screen):
    """Screen dengan warna latar penuh."""
    def __init__(self, bg=ORANGE, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*bg)
            self._bgr = Rectangle(pos=self.pos, size=self.size)
            Color(0.08, 0.16, 0.25, 0.16)
            self._glow = Ellipse(pos=(-dp(100), self.height - dp(180)), size=(dp(360), dp(360)))
        self.bind(pos=self._ub, size=self._ub)

    def _ub(self, *a):
        self._bgr.pos = self.pos
        self._bgr.size = self.size
        self._glow.pos = (self.x - dp(100), self.top - dp(180))


class ModernButton(Button):
    def __init__(self, fill=(0.12, 0.18, 0.28, 1), **kw):
        super().__init__(background_normal='', background_down='', **kw)
        self.fill = fill
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        shade = tuple(min(1, c * 1.18) for c in self.fill[:3]) + (1,)
        if self.state == 'down':
            shade = tuple(c * 0.78 for c in shade[:3]) + (1,)
        with self.canvas.before:
            Color(*shade)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(1, 1, 1, 0.1)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)), width=dp(1))


class GameCard(ModernButton):
    def __init__(self, title, subtitle, accent=(0.12, 0.3, 0.58, 1), symbol='>', **kw):
        super().__init__(fill=accent, **kw)
        self.text = f'{symbol}   {title}\n       {subtitle}'
        self.halign = 'left'
        self.valign = 'middle'
        self.font_size = dp(15)
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.padding = [dp(18), 0]


class IconButton(ButtonBehavior, Widget):
    """Tombol bulat dengan ikon digambar canvas (tanpa file gambar)."""
    def __init__(self, sym='back', bg=(1, 1, 1, 1), fg=(0.25, 0.25, 0.3, 1), **kw):
        super().__init__(**kw)
        self.sym, self.bgc, self.fgc = sym, bg, fg
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        x, y, w, h = self.pos[0], self.pos[1], self.size[0], self.size[1]
        if w <= 0 or h <= 0:
            return
        s = min(w, h); cx, cy = x + w / 2, y + h / 2; d = s * 0.26
        with self.canvas:
            Color(*self.bgc)
            Ellipse(pos=(x + (w - s) / 2, y + (h - s) / 2), size=(s, s))
            Color(*self.fgc)
            if self.sym == 'back':
                Line(points=[cx - d, cy, cx + d * 0.9, cy], width=dp(2))
                Line(points=[cx - d, cy, cx - d * 0.45, cy + d * 0.55], width=dp(2))
                Line(points=[cx - d, cy, cx - d * 0.45, cy - d * 0.55], width=dp(2))
            elif self.sym == 'refresh':
                Line(circle=(cx, cy, d, 40, 300), width=dp(2))
                Triangle(points=[cx + d * 0.77, cy + d * 0.64 + dp(5),
                                 cx + d * 0.77 + dp(9), cy + d * 0.64 - dp(3),
                                 cx + d * 0.77 - dp(7), cy + d * 0.64 - dp(5)])
            elif self.sym == 'bulb':
                Color(1, 0.98, 0.9, 1)
                Ellipse(pos=(cx - d * 0.7, cy - d * 0.1), size=(d * 1.4, d * 1.4))
                Color(*self.fgc)
                Rectangle(pos=(cx - d * 0.32, cy - d * 0.55), size=(d * 0.64, d * 0.4))
                Line(points=[cx - d * 0.35, cy + d * 0.6, cx - d * 0.55, cy + d * 0.95], width=dp(1.5))
                Line(points=[cx + d * 0.35, cy + d * 0.6, cx + d * 0.55, cy + d * 0.95], width=dp(1.5))
                Line(points=[cx, cy + d * 0.75, cx, cy + d * 1.05], width=dp(1.5))
            elif self.sym in ('music_on', 'music_off'):
                Line(points=[cx + d * 0.35, cy + d * 0.72, cx + d * 0.35, cy - d * 0.38], width=dp(2.2))
                Line(points=[cx + d * 0.35, cy + d * 0.72, cx + d * 0.82, cy + d * 0.82], width=dp(2.2))
                Ellipse(pos=(cx - d * 0.15, cy - d * 0.65), size=(d * 0.52, d * 0.34))
                if self.sym == 'music_off':
                    Line(points=[cx - d * 0.9, cy + d * 0.9, cx + d * 0.9, cy - d * 0.9], width=dp(2.4))
            else:  # panah: up / down / left / right
                if self.sym == 'up':
                    pts = [cx, cy + d, cx - d, cy - d * 0.6, cx + d, cy - d * 0.6]
                elif self.sym == 'down':
                    pts = [cx, cy - d, cx - d, cy + d * 0.6, cx + d, cy + d * 0.6]
                elif self.sym == 'left':
                    pts = [cx - d, cy, cx + d * 0.6, cy + d, cx + d * 0.6, cy - d]
                else:
                    pts = [cx + d, cy, cx - d * 0.6, cy + d, cx - d * 0.6, cy - d]
                Triangle(points=pts)


class TopBar(BoxLayout):
    """Bar atas: tombol back, judul, dan (opsional) tombol refresh."""
    def __init__(self, sm, title='', on_refresh=None, **kw):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         height=dp(54), padding=[dp(8), dp(7)], spacing=dp(6), **kw)
        self.sm = sm
        with self.canvas.before:
            Color(0.035, 0.05, 0.09, 0.92)
            self._bar_bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        b = IconButton(sym='back', bg=(0.12, 0.18, 0.28, 1), fg=(0.75, 0.9, 0.95, 1), size_hint=(None, None), size=(dp(40), dp(40)))
        b.bind(on_press=lambda *a: self.go_menu())
        self.add_widget(b)
        self.add_widget(Label(text=title, bold=True, font_size=dp(20), color=(1, 1, 1, 1)))
        if on_refresh:
            r = IconButton(sym='refresh', bg=(0.12, 0.18, 0.28, 1), fg=(0.75, 0.9, 0.95, 1), size_hint=(None, None), size=(dp(40), dp(40)))
            r.bind(on_press=lambda *a: on_refresh())
            self.add_widget(r)

    def _update_bg(self, *args):
        self._bar_bg.pos = self.pos
        self._bar_bg.size = self.size

    def go_menu(self):
        self.sm.transition.direction = 'right'
        self.sm.current = 'menu'


class Hearts(Widget):
    """Nyawa berbentuk hati (digambar canvas, tanpa file gambar)."""
    n = NumericProperty(3)
    total = NumericProperty(3)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(n=self._draw, total=self._draw, pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
        slot = self.width / max(1, self.total)
        s = min(self.height, slot * 0.95)
        r = s * 0.22
        for i in range(self.total):
            cx = self.x + slot * (i + 0.5)
            cyy = self.y + self.height * 0.58
            col = (0.9, 0.16, 0.24, 1) if i < self.n else (0.35, 0.35, 0.38, 1)
            with self.canvas:
                Color(*col)
                Ellipse(pos=(cx - 2 * r, cyy - r), size=(2 * r, 2 * r))
                Ellipse(pos=(cx, cyy - r), size=(2 * r, 2 * r))
                Triangle(points=[cx - 2 * r, cyy, cx + 2 * r, cyy, cx, cyy - 2 * r])


def info_popup(title, msg, on_ok=None, btn='OK'):
    """Popup pesan sederhana."""
    box = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
    lbl = Label(text=msg, color=(0.96, 0.98, 1, 1), bold=True)
    lbl.text_size = (dp(250), None)
    lbl.halign = 'center'
    lbl.valign = 'middle'
    box.add_widget(lbl)
    b = ModernButton(text=btn, size_hint_y=None, height=dp(44), fill=ORANGE,
                     color=(1, 1, 1, 1), bold=True)
    box.add_widget(b)
    pop = Popup(title=title, content=box, size_hint=(None, None), size=(dp(310), dp(200)),
                background_color=(0.08, 0.11, 0.17, 1), separator_color=ORANGE,
                title_color=(1, 1, 1, 1), title_size=dp(18))

    def close(*_):
        pop.dismiss()
        if on_ok:
            on_ok()
    b.bind(on_press=close)
    pop.open()