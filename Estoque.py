"""
estoque.py
Coração do sistema. Gerencia duas estruturas de dados em memória:
  - vetor_nao_ordenado: inserção por append (O(1)), busca linear por nome (O(n)).
  - vetor_ordenado:     mantido ordenado por código a cada operação (O(n) inserção/remoção),
                        com busca binária por código (O(log n)).
"""

from datetime import datetime
from typing import Optional

from produto import Produto


# ---------------------------------------------------------------------------
# Helpers de log
# ---------------------------------------------------------------------------

def _log(operacao: str, detalhe: str = "") -> None:
    """Imprime uma linha de log com timestamp para operações críticas."""
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg = f"[LOG {ts}] {operacao}"
    if detalhe:
        msg += f" — {detalhe}"
    print(msg)


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class Estoque:
    def __init__(self) -> None:
        # Vetor não ordenado: nova chegada sempre vai para o final.
        self._vetor_nao_ordenado: list[Produto] = []

        # Vetor ordenado por código: mantido em ordem crescente o tempo todo.
        self._vetor_ordenado: list[Produto] = []

    # =======================================================================
    # Propriedades de acesso somente leitura
    # =======================================================================

    @property
    def vetor_ordenado(self) -> list[Produto]:
        return self._vetor_ordenado

    @property
    def vetor_nao_ordenado(self) -> list[Produto]:
        return self._vetor_nao_ordenado

    def total_produtos(self) -> int:
        return len(self._vetor_ordenado)

    # =======================================================================
    # CADASTRAR PRODUTO
    # =======================================================================

    def cadastrar(self, produto: Produto) -> None:
        """
        Cadastra um produto nos dois vetores.
        - Vetor não ordenado: append (O(1)).
        - Vetor ordenado: inserção na posição correta com shift (O(n)).
        Lança ValueError se o código já existir.
        """
        if self._busca_binaria(produto.codigo) != -1:
            raise ValueError(f"Código {produto.codigo} já cadastrado.")

        # 1. Vetor não ordenado — simplesmente adiciona ao final
        self._vetor_nao_ordenado.append(produto)

        # 2. Vetor ordenado — encontra posição correta e faz shift
        self._inserir_ordenado(produto)

        _log("CADASTRO", f"Produto '{produto.nome}' (cód. {produto.codigo})")

    def _inserir_ordenado(self, produto: Produto) -> None:
        """
        Insere `produto` no vetor ordenado mantendo a ordem por código.
        Usa busca linear para encontrar a posição e shift manual dos elementos.
        Complexidade: O(n).
        """
        vetor = self._vetor_ordenado
        n = len(vetor)

        # Encontra a posição de inserção
        pos = n  # padrão: insere no final
        for i in range(n):
            if produto.codigo < vetor[i].codigo:
                pos = i
                break

        # Adiciona uma posição extra ao final (sentinela temporária)
        vetor.append(produto)  # aumenta o tamanho; será sobrescrito

        # Shift dos elementos à direita para abrir espaço em `pos`
        for i in range(n, pos, -1):
            vetor[i] = vetor[i - 1]

        vetor[pos] = produto

    # =======================================================================
    # REMOVER PRODUTO
    # =======================================================================

    def remover(self, codigo: int) -> Produto:
        """
        Remove o produto de ambos os vetores pelo código.
        - Vetor ordenado: busca binária + shift (O(n)).
        - Vetor não ordenado: busca linear + remoção (O(n)).
        Lança KeyError se não encontrado.
        """
        idx_ord = self._busca_binaria(codigo)
        if idx_ord == -1:
            raise KeyError(f"Produto com código {codigo} não encontrado.")

        produto = self._vetor_ordenado[idx_ord]

        # 1. Remove do vetor ordenado com shift
        self._remover_ordenado(idx_ord)

        # 2. Remove do vetor não ordenado com busca linear
        self._remover_nao_ordenado(codigo)

        _log("REMOÇÃO", f"Produto '{produto.nome}' (cód. {codigo})")
        return produto

    def _remover_ordenado(self, idx: int) -> None:
        """Shift para preencher o espaço vazio no vetor ordenado. O(n)."""
        vetor = self._vetor_ordenado
        n = len(vetor)
        for i in range(idx, n - 1):
            vetor[i] = vetor[i + 1]
        vetor.pop()  # remove o último elemento duplicado

    def _remover_nao_ordenado(self, codigo: int) -> None:
        """Busca linear e remoção no vetor não ordenado. O(n)."""
        vetor = self._vetor_nao_ordenado
        for i in range(len(vetor)):
            if vetor[i].codigo == codigo:
                # Substitui pelo último e remove o final (O(1) final, O(n) busca)
                vetor[i] = vetor[-1]
                vetor.pop()
                return

    # =======================================================================
    # EDITAR PRODUTO
    # =======================================================================

    def editar(
        self,
        codigo: int,
        nome: Optional[str] = None,
        categoria: Optional[str] = None,
        preco: Optional[float] = None,
        quantidade: Optional[int] = None,
    ) -> Produto:
        """
        Edita campos de um produto buscado pelo código.
        Utiliza busca binária para localizar no vetor ordenado,
        depois localiza no não ordenado por busca linear.
        """
        idx_ord = self._busca_binaria(codigo)
        if idx_ord == -1:
            raise KeyError(f"Produto com código {codigo} não encontrado.")

        produto = self._vetor_ordenado[idx_ord]

        # Aplica as alterações com re-validação
        if nome is not None:
            produto.nome = nome.strip()
            produto._validar_nome()
        if categoria is not None:
            produto.categoria = categoria.strip()
            produto._validar_categoria()
        if preco is not None:
            produto.preco = preco
            produto._validar_preco()
        if quantidade is not None:
            produto.quantidade = quantidade
            produto._validar_quantidade()

        # O objeto é compartilhado entre os dois vetores (referência),
        # portanto não é necessário atualizar o vetor não ordenado separadamente.

        _log("EDIÇÃO", f"Produto cód. {codigo} atualizado")
        return produto

    # =======================================================================
    # BUSCA BINÁRIA — vetor ordenado por código  O(log n)
    # =======================================================================

    def _busca_binaria(self, codigo: int) -> int:
        """
        Retorna o índice do produto no vetor ordenado ou -1 se não encontrado.
        Complexidade: O(log n).
        """
        vetor = self._vetor_ordenado
        esquerda, direita = 0, len(vetor) - 1

        while esquerda <= direita:
            meio = (esquerda + direita) // 2
            if vetor[meio].codigo == codigo:
                return meio
            elif vetor[meio].codigo < codigo:
                esquerda = meio + 1
            else:
                direita = meio - 1

        return -1

    def buscar_por_codigo(self, codigo: int) -> Optional[Produto]:
        """Interface pública para busca por código (usa busca binária)."""
        idx = self._busca_binaria(codigo)
        return self._vetor_ordenado[idx] if idx != -1 else None

    # =======================================================================
    # BUSCA LINEAR — vetor não ordenado por nome  O(n)
    # =======================================================================

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        """
        Busca linear no vetor não ordenado.
        Retorna todos os produtos cujo nome contenha a substring (case-insensitive).
        Complexidade: O(n).
        """
        nome_lower = nome.strip().lower()
        resultados: list[Produto] = []
        for produto in self._vetor_nao_ordenado:
            if nome_lower in produto.nome.lower():
                resultados.append(produto)
        return resultados

    # =======================================================================
    # REGISTRAR VENDA
    # =======================================================================

    def registrar_venda(self, codigo: int, quantidade: int) -> Produto:
        """
        Registra uma venda: valida estoque e decrementa a quantidade.
        Lança KeyError se não encontrado, ValueError se estoque insuficiente.
        """
        if quantidade <= 0:
            raise ValueError("Quantidade vendida deve ser positiva.")

        produto = self.buscar_por_codigo(codigo)
        if produto is None:
            raise KeyError(f"Produto com código {codigo} não encontrado.")

        if produto.quantidade < quantidade:
            raise ValueError(
                f"Estoque insuficiente. Disponível: {produto.quantidade}, "
                f"solicitado: {quantidade}."
            )

        produto.quantidade -= quantidade
        _log(
            "VENDA",
            f"{quantidade}x '{produto.nome}' (cód. {codigo}) | "
            f"Estoque restante: {produto.quantidade}",
        )
        return produto

    # =======================================================================
    # LISTAGENS E RELATÓRIOS
    # =======================================================================

    def listar_por_codigo(self) -> list[Produto]:
        """Retorna o vetor já ordenado por código."""
        return list(self._vetor_ordenado)

    def listar_por_categoria(self, categoria: str) -> list[Produto]:
        """Filtro linear no vetor não ordenado. O(n)."""
        cat = categoria.strip().lower()
        return [p for p in self._vetor_nao_ordenado if p.categoria.lower() == cat]

    def relatorio_estoque_baixo(self, limite: int = 5) -> list[Produto]:
        """Retorna produtos com quantidade abaixo do limite. O(n)."""
        return [p for p in self._vetor_ordenado if p.quantidade < limite]

    # =======================================================================
    # CARGA DE DADOS (usado por arquivos.py)
    # =======================================================================

    def carregar_lista(self, produtos: list[Produto]) -> None:
        """Popula os dois vetores a partir de uma lista (ex.: carregada do disco)."""
        self._vetor_nao_ordenado.clear()
        self._vetor_ordenado.clear()
        for produto in produtos:
            self._vetor_nao_ordenado.append(produto)
            self._inserir_ordenado(produto)