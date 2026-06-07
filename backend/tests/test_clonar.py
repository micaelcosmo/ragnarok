"""E36: clonar personagem (duplicar ficha para o usuário atual)."""

URL = "/api/v1/characters"


def test_clonar_cria_copia(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Original", "nivel": 5, "atributos": {"for": 16},
                                 "recursos": [{"nome": "Fúria", "max": 3, "atual": 3, "recarga": "longo"}]},
                      headers=auth(token)).get_json()["data"]["id"]
    r = client.post(f"{URL}/{pid}/clonar", headers=auth(token))
    assert r.status_code == 201
    copia = r.get_json()["data"]
    assert copia["id"] != pid
    assert copia["nome"] == "Original (cópia)"
    assert copia["nivel"] == 5 and copia["atributos"]["for"] == 16
    assert copia["recursos"][0]["nome"] == "Fúria"


def test_clonar_inexistente_404(client, make_user, auth):
    _u, token = make_user()
    assert client.post(f"{URL}/999999/clonar", headers=auth(token)).status_code == 404


def test_clonar_sem_acesso_403(client, make_user, auth):
    _dono, t1 = make_user()
    pid = client.post(URL, json={"nome": "Alheio"}, headers=auth(t1)).get_json()["data"]["id"]
    _outro, t2 = make_user()
    assert client.post(f"{URL}/{pid}/clonar", headers=auth(t2)).status_code == 403
