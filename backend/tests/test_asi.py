"""E26: Aumentos de Habilidade (ASI) por nível — pool reversível (base + fontes + ASI manual)."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_asi_pontos_por_nivel():
    assert dnd5e.asi_pontos_por_nivel(3) == 0
    assert dnd5e.asi_pontos_por_nivel(4) == 2
    assert dnd5e.asi_pontos_por_nivel(9) == 4
    assert dnd5e.asi_pontos_por_nivel(12) == 6
    assert dnd5e.asi_pontos_por_nivel(19) == 10
    assert dnd5e.asi_pontos_por_nivel(20) == 10


def test_sanear_asi_respeita_orcamento_e_teto():
    base = {"for": 18, "con": 14}
    # orçamento 2, pediu 3 em FOR -> corta para 2
    assert dnd5e.sanear_asi({"for": 3}, 2, base) == {"for": 2}
    # ordem determinística: FOR consome o orçamento, DES fica zerado
    assert dnd5e.sanear_asi({"for": 2, "des": 2}, 2, base) == {"for": 2}
    # teto final 20: FOR base 18 só aceita +2 mesmo com orçamento 6
    assert dnd5e.sanear_asi({"for": 5}, 6, base) == {"for": 2}
    # chaves inválidas e negativos são ignorados
    assert dnd5e.sanear_asi({"xyz": 2, "con": -3}, 4, base) == {}


def test_construtor_soma_e_reverte_asi(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "ASIzin", "nivel": 4, "atributos": {"con": 14}},
                      headers=auth(token)).get_json()["data"]["id"]

    com = client.put(f"{URL}/{pid}", json={"bonus_atributos_manuais": {"con": 2}},
                     headers=auth(token)).get_json()["data"]
    assert com["derivados"]["atributos_final"]["con"] == 16
    assert com["derivados"]["asi"] == {"pontos_total": 2, "pontos_usados": 2, "pontos_restantes": 0}

    sem = client.put(f"{URL}/{pid}", json={"bonus_atributos_manuais": {}},
                     headers=auth(token)).get_json()["data"]
    assert sem["derivados"]["atributos_final"]["con"] == 14
    assert sem["derivados"]["asi"]["pontos_usados"] == 0


def test_api_clampa_alocacao_acima_do_orcamento(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Estouro", "nivel": 4, "atributos": {"for": 10}},
                      headers=auth(token)).get_json()["data"]["id"]
    d = client.put(f"{URL}/{pid}", json={"bonus_atributos_manuais": {"for": 9}},
                   headers=auth(token)).get_json()["data"]
    # nível 4 = 2 pontos: pediu 9, recebe só 2
    assert d["bonus_atributos_manuais"] == {"for": 2}
    assert d["derivados"]["atributos_final"]["for"] == 12
    assert d["derivados"]["asi"]["pontos_restantes"] == 0
