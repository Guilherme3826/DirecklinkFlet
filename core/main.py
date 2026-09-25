from kivy.app import App
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from config.configuracoes import Configuracoes
from core.controlador_ir import ControladorIR
from core.controle_som import ControleSom
from core.controle_tv import ControleTV
from core.controle_ar import ControleAr
from ui.tela_principal import TelaPrincipal

class DirectLinkMobileApp(App):
 def build(self):
  Window.clearcolor=get_color_from_hex("#121212"); self.title="DirectLink Mobile"
  self.cfg=Configuracoes(); self.ir=ControladorIR(self.cfg); self.som=ControleSom(self.cfg,self.ir); self.tv=ControleTV(self.ir); self.ar=ControleAr(self.cfg,self.ir)
  self.ui=TelaPrincipal(self)
  if self.ir.erro: self.ui.erro("Falha na inicialização",self.ir.erro)
  return self.ui
 def executar(self,fn):
  try: fn(); self.ui.atualizar("Comando enviado.")
  except Exception as e: self.ui.atualizar("Falha ao executar comando."); self.ui.erro("Erro",str(e))
 def volume_text(self): return f"Volume: {self.cfg.estado['som']['volume']}%"
 def temp_text(self): return f"{self.cfg.estado['ar_condicionado']['temperatura_atual_configurada']} °C"
 def som_power(self): self.som.power()
 def som_entrada(self,n): self.som.entrada(n)
 def som_volume(self,d): self.som.volume(d)
 def tv_comando(self,n): self.tv.comando(n)
 def ar_power(self): self.ar.alterar(ligado=not self.ar.estado["ligado"])
 def ar_temp(self,d):
  t=max(16,min(30,self.ar.estado["temperatura_atual_configurada"]+d)); self.ar.alterar(temperatura_atual_configurada=t)
 def ar_windfree(self): self.ar.alterar(windfree_ligado=not self.ar.estado["windfree_ligado"])
 def ar_display(self): self.ar.alterar(display_ligado=not self.ar.estado["display_ligado"])
if __name__=="__main__": DirectLinkMobileApp().run()
