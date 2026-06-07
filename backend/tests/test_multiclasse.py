"""E35: multiclasse — nível total dirige o bônus de proficiência; salvaguardas só da 1ª classe."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_nivel_total_e_sanear():
    assert dnd5e.nivel_total(4, [{"slug": "wizard", "nivel": 1}]) == 5
    assert dnd5e.nivel_total(5, []) == 5
    assert dnd5e.nivel_total(18, [{"slug": "a", "nivel": 9}]) == 20      # clamp 20
    assert dnd5e.sanear_classes_extras([{"slug": "wizard", "nivel": 2},
                                        {"slug": "", "nivel": 3},
                                        {"slug": "rogue", "nivel": 0}]) == [{"slug": "wizard", "nivel": 2}]


def test_construtor_usa_nivel_total(client, make_user, auth):
    _u, token = make_user()
    # primária nível 4 (proficiência +2). Multiclasse +1 -> total 5 (proficiência +3).
    pid = client.post(URL, json={"nome": "Multi", "classe_slug": "barbarian", "nivel": 4},
                      headers=auth(token)).get_json()["data"]["id"]
    antes = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert antes["bonus_proficiencia"] == 2 and antes["nivel_total"] == 4

    d = client.put(f"{URL}/{pid}", json={"classes_extras": [{"slug": "wizard", "nivel": 1}]},
                   headers=auth(token)).get_json()["data"]["derivados"]
    assert d["nivel_total"] == 5
    assert d["bonus_proficiencia"] == 3
    assert {"slug": "barbarian", "nivel": 4} in d["classes"]
    assert {"slug": "wizard", "nivel": 1} in d["classes"]
