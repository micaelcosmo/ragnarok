"""E27: recursos de classe com usos (máx/atual/recarga) + descanso curto/longo."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_sanear_recursos_clampa():
    bruto = [
        {"nome": "Fúria", "max": 4, "atual": 9, "recarga": "longo"},      # atual > max -> 4
        {"nome": "Bardo", "max": 3, "atual": -2, "recarga": "curto"},     # atual < 0 -> 0
        {"nome": "", "max": 2, "atual": 1, "recarga": "longo"},           # nome vazio -> descartado
        {"nome": "Ruim", "max": 2, "atual": 1, "recarga": "xpto"},        # recarga inválida -> descartado
    ]
    limpo = dnd5e.sanear_recursos(bruto)
    assert limpo == [
        {"nome": "Fúria", "max": 4, "atual": 4, "recarga": "longo", "descricao": ""},
        {"nome": "Bardo", "max": 3, "atual": 0, "recarga": "curto", "descricao": ""},
    ]


def test_aplicar_descanso_por_tipo():
    recursos = [
        {"nome": "Fúria", "max": 4, "atual": 1, "recarga": "longo", "descricao": ""},
        {"nome": "Maneuver", "max": 3, "atual": 0, "recarga": "curto", "descricao": ""},
        {"nome": "Item 1/dia", "max": 1, "atual": 0, "recarga": "nenhum", "descricao": ""},
    ]
    curto = dnd5e.aplicar_descanso(recursos, "curto")
    assert curto[0]["atual"] == 1 and curto[1]["atual"] == 3 and curto[2]["atual"] == 0
    longo = dnd5e.aplicar_descanso(recursos, "longo")
    assert longo[0]["atual"] == 4 and longo[1]["atual"] == 3 and longo[2]["atual"] == 0


def test_put_e_ajustar(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Bárbaro", "pv_max": 50, "pv_atual": 20},
                      headers=auth(token)).get_json()["data"]["id"]
    rec = [{"nome": "Fúria", "max": 4, "atual": 4, "recarga": "longo"}]
    d = client.put(f"{URL}/{pid}", json={"recursos": rec}, headers=auth(token)).get_json()["data"]
    assert d["recursos"][0]["atual"] == 4

    g = client.post(f"{URL}/{pid}/recursos/ajustar", json={"indice": 0, "delta": -1},
                    headers=auth(token)).get_json()["data"]
    assert g["recursos"][0]["atual"] == 3
    # não passa de 0
    for _ in range(5):
        g = client.post(f"{URL}/{pid}/recursos/ajustar", json={"indice": 0, "delta": -1},
                        headers=auth(token)).get_json()["data"]
    assert g["recursos"][0]["atual"] == 0


def test_descanso_recarrega_e_restaura_pv(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Cansado", "pv_max": 50, "pv_atual": 12},
                      headers=auth(token)).get_json()["data"]["id"]
    client.put(f"{URL}/{pid}", json={"recursos": [
        {"nome": "Fúria", "max": 4, "atual": 0, "recarga": "longo"},
        {"nome": "Superioridade", "max": 3, "atual": 0, "recarga": "curto"},
    ]}, headers=auth(token))

    curto = client.post(f"{URL}/{pid}/descanso", json={"tipo": "curto"}, headers=auth(token)).get_json()["data"]
    assert curto["recursos"][0]["atual"] == 0 and curto["recursos"][1]["atual"] == 3  # só o curto
    assert curto["pv_atual"] == 12  # descanso curto não restaura PV aqui

    longo = client.post(f"{URL}/{pid}/descanso", json={"tipo": "longo"}, headers=auth(token)).get_json()["data"]
    assert longo["recursos"][0]["atual"] == 4 and longo["recursos"][1]["atual"] == 3
    assert longo["pv_atual"] == 50  # descanso longo restaura PV
