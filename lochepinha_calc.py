import tkinter as tk


# ==============================================================================
# LÓGICA DE CÁLCULO (Separada da interface gráfica)
# ==============================================================================

def calcular(operando1: float, operando2: float, operador: str) -> float:
    """Executa a operação matemática básica entre dois números."""
    if operador == "+":
        return operando1 + operando2
    elif operador == "-":
        return operando1 - operando2
    elif operador == "×":
        return operando1 * operando2
    elif operador == "÷":
        if operando2 == 0:
            raise ZeroDivisionError("Divisão por zero não é permitida.")
        return operando1 / operando2
    else:
        raise ValueError(f"Operador desconhecido: {operador}")


def calcular_porcentagem(valor: float, base: float = None, operador: str = None) -> float:
    """Calcula a porcentagem respeitando o contexto da operação.

    - Se houver soma (+) ou subtração (-) com uma base anterior (ex: 200 + 10%),
      calcula a porcentagem relativa à base (10% de 200 = 20).
    - Caso contrário (ex: 50%, ou 200 × 10%), converte para o valor centesimal direto (10 / 100 = 0.1).
    """
    if base is not None and operador in ("+", "-"):
        return base * (valor / 100)
    return valor / 100


def formatar_numero(valor: float) -> str:
    """Evita dízimas estranhas por imprecisão binária e remove .0 de inteiros."""
    valor_arredondado = round(valor, 8)
    if valor_arredondado.is_integer():
        return str(int(valor_arredondado))
    return str(valor_arredondado)


# ==============================================================================
# INTERFACE GRÁFICA COM TKINTER
# ==============================================================================

class ChepasCalc:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ChepasCalc")
        self.root.geometry("340x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E2E")

        # Variáveis de estado da calculadora
        self.primeiro_numero = None
        self.operador_atual = None
        self.aguardando_proximo_numero = False
        self.em_estado_de_erro = False

        # Configuração visual
        self._configurar_interface()

    def _configurar_interface(self):
        """Cria e posiciona o visor e o teclado de botões."""
        # Painel do Visor
        frame_visor = tk.Frame(self.root, bg="#1E1E2E", padx=15, pady=15)
        frame_visor.pack(fill="x")

        # Rótulo de histórico (mostra a operação anterior, ex: "5 +")
        self.lbl_historico = tk.Label(
            frame_visor,
            text="",
            font=("Segoe UI", 11),
            fg="#A6ADC8",
            bg="#181825",
            anchor="e",
            padx=10
        )
        self.lbl_historico.pack(fill="x")

        # Visor principal (mostra o número digitado ou resultado)
        self.lbl_visor = tk.Label(
            frame_visor,
            text="0",
            font=("Segoe UI", 26, "bold"),
            fg="#CDD6F4",
            bg="#181825",
            anchor="e",
            padx=10,
            pady=8
        )
        self.lbl_visor.pack(fill="x")

        # Painel de Botões
        frame_botoes = tk.Frame(self.root, bg="#1E1E2E", padx=15, pady=5)
        frame_botoes.pack(fill="both", expand=True)

        for col in range(4):
            frame_botoes.columnconfigure(col, weight=1)
        for lin in range(5):
            frame_botoes.rowconfigure(lin, weight=1)

        # Paleta de cores moderna
        c_num_bg = "#313244"
        c_num_fg = "#CDD6F4"
        c_op_bg = "#45475A"
        c_op_fg = "#89B4FA"
        c_limpar_bg = "#E78284"
        c_limpar_fg = "#1E1E2E"
        c_igual_bg = "#A6E3A1"
        c_igual_fg = "#1E1E2E"

        # Definição do layout: (Texto, Linha, Coluna, Colspan, Rowspan, Cor_BG, Cor_FG)
        botoes = [
            ("C", 0, 0, 1, 1, c_limpar_bg, c_limpar_fg),
            ("%", 0, 1, 1, 1, c_op_bg, c_op_fg),
            ("÷", 0, 2, 1, 1, c_op_bg, c_op_fg),
            ("×", 0, 3, 1, 1, c_op_bg, c_op_fg),

            ("7", 1, 0, 1, 1, c_num_bg, c_num_fg),
            ("8", 1, 1, 1, 1, c_num_bg, c_num_fg),
            ("9", 1, 2, 1, 1, c_num_bg, c_num_fg),
            ("-", 1, 3, 1, 1, c_op_bg, c_op_fg),

            ("4", 2, 0, 1, 1, c_num_bg, c_num_fg),
            ("5", 2, 1, 1, 1, c_num_bg, c_num_fg),
            ("6", 2, 2, 1, 1, c_num_bg, c_num_fg),
            ("+", 2, 3, 1, 1, c_op_bg, c_op_fg),

            ("1", 3, 0, 1, 1, c_num_bg, c_num_fg),
            ("2", 3, 1, 1, 1, c_num_bg, c_num_fg),
            ("3", 3, 2, 1, 1, c_num_bg, c_num_fg),
            ("=", 3, 3, 1, 2, c_igual_bg, c_igual_fg),

            ("0", 4, 0, 2, 1, c_num_bg, c_num_fg),
            (".", 4, 2, 1, 1, c_num_bg, c_num_fg),
        ]

        for texto, linha, col, colspan, rowspan, bg, fg in botoes:
            btn = tk.Button(
                frame_botoes,
                text=texto,
                font=("Segoe UI", 13, "bold"),
                bg=bg,
                fg=fg,
                activebackground=fg,
                activeforeground=bg,
                bd=0,
                relief="flat",
                command=lambda t=texto: self._ao_pressionar_botao(t)
            )
            btn.grid(
                row=linha,
                column=col,
                columnspan=colspan,
                rowspan=rowspan,
                padx=4,
                pady=4,
                sticky="nsew"
            )

    # ==========================================================================
    # MANIPULAÇÃO DE EVENTOS E FLUXO DA APLICAÇÃO
    # ==========================================================================

    def _ao_pressionar_botao(self, caractere: str):
        """Roteia a ação do botão clicado para a rotina correspondente."""
        if caractere.isdigit():
            self._adicionar_digito(caractere)
        elif caractere == ".":
            self._adicionar_ponto()
        elif caractere in ("+", "-", "×", "÷"):
            self._selecionar_operador(caractere)
        elif caractere == "%":
            self._aplicar_porcentagem()
        elif caractere == "=":
            self._concluir_calculo()
        elif caractere == "C":
            self._limpar_tudo()

    def _adicionar_digito(self, digito: str):
        """Insere um novo dígito no visor."""
        if self.em_estado_de_erro or self.aguardando_proximo_numero:
            self.lbl_visor.config(text=digito)
            self.aguardando_proximo_numero = False
            self.em_estado_de_erro = False
        else:
            texto_atual = self.lbl_visor.cget("text")
            if texto_atual == "0":
                self.lbl_visor.config(text=digito)
            else:
                self.lbl_visor.config(text=texto_atual + digito)

    def _adicionar_ponto(self):
        """Adiciona o ponto decimal, garantindo que não ocorram repetições."""
        if self.em_estado_de_erro or self.aguardando_proximo_numero:
            self.lbl_visor.config(text="0.")
            self.aguardando_proximo_numero = False
            self.em_estado_de_erro = False
            return

        texto_atual = self.lbl_visor.cget("text")
        if "." not in texto_atual:
            self.lbl_visor.config(text=texto_atual + ".")

    def _selecionar_operador(self, operador: str):
        """Salva o primeiro número e prepara a calculadora para o segundo."""
        if self.em_estado_de_erro:
            return

        # Permite trocar de operador caso o usuário ainda não tenha digitado o segundo número
        if self.aguardando_proximo_numero and self.primeiro_numero is not None:
            self.operador_atual = operador
            self.lbl_historico.config(
                text=f"{formatar_numero(self.primeiro_numero)} {self.operador_atual}"
            )
            return

        # Se já existe um cálculo em aberto, calcula o resultado parcial antes
        if self.primeiro_numero is not None and self.operador_atual is not None:
            if not self._processar_operacao():
                return

        try:
            self.primeiro_numero = float(self.lbl_visor.cget("text"))
            self.operador_atual = operador
            self.aguardando_proximo_numero = True
            self.lbl_historico.config(
                text=f"{formatar_numero(self.primeiro_numero)} {self.operador_atual}"
            )
        except ValueError:
            self._exibir_erro("Entrada inválida")

    def _aplicar_porcentagem(self):
        """Aplica o cálculo de porcentagem sobre o valor exibido no visor."""
        if self.em_estado_de_erro:
            return

        try:
            valor_atual = float(self.lbl_visor.cget("text"))
            resultado = calcular_porcentagem(valor_atual, self.primeiro_numero, self.operador_atual)
            self.lbl_visor.config(text=formatar_numero(resultado))

            # Se a porcentagem foi chamada de forma avulsa (sem operador pendente),
            # o próximo dígito digitado deve iniciar um novo número.
            if self.operador_atual is None:
                self.aguardando_proximo_numero = True
        except ValueError:
            self._exibir_erro("Entrada inválida")

    def _concluir_calculo(self):
        """Finaliza a operação atual ao pressionar o botão de igual (=)."""
        if self.em_estado_de_erro or self.primeiro_numero is None or self.operador_atual is None:
            return

        if self._processar_operacao():
            self.lbl_historico.config(text="")
            self.primeiro_numero = None
            self.operador_atual = None
            self.aguardando_proximo_numero = True

    def _processar_operacao(self) -> bool:
        """Executa a lógica matemática e atualiza a interface."""
        try:
            segundo_numero = float(self.lbl_visor.cget("text"))
            resultado = calcular(self.primeiro_numero, segundo_numero, self.operador_atual)
            self.lbl_visor.config(text=formatar_numero(resultado))
            self.primeiro_numero = resultado
            return True
        except ZeroDivisionError:
            self._exibir_erro("Divisão por 0")
            return False
        except Exception:
            self._exibir_erro("Erro de cálculo")
            return False

    def _limpar_tudo(self):
        """Restaura o estado inicial da calculadora."""
        self.primeiro_numero = None
        self.operador_atual = None
        self.aguardando_proximo_numero = False
        self.em_estado_de_erro = False
        self.lbl_visor.config(text="0")
        self.lbl_historico.config(text="")

    def _exibir_erro(self, mensagem: str):
        """Atualiza a tela com o erro ocorrido e bloqueia novos passos até o reset."""
        self.lbl_visor.config(text=f"Erro: {mensagem}")
        self.lbl_historico.config(text="")
        self.primeiro_numero = None
        self.operador_atual = None
        self.em_estado_de_erro = True


# ==============================================================================
# PONTO DE ENTRADA DO PROGRAMA
# ==============================================================================

if __name__ == "__main__":
    janela_principal = tk.Tk()
    app = ChepasCalc(janela_principal)
    janela_principal.mainloop()
