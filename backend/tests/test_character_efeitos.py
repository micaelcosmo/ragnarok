"""Integração: escolhas (raça/antecedente/talento) aplicam bônus na ficha — reversível."""
from app.extensions import db
from app.models.reference import Antecedente, Raca, Talento

URL = "/api/v1/characters"


def _semear_catalogo(app):
    """Cria conteúdo de referência com `efeitos` para os testes."""
    with app.app_context():
        db.session.add(Raca(
            slug="anao", nome="Anão", bonus_atributos={"con": 2},
            efeitos={"atributos": {"con": 2}, "sentidos": ["Visão no escuro 18m"]},
        ))
        db.session.add(Antecedente(
            slug="sabio", nome="Sábio", pericias=["Arcanismo", "História"],
            efeitos={"pericias": ["Arcanismo", "História"]},
        ))
        db.session.add(Talento(
            slug="alerta-teste", nome="Alerta (teste)",
            efeitos={"iniciativa": 5, "recursos": ["Você não pode ser surpreendido."]},
        ))
        db.session.commit()


def test_raca_e_antecedente_aplicam_bonus(client, app, make_user, auth):
    _semear_catalogo(app)
    _u, token = make_user()
    criado = client.post(URL, json={
        "nome": "Thrain", "raca_slug": "anao", "antecedente_slug": "sabio",
        "atributos": {"con": 14},
    }, headers=auth(token)).get_json()["data"]

    derivados = criado["derivados"]
    # CON base 14 + 2 (raça) = 16 -> mod +3
    assert derivados["atributos_final"]["con"] == 16
    assert derivados["modificadores"]["con"] == 3
    # Antecedente concede perícias proficientes
    arcanismo = next(p for p in derivados["pericias"] if p["nome"] == "Arcanismo")
    assert arcanismo["proficiente"] is True
    # Sentido concedido pela raça aparece
    assert "Visão no escuro 18m" in derivados["sentidos"]


def test_adicionar_e_remover_talento_e_reversivel(client, app, make_user, auth):
    _semear_catalogo(app)
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Lyra", "atributos": {"des": 14}}, headers=auth(token)).get_json()["data"]["id"]

    # Iniciativa base = mod DES (+2)
    base = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]
    assert base["derivados"]["iniciativa"] == 2

    # Adiciona o talento (+5 iniciativa) -> soma automática
    com = client.put(f"{URL}/{pid}", json={"talentos": ["alerta-teste"]}, headers=auth(token)).get_json()["data"]
    assert com["derivados"]["iniciativa"] == 7
    assert "Você não pode ser surpreendido." in com["derivados"]["recursos"]

    # Remove o talento -> subtrai automático (reversível)
    sem = client.put(f"{URL}/{pid}", json={"talentos": []}, headers=auth(token)).get_json()["data"]
    assert sem["derivados"]["iniciativa"] == 2
    assert "Você não pode ser surpreendido." not in sem["derivados"]["recursos"]


def test_ca_ajuste_manual_soma(client, app, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Borin", "ca": 16}, headers=auth(token)).get_json()["data"]["id"]
    ajustado = client.put(f"{URL}/{pid}", json={"ca_ajuste": 2}, headers=auth(token)).get_json()["data"]
    assert ajustado["derivados"]["ca"] == 18  # 16 + 2 manual
