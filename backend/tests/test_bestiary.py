"""Testes do Bestiário: escopo global/mesa e permissões."""

URL = "/api/v1/bestiary"
URL_MESAS = "/api/v1/campaigns"


def test_jogador_nao_cria_monstro(client, make_user, auth):
    _usuario, token = make_user(role="JOGADOR")
    resposta = client.post(URL, json={"nome": "Goblin"}, headers=auth(token))
    assert resposta.status_code == 403


def test_mestre_cria_monstro_na_mesa(client, make_user, auth):
    _mestre, token = make_user(role="MESTRE")
    mesa = client.post(URL_MESAS, json={"nome": "Mesa"}, headers=auth(token)).get_json()["data"]

    resposta = client.post(
        URL, json={"nome": "Goblin Batedor", "mesa_id": mesa["id"], "ca": 15, "pv": 7},
        headers=auth(token),
    )
    assert resposta.status_code == 201
    assert resposta.get_json()["data"]["mesa_id"] == mesa["id"]


def test_listagem_mesa_inclui_global_e_criado(client, make_user, auth):
    admin, token_admin = make_user(role="ADMIN")
    # ADMIN cria um monstro SRD global (sem mesa).
    client.post(URL, json={"nome": "Dragão Vermelho"}, headers=auth(token_admin))

    _mestre, token_mestre = make_user(role="MESTRE")
    mesa = client.post(URL_MESAS, json={"nome": "Mesa"}, headers=auth(token_mestre)).get_json()["data"]
    client.post(URL, json={"nome": "Kobold", "mesa_id": mesa["id"]}, headers=auth(token_mestre))

    lista = client.get(f"{URL}?mesa_id={mesa['id']}", headers=auth(token_mestre)).get_json()["data"]
    nomes = {monstro["nome"] for monstro in lista}
    assert "Dragão Vermelho" in nomes   # global
    assert "Kobold" in nomes            # da mesa


def test_mestre_nao_edita_monstro_de_outra_mesa(client, make_user, auth):
    _mestre_a, token_a = make_user(role="MESTRE")
    mesa_a = client.post(URL_MESAS, json={"nome": "A"}, headers=auth(token_a)).get_json()["data"]
    monstro = client.post(
        URL, json={"nome": "Ogro", "mesa_id": mesa_a["id"]}, headers=auth(token_a)
    ).get_json()["data"]

    _mestre_b, token_b = make_user(role="MESTRE")
    resposta = client.put(
        f"{URL}/{monstro['id']}", json={"nome": "Ogro Hackeado"}, headers=auth(token_b)
    )
    assert resposta.status_code == 403
