"""E38: cálculo automático de PV (sugestão por classe/nível/CON)."""
from app.extensions import db
from app.models.reference import Classe
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_pv_sugerido_regra():
    assert dnd5e.pv_sugerido(12, 1, 3) == 15        # 12+3
    assert dnd5e.pv_sugerido(12, 3, 3) == 35        # 15 + 2*(6+1+3)
    assert dnd5e.pv_sugerido(6, 1, -1) == 5         # 6-1
    assert dnd5e.pv_sugerido(8, 1, -5) == 3         # 8-5 (nível 1 = dado+CON)
    assert dnd5e.pv_sugerido(6, 1, -10) == 1        # piso mínimo 1


def test_derivados_pv_sugerido(client, app, make_user, auth):
    with app.app_context():
        db.session.add(Classe(slug="barbaro-teste", nome="Bárbaro Teste", dado_vida=12))
        db.session.commit()
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Tank", "classe_slug": "barbaro-teste", "nivel": 3,
                                 "atributos": {"con": 16}}, headers=auth(token)).get_json()["data"]["id"]
    d = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert d["dado_vida_classe"] == 12
    assert d["pv_sugerido"] == 35    # d12, nível 3, CON +3
