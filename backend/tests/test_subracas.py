"""E29: sub-raça aplica efeitos automaticamente (base + fontes, reversível)."""
from app.extensions import db
from app.models.reference import Raca

URL = "/api/v1/characters"


def _seed_raca(app):
    with app.app_context():
        raca = Raca(
            slug="anao-teste", nome="Anão de Teste",
            bonus_atributos={"for": 2}, efeitos={"atributos": {"for": 2}},
            subracas=[
                {"slug": "montanha", "nome": "Da Montanha", "bonus_atributos": {"con": 1},
                 "tracos": [{"nome": "Treino com Armaduras", "descricao": "Proficiência em armaduras leves e médias."}]},
            ],
        )
        db.session.add(raca)
        db.session.commit()


def test_subraca_soma_e_reverte(client, app, make_user, auth):
    _seed_raca(app)
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Durin", "raca_slug": "anao-teste",
                                 "atributos": {"for": 10, "con": 12}}, headers=auth(token)).get_json()["data"]["id"]

    # só raça: FOR +2
    so_raca = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert so_raca["atributos_final"]["for"] == 12 and so_raca["atributos_final"]["con"] == 12

    com = client.put(f"{URL}/{pid}", json={"subraca_slug": "montanha"}, headers=auth(token)).get_json()["data"]
    d = com["derivados"]
    assert d["atributos_final"]["for"] == 12 and d["atributos_final"]["con"] == 13   # sub-raça +1 CON
    assert d["subraca"]["nome"] == "Da Montanha"
    assert any(t.get("origem") == "subraca" for t in d["tracos_ativos"])

    sem = client.put(f"{URL}/{pid}", json={"subraca_slug": None}, headers=auth(token)).get_json()["data"]
    assert sem["derivados"]["atributos_final"]["con"] == 12
    assert sem["derivados"]["subraca"] is None


def test_subraca_inexistente_e_ignorada(client, app, make_user, auth):
    _seed_raca(app)
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "X", "raca_slug": "anao-teste", "atributos": {"con": 12}},
                      headers=auth(token)).get_json()["data"]["id"]
    d = client.put(f"{URL}/{pid}", json={"subraca_slug": "nao-existe"}, headers=auth(token)).get_json()["data"]["derivados"]
    assert d["atributos_final"]["con"] == 12   # nada somado
    assert d["subraca"] is None
