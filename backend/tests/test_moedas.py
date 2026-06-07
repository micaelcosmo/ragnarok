"""E33: moedas por tipo (PC/PP/PE/PO/PL) + total em PO."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_sanear_e_total():
    assert dnd5e.sanear_moedas({"po": 10, "pp": 5, "xx": 3, "pc": -2}) == {"po": 10, "pp": 5, "pc": 0}
    assert dnd5e.moedas_total_po({"po": 10, "pp": 5}) == 10.5
    assert dnd5e.moedas_total_po({"pl": 1, "pe": 2}) == 11.0   # 10 + 2*0.5
    assert dnd5e.moedas_total_po({}) == 0


def test_api_moedas(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Rico"}, headers=auth(token)).get_json()["data"]["id"]
    d = client.put(f"{URL}/{pid}", json={"moedas": {"po": 100, "pp": 30, "pc": -5}},
                   headers=auth(token)).get_json()["data"]
    assert d["moedas"] == {"po": 100, "pp": 30, "pc": 0}
    assert d["derivados"]["total_po"] == 103.0
