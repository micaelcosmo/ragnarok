"""Fase 3: CRUD de itens com ownership + equipar (CA/ataque na ficha)."""

CAT = "/api/v1/catalog"
CHARS = "/api/v1/characters"


def _criar_personagem(client, auth, token, **extra):
    payload = {"nome": "Herói", "atributos": {"for": 16, "des": 12}}
    payload.update(extra)
    return client.post(CHARS, json=payload, headers=auth(token)).get_json()["data"]


def test_jogador_cria_item_vinculado_ao_personagem(client, make_user, auth):
    _u, token = make_user(role="JOGADOR")
    p = _criar_personagem(client, auth, token)
    # sem personagem_id -> 400
    assert client.post(f"{CAT}/weapons", json={"nome": "Espada Caseira"}, headers=auth(token)).status_code == 400
    # com personagem_id -> 201, vinculado e homebrew
    r = client.post(f"{CAT}/weapons", json={"nome": "Espada Caseira", "dano": "1d8",
                    "personagem_id": p["id"]}, headers=auth(token))
    assert r.status_code == 201
    item = r.get_json()["data"]
    assert item["personagem_id"] == p["id"]
    assert item["homebrew"] is True and item["oficial"] is False


def test_mestre_cria_item_global(client, make_user, auth):
    _m, token = make_user(role="MESTRE")
    r = client.post(f"{CAT}/weapons", json={"nome": "Lâmina do Mestre", "dano": "1d10"}, headers=auth(token))
    assert r.status_code == 201
    assert r.get_json()["data"]["global"] is True


def test_jogador_nao_edita_item_de_outro(client, make_user, auth):
    _m, token_m = make_user(role="MESTRE")
    item = client.post(f"{CAT}/weapons", json={"nome": "Adaga Global"}, headers=auth(token_m)).get_json()["data"]
    _j, token_j = make_user(role="JOGADOR")
    assert client.put(f"{CAT}/weapons/{item['id']}", json={"nome": "Roubada"}, headers=auth(token_j)).status_code == 403


def test_equipar_armadura_altera_ca(client, make_user, auth):
    _m, token_m = make_user(role="MESTRE")
    # armadura global: CA base 16 (cota de malha, sem DES)
    armadura = client.post(f"{CAT}/armor", json={"nome": "Cota de Malha", "ca_base": 16,
                          "ca_soma_des": False}, headers=auth(token_m)).get_json()["data"]
    _j, token_j = make_user(role="JOGADOR")
    p = _criar_personagem(client, auth, token_j, ca=10)
    equipado = client.post(f"{CHARS}/{p['id']}/equipar",
                          json={"tipo": "armadura", "item_id": armadura["id"]}, headers=auth(token_j))
    assert equipado.status_code == 200
    assert equipado.get_json()["data"]["derivados"]["ca"] == 16
    # desequipar volta para a CA base manual (10)
    desq = client.post(f"{CHARS}/{p['id']}/desequipar", json={"tipo": "armadura"}, headers=auth(token_j))
    assert desq.get_json()["data"]["derivados"]["ca"] == 10


def test_equipar_arma_gera_ataque(client, make_user, auth):
    _m, token_m = make_user(role="MESTRE")
    arma = client.post(f"{CAT}/weapons", json={"nome": "Espada Longa", "dano": "1d8",
                       "tipo_dano": "cortante"}, headers=auth(token_m)).get_json()["data"]
    _j, token_j = make_user(role="JOGADOR")
    p = _criar_personagem(client, auth, token_j)  # FOR 16 -> +3
    eq = client.post(f"{CHARS}/{p['id']}/equipar",
                    json={"tipo": "arma", "item_id": arma["id"]}, headers=auth(token_j))
    ataques = eq.get_json()["data"]["derivados"]["ataques_equipados"]
    assert len(ataques) == 1
    # FOR +3 + proficiência +2 (nível 1) = +5 para acertar
    assert ataques[0]["bonus_acerto"] == 5
    assert ataques[0]["dano"] == "1d8"
