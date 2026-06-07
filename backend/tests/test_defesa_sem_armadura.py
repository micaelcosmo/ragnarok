"""E30: Defesa sem Armadura automática (Bárbaro 10+DES+CON, Monge 10+DES+SAB)."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_ca_sem_armadura_regra():
    mods = {"for": 0, "des": 2, "con": 3, "int": 0, "sab": 1, "car": 0}
    assert dnd5e.ca_sem_armadura("barbarian", mods) == 15   # 10+2+3
    assert dnd5e.ca_sem_armadura("monk", mods) == 13        # 10+2+1
    assert dnd5e.ca_sem_armadura("wizard", mods) is None


def test_construtor_barbaro_sem_armadura(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Conan", "classe_slug": "barbarian",
                                 "atributos": {"des": 14, "con": 16}, "ca": 10}, headers=auth(token)).get_json()["data"]["id"]
    d = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert d["ca"] == 15                       # 10 + 2(DES) + 3(CON)
    assert "sem Armadura" in d["ca_detalhe"]


def test_construtor_classe_comum_usa_ca_manual(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Mago", "classe_slug": "wizard",
                                 "atributos": {"des": 14, "con": 16}, "ca": 12}, headers=auth(token)).get_json()["data"]["id"]
    d = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert d["ca"] == 12                       # CA manual, sem fórmula de classe
