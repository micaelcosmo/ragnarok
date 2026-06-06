"""Testes dos endpoints de referência (catálogo + talentos + filtro por fonte)."""
from app.content.local_source import LocalSource
from app.content.pipeline import ContentPipeline


def _semear_local(app):
    with app.app_context():
        ContentPipeline(LocalSource()).executar(["races", "spells", "feats"])


def test_listar_talentos(client, app, make_user, auth):
    _semear_local(app)
    _usuario, token = make_user()
    resposta = client.get("/api/v1/reference/feats", headers=auth(token))
    assert resposta.status_code == 200
    nomes = {t["slug"] for t in resposta.get_json()["data"]}
    assert "grappler" in nomes


def test_filtro_por_fonte(client, app, make_user, auth):
    _semear_local(app)
    _usuario, token = make_user()
    # Tudo do seed local é "SRD 5.1".
    resposta = client.get("/api/v1/reference/races?fonte=SRD 5.1", headers=auth(token))
    assert resposta.status_code == 200
    assert len(resposta.get_json()["data"]) >= 1
    # Fonte inexistente -> vazio.
    vazio = client.get("/api/v1/reference/races?fonte=Inexistente", headers=auth(token))
    assert vazio.get_json()["data"] == []


def test_listar_fontes(client, app, make_user, auth):
    _semear_local(app)
    _usuario, token = make_user()
    resposta = client.get("/api/v1/reference/sources", headers=auth(token))
    assert resposta.status_code == 200
    assert "SRD 5.1" in resposta.get_json()["data"]


def test_feats_exige_autenticacao(client):
    assert client.get("/api/v1/reference/feats").status_code == 401
