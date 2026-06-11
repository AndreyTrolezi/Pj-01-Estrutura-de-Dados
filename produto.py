"""
produto.py
Definição da classe Produto com atributos e validações de regras de negócio.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Produto:
    codigo: int
    nome: str
    categoria: str
    preco: float
    quantidade: int

    def __post_init__(self) -> None:
        self.validar()

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------
    def validar(self) -> None:
        """Valida todas as regras de negócio do produto."""
        self._validar_codigo()
        self._validar_nome()
        self._validar_categoria()
        self._validar_preco()
        self._validar_quantidade()

    def _validar_codigo(self) -> None:
        if not isinstance(self.codigo, int) or self.codigo <= 0:
            raise ValueError(f"Código inválido: '{self.codigo}'. Deve ser um inteiro positivo.")

    def _validar_nome(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("Nome inválido: não pode ser vazio.")
        self.nome = self.nome.strip()

    def _validar_categoria(self) -> None:
        if not isinstance(self.categoria, str) or not self.categoria.strip():
            raise ValueError("Categoria inválida: não pode ser vazia.")
        self.categoria = self.categoria.strip()

    def _validar_preco(self) -> None:
        if not isinstance(self.preco, (int, float)) or self.preco <= 0:
            raise ValueError(f"Preço inválido: '{self.preco}'. Deve ser um número positivo.")

    def _validar_quantidade(self) -> None:
        if not isinstance(self.quantidade, int) or self.quantidade < 0:
            raise ValueError(f"Quantidade inválida: '{self.quantidade}'. Deve ser um inteiro não-negativo.")

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Serializa o produto para dicionário (usado na persistência)."""
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "quantidade": self.quantidade,
        }

    @staticmethod
    def from_dict(dados: dict) -> "Produto":
        """Cria um Produto a partir de um dicionário."""
        return Produto(
            codigo=int(dados["codigo"]),
            nome=str(dados["nome"]),
            categoria=str(dados["categoria"]),
            preco=float(dados["preco"]),
            quantidade=int(dados["quantidade"]),
        )

    def __str__(self) -> str:
        return (
            f"[{self.codigo:>6}] {self.nome:<30} | "
            f"Cat: {self.categoria:<15} | "
            f"R$ {self.preco:>8.2f} | "
            f"Qtd: {self.quantidade:>5}"
        )