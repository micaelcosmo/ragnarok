"""Contratos da pipeline de conteúdo: fonte (ContentSource) e relatório (Relatorio)."""
from abc import ABC, abstractmethod

# Tipos de conteúdo suportados pela pipeline.
TIPOS = ("races", "classes", "backgrounds", "spells", "monsters", "feats")


class ContentSource(ABC):
    """
    Fonte de conteúdo. Cada adapter é responsável por buscar e **normalizar** os
    registros para o schema canônico (mesmas chaves dos modelos), retornando dicts.
    """

    #: tipos que esta fonte sabe fornecer (subconjunto de TIPOS)
    tipos_suportados = TIPOS

    @property
    @abstractmethod
    def nome(self) -> str:
        """Rótulo legível da fonte (vira o `fonte` dos registros quando ausente)."""

    @abstractmethod
    def buscar(self, tipo: str) -> list[dict]:
        """Retorna registros canônicos (já normalizados) para o tipo pedido."""

    def suporta(self, tipo: str) -> bool:
        return tipo in self.tipos_suportados


class Relatorio:
    """Acumula contagens da ingestão por tipo."""

    def __init__(self):
        self.por_tipo: dict[str, dict[str, int]] = {}
        self.mensagens: list[str] = []

    def _slot(self, tipo: str) -> dict[str, int]:
        return self.por_tipo.setdefault(
            tipo, {"inseridos": 0, "atualizados": 0, "ignorados": 0}
        )

    def inserido(self, tipo: str):
        self._slot(tipo)["inseridos"] += 1

    def atualizado(self, tipo: str):
        self._slot(tipo)["atualizados"] += 1

    def ignorado(self, tipo: str):
        self._slot(tipo)["ignorados"] += 1

    def total(self, chave: str) -> int:
        return sum(slot[chave] for slot in self.por_tipo.values())

    def to_dict(self) -> dict:
        return {"por_tipo": self.por_tipo, "mensagens": self.mensagens}

    def __str__(self) -> str:
        linhas = ["Relatório de ingestão:"]
        for tipo, slot in self.por_tipo.items():
            linhas.append(
                f"  - {tipo:12} inseridos={slot['inseridos']:4} "
                f"atualizados={slot['atualizados']:4} ignorados={slot['ignorados']:4}"
            )
        for mensagem in self.mensagens:
            linhas.append(f"  · {mensagem}")
        return "\n".join(linhas)
