from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivymd.app import MDApp

from config.configuracoes import Configuracoes
from core.controlador_ir import ControladorIR
from core.controle_som import ControleSom
from core.controle_tv import ControleTV
from core.controle_ar import ControleAr
from ui.tela_principal import TelaPrincipal
from ui.tela_configuracoes import TelaConfiguracoes


class DirectLinkMobileApp(MDApp):
    def build(self):
        self.title = "DirectLink Mobile"

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        Window.clearcolor = self.theme_cls.bg_dark

        self.cfg = Configuracoes()

        # Comunicação IR e controles são inicializados depois da UI.
        self.ir = None
        self.som = None
        self.tv = None
        self.ar = None

        self.ui = TelaPrincipal(self)

        # Deixa a primeira renderização acontecer antes da inicialização Tuya.
        Clock.schedule_once(self.inicializar_controladores, 0.15)

        return self.ui

    def inicializar_controladores(self, *_):
        try:
            self.mostrar_status("Conectando ao controlador IR...")

            self.ir = ControladorIR(self.cfg)

            if self.ir.erro:
                raise RuntimeError(self.ir.erro)

            self.som = ControleSom(self.cfg, self.ir)
            self.tv = ControleTV(self.ir)
            self.ar = ControleAr(self.cfg, self.ir)

            self.ui.controladores_prontos = True
            self.ui.atualizar_controles_habilitados()
            self.ui.atualizar("Conectado")

        except Exception as erro:
            self.ui.controladores_prontos = False
            self.ui.atualizar_controles_habilitados()
            self.mostrar_status("Falha na conexão")
            self.exibir_popup_erro(
                "Falha na inicialização",
                str(erro)
            )

    def abrir_configuracoes(self):
        TelaConfiguracoes(self).open()

    def controladores_disponiveis(self):
        return all(
            (
                self.ir is not None,
                self.som is not None,
                self.tv is not None,
                self.ar is not None,
            )
        )

    def executar(self, funcao, *args):
        if not self.controladores_disponiveis():
            self.mostrar_status(
                "Aguarde a conexão com o controlador IR."
            )
            return

        try:
            funcao(*args)
            self.ui.atualizar("Comando enviado")

        except Exception as erro:
            self.mostrar_status("Falha ao executar comando")
            self.exibir_popup_erro("Erro", str(erro))

    def mostrar_status(self, mensagem):
        if getattr(self, "ui", None) is not None:
            self.ui.atualizar(mensagem)

    def exibir_popup_erro(self, titulo, mensagem):
        conteudo = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(14)
        )

        texto = Label(
            text=str(mensagem),
            halign="center",
            valign="middle"
        )
        texto.bind(size=texto.setter("text_size"))

        fechar = Label(
            text="FECHAR",
            size_hint_y=None,
            height=dp(48),
            halign="center",
            valign="middle"
        )

        from kivy.uix.button import Button
        botao = Button(
            text="Fechar",
            size_hint_y=None,
            height=dp(50)
        )

        conteudo.add_widget(texto)
        conteudo.add_widget(botao)

        popup = Popup(
            title=titulo,
            content=conteudo,
            size_hint=(0.88, 0.42),
            auto_dismiss=False
        )

        botao.bind(on_release=popup.dismiss)
        popup.open()

    def volume_text(self):
        volume = self.cfg.estado["som"].get("volume", 45)
        return f"{volume}%"

    def temp_text(self):
        temperatura = self.cfg.estado["ar_condicionado"].get(
            "temperatura_atual_configurada",
            24
        )
        return f"{temperatura}°"

    def som_power(self):
        self.som.power()

    def som_entrada(self, nome):
        self.som.entrada(nome)

    def som_volume(self, delta):
        self.som.volume(delta)

    def tv_comando(self, comando):
        self.tv.comando(comando)

    def ar_power(self):
        self.ar.alterar(
            ligado=not self.ar.estado["ligado"]
        )

    def ar_temp(self, delta):
        atual = int(
            self.ar.estado.get(
                "temperatura_atual_configurada",
                24
            )
        )
        nova = max(16, min(30, atual + delta))

        if nova != atual:
            self.ar.alterar(
                temperatura_atual_configurada=nova
            )

    def ar_windfree(self):
        self.ar.alterar(
            windfree_ligado=not self.ar.estado["windfree_ligado"]
        )

    def ar_display(self):
        self.ar.alterar(
            display_ligado=not self.ar.estado["display_ligado"]
        )


if __name__ == "__main__":
    DirectLinkMobileApp().run()
