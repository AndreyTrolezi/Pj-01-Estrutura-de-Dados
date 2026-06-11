"""
main.py
Menu interativo em linha de comando para o Sistema de Estoque e Vendas.
Toda entrada do usuário é tratada com try/except para evitar quebras.
"""

import os
from pathlib import Path

from produto import Produto
from estoque import Estoque
from arquivos import salvar, carregar

ARQUIVO_DADOS = Path("produtos.json")
LIMITE_ESTOQUE_BAIXO_PADRAO = 5

# ---------------------------------------------------------------------------
# Utilitários de I/O
# ---------------------------------------------------------------------------

def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def linha(char: str = "─", largura: int = 65) -> None:
    print(char * largura)


def cabecalho(titulo: str) -> None:
    limpar_tela()
    linha("═")
    print(f"  🗃  SISTEMA DE ESTOQUE E VENDAS  —  {titulo}")
    linha("═")


def pausar() -> None:
    input("\n  Pressione ENTER para continuar...")


def ler_inteiro(prompt: str, minimo: int = 1) -> int:
    """Lê um inteiro >= minimo; lança ValueError em caso de entrada inválida."""
    valor = input(prompt).strip()
    if not valor:
        raise ValueError("Campo obrigatório não pode ser vazio.")
    num = int(valor)  # lança ValueError automaticamente se não for número
    if num < minimo:
        raise ValueError(f"O valor deve ser >= {minimo}.")
    return num


def ler_float(prompt: str, minimo: float = 0.01) -> float:
    """Lê um float >= minimo; lança ValueError em caso de entrada inválida."""
    valor = input(prompt).strip().replace(",", ".")
    if not valor:
        raise ValueError("Campo obrigatório não pode ser vazio.")
    num = float(valor)
    if num < minimo:
        raise ValueError(f"O valor deve ser >= {minimo}.")
    return num


def ler_str(prompt: str) -> str:
    """Lê uma string não vazia."""
    valor = input(prompt).strip()
    if not valor:
        raise ValueError("Campo obrigatório não pode ser vazio.")
    return valor


# ---------------------------------------------------------------------------
# Ações do menu
# ---------------------------------------------------------------------------

def acao_cadastrar(estoque: Estoque) -> None:
    cabecalho("CADASTRAR PRODUTO")
    try:
        codigo    = ler_inteiro("  Código (inteiro positivo): ")
        nome      = ler_str    ("  Nome: ")
        categoria = ler_str    ("  Categoria: ")
        preco     = ler_float  ("  Preço (R$): ")
        quantidade = ler_inteiro("  Quantidade inicial: ", minimo=0)

        produto = Produto(codigo, nome, categoria, preco, quantidade)
        estoque.cadastrar(produto)
        print(f"\n  ✔ Produto cadastrado com sucesso!\n  {produto}")
    except (ValueError, KeyError) as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_editar(estoque: Estoque) -> None:
    cabecalho("EDITAR PRODUTO")
    try:
        codigo = ler_inteiro("  Código do produto a editar: ")
        produto = estoque.buscar_por_codigo(codigo)
        if produto is None:
            print(f"\n  ✖ Produto com código {codigo} não encontrado.")
            pausar()
            return

        print(f"\n  Produto atual:\n  {produto}")
        print("\n  Deixe em branco para manter o valor atual.")

        # Leitura opcional de cada campo
        nome_novo      = input(f"  Novo nome [{produto.nome}]: ").strip() or None
        cat_nova       = input(f"  Nova categoria [{produto.categoria}]: ").strip() or None
        preco_str      = input(f"  Novo preço [{produto.preco:.2f}]: ").strip().replace(",", ".")
        preco_novo     = float(preco_str) if preco_str else None
        qtd_str        = input(f"  Nova quantidade [{produto.quantidade}]: ").strip()
        qtd_nova       = int(qtd_str) if qtd_str else None

        estoque.editar(
            codigo,
            nome=nome_novo,
            categoria=cat_nova,
            preco=preco_novo,
            quantidade=qtd_nova,
        )
        produto_atualizado = estoque.buscar_por_codigo(codigo)
        print(f"\n  ✔ Produto atualizado!\n  {produto_atualizado}")
    except (ValueError, KeyError) as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_remover(estoque: Estoque) -> None:
    cabecalho("REMOVER PRODUTO")
    try:
        codigo = ler_inteiro("  Código do produto a remover: ")
        produto = estoque.buscar_por_codigo(codigo)
        if produto is None:
            print(f"\n  ✖ Produto com código {codigo} não encontrado.")
            pausar()
            return

        print(f"\n  Produto encontrado:\n  {produto}")
        confirmacao = input("\n  Confirmar remoção? (s/N): ").strip().lower()
        if confirmacao == "s":
            estoque.remover(codigo)
            print("  ✔ Produto removido com sucesso.")
        else:
            print("  Operação cancelada.")
    except (ValueError, KeyError) as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_buscar_codigo(estoque: Estoque) -> None:
    cabecalho("BUSCAR POR CÓDIGO  [Busca Binária O(log n)]")
    try:
        codigo = ler_inteiro("  Código a buscar: ")
        produto = estoque.buscar_por_codigo(codigo)
        if produto:
            print(f"\n  ✔ Produto encontrado:\n  {produto}")
        else:
            print(f"\n  ✖ Nenhum produto com código {codigo}.")
    except ValueError as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_buscar_nome(estoque: Estoque) -> None:
    cabecalho("BUSCAR POR NOME  [Busca Linear O(n)]")
    try:
        nome = ler_str("  Nome (ou parte do nome): ")
        resultados = estoque.buscar_por_nome(nome)
        if resultados:
            print(f"\n  ✔ {len(resultados)} produto(s) encontrado(s):")
            linha()
            for p in resultados:
                print(f"  {p}")
        else:
            print(f"\n  ✖ Nenhum produto encontrado para '{nome}'.")
    except ValueError as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_registrar_venda(estoque: Estoque) -> None:
    cabecalho("REGISTRAR VENDA")
    try:
        codigo     = ler_inteiro("  Código do produto: ")
        quantidade = ler_inteiro("  Quantidade vendida: ")
        produto    = estoque.registrar_venda(codigo, quantidade)
        print(
            f"\n  ✔ Venda registrada!\n"
            f"  Produto: {produto.nome}\n"
            f"  Qtd vendida: {quantidade} | Estoque restante: {produto.quantidade}"
        )
    except (ValueError, KeyError) as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_listar_por_codigo(estoque: Estoque) -> None:
    cabecalho("LISTAR PRODUTOS — ordenado por código")
    produtos = estoque.listar_por_codigo()
    if not produtos:
        print("  Estoque vazio.")
    else:
        linha()
        print(f"  {'CÓD':>6}  {'NOME':<30}  {'CATEGORIA':<15}  {'PREÇO':>10}  {'QTD':>5}")
        linha()
        for p in produtos:
            print(f"  {p}")
        linha()
        print(f"  Total: {len(produtos)} produto(s).")
    pausar()


def acao_listar_por_categoria(estoque: Estoque) -> None:
    cabecalho("LISTAR POR CATEGORIA")
    try:
        categoria = ler_str("  Categoria: ")
        produtos  = estoque.listar_por_categoria(categoria)
        if not produtos:
            print(f"\n  ✖ Nenhum produto na categoria '{categoria}'.")
        else:
            linha()
            for p in produtos:
                print(f"  {p}")
            linha()
            print(f"  Total: {len(produtos)} produto(s).")
    except ValueError as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_estoque_baixo(estoque: Estoque) -> None:
    cabecalho("RELATÓRIO — ESTOQUE BAIXO")
    try:
        limite_str = input(
            f"  Limite de quantidade (padrão {LIMITE_ESTOQUE_BAIXO_PADRAO}): "
        ).strip()
        limite = int(limite_str) if limite_str else LIMITE_ESTOQUE_BAIXO_PADRAO
        if limite < 0:
            raise ValueError("Limite deve ser >= 0.")

        produtos = estoque.relatorio_estoque_baixo(limite)
        if not produtos:
            print(f"\n  ✔ Nenhum produto abaixo de {limite} unidade(s).")
        else:
            print(f"\n  ⚠  {len(produtos)} produto(s) com estoque < {limite}:")
            linha()
            for p in produtos:
                print(f"  {p}")
    except ValueError as exc:
        print(f"\n  ✖ Erro: {exc}")
    pausar()


def acao_salvar(estoque: Estoque) -> None:
    cabecalho("SALVAR DADOS")
    salvar(estoque, ARQUIVO_DADOS)
    pausar()


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------

MENU = """
  ┌─────────────────────────────────────────┐
  │         SISTEMA DE ESTOQUE E VENDAS     │
  ├─────────────────────────────────────────┤
  │  1. Cadastrar produto                   │
  │  2. Editar produto                      │
  │  3. Remover produto                     │
  │  4. Buscar por código  (binária)        │
  │  5. Buscar por nome    (linear)         │
  │  6. Registrar venda                     │
  │  7. Listar por código                   │
  │  8. Listar por categoria                │
  │  9. Relatório: estoque baixo            │
  │ 10. Salvar dados                        │
  │  0. Sair (salva automaticamente)        │
  └─────────────────────────────────────────┘
  Opção: """


def menu_principal() -> None:
    estoque = Estoque()

    # Tenta carregar dados existentes ao iniciar
    limpar_tela()
    linha("═")
    print("  🗃  SISTEMA DE ESTOQUE E VENDAS — INICIANDO")
    linha("═")
    carregar(estoque, ARQUIVO_DADOS)
    pausar()

    acoes = {
        "1":  lambda: acao_cadastrar(estoque),
        "2":  lambda: acao_editar(estoque),
        "3":  lambda: acao_remover(estoque),
        "4":  lambda: acao_buscar_codigo(estoque),
        "5":  lambda: acao_buscar_nome(estoque),
        "6":  lambda: acao_registrar_venda(estoque),
        "7":  lambda: acao_listar_por_codigo(estoque),
        "8":  lambda: acao_listar_por_categoria(estoque),
        "9":  lambda: acao_estoque_baixo(estoque),
        "10": lambda: acao_salvar(estoque),
    }

    while True:
        limpar_tela()
        opcao = input(MENU).strip()

        if opcao == "0":
            salvar(estoque, ARQUIVO_DADOS)
            print("\n  Até logo! 👋\n")
            break

        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print(f"\n  ✖ Opção '{opcao}' inválida. Tente novamente.")
            pausar()


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    menu_principal()