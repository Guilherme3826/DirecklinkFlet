import json
import shutil
from pathlib import Path

from kivy.app import App
from kivy.resources import resource_find
from kivy.utils import platform


class Configuracoes:
    """
    Gerencia configurações e estados persistentes do aplicativo.

    Regras:
    - configuracoes.json é salvo na pasta gravável do aplicativo.
    - codigos_ir.json permanece configurado como caminho relativo.
    - No Android, arquivos graváveis são armazenados em user_data_dir.
    - Nenhum caminho absoluto fixo é gravado no JSON.
    """

    NOME_CONFIGURACOES = "configuracoes.json"
    NOME_CODIGOS_IR = "codigos_ir.json"

    def __init__(self):
        self.diretorio_projeto = Path(__file__).resolve().parent.parent

        app = App.get_running_app()

        if platform == "android" and app is not None:
            self.diretorio_dados = Path(app.user_data_dir)
        else:
            self.diretorio_dados = self.diretorio_projeto

        self.diretorio_config = self.diretorio_dados / "config"
        self.diretorio_config.mkdir(parents=True, exist_ok=True)

        self.caminho_configuracoes = (
            self.diretorio_config / self.NOME_CONFIGURACOES
        )

        self._garantir_configuracoes()

        self.dados = self._ler_configuracoes()

        self._garantir_estrutura_dados()

        # Mantém sempre o valor salvo como caminho relativo.
        caminho_ir = self.ambiente.get(
            "caminho_codigos_ir",
            self.NOME_CODIGOS_IR
        )

        self.ambiente["caminho_codigos_ir"] = (
            Path(caminho_ir).name or self.NOME_CODIGOS_IR
        )

        self._garantir_codigos_ir()

        self.salvar()

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    def _garantir_configuracoes(self):
        """
        Cria configuracoes.json caso ainda não exista.

        No Windows, tenta usar o arquivo presente no projeto.
        No Android, cria uma cópia inicial na pasta de dados do aplicativo.
        """

        if self.caminho_configuracoes.exists():
            return

        configuracao_original = (
            self.diretorio_projeto
            / "config"
            / self.NOME_CONFIGURACOES
        )

        if configuracao_original.exists():
            shutil.copy2(
                configuracao_original,
                self.caminho_configuracoes
            )
        else:
            self.dados = self._padrao()
            self.salvar()

    def _garantir_codigos_ir(self):
        """
        Garante que codigos_ir.json esteja disponível no diretório
        gravável utilizado pelo aplicativo.

        O nome salvo no JSON continua sendo apenas:
            codigos_ir.json
        """

        destino = self.diretorio_dados / self.NOME_CODIGOS_IR

        if destino.exists():
            return

        # Possível localização no diretório raiz do projeto.
        origens_possiveis = [
            self.diretorio_projeto / self.NOME_CODIGOS_IR,
            self.diretorio_projeto / "assets" / self.NOME_CODIGOS_IR,
            self.diretorio_projeto / "data" / self.NOME_CODIGOS_IR,
        ]

        # resource_find também pode localizar arquivos empacotados.
        recurso = resource_find(self.NOME_CODIGOS_IR)

        if recurso:
            origens_possiveis.insert(0, Path(recurso))

        for origem in origens_possiveis:
            if origem.exists() and origem.is_file():
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origem, destino)
                return

    # ------------------------------------------------------------------
    # Valores padrão
    # ------------------------------------------------------------------

    def _padrao(self):
        return {
            "ambiente": {
                "tuya_ip": "192.168.0.188",
                "tuya_device_id": "eb840a19823cfd2ef6dafd",
                "tuya_local_key": "]Ky1/}?'stR&oQwe",
                "tuya_version": 3.3,
                "tuya_persist": True,
                "tuya_control_type": 1,

                # IMPORTANTE:
                # Este valor deve permanecer relativo.
                "caminho_codigos_ir": "codigos_ir.json"
            },

            "estado": {
                "som": {
                    "ligado": False,
                    "entrada": "Bluetooth",
                    "volume": 45
                },

                "televisao": {
                    "ligada": False
                },

                "ar_condicionado": {
                    "ligado": False,
                    "display_ligado": True,
                    "windfree_ligado": False,
                    "temperatura_atual_configurada": 24
                }
            }
        }

    # ------------------------------------------------------------------
    # Leitura e validação
    # ------------------------------------------------------------------

    def _ler_configuracoes(self):
        try:
            with self.caminho_configuracoes.open(
                "r",
                encoding="utf-8"
            ) as arquivo:
                return json.load(arquivo)

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError
        ):
            self.dados = self._padrao()
            self.salvar()
            return self.dados

    def _garantir_estrutura_dados(self):
        padrao = self._padrao()

        if not isinstance(self.dados, dict):
            self.dados = padrao
            return

        self.dados.setdefault("ambiente", {})
        self.dados.setdefault("estado", {})

        for chave, valor in padrao["ambiente"].items():
            self.dados["ambiente"].setdefault(chave, valor)

        for dispositivo, valores in padrao["estado"].items():
            self.dados["estado"].setdefault(dispositivo, {})

            for chave, valor in valores.items():
                self.dados["estado"][dispositivo].setdefault(
                    chave,
                    valor
                )

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def salvar(self):
        """
        Salva o JSON de maneira segura usando arquivo temporário.
        """

        self.caminho_configuracoes.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporario = self.caminho_configuracoes.with_suffix(".tmp")

        temporario.write_text(
            json.dumps(
                self.dados,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temporario.replace(self.caminho_configuracoes)

    # ------------------------------------------------------------------
    # Acesso aos dados
    # ------------------------------------------------------------------

    @property
    def ambiente(self):
        return self.dados["ambiente"]

    @property
    def estado(self):
        return self.dados["estado"]

    def atualizar_ambiente(self, **valores):
        """
        Atualiza configurações do ambiente.

        O caminho de codigos_ir.json é sempre normalizado para
        permanecer relativo.
        """

        if "caminho_codigos_ir" in valores:
            valores["caminho_codigos_ir"] = (
                Path(valores["caminho_codigos_ir"]).name
                or self.NOME_CODIGOS_IR
            )

        self.ambiente.update(valores)
        self.salvar()

    def atualizar_estado(self, dispositivo, **valores):
        if dispositivo not in self.estado:
            self.estado[dispositivo] = {}

        self.estado[dispositivo].update(valores)
        self.salvar()

    def obter_caminho_codigos_ir(self) -> Path:
        """
        Retorna o caminho físico utilizado internamente pelo programa.

        Esse caminho NÃO é gravado no configuracoes.json.
        """

        nome_arquivo = self.ambiente.get(
            "caminho_codigos_ir",
            self.NOME_CODIGOS_IR
        )

        nome_arquivo = Path(nome_arquivo).name

        caminho = self.diretorio_dados / nome_arquivo

        if not caminho.exists():
            self._garantir_codigos_ir()

        return caminho