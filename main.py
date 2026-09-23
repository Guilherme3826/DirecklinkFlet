import os
import json
import tinytuya
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# ==========================================
# CONFIGURAÇÕES DO DISPOSITIVO TUYA IR
# ==========================================
IP_DISPOSITIVO = os.environ.get("TUYA_IP", "192.168.18.237")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID", "eb840a19823cfd2ef6dafd")
LOCAL_KEY = os.environ.get("TUYA_LOCAL_KEY", "AXd8$9h(b[3t}DZ~")
CAMINHO_JSON = "codigos_ir.json"

def carregar_codigos():
    """Carrega o dicionário de códigos IR do arquivo JSON, com log de erros."""
    if os.path.exists(CAMINHO_JSON):
        try:
            with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar '{CAMINHO_JSON}': {e}")
            return {}
    print(f"[AVISO] Arquivo '{CAMINHO_JSON}' não encontrado. Nenhum código carregado.")
    return {}

class DirectLinkMobileApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex("#121212")
        self.title = "DirectLink Mobile"

        # Estados e instâncias
        self.estado_ac = {
            "is_ac_on": False,
            "is_display_on": True,
            "is_windfree_on": False,
            "ac_temperature": 24,
        }
        self.estado_som = {"volume": 45}
        
        self.codigos = carregar_codigos()
        
        try:
            self.ir_device = tinytuya.Contrib.IRRemoteControlDevice(
                DEVICE_ID, IP_DISPOSITIVO, LOCAL_KEY, version=3.3, persist=True
            )
        except Exception as e:
            print(f"[ERRO] Falha ao inicializar dispositivo IR: {e}")
            self.ir_device = None

        # Elementos de UI
        self.status_text = Label(text="", font_size=14, color=get_color_from_hex("#E57373"), size_hint_y=None, height=30)
        self.texto_temp = Label(text=f"{self.estado_ac['ac_temperature']} °C", font_size=48, bold=True, size_hint_x=None, width=120)
        self.texto_volume = Label(text=f"{self.estado_som['volume']}%", font_size=28, bold=True, size_hint_x=None, width=100)

        # Montagem do Layout Principal
        scroll = ScrollView(size_hint=(1, 1))
        main_layout = BoxLayout(orientation='vertical', padding=24, spacing=20, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        main_layout.add_widget(self.status_text)
        main_layout.add_widget(self.criar_card_som())
        main_layout.add_widget(self.criar_card_tv())
        main_layout.add_widget(self.criar_card_ac())

        scroll.add_widget(main_layout)
        return scroll

    def mostrar_status(self, msg: str):
        self.status_text.text = msg

    def enviar_comando(self, nome_comando):
        codigo_base64 = self.codigos.get(nome_comando)
        if not self.ir_device:
            print("[AVISO] Dispositivo IR não inicializado.")
            self.mostrar_status("Dispositivo IR indisponível.")
            return
        if not codigo_base64:
            print(f"[AVISO] Comando '{nome_comando}' não encontrado no JSON.")
            self.mostrar_status(f"Comando '{nome_comando}' não encontrado.")
            return
        try:
            self.ir_device.send_button(codigo_base64)
            print(f"Comando enviado: {nome_comando}")
            self.mostrar_status("")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar comando '{nome_comando}': {e}")
            self.mostrar_status("Falha ao enviar comando (dispositivo offline?).")

    # ==========================================
    # LÓGICAS DO AR-CONDICIONADO
    # ==========================================
    def sincronizar_estado_ac(self):
        if not self.estado_ac["is_ac_on"]:
            self.enviar_comando("AC_Desligar")
            return

        temp = str(self.estado_ac["ac_temperature"])
        wf = self.estado_ac["is_windfree_on"]
        disp = self.estado_ac["is_display_on"]

        if not wf and not disp:
            comando = f"AC_WindFreeOff_DisplayOff_T{temp}"
        elif wf and not disp:
            comando = f"AC_WindFreeOn_DisplayOff_T{temp}"
        elif not wf and disp:
            comando = f"AC_WindFreeOff_DisplayOn_T{temp}"
        else:
            comando = f"AC_WindFreeOn_DisplayOn_T{temp}"

        self.enviar_comando(comando)

    def toggle_ac_power(self, instance):
        self.estado_ac["is_ac_on"] = not self.estado_ac["is_ac_on"]
        self.sincronizar_estado_ac()

    def toggle_ac_lights(self, instance):
        self.estado_ac["is_display_on"] = not self.estado_ac["is_display_on"]
        if self.estado_ac["is_ac_on"]:
            self.sincronizar_estado_ac()

    def toggle_windfree(self, instance):
        self.estado_ac["is_windfree_on"] = not self.estado_ac["is_windfree_on"]
        if self.estado_ac["is_ac_on"]:
            self.sincronizar_estado_ac()

    def increase_temp(self, instance):
        if self.estado_ac["ac_temperature"] < 30:
            self.estado_ac["ac_temperature"] += 1
            self.texto_temp.text = f"{self.estado_ac['ac_temperature']} °C"
            if self.estado_ac["is_ac_on"]:
                self.sincronizar_estado_ac()

    def decrease_temp(self, instance):
        if self.estado_ac["ac_temperature"] > 16:
            self.estado_ac["ac_temperature"] -= 1
            self.texto_temp.text = f"{self.estado_ac['ac_temperature']} °C"
            if self.estado_ac["is_ac_on"]:
                self.sincronizar_estado_ac()

    # ==========================================
    # LÓGICAS DO SOM
    # ==========================================
    def increase_volume(self, instance):
        if self.estado_som["volume"] < 100:
            self.estado_som["volume"] += 5
            self.texto_volume.text = f"{self.estado_som['volume']}%"
            self.enviar_comando("EDF_AumentarVolume")

    def decrease_volume(self, instance):
        if self.estado_som["volume"] > 0:
            self.estado_som["volume"] -= 5
            self.texto_volume.text = f"{self.estado_som['volume']}%"
            self.enviar_comando("EDF_DiminuirVolume")

    # ==========================================
    # CONSTRUÇÃO DA INTERFACE (UI KIVY)
    # ==========================================
    def criar_card_som(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=220)
        
        layout.add_widget(Label(text="SISTEMA DE SOM", bold=True, size_hint_y=None, height=30))
        layout.add_widget(Button(text="Ligar / Desligar Sistema", on_press=lambda x: self.enviar_comando("EDF_LigarDesligar"), size_hint_y=None, height=40))
        
        layout.add_widget(Label(text="Modo de Entrada", color=get_color_from_hex("#9E9E9E"), size_hint_y=None, height=20))
        botoes_entrada = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        botoes_entrada.add_widget(Button(text="Bluetooth", on_press=lambda x: self.enviar_comando("EDF_Bluetooth")))
        botoes_entrada.add_widget(Button(text="Coaxial", on_press=lambda x: self.enviar_comando("EDF_Coaxial")))
        botoes_entrada.add_widget(Button(text="Óptico", on_press=lambda x: self.enviar_comando("EDF_Optico")))
        layout.add_widget(botoes_entrada)

        layout.add_widget(Label(text="Volume", color=get_color_from_hex("#9E9E9E"), size_hint_y=None, height=20))
        controles_volume = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        controles_volume.add_widget(Button(text="-", font_size=24, on_press=self.decrease_volume))
        controles_volume.add_widget(self.texto_volume)
        controles_volume.add_widget(Button(text="+", font_size=24, on_press=self.increase_volume))
        layout.add_widget(controles_volume)
        
        return layout

    def criar_card_tv(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=300)
        
        layout.add_widget(Label(text="TELEVISÃO", bold=True, size_hint_y=None, height=30))
        
        botoes_topo = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        botoes_topo.add_widget(Button(text="Power", on_press=lambda x: self.enviar_comando("TV_Liga_Desliga")))
        botoes_topo.add_widget(Button(text="Menu", on_press=lambda x: self.enviar_comando("TV_Command_Home")))
        layout.add_widget(botoes_topo)

        # D-Pad Simulado
        dpad = GridLayout(cols=3, rows=3, size_hint_y=None, height=150, spacing=5)
        dpad.add_widget(Label(text="")) # Vazio superior esquerdo
        dpad.add_widget(Button(text="Cima", on_press=lambda x: self.enviar_comando("TV_Cursor_Cima")))
        dpad.add_widget(Label(text="")) # Vazio superior direito
        
        dpad.add_widget(Button(text="Esq", on_press=lambda x: self.enviar_comando("TV_Cursor_Esquerda")))
        dpad.add_widget(Button(text="OK", on_press=lambda x: self.enviar_comando("TV_Command_OK")))
        dpad.add_widget(Button(text="Dir", on_press=lambda x: self.enviar_comando("TV_Cursor_Direita")))
        
        dpad.add_widget(Label(text="")) # Vazio inferior esquerdo
        dpad.add_widget(Button(text="Baixo", on_press=lambda x: self.enviar_comando("TV_Cursor_Baixo")))
        dpad.add_widget(Label(text="")) # Vazio inferior direito
        layout.add_widget(dpad)

        layout.add_widget(Button(text="Voltar", on_press=lambda x: self.enviar_comando("TV_Command_Return"), size_hint_y=None, height=40))
        
        return layout

    def criar_card_ac(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=200)
        
        layout.add_widget(Label(text="AR-CONDICIONADO", bold=True, size_hint_y=None, height=30))
        
        botoes_topo = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        botoes_topo.add_widget(Button(text="Ligar AC", on_press=self.toggle_ac_power))
        botoes_topo.add_widget(Button(text="Luzes", on_press=self.toggle_ac_lights))
        layout.add_widget(botoes_topo)

        controles_temp = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        controles_temp.add_widget(Button(text="-", font_size=36, on_press=self.decrease_temp))
        controles_temp.add_widget(self.texto_temp)
        controles_temp.add_widget(Button(text="+", font_size=36, on_press=self.increase_temp))
        layout.add_widget(controles_temp)

        layout.add_widget(Button(text="Ativar WindFree", on_press=self.toggle_windfree, size_hint_y=None, height=40))
        
        return layout

if __name__ == "__main__":
    DirectLinkMobileApp().run()