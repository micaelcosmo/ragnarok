"""E39: revisão automática da ficha (lint de inconsistências)."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def _msgs(avisos, nivel=None):
    return [a["msg"] for a in avisos if nivel is None or a["nivel"] == nivel]


def test_revisar_ficha_alertas_e_infos():
    p = {
        "pv_max": 10, "pv_atual": 99, "classe_slug": None, "raca_slug": "elf",
        "exaustao": 6, "atributo_conjuracao": "xyz",
        "pericias_proficientes": ["Atletismo", "Voar"],
    }
    d = {"atributos_final": {"for": 25, "con": 14}, "asi": {"pontos_usados": 4, "pontos_total": 2}}
    avisos = dnd5e.revisar_ficha(p, d)
    alertas = _msgs(avisos, "alerta")
    assert any("PV atual" in m for m in alertas)
    assert any("Voar" in m for m in alertas)                 # perícia inválida
    assert any("orçamento" in m for m in alertas)            # ASI acima do orçamento
    assert any("Exaustão" in m or "exaustão" in m for m in alertas)
    assert any("conjuração" in m.lower() for m in alertas)
    infos = _msgs(avisos, "info")
    assert any("classe" in m for m in infos)                 # sem classe


def test_ficha_consistente_sem_alertas():
    p = {"pv_max": 30, "pv_atual": 30, "classe_slug": "barbarian", "raca_slug": "halfling",
         "exaustao": 0, "atributo_conjuracao": None, "pericias_proficientes": ["Atletismo"]}
    d = {"atributos_final": {"for": 16}, "asi": {"pontos_usados": 0, "pontos_total": 0}}
    assert _msgs(dnd5e.revisar_ficha(p, d), "alerta") == []


def test_derivados_revisao_via_api(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Bugada", "pv_max": 10, "pv_atual": 999},
                      headers=auth(token)).get_json()["data"]["id"]
    d = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert any("PV atual" in a["msg"] for a in d["revisao"])
