from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color,RoundedRectangle
from kivy.utils import get_color_from_hex
class CardLayout(BoxLayout):
    def __init__(self,**kw):
        super().__init__(orientation="vertical",padding=[20,25,20,25],spacing=15,size_hint_y=None,**kw)
        with self.canvas.before: Color(rgba=get_color_from_hex("#1E1E1E")); self.bg=RoundedRectangle(radius=[25])
        self.bind(pos=self.up,size=self.up,minimum_height=self.setter("height"))
    def up(self,*_): self.bg.pos=self.pos; self.bg.size=self.size
class ModernButton(Button):
    def __init__(self,bg_color="#2C2C2C",font_color="#FFFFFF",**kw):
        super().__init__(background_normal="",background_color=(0,0,0,0),**kw); self.hex=bg_color; self.color=get_color_from_hex(font_color); self.bold=True
        with self.canvas.before: self.c=Color(rgba=get_color_from_hex(bg_color)); self.r=RoundedRectangle(radius=[12])
        self.bind(pos=self.up,size=self.up,state=self.state)
    def up(self,*_): self.r.pos=self.pos; self.r.size=self.size
    def state(self,_,v): self.c.rgba=get_color_from_hex(self.hex)[:3]+([.7] if v=="down" else [1])
