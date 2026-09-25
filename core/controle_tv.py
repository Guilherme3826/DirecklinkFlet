class ControleTV:
    def __init__(self,ir): self.ir=ir
    def comando(self,nome): self.ir.enviar(nome)
