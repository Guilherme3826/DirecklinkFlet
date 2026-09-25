class ControleAr:
    def __init__(self, cfg, ir):
        self.cfg = cfg
        self.ir = ir
        self.estado = cfg.estado["ar_condicionado"]

    # ==============================================================
    # COMANDO COMPLETO DO AR
    # ==============================================================

    def _comando_estado_atual(self, temperatura=None):
        """
        Monta o nome do comando IR usando:

        - temperatura atual
        - estado do WindFree
        - estado do Display

        Exemplo:
            Ac_WindFreeOn_DisplayOn_T24
        """

        if temperatura is None:
            temperatura = int(
                self.estado.get(
                    "temperatura_atual_configurada",
                    24
                )
            )

        windfree = bool(
            self.estado.get(
                "windfree_ligado",
                False
            )
        )

        display = bool(
            self.estado.get(
                "display_ligado",
                True
            )
        )

        # WindFree OFF + Display OFF
        if not windfree and not display:
            return (
                f"AC_WindFreeOFF_DisplayOFF_T{temperatura}"
            )

        # WindFree ON + Display OFF
        if windfree and not display:
            return (
                f"AC_WindFreeOn_DisplayOff_T{temperatura}"
            )

        # WindFree OFF + Display ON
        if not windfree and display:
            return (
                f"AC_WindFreeOff_DisplayOn_T{temperatura}"
            )

        # WindFree ON + Display ON
        return (
            f"Ac_WindFreeOn_DisplayOn_T{temperatura}"
        )

    # ==============================================================
    # ALTERAÇÃO DE ESTADO
    # ==============================================================

    def alterar(self, **mudancas):
        """
        Altera o estado e envia o comando IR correspondente.

        Para mudanças em:
            - display_ligado
            - windfree_ligado
            - temperatura_atual_configurada

        o comando sempre carrega a temperatura atual.

        O estado só é persistido depois que o comando IR foi
        enviado com sucesso.
        """

        estado_novo = dict(self.estado)
        estado_novo.update(mudancas)

        ligado_atual = bool(
            self.estado.get(
                "ligado",
                False
            )
        )

        ligado_novo = bool(
            estado_novo.get(
                "ligado",
                ligado_atual
            )
        )

        # ==========================================================
        # DESLIGAR
        # ==========================================================

        if "ligado" in mudancas and not ligado_novo:
            self.ir.enviar(
                "AC_Desligar"
            )

            self.cfg.atualizar_estado(
                "ar_condicionado",
                **mudancas
            )

            return

        # ==========================================================
        # ALTERAÇÃO DE TEMPERATURA / WINDFREE / DISPLAY
        # ==========================================================

        temperatura = int(
            estado_novo.get(
                "temperatura_atual_configurada",
                24
            )
        )

        # Cria o comando usando o estado NOVO.
        windfree = bool(
            estado_novo.get(
                "windfree_ligado",
                False
            )
        )

        display = bool(
            estado_novo.get(
                "display_ligado",
                True
            )
        )

        if not windfree and not display:
            comando = (
                f"AC_WindFreeOFF_DisplayOFF_T{temperatura}"
            )

        elif windfree and not display:
            comando = (
                f"AC_WindFreeOn_DisplayOff_T{temperatura}"
            )

        elif not windfree and display:
            comando = (
                f"AC_WindFreeOff_DisplayOn_T{temperatura}"
            )

        else:
            comando = (
                f"Ac_WindFreeOn_DisplayOn_T{temperatura}"
            )

        # Envia primeiro.
        self.ir.enviar(comando)

        # Só persiste depois do envio bem-sucedido.
        self.cfg.atualizar_estado(
            "ar_condicionado",
            **mudancas
        )

    # ==============================================================
    # TEMPERATURA
    # ==============================================================

    def temperatura(self, delta):
        atual = int(
            self.estado.get(
                "temperatura_atual_configurada",
                24
            )
        )

        nova = max(
            16,
            min(30, atual + delta)
        )

        if nova == atual:
            return

        self.alterar(
            temperatura_atual_configurada=nova
        )

    # ==============================================================
    # POWER
    # ==============================================================

    def power(self):
        ligado = bool(
            self.estado.get(
                "ligado",
                False
            )
        )

        if ligado:
            self.alterar(
                ligado=False
            )
            return

        # Para ligar, utiliza o estado atual de:
        # temperatura + WindFree + Display.
        temperatura = int(
            self.estado.get(
                "temperatura_atual_configurada",
                24
            )
        )

        windfree = bool(
            self.estado.get(
                "windfree_ligado",
                False
            )
        )

        display = bool(
            self.estado.get(
                "display_ligado",
                True
            )
        )

        # Mantemos a mesma convenção dos códigos existentes.
        if not windfree and display:
            comando = (
                f"AC_Ligar_WindFreeOff_DisplayOn_T{temperatura}"
            )
        else:
            comando = self._comando_estado_atual(
                temperatura
            )

        self.ir.enviar(comando)

        self.cfg.atualizar_estado(
            "ar_condicionado",
            ligado=True
        )