"""E37: exportar/importar ficha em JSON (backup/portabilidade)."""

URL = "/api/v1/characters"


def test_export_e_import(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Exportável", "nivel": 6, "atributos": {"des": 17},
                                 "moedas": {"po": 50}}, headers=auth(token)).get_json()["data"]["id"]
    exp = client.get(f"{URL}/{pid}/export", headers=auth(token))
    assert exp.status_code == 200 and exp.mimetype == "application/json"
    pacote = exp.get_json()
    assert pacote["_ragnarok"] == "ficha" and pacote["dados"]["nome"] == "Exportável"
    assert "id" not in pacote["dados"] and "derivados" not in pacote["dados"]

    # importa em outra conta
    _outro, token2 = make_user()
    novo = client.post(f"{URL}/import", json=pacote, headers=auth(token2))
    assert novo.status_code == 201
    d = novo.get_json()["data"]
    assert d["nome"] == "Exportável" and d["nivel"] == 6 and d["atributos"]["des"] == 17
    assert d["moedas"] == {"po": 50}
    assert d["user_id"] != pid  # pertence a quem importou (id de usuário diferente da origem)


def test_import_sem_nome_400(client, make_user, auth):
    _u, token = make_user()
    r = client.post(f"{URL}/import", json={"dados": {"nivel": 3}}, headers=auth(token))
    assert r.status_code == 400
