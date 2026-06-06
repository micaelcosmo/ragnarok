"""Fase 6: tradução en->pt com cache e fallback gracioso (sem motor instalado)."""
from app.extensions import db
from app.models.items import Arma
from app.models.translation import Traducao
from app.services.tradutor import Tradutor


def test_fallback_devolve_original(app):
    """Sem motor/cache, devolve o original marcando traduzido=False (não quebra)."""
    with app.app_context():
        registro = {"slug": "longsword", "nome": "Longsword", "descricao": "A sword.", "idioma": "en"}
        resultado = Tradutor("pt").aplicar("weapons", registro)
        assert resultado["nome"] == "Longsword"
        assert resultado["traduzido"] is False


def test_usa_cache_quando_existe(app):
    with app.app_context():
        db.session.add(Traducao(tipo="weapons", slug="longsword", campo="nome",
                                idioma="pt", texto="Espada Longa"))
        db.session.commit()
        registro = {"slug": "longsword", "nome": "Longsword", "idioma": "en"}
        resultado = Tradutor("pt").aplicar("weapons", registro)
        assert resultado["nome"] == "Espada Longa"
        assert resultado["traduzido"] is True


def test_conteudo_pt_nao_e_tocado(app):
    with app.app_context():
        registro = {"slug": "adaga", "nome": "Adaga", "idioma": "pt"}
        resultado = Tradutor("pt").aplicar("weapons", registro)
        assert resultado["nome"] == "Adaga"


def test_endpoint_catalog_idioma_pt(client, app, make_user, auth):
    with app.app_context():
        db.session.add(Arma(slug="club", nome="Club", descricao="A club.",
                            fonte="SRD", homebrew=False, idioma="en"))
        db.session.add(Traducao(tipo="weapons", slug="club", campo="nome", idioma="pt", texto="Clava"))
        db.session.commit()
    _u, token = make_user()
    dados = client.get("/api/v1/catalog/weapons?idioma=pt", headers=auth(token)).get_json()["data"]
    club = next(a for a in dados if a["slug"] == "club")
    assert club["nome"] == "Clava"


def test_seed_traducoes_idempotente(app):
    """O de-para PT curado é semeado uma vez e re-rodar não duplica (idempotente)."""
    from app.seed import SeedRunner

    with app.app_context():
        runner = SeedRunner(app)
        runner.semear_traducoes()
        primeiro = Traducao.query.filter_by(idioma="pt").count()
        assert primeiro > 0
        greataxe = Traducao.query.filter_by(tipo="weapons", slug="greataxe", campo="nome").first()
        assert greataxe is not None and greataxe.texto == "Machado Grande"

        runner.semear_traducoes()  # segunda passada: nada novo
        assert Traducao.query.filter_by(idioma="pt").count() == primeiro
        assert runner.resumo["traducoes"] == 0
