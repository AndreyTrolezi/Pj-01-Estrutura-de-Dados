"""
arquivos.py
Funções de persistência: salvar e carregar o estoque em formato JSON.
Utiliza apenas a biblioteca padrão do Python (json, os, pathlib).

"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from produto import Produto

if TYPE_CHECKING:
    from estoque import Estoque

ARQUIVO_PADRAO = Path("produtos.json")


# ---------------------------------------------------------------------------
# Salvar
# ---------------------------------------------------------------------------

def salvar(estoque: "Estoque", caminho: Path = ARQUIVO_PADRAO) -> None:
    """
    Serializa todos os produtos do estoque em JSON e grava no arquivo.
    Usa o vetor ordenado para que o arquivo já fique organizado por código.

    Args:
        estoque: instância de Estoque com os dados em memória.
        caminho: caminho do arquivo de destino (padrão: produtos.json).
    """
    dados = [produto.to_dict() for produto in estoque.vetor_ordenado]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    print(f"✔ Dados salvos em '{caminho}' ({len(dados)} produto(s)).")


# ---------------------------------------------------------------------------
# Carregar
# ---------------------------------------------------------------------------

def carregar(estoque: "Estoque", caminho: Path = ARQUIVO_PADRAO) -> int:
    """
    Lê o arquivo JSON e popula o estoque com os produtos encontrados.

    Args:
        estoque: instância de Estoque a ser populada.
        caminho: caminho do arquivo de origem (padrão: produtos.json).

    Returns:
        Número de produtos carregados. Retorna 0 se o arquivo não existir.
    """
    if not os.path.exists(caminho):
        print(f"⚠ Arquivo '{caminho}' não encontrado. Iniciando com estoque vazio.")
        return 0

    with open(caminho, "r", encoding="utf-8") as arquivo:
        try:
            dados: list[dict] = json.load(arquivo)
        except json.JSONDecodeError as exc:
            print(f"✖ Erro ao ler '{caminho}': {exc}. Iniciando com estoque vazio.")
            return 0

    produtos: list[Produto] = []
    erros = 0
    for i, item in enumerate(dados):
        try:
            produtos.append(Produto.from_dict(item))
        except (KeyError, ValueError) as exc:
            print(f"  ⚠ Registro {i + 1} ignorado: {exc}")
            erros += 1

    estoque.carregar_lista(produtos)
    print(
        f"✔ {len(produtos)} produto(s) carregado(s) de '{caminho}'"
        + (f" ({erros} ignorado(s) por erro)." if erros else ".")
    )
    return len(produtos)