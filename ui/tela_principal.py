from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.utils import get_color_from_hex
from kivymd.uix.label import MDIcon


class MaterialCard(BoxLayout):
    bg_color = ListProperty(get_color_from_hex("#151A1E"))

    def __init__(self, **kwargs):
        self._radius = dp(18)
        orientation = kwargs.pop("orientation", "vertical")
        super().__init__(orientation=orientation, **kwargs)
        with self.canvas.before:
            self._background_color = Color(*self.bg_color)
            self._background = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[(self._radius, self._radius)] * 4
            )
        self.bind(pos=self._atualizar_fundo, size=self._atualizar_fundo,
                  bg_color=self._atualizar_fundo)

    def _atualizar_fundo(self, *_):
        self._background_color.rgba = self.bg_color
        self._background.pos = self.pos
        self._background.size = self.size
        self._background.radius = [(self._radius, self._radius)] * 4


class MaterialButton(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon = StringProperty("")
    bg_color = ListProperty(get_color_from_hex("#263238"))
    text_color = ListProperty(get_color_from_hex("#ECEFF1"))
    icon_color = ListProperty(get_color_from_hex("#ECEFF1"))
    disabled = BooleanProperty(False)

    def __init__(self, text="", icon="", bg_color="#263238",
                 text_color="#ECEFF1", icon_color="#ECEFF1",
                 callback=None, fonte=15, **kwargs):
        self.text = text
        self.icon = icon
        self.bg_color = get_color_from_hex(bg_color)
        self.text_color = get_color_from_hex(text_color)
        self.icon_color = get_color_from_hex(icon_color)
        super().__init__(
            orientation="horizontal",
            spacing=dp(7),
            padding=(dp(12), dp(6)),
            size_hint_y=None,
            **kwargs
        )
        with self.canvas.before:
            self._background_color = Color(*self.bg_color)
            self._background = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[(dp(14), dp(14))] * 4
            )
        self.bind(pos=self._atualizar_visual, size=self._atualizar_visual,
                  state=self._atualizar_visual, disabled=self._atualizar_visual)

        if icon:
            self._icone = MDIcon(
                icon=icon,
                theme_text_color="Custom",
                text_color=self.icon_color,
                font_size=sp(21),
                size_hint=(None, 1),
                width=dp(30),
            )
            self.add_widget(self._icone)

        self._label = Label(
            text=text,
            font_size=sp(fonte),
            color=self.text_color,
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self._label.bind(size=self._label.setter("text_size"))
        self.add_widget(self._label)

        if callback is not None:
            self.bind(on_release=callback)

    def _atualizar_visual(self, *_):
        cor = list(self.bg_color)
        if self.disabled:
            cor[3] *= 0.40
            cor[:3] = [min(1.0, v * 0.55) for v in cor[:3]]
        elif self.state == "down":
            cor[:3] = [min(1.0, v * 0.72) for v in cor[:3]]
        self._background_color.rgba = cor
        self._background.pos = self.pos
        self._background.size = self.size
        self._background.radius = [(dp(14), dp(14))] * 4


class MaterialIconButton(ButtonBehavior, FloatLayout):
    icon = StringProperty("")
    bg_color = ListProperty(get_color_from_hex("#263238"))
    icon_color = ListProperty(get_color_from_hex("#ECEFF1"))
    disabled = BooleanProperty(False)

    def __init__(self, icon, callback=None, bg_color="#263238",
                 icon_color="#ECEFF1", **kwargs):
        self.icon = icon
        self.bg_color = get_color_from_hex(bg_color)
        self.icon_color = get_color_from_hex(icon_color)
        super().__init__(size_hint_y=None, **kwargs)
        with self.canvas.before:
            self._background_color = Color(*self.bg_color)
            self._background = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[(dp(16), dp(16))] * 4
            )
        self._icone = MDIcon(
            icon=icon,
            theme_text_color="Custom",
            text_color=self.icon_color,
            font_size=sp(27),
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(self._icone)
        self.bind(pos=self._atualizar_visual, size=self._atualizar_visual,
                  state=self._atualizar_visual, disabled=self._atualizar_visual)
        if callback is not None:
            self.bind(on_release=callback)

    def _atualizar_visual(self, *_):
        cor = list(self.bg_color)
        if self.disabled:
            cor[:3] = [min(1.0, v * 0.55) for v in cor[:3]]
            cor[3] *= 0.40
        elif self.state == "down":
            cor[:3] = [min(1.0, v * 0.72) for v in cor[:3]]
        self._background_color.rgba = cor
        self._background.pos = self.pos
        self._background.size = self.size
        self._background.radius = [(dp(16), dp(16))] * 4


class EstadoSwitch(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    disabled = BooleanProperty(False)
    track_on = ListProperty(get_color_from_hex("#1976D2"))
    track_off = ListProperty(get_color_from_hex("#37474F"))
    thumb_on = ListProperty(get_color_from_hex("#E3F2FD"))
    thumb_off = ListProperty(get_color_from_hex("#90A4AE"))

    def __init__(self, active=False, callback=None, **kwargs):
        self.active = active

        # height/size_hint_y/orientation podem ser fornecidos pelo
        # container pai; remova-os de kwargs antes do super() para
        # evitar que ButtonBehavior receba o mesmo argumento duas vezes.
        altura = kwargs.pop("height", dp(52))
        size_hint_y = kwargs.pop("size_hint_y", None)
        orientacao = kwargs.pop("orientation", "horizontal")

        super().__init__(
            orientation=orientacao,
            size_hint_y=size_hint_y,
            height=altura,
            **kwargs
        )
        with self.canvas:
            self._track_color = Color(*self.track_off)
            self._track = RoundedRectangle(
                pos=(0, 0), size=(dp(62), dp(30)),
                radius=[(dp(15), dp(15))] * 4
            )
            self._thumb_color = Color(*self.thumb_off)
            self._thumb = Ellipse(
                pos=(0, 0), size=(dp(28), dp(28))
            )
        self.bind(
            pos=self._atualizar_visual, size=self._atualizar_visual,
            active=self._atualizar_visual, disabled=self._atualizar_visual,
        )
        if callback is not None:
            self.bind(on_release=callback)
        self._atualizar_visual()

    def _atualizar_visual(self, *_):
        largura, altura = dp(62), dp(30)
        x = self.x + self.width - largura
        y = self.y + (self.height - altura) / 2
        self._track.pos = (x, y)
        self._track.size = (largura, altura)

        thumb = dp(28)
        if self.active:
            track_color = self.track_on
            thumb_color = self.thumb_on
            thumb_x = x + largura - thumb - dp(1)
        else:
            track_color = self.track_off
            thumb_color = self.thumb_off
            thumb_x = x + dp(1)
        thumb_y = y + (altura - thumb) / 2

        if self.disabled:
            track_color = [track_color[0], track_color[1], track_color[2], track_color[3] * 0.45]
            thumb_color = [thumb_color[0], thumb_color[1], thumb_color[2], thumb_color[3] * 0.55]

        self._track_color.rgba = track_color
        self._thumb_color.rgba = thumb_color
        self._thumb.pos = (thumb_x, thumb_y)
        self._thumb.size = (thumb, thumb)


class Spacer(Widget):
    pass


class TelaPrincipal(ScrollView):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.do_scroll_x = False
        self.bar_width = dp(3)
        self.controladores_prontos = False
        self._botoes_comando = []
        self._switches_estado = []

        principal = BoxLayout(
            orientation="vertical",
            padding=(dp(12), dp(10), dp(12), dp(26)),
            spacing=dp(12),
            size_hint_y=None,
        )
        principal.bind(minimum_height=principal.setter("height"))

        cabecalho = BoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint_y=None, height=dp(64),
        )
        identidade = BoxLayout(orientation="vertical", spacing=0)
        identidade.add_widget(Label(
            text="DIRECTLINK", font_size=sp(24), bold=True,
            color=get_color_from_hex("#E3F2FD"),
            halign="left", valign="middle",
        ))
        identidade.add_widget(Label(
            text="CONTROLE RESIDENCIAL", font_size=sp(10),
            color=get_color_from_hex("#78909C"),
            halign="left", valign="middle",
        ))
        cabecalho.add_widget(identidade)
        cabecalho.add_widget(MaterialIconButton(
            "cog-outline",
            callback=lambda *_: self.app.abrir_configuracoes(),
            bg_color="#263238",
            size=(dp(58), dp(58)),
            size_hint=(None, None),
        ))
        principal.add_widget(cabecalho)

        status_card = MaterialCard(
            orientation="horizontal",
            padding=(dp(12), dp(8)),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
            bg_color=get_color_from_hex("#18242C"),
        )
        self.status_icon = MDIcon(
            icon="wifi-off", font_size=sp(19),
            theme_text_color="Custom",
            text_color=get_color_from_hex("#EF5350"),
            size_hint=(None, None), size=(dp(28), dp(28)),
        )
        self.status = Label(
            text="Inicializando...", font_size=sp(13),
            color=get_color_from_hex("#B0BEC5"),
            halign="left", valign="middle",
        )
        self.status.bind(size=self.status.setter("text_size"))
        status_card.add_widget(self.status_icon)
        status_card.add_widget(self.status)
        principal.add_widget(status_card)

        principal.add_widget(self.criar_card_som())
        principal.add_widget(self.criar_card_tv())
        principal.add_widget(self.criar_card_ar())
        self.add_widget(principal)

    def _titulo_card(self, icone, titulo, subtitulo, cor):
        cabecalho = BoxLayout(
            orientation="horizontal", spacing=dp(10),
            size_hint_y=None, height=dp(42),
        )
        cabecalho.add_widget(MDIcon(
            icon=icone,
            theme_text_color="Custom",
            text_color=get_color_from_hex(cor),
            font_size=sp(24),
            size_hint=(None, None), size=(dp(32), dp(32)),
        ))
        textos = BoxLayout(orientation="vertical", spacing=0)
        textos.add_widget(Label(
            text=titulo, font_size=sp(17), bold=True,
            color=get_color_from_hex("#ECEFF1"),
            halign="left", valign="middle",
        ))
        textos.add_widget(Label(
            text=subtitulo, font_size=sp(10),
            color=get_color_from_hex("#78909C"),
            halign="left", valign="middle",
        ))
        cabecalho.add_widget(textos)
        return cabecalho

    def _card(self):
        return MaterialCard(
            padding=(dp(13), dp(13), dp(13), dp(16)),
            spacing=dp(10), size_hint_y=None,
            bg_color=get_color_from_hex("#151A1E"),
        )

    def _registrar(self, botao):
        self._botoes_comando.append(botao)
        return botao

    def _registrar_switch(self, switch):
        self._switches_estado.append(switch)
        return switch

    def _linha_switch(self, icone, titulo, subtitulo, active,
                      callback, cor_icone="#4FC3F7"):
        linha = BoxLayout(
            orientation="horizontal", spacing=dp(10),
            padding=(dp(4), dp(3)),
            size_hint_y=None, height=dp(64),
        )
        linha.add_widget(MDIcon(
            icon=icone, theme_text_color="Custom",
            text_color=get_color_from_hex(cor_icone),
            font_size=sp(22), size_hint=(None, None),
            size=(dp(30), dp(30)),
        ))
        textos = BoxLayout(orientation="vertical", spacing=0)
        textos.add_widget(Label(
            text=titulo, font_size=sp(14), bold=True,
            color=get_color_from_hex("#ECEFF1"),
            halign="left", valign="middle",
        ))
        textos.add_widget(Label(
            text=subtitulo, font_size=sp(10),
            color=get_color_from_hex("#78909C"),
            halign="left", valign="middle",
        ))
        linha.add_widget(textos)
        linha.add_widget(self._registrar_switch(
            EstadoSwitch(
                active=active, callback=callback,
                size_hint=(None, None),
                width=dp(68), height=dp(52),
            )
        ))
        return linha

    def criar_card_som(self):
        card = self._card()
        card.add_widget(self._titulo_card(
            "speaker", "Sistema de som", "ENTRADA • VOLUME", "#64B5F6"
        ))
        card.add_widget(self._registrar(MaterialButton(
            text="Ligar / desligar", icon="power",
            bg_color="#7F1D1D",
            callback=lambda *_: self.app.executar(self.app.som_power),
            fonte=15, height=dp(62),
        )))
        card.add_widget(Label(
            text="ENTRADA", font_size=sp(10), bold=True,
            color=get_color_from_hex("#78909C"),
            size_hint_y=None, height=dp(20),
            halign="left", valign="middle",
        ))
        entradas = BoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint_y=None, height=dp(62),
        )
        for nome, icone, cor in (
            ("Bluetooth", "bluetooth", "#1565C0"),
            ("Coaxial", "import", "#455A64"),
            ("Óptico", "audio-video", "#6A1B9A"),
        ):
            entradas.add_widget(self._registrar(MaterialButton(
                text=nome, icon=icone, bg_color=cor,
                callback=lambda _, n=nome: self.app.executar(self.app.som_entrada, n),
                fonte=12, height=dp(62),
            )))
        card.add_widget(entradas)

        volume_linha = BoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint_y=None, height=dp(48),
        )
        volume_linha.add_widget(MDIcon(
            icon="volume-medium", theme_text_color="Custom",
            text_color=get_color_from_hex("#90A4AE"),
            font_size=sp(21), size_hint=(None, None),
            size=(dp(28), dp(28)),
        ))
        self.texto_volume = Label(
            text=self.app.volume_text(), font_size=sp(28), bold=True,
            color=get_color_from_hex("#FFFFFF"),
            halign="left", valign="middle",
        )
        self.texto_volume.bind(size=self.texto_volume.setter("text_size"))
        volume_linha.add_widget(self.texto_volume)
        card.add_widget(volume_linha)

        controles = BoxLayout(
            orientation="horizontal", spacing=dp(10),
            size_hint_y=None, height=dp(68),
        )
        controles.add_widget(self._registrar(MaterialIconButton(
            "volume-minus", callback=lambda *_: self.app.executar(self.app.som_volume, -5),
            bg_color="#263238", size=(dp(68), dp(68)), size_hint=(1, None),
        )))
        controles.add_widget(self._registrar(MaterialIconButton(
            "volume-plus", callback=lambda *_: self.app.executar(self.app.som_volume, 5),
            bg_color="#263238", size=(dp(68), dp(68)), size_hint=(1, None),
        )))
        card.add_widget(controles)
        self._ajustar_altura_card(card)
        return card

    def criar_card_tv(self):
        card = self._card()
        card.add_widget(self._titulo_card(
            "television", "Televisão", "CONTROLE REMOTO", "#81C784"
        ))
        topo = BoxLayout(
            orientation="horizontal", spacing=dp(10),
            size_hint_y=None, height=dp(62),
        )
        topo.add_widget(self._registrar(MaterialButton(
            text="Power", icon="power", bg_color="#7F1D1D",
            callback=lambda *_: self.app.executar(self.app.tv_comando, "TV_Liga_Desliga"),
            height=dp(62),
        )))
        topo.add_widget(self._registrar(MaterialButton(
            text="Home", icon="home-outline", bg_color="#3949AB",
            callback=lambda *_: self.app.executar(self.app.tv_comando, "TV_Command_Home"),
            height=dp(62),
        )))
        card.add_widget(topo)

        grade = GridLayout(
            cols=3, rows=3, spacing=dp(7),
            size_hint_y=None, height=dp(225),
        )
        comandos = (
            None, ("arrow-up", "TV_Cursor_Cima"), None,
            ("arrow-left", "TV_Cursor_Esquerda"),
            ("check", "TV_Command_OK"),
            ("arrow-right", "TV_Cursor_Direita"),
            None, ("arrow-down", "TV_Cursor_Baixo"), None,
        )
        for item in comandos:
            if item is None:
                grade.add_widget(Spacer())
                continue
            icone, comando = item
            grade.add_widget(self._registrar(MaterialIconButton(
                icone,
                callback=lambda _, c=comando: self.app.executar(self.app.tv_comando, c),
                bg_color="#1976D2" if comando == "TV_Command_OK" else "#263238",
                size=(dp(70), dp(70)),
                size_hint=(1, 1),
            )))
        card.add_widget(grade)
        card.add_widget(self._registrar(MaterialButton(
            text="Voltar", icon="keyboard-return", bg_color="#37474F",
            callback=lambda *_: self.app.executar(self.app.tv_comando, "TV_Command_Return"),
            height=dp(62),
        )))
        self._ajustar_altura_card(card)
        return card

    def criar_card_ar(self):
        card = self._card()
        card.add_widget(self._titulo_card(
            "snowflake", "Ar-condicionado", "TEMPERATURA • FUNÇÕES", "#4DD0E1"
        ))
        estado_ar = self.app.cfg.estado["ar_condicionado"]

        card.add_widget(self._linha_switch(
            "power", "Power", "Ligado / desligado",
            bool(estado_ar.get("ligado", False)),
            lambda *_: self.app.executar(self.app.ar_power),
            "#EF5350",
        ))
        card.add_widget(self._linha_switch(
            "lightbulb-outline", "Luzes do display", "Display ligado / desligado",
            bool(estado_ar.get("display_ligado", True)),
            lambda *_: self.app.executar(self.app.ar_display),
            "#FFD54F",
        ))
        card.add_widget(self._linha_switch(
            "fan", "WindFree", "Fluxo WindFree ligado / desligado",
            bool(estado_ar.get("windfree_ligado", False)),
            lambda *_: self.app.executar(self.app.ar_windfree),
            "#4DD0E1",
        ))

        card.add_widget(Label(
            text="TEMPERATURA", font_size=sp(10), bold=True,
            color=get_color_from_hex("#78909C"),
            size_hint_y=None, height=dp(20),
            halign="center", valign="middle",
        ))
        self.texto_temp = Label(
            text=self.app.temp_text(), font_size=sp(43), bold=True,
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None, height=dp(68),
            halign="center", valign="middle",
        )
        self.texto_temp.bind(size=self.texto_temp.setter("text_size"))
        card.add_widget(self.texto_temp)

        temperatura = BoxLayout(
            orientation="horizontal", spacing=dp(10),
            size_hint_y=None, height=dp(70),
        )
        temperatura.add_widget(self._registrar(MaterialIconButton(
            "minus", callback=lambda *_: self.app.executar(self.app.ar_temp, -1),
            bg_color="#1565C0", size=(dp(70), dp(70)), size_hint=(1, None),
        )))
        temperatura.add_widget(self._registrar(MaterialIconButton(
            "plus", callback=lambda *_: self.app.executar(self.app.ar_temp, 1),
            bg_color="#7F1D1D", size=(dp(70), dp(70)), size_hint=(1, None),
        )))
        card.add_widget(temperatura)
        self._ajustar_altura_card(card)
        return card

    @staticmethod
    def _ajustar_altura_card(card):
        card.height = (
            sum(child.height for child in card.children)
            + card.padding[1] + card.padding[3]
            + card.spacing * max(0, len(card.children) - 1)
        )

    def atualizar_controles_habilitados(self):
        disponivel = self.controladores_prontos
        for botao in self._botoes_comando:
            botao.disabled = not disponivel
        for switch in self._switches_estado:
            switch.disabled = not disponivel
        if disponivel:
            self.status_icon.icon = "wifi"
            self.status_icon.text_color = get_color_from_hex("#4FC3F7")
        else:
            self.status_icon.icon = "wifi-off"
            self.status_icon.text_color = get_color_from_hex("#EF5350")

    def _sincronizar_switches(self):
        if len(self._switches_estado) < 3:
            return
        estado = self.app.cfg.estado["ar_condicionado"]
        self._switches_estado[0].active = bool(estado.get("ligado", False))
        self._switches_estado[1].active = bool(estado.get("display_ligado", True))
        self._switches_estado[2].active = bool(estado.get("windfree_ligado", False))

    def atualizar(self, mensagem=""):
        self.status.text = mensagem
        if hasattr(self, "texto_volume"):
            self.texto_volume.text = self.app.volume_text()
        if hasattr(self, "texto_temp"):
            self.texto_temp.text = self.app.temp_text()
        self._sincronizar_switches()
        self.atualizar_controles_habilitados()
