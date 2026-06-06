"""#6: traços/recursos extras — incrementais (somam, reversível) e descritivos."""

URL = "/api/v1/characters"


def test_traco_numerico_soma_e_reverte(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Atila", "atributos": {"con": 14}}, headers=auth(token)).get_json()["data"]["id"]

    boon = {"nome": "Bênção da Grande Serpente", "descricao": "+2 CON da campanha",
            "fonte": "StormKing - Mestre Atila", "efeitos": {"atributos": {"con": 2}}}
    com = client.put(f"{URL}/{pid}", json={"tracos_extras": [boon]}, headers=auth(token)).get_json()["data"]
    assert com["derivados"]["atributos_final"]["con"] == 16
    card = next(t for t in com["derivados"]["tracos_ativos"] if t["nome"] == "Bênção da Grande Serpente")
    assert card["tipo"] == "numerico" and card["origem"] == "extra"

    sem = client.put(f"{URL}/{pid}", json={"tracos_extras": []}, headers=auth(token)).get_json()["data"]
    assert sem["derivados"]["atributos_final"]["con"] == 14
    assert sem["derivados"]["tracos_ativos"] == []


def test_traco_descritivo_nao_muda_numero(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Sentinela", "atributos": {"des": 14}}, headers=auth(token)).get_json()["data"]["id"]
    traco = {"nome": "Nunca surpreendido", "descricao": "Você não pode ser surpreendido."}
    d = client.put(f"{URL}/{pid}", json={"tracos_extras": [traco]}, headers=auth(token)).get_json()["data"]["derivados"]
    assert d["atributos_final"]["des"] == 14   # sem efeito numérico
    card = d["tracos_ativos"][0]
    assert card["tipo"] == "descritivo"
