from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from kivymd.uix.label import MDIcon

from .componentes import ModernButton


class CampoConfiguracao(BoxLayout):
    """
    Campo de configuração otimizado para toque em Android.

    Cada configuração ocupa uma linha vertical completa:
    ícone + título + campo de entrada.
    """

    def __init__(
        self,
        chave,
        legenda,
        valor,
        icone="cog-outline",
        password=False,
        dica="",
        **kwargs
    ):
        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(96),
            **kwargs
        )

        cabecalho = BoxLayout(
            orientation="horizontal",
            spacing=dp(7),
            size_hint_y=None,
            height=dp(26)
        )

        cabecalho.add_widget(
            MDIcon(
                icon=icone,
                theme_text_color="Custom",
                text_color=get_color_from_hex("#64B5F6"),
                font_size=sp(17),
                size_hint=(None, None),
                size=(dp(24), dp(24))
            )
        )

        texto_legenda = Label(
            text=legenda,
            font_size=sp(12),
            bold=True,
            color=get_color_from_hex("#B0BEC5"),
            halign="left",
            valign="middle"
        )
        texto_legenda.bind(
            size=texto_legenda.setter("text_size")
        )

        cabecalho.add_widget(texto_legenda)
        self.add_widget(cabecalho)

        self.entrada = TextInput(
            text=str(valor),
            multiline=False,
            password=password,
            font_size=sp(15),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex("#202A30"),
            foreground_color=get_color_from_hex("#ECEFF1"),
            cursor_color=get_color_from_hex("#64B5F6"),
            selection_color=get_color_from_hex("#296A92"),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            size_hint_y=None,
            height=dp(58)
        )

        self.entrada.bind(
            focus=self._atualizar_borda
        )

        # Dica fica como texto auxiliar dentro do bloco, apenas quando usada.
        if dica:
            self.entrada.hint_text = dica

        self.add_widget(self.entrada)

        with self.canvas.after:
            self._borda_cor = Color(
                *get_color_from_hex("#263238")
            )
            self._borda = Line(
                rounded_rectangle=(
                    0,
                    0,
                    dp(100),
                    dp(58),
                    dp(10)
                ),
                width=0.8
            )

        self.entrada.bind(
            pos=self._atualizar_borda,
            size=self._atualizar_borda
        )

    def _atualizar_borda(self, *_):
        if self.entrada.focus:
            self._borda_cor.rgba = get_color_from_hex(
                "#64B5F6"
            )
            self._borda.width = 1.2
        else:
            self._borda_cor.rgba = get_color_from_hex(
                "#263238"
            )
            self._borda.width = 0.8

        x, y = self.entrada.pos
        w, h = self.entrada.size

        self._borda.rounded_rectangle = (
            x,
            y,
            w,
            h,
            dp(10)
        )


class Separador(Widget):
    def __init__(self, **kwargs):
        super().__init__(
            size_hint_y=None,
            height=dp(1),
            **kwargs
        )

        with self.canvas:
            Color(
                *get_color_from_hex("#263238")
            )
            self.linha = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[(dp(1), dp(1))] * 4
            )

        self.bind(
            pos=self._atualizar,
            size=self._atualizar
        )

    def _atualizar(self, *_):
        self.linha.pos = self.pos
        self.linha.size = self.size


class TelaConfiguracoes(Popup):

    def __init__(self, app, **kwargs):
        self.app = app
        self.inputs = {}

        super().__init__(
            title="",
            size_hint=(0.96, 0.93),
            auto_dismiss=False,
            separator_height=0,
            background="",
            **kwargs
        )

        self.background_color = get_color_from_hex(
            "#11181D"
        )

        principal = BoxLayout(
            orientation="vertical",
            padding=(dp(14), dp(12), dp(14), dp(12)),
            spacing=dp(10)
        )

        # ==============================================================
        # CABEÇALHO
        # ==============================================================

        cabecalho = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(64)
        )

        cabecalho.add_widget(
            MDIcon(
                icon="tune-variant",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#64B5F6"),
                font_size=sp(27),
                size_hint=(None, None),
                size=(dp(36), dp(36))
            )
        )

        titulos = BoxLayout(
            orientation="vertical",
            spacing=0
        )

        titulos.add_widget(
            Label(
                text="CONFIGURAÇÕES",
                font_size=sp(21),
                bold=True,
                color=get_color_from_hex("#E3F2FD"),
                halign="left",
                valign="middle"
            )
        )

        titulos.add_widget(
            Label(
                text="Conexão e parâmetros do dispositivo Tuya",
                font_size=sp(11),
                color=get_color_from_hex("#78909C"),
                halign="left",
                valign="middle"
            )
        )

        cabecalho.add_widget(titulos)

        principal.add_widget(cabecalho)

        # ==============================================================
        # ÁREA ROLÁVEL
        # ==============================================================

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"]
        )

        conteudo = BoxLayout(
            orientation="vertical",
            padding=(dp(2), dp(4), dp(4), dp(12)),
            spacing=dp(11),
            size_hint_y=None
        )
        conteudo.bind(
            minimum_height=conteudo.setter("height")
        )

        ambiente = app.cfg.ambiente

        # ==============================================================
        # SEÇÃO: TUYA
        # ==============================================================

        conteudo.add_widget(
            self._titulo_secao(
                "TUYA",
                "PARÂMETROS DE COMUNICAÇÃO",
                "access-point"
            )
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "tuya_ip",
            "Endereço IP",
            "IP do dispositivo na rede local",
            "192.168.0.188",
            "lan-connect"
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "tuya_device_id",
            "Device ID",
            "Identificador exclusivo do dispositivo",
            "Device ID",
            "identifier"
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "tuya_local_key",
            "Local Key",
            "Chave local usada para comunicação",
            "Local Key",
            "key-variant",
            password=True
        )

        # ==============================================================
        # SEÇÃO: PROTOCOLO
        # ==============================================================

        conteudo.add_widget(
            Separador()
        )

        conteudo.add_widget(
            self._titulo_secao(
                "PROTOCOLO",
                "PARÂMETROS DO TINYTUYA",
                "tune"
            )
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "tuya_version",
            "Versão Tuya",
            "Versão do protocolo",
            "3.3",
            "numeric-3-box"
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "tuya_control_type",
            "Tipo de controle",
            "Tipo utilizado pelo dispositivo IR",
            "1",
            "remote"
        )

        # ==============================================================
        # SEÇÃO: ARQUIVO IR
        # ==============================================================

        conteudo.add_widget(
            Separador()
        )

        conteudo.add_widget(
            self._titulo_secao(
                "CÓDIGOS IR",
                "ARQUIVO UTILIZADO PELO CONTROLE",
                "file-code-outline"
            )
        )

        self._adicionar_campo(
            conteudo,
            ambiente,
            "caminho_codigos_ir",
            "Arquivo de códigos IR",
            "Nome relativo do arquivo de comandos",
            "codigos_ir.json",
            "file-code"
        )

        aviso = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            padding=(dp(10), dp(8)),
            size_hint_y=None,
            height=dp(58)
        )

        with aviso.canvas.before:
            Color(
                *get_color_from_hex("#17252D")
            )
            self._aviso_fundo = RoundedRectangle(
                pos=aviso.pos,
                size=aviso.size,
                radius=[(dp(10), dp(10))] * 4
            )

        aviso.bind(
            pos=lambda *_: self._atualizar_fundo(
                aviso,
                self._aviso_fundo
            ),
            size=lambda *_: self._atualizar_fundo(
                aviso,
                self._aviso_fundo
            )
        )

        aviso.add_widget(
            MDIcon(
                icon="information-outline",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#4FC3F7"),
                font_size=sp(18),
                size_hint=(None, None),
                size=(dp(26), dp(26))
            )
        )

        aviso.add_widget(
            Label(
                text=(
                    "Use somente o nome do arquivo. "
                    "Não informe caminhos absolutos."
                ),
                font_size=sp(11),
                color=get_color_from_hex("#90A4AE"),
                halign="left",
                valign="middle"
            )
        )

        conteudo.add_widget(aviso)

        scroll.add_widget(conteudo)
        principal.add_widget(scroll)

        # ==============================================================
        # AÇÕES
        # ==============================================================

        botoes = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(62)
        )

        botoes.add_widget(
            ModernButton(
                text="Cancelar",
                bg_color="#37474F",
                font_size=sp(15),
                size_hint_y=None,
                height=dp(62),
                on_press=lambda *_:
                    self.dismiss()
            )
        )

        botoes.add_widget(
            ModernButton(
                text="Salvar configurações",
                bg_color="#1976D2",
                font_size=sp(15),
                size_hint_y=None,
                height=dp(62),
                on_press=self.salvar
            )
        )

        principal.add_widget(botoes)

        self.content = principal

    # ==================================================================
    # HELPERS
    # ==================================================================

    def _titulo_secao(self, titulo, subtitulo, icone):
        bloco = BoxLayout(
            orientation="horizontal",
            spacing=dp(9),
            size_hint_y=None,
            height=dp(42)
        )

        bloco.add_widget(
            MDIcon(
                icon=icone,
                theme_text_color="Custom",
                text_color=get_color_from_hex("#4FC3F7"),
                font_size=sp(20),
                size_hint=(None, None),
                size=(dp(28), dp(28))
            )
        )

        textos = BoxLayout(
            orientation="vertical",
            spacing=0
        )

        textos.add_widget(
            Label(
                text=titulo,
                font_size=sp(13),
                bold=True,
                color=get_color_from_hex("#ECEFF1"),
                halign="left",
                valign="middle"
            )
        )

        textos.add_widget(
            Label(
                text=subtitulo,
                font_size=sp(9),
                color=get_color_from_hex("#607D8B"),
                halign="left",
                valign="middle"
            )
        )

        bloco.add_widget(textos)

        return bloco

    def _adicionar_campo(
        self,
        conteudo,
        ambiente,
        chave,
        legenda,
        descricao,
        placeholder,
        icone,
        password=False
    ):
        campo = CampoConfiguracao(
            chave=chave,
            legenda=legenda,
            valor=ambiente.get(chave, ""),
            icone=icone,
            password=password,
            dica=placeholder
        )

        self.inputs[chave] = campo.entrada

        conteudo.add_widget(campo)

    @staticmethod
    def _atualizar_fundo(widget, fundo):
        fundo.pos = widget.pos
        fundo.size = widget.size

    # ==================================================================
    # SALVAR
    # ==================================================================

    def salvar(self, *_):
        try:
            ip = self.inputs["tuya_ip"].text.strip()
            device_id = self.inputs["tuya_device_id"].text.strip()
            local_key = self.inputs["tuya_local_key"].text
            versao_texto = self.inputs["tuya_version"].text.strip()
            control_type_texto = (
                self.inputs["tuya_control_type"].text.strip()
            )
            caminho_ir = (
                self.inputs["caminho_codigos_ir"].text.strip()
            )

            if not ip:
                raise ValueError(
                    "O endereço IP não pode ficar vazio."
                )

            if not device_id:
                raise ValueError(
                    "O Device ID não pode ficar vazio."
                )

            if not local_key:
                raise ValueError(
                    "A Local Key não pode ficar vazia."
                )

            if not versao_texto:
                raise ValueError(
                    "Informe a versão do protocolo Tuya."
                )

            if not control_type_texto:
                raise ValueError(
                    "Informe o tipo de controle."
                )

            if not caminho_ir:
                caminho_ir = "codigos_ir.json"

            # Mantém somente o nome do arquivo.
            caminho_ir = caminho_ir.replace("\\", "/")
            caminho_ir = caminho_ir.split("/")[-1]

            versao = float(
                versao_texto.replace(",", ".")
            )

            control_type = int(
                control_type_texto
            )

            self.app.cfg.atualizar_ambiente(
                tuya_ip=ip,
                tuya_device_id=device_id,
                tuya_local_key=local_key,
                tuya_version=versao,
                tuya_control_type=control_type,
                caminho_codigos_ir=caminho_ir
            )

            self.app.mostrar_status(
                "Configurações salvas. "
                "Reinicie o aplicativo para reconectar."
            )

            self.dismiss()

        except Exception as exc:
            self.app.exibir_popup_erro(
                "Erro ao salvar",
                (
                    "Não foi possível salvar as configurações.\n\n"
                    f"{exc}"
                )
            )
