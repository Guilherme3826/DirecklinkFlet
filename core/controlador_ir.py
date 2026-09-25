import json

from tinytuya.Contrib.IRRemoteControlDevice import (
    IRRemoteControlDevice
)


class ControladorIR:

    def __init__(self, config):
        self.config = config
        self.erro = None
        self.dispositivo = None
        self.codigos = {}

        ambiente = config.ambiente

        try:
            # Resolve o caminho físico somente internamente.
            # O JSON continua contendo apenas "codigos_ir.json".
            caminho_json = config.obter_caminho_codigos_ir()

            if not caminho_json.exists():
                raise FileNotFoundError(
                    "Arquivo codigos_ir.json não encontrado."
                )

            self.codigos = json.loads(
                caminho_json.read_text(
                    encoding="utf-8"
                )
            )

            self.dispositivo = IRRemoteControlDevice(
                ambiente["tuya_device_id"],
                ambiente["tuya_ip"],
                ambiente["tuya_local_key"],
                version=ambiente.get(
                    "tuya_version",
                    3.3
                ),
                persist=ambiente.get(
                    "tuya_persist",
                    True
                ),
                control_type=ambiente.get(
                    "tuya_control_type",
                    1
                )
            )

        except Exception as erro:
            self.erro = str(erro)
            self.dispositivo = None

    def enviar(self, nome):
        if self.dispositivo is None:
            raise RuntimeError(
                self.erro or "Dispositivo IR indisponível."
            )

        codigo = self.codigos.get(nome)

        if codigo is None:
            raise KeyError(
                f"Comando '{nome}' não encontrado "
                "no arquivo codigos_ir.json."
            )

        try:
            return self.dispositivo.send_button(
                codigo
            )

        except Exception as erro:
            self.erro = str(erro)

            raise RuntimeError(
                f"Erro ao enviar o comando IR '{nome}': "
                f"{erro}"
            ) from erro