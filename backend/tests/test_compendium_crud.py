"""Fase 5: CRUD do compêndio (MESTRE/ADMIN), homebrew/oficial e aceitação por mesa."""
from app.extensions import db
from app.models.reference import Magia

REF = "/api/v1/reference"


def test_jogador_nao_cria_conteudo(client, make_user, auth):
    _u, token = make_user(role="JOGADOR")
    r = client.post(f"{REF}/feats", json={"slug": "x", "nome": "X", "fonte": "Y"}, headers=auth(token))
    assert r.status_code == 403


def test_mestre_cria_homebrew_com_fonte(client, make_user, auth):
    _m, token = make_user(role="MESTRE")
    # sem fonte -> 400 (obrigatória)
    assert client.post(f"{REF}/feats", json={"slug": "afiado", "nome": "Afiado"}, headers=auth(token)).status_code == 400
    r = client.post(f"{REF}/feats", json={"slug": "afiado", "nome": "Afiado",
                    "fonte": "Homebrew do Mestre"}, headers=auth(token))
    assert r.status_code == 201
    dados = r.get_json()["data"]
    assert dados["homebrew"] is True and dados["oficial"] is False
    assert dados["fonte"] == "Homebrew do Mestre"


def test_editar_oficial_cria_variante_homebrew(client, app, make_user, auth):
    with app.app_context():
        db.session.add(Magia(slug="bola-fogo", nome="Bola de Fogo", nivel=3, fonte="SRD 5.1"))
        db.session.commit()
    _m, token = make_user(role="MESTRE")
    r = client.put(f"{REF}/spells/bola-fogo", json={"nome": "Bola de Fogo Azul",
                   "fonte": "Homebrew"}, headers=auth(token))
    # cria variante homebrew (201), preservando a oficial
    assert r.status_code == 201
    assert r.get_json()["data"]["homebrew"] is True
    # a oficial continua intacta
    oficial = client.get(f"{REF}/spells/bola-fogo", headers=auth(token)).get_json()["data"]
    assert oficial["nome"] == "Bola de Fogo" and oficial["oficial"] is True


def test_mestre_aceita_fonte_homebrew_na_mesa(client, make_user, auth):
    _m, token = make_user(role="MESTRE")
    mesa = client.post("/api/v1/campaigns", json={"nome": "Mesa"}, headers=auth(token)).get_json()["data"]
    r = client.post(f"/api/v1/campaigns/{mesa['id']}/fontes",
                   json={"fonte": "Tome of Beasts"}, headers=auth(token))
    assert r.status_code == 200
    assert "Tome of Beasts" in r.get_json()["data"]["fontes_aceitas"]
    # jogador comum não aceita fontes
    _j, token_j = make_user(role="JOGADOR")
    assert client.post(f"/api/v1/campaigns/{mesa['id']}/fontes",
                      json={"fonte": "X"}, headers=auth(token_j)).status_code == 403
