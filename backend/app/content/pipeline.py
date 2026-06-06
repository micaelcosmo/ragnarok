"""Runner da pipeline: filtra, faz upsert idempotente e gera relatório."""
from sqlalchemy import String

from app.extensions import db
from app.models.items import Arma, Armadura, Item
from app.models.monster import Monstro
from app.models.reference import Antecedente, Classe, Magia, Raca, Talento
from app.content.base import Relatorio


def _ajustar_tamanho(modelo, campo, valor):
    """Trunca strings ao tamanho da coluna (evita StringDataRightTruncation)."""
    if not isinstance(valor, str):
        return valor
    coluna = modelo.__table__.columns.get(campo)
    tipo = getattr(coluna, "type", None)
    limite = getattr(tipo, "length", None) if isinstance(tipo, String) else None
    if limite and len(valor) > limite:
        return valor[: limite - 1] + "…"
    return valor

# Configuração por tipo: modelo + campos canônicos que aceitamos persistir.
TIPOS_CONFIG = {
    "races": (Raca, [
        "slug", "nome", "descricao", "deslocamento", "tamanho",
        "bonus_atributos", "tracos", "subracas",
    ]),
    "classes": (Classe, [
        "slug", "nome", "descricao", "dado_vida", "atributo_principal",
        "salvaguardas", "pericias_disponiveis", "num_pericias",
        "conjurador", "atributo_conjuracao", "proficiencias_armadura", "proficiencias_arma",
    ]),
    "backgrounds": (Antecedente, [
        "slug", "nome", "descricao", "pericias", "idiomas", "equipamento",
    ]),
    "spells": (Magia, [
        "slug", "nome", "nivel", "escola", "tempo_conjuracao", "alcance",
        "componentes", "duracao", "concentracao", "ritual", "classes", "descricao",
    ]),
    "monsters": (Monstro, [
        "slug", "nome", "tipo", "tamanho", "alinhamento", "ca", "pv", "pv_formula",
        "deslocamento", "atributos", "nd", "xp", "pericias", "sentidos", "idiomas",
        "habilidades", "acoes",
    ]),
    "feats": (Talento, ["slug", "nome", "descricao", "pre_requisito", "efeitos"]),
    "weapons": (Arma, [
        "slug", "nome", "descricao", "categoria", "alcance", "dano", "tipo_dano",
        "propriedades", "bonus_magico", "efeitos", "homebrew", "idioma",
    ]),
    "armor": (Armadura, [
        "slug", "nome", "descricao", "categoria", "ca_base", "ca_soma_des", "ca_des_max",
        "ca_bonus", "requisito_forca", "furtividade_desvantagem", "efeitos", "homebrew", "idioma",
    ]),
    "items": (Item, [
        "slug", "nome", "descricao", "tipo_item", "raridade", "requer_sintonia",
        "homebrew", "idioma",
    ]),
}


class ContentPipeline:
    """
    Orquestra a ingestão de uma `ContentSource` no banco.

    POO: encapsula a fonte, o rótulo de procedência e a política de sobrescrita.
    """

    def __init__(self, source, fonte=None, force=False):
        self.source = source
        self.fonte = fonte or source.nome
        self.force = force

    def executar(self, tipos) -> Relatorio:
        relatorio = Relatorio()
        for tipo in tipos:
            if tipo not in TIPOS_CONFIG:
                relatorio.mensagens.append(f"tipo desconhecido ignorado: {tipo}")
                continue
            if not self.source.suporta(tipo):
                relatorio.mensagens.append(f"{self.source.nome} não suporta '{tipo}'")
                continue
            self._ingerir_tipo(tipo, relatorio)
        db.session.commit()
        return relatorio

    def _ingerir_tipo(self, tipo, relatorio):
        modelo, campos = TIPOS_CONFIG[tipo]
        for bruto in self.source.buscar(tipo):
            slug = (bruto or {}).get("slug")
            nome = (bruto or {}).get("nome")
            if not slug or not nome:
                relatorio.ignorado(tipo)
                continue
            self._upsert(modelo, campos, slug, bruto, tipo, relatorio)

    def _upsert(self, modelo, campos, slug, bruto, tipo, relatorio):
        existente = modelo.query.filter_by(slug=slug).first()
        if existente is None:
            dados = {
                campo: _ajustar_tamanho(modelo, campo, bruto[campo])
                for campo in campos if campo in bruto
            }
            dados["fonte"] = _ajustar_tamanho(modelo, "fonte", bruto.get("fonte") or self.fonte)
            db.session.add(modelo(**dados))
            relatorio.inserido(tipo)
            return

        mudou = False
        for campo in campos:
            if campo not in bruto:
                continue
            atual = getattr(existente, campo, None)
            vazio = atual in (None, "", [], {})
            if self.force or vazio:
                setattr(existente, campo, _ajustar_tamanho(modelo, campo, bruto[campo]))
                mudou = True
        if mudou:
            relatorio.atualizado(tipo)
