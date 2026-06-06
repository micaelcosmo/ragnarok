"""Testes da pipeline de conteúdo (offline — sem acesso à rede)."""
from app.content.base import ContentSource
from app.content.local_source import LocalSource
from app.content.open5e_source import Open5eSource
from app.content.pipeline import ContentPipeline
from app.models.reference import Talento


class FakeSource(ContentSource):
    """Fonte em memória para testar a pipeline sem rede."""

    tipos_suportados = ("feats",)

    def __init__(self, registros):
        self._registros = registros

    @property
    def nome(self):
        return "Fonte Fake"

    def buscar(self, tipo):
        return list(self._registros) if tipo == "feats" else []


def _tres_talentos():
    return [
        {"slug": "alerta", "nome": "Alerta", "descricao": "Sempre em guarda."},
        {"slug": "atletico", "nome": "Atlético", "descricao": "Mais ágil."},
        {"slug": "sem-nome"},  # sem 'nome' -> deve ser ignorado
    ]


def test_pipeline_insere_e_e_idempotente(app):
    fonte = FakeSource(_tres_talentos())
    pipeline = ContentPipeline(fonte)

    primeiro = pipeline.executar(["feats"])
    assert primeiro.por_tipo["feats"]["inseridos"] == 2
    assert primeiro.por_tipo["feats"]["ignorados"] == 1
    assert Talento.query.count() == 2

    # Segunda execução não duplica e não altera (campos já preenchidos).
    segundo = pipeline.executar(["feats"])
    assert segundo.por_tipo["feats"]["inseridos"] == 0
    assert segundo.por_tipo["feats"]["atualizados"] == 0
    assert Talento.query.count() == 2


def test_pipeline_grava_fonte(app):
    pipeline = ContentPipeline(FakeSource([
        {"slug": "perito", "nome": "Perito"},
    ]))
    pipeline.executar(["feats"])
    talento = Talento.query.filter_by(slug="perito").first()
    assert talento.fonte == "Fonte Fake"


def test_pipeline_force_sobrescreve(app):
    base = [{"slug": "duro", "nome": "Durão", "descricao": "Original"}]
    ContentPipeline(FakeSource(base)).executar(["feats"])

    novo = [{"slug": "duro", "nome": "Durão", "descricao": "Reescrito"}]
    # Sem force: preserva a descrição original.
    ContentPipeline(FakeSource(novo)).executar(["feats"])
    assert Talento.query.filter_by(slug="duro").first().descricao == "Original"

    # Com force: sobrescreve.
    ContentPipeline(FakeSource(novo), force=True).executar(["feats"])
    assert Talento.query.filter_by(slug="duro").first().descricao == "Reescrito"


def test_local_source_carrega_feats(app):
    pipeline = ContentPipeline(LocalSource())
    relatorio = pipeline.executar(["feats"])
    assert relatorio.por_tipo["feats"]["inseridos"] >= 1
    assert Talento.query.filter_by(slug="grappler").first() is not None


def test_open5e_normaliza_atributos_de_monstro():
    """Normalização do open5e mapeia atributos EN -> for/des/con/int/sab/car (sem rede)."""
    fonte = Open5eSource()
    bruto = {
        "slug": "goblin", "name": "Goblin", "type": "humanoid", "size": "Small",
        "armor_class": 15, "hit_points": 7, "hit_dice": "2d6",
        "strength": 8, "dexterity": 14, "constitution": 10,
        "intelligence": 10, "wisdom": 8, "charisma": 8,
        "speed": {"walk": 30}, "challenge_rating": "0.25",
        "actions": [{"name": "Scimitar", "desc": "+4 to hit"}],
        "document__title": "SRD",
    }
    canonico = fonte._norm_monsters(bruto)
    assert canonico["atributos"] == {
        "for": 8, "des": 14, "con": 10, "int": 10, "sab": 8, "car": 8,
    }
    assert canonico["deslocamento"] == "9 m"  # 30 pés -> 9 m
    assert canonico["fonte"] == "SRD"
