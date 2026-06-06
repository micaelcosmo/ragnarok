"""Fonte local: lê os JSON curados de backend/data/ (conteúdo SRD offline)."""
import json
from pathlib import Path

from app.content.base import ContentSource
from app.models.reference import FONTE_PADRAO

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Mapa tipo -> arquivo JSON em data/.
_ARQUIVOS = {
    "races": "races.json",
    "classes": "classes.json",
    "backgrounds": "backgrounds.json",
    "spells": "spells.json",
    "monsters": "monsters.json",
    "feats": "feats.json",
}


class LocalSource(ContentSource):
    """Conteúdo curado embutido. Sempre disponível (não precisa de internet)."""

    @property
    def nome(self) -> str:
        return FONTE_PADRAO

    def buscar(self, tipo: str) -> list[dict]:
        arquivo = _ARQUIVOS.get(tipo)
        if not arquivo:
            return []
        caminho = DATA_DIR / arquivo
        if not caminho.exists():
            return []
        with caminho.open(encoding="utf-8") as conteudo:
            registros = json.load(conteudo)
        # Os JSON já estão no schema canônico; garante a fonte padrão.
        for registro in registros:
            registro.setdefault("fonte", FONTE_PADRAO)
        return registros
