class ControleSom:
    def __init__(self, cfg, ir):
        self.cfg = cfg
        self.ir = ir
        self.estado = cfg.estado["som"]

    def power(self):
        self.ir.enviar("EDF_Ligar/Desligar")

        self.cfg.atualizar_estado(
            "som",
            ligado=not self.estado["ligado"]
        )

    def entrada(self, nome):
        comandos = {
            "Bluetooth": "EDF_Bluetooth",
            "Coaxial": "EDF_Coaxial",

            # Nome usado pela interface.
            "Óptico": "EDF_Optico",

            # Aceita também a grafia sem acento.
            "Optico": "EDF_Optico",

            # Caso queira manter compatibilidade com versões anteriores.
            "Óptico": "EDF_Optico"
        }

        comando = comandos.get(nome)

        if comando is None:
            raise KeyError(
                f"Entrada de som '{nome}' não possui comando configurado."
            )

        self.ir.enviar(comando)

        self.cfg.atualizar_estado(
            "som",
            entrada=nome
        )

    def volume(self, delta):
        if delta == 0:
            return

        volume_atual = int(
            self.estado.get("volume", 45)
        )

        novo = max(
            0,
            min(100, volume_atual + delta)
        )

        comando = (
            "EDF_AumentarVolume"
            if delta > 0
            else "EDF_DiminuirVolume"
        )

        # Só altera o estado se o comando IR for enviado.
        self.ir.enviar(comando)

        self.cfg.atualizar_estado(
            "som",
            volume=novo
        )