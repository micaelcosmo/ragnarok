"""E31: testes contra a morte (sucesso/falha) + exaustão (0–6) com efeitos descritivos."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_clamps_e_efeito_exaustao():
    assert dnd5e.clamp_morte(9) == 3 and dnd5e.clamp_morte(-2) == 0
    assert dnd5e.clamp_exaustao(99) == 6 and dnd5e.clamp_exaustao(-1) == 0
    assert dnd5e.efeito_exaustao(0) == ""
    assert "Desvantagem" in dnd5e.efeito_exaustao(1)
    assert dnd5e.efeito_exaustao(6) == "Morte"


def test_api_clampa_e_expõe_efeito(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Moribundo"}, headers=auth(token)).get_json()["data"]["id"]
    d = client.put(f"{URL}/{pid}", json={"mortes_sucesso": 2, "mortes_falha": 5, "exaustao": 9},
                   headers=auth(token)).get_json()["data"]
    assert d["mortes_sucesso"] == 2
    assert d["mortes_falha"] == 3          # clampado
    assert d["exaustao"] == 6              # clampado
    assert d["derivados"]["exaustao_efeito"] == "Morte"

    z = client.put(f"{URL}/{pid}", json={"exaustao": 0}, headers=auth(token)).get_json()["data"]
    assert z["derivados"]["exaustao_efeito"] == ""
