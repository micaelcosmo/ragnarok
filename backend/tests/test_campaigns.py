"""Testes de Mesas/Campanhas: criação, ingresso por código e permissões."""

URL = "/api/v1/campaigns"


def _criar_mesa(client, auth, token, nome="A Mina Perdida"):
    return client.post(URL, json={"nome": nome}, headers=auth(token))


def test_jogador_nao_cria_mesa(client, make_user, auth):
    _usuario, token = make_user(role="JOGADOR")
    resposta = _criar_mesa(client, auth, token)
    assert resposta.status_code == 403


def test_mestre_cria_mesa(client, make_user, auth):
    _mestre, token = make_user(role="MESTRE")
    resposta = _criar_mesa(client, auth, token)
    assert resposta.status_code == 201
    assert len(resposta.get_json()["data"]["codigo_convite"]) == 6


def test_jogador_entra_por_codigo(client, make_user, auth):
    _mestre, token_mestre = make_user(role="MESTRE")
    mesa = _criar_mesa(client, auth, token_mestre).get_json()["data"]

    jogador, token_jogador = make_user(role="JOGADOR")
    entrada = client.post(
        f"{URL}/join", json={"codigo": mesa["codigo_convite"]}, headers=auth(token_jogador)
    )
    assert entrada.status_code == 200
    membros = entrada.get_json()["data"]["membros"]
    assert any(membro["user_id"] == jogador.id for membro in membros)


def test_join_codigo_invalido(client, make_user, auth):
    _usuario, token = make_user(role="JOGADOR")
    resposta = client.post(f"{URL}/join", json={"codigo": "ZZZZZZ"}, headers=auth(token))
    assert resposta.status_code == 404


def test_nao_membro_nao_ve_mesa(client, make_user, auth):
    _mestre, token_mestre = make_user(role="MESTRE")
    mesa = _criar_mesa(client, auth, token_mestre).get_json()["data"]

    _intruso, token_intruso = make_user(role="JOGADOR")
    resposta = client.get(f"{URL}/{mesa['id']}", headers=auth(token_intruso))
    assert resposta.status_code == 403


def test_mestre_ve_personagem_vinculado(client, make_user, auth):
    _mestre, token_mestre = make_user(role="MESTRE")
    mesa = _criar_mesa(client, auth, token_mestre).get_json()["data"]

    jogador, token_jogador = make_user(role="JOGADOR")
    client.post(f"{URL}/join", json={"codigo": mesa["codigo_convite"]}, headers=auth(token_jogador))

    personagem = client.post(
        "/api/v1/characters", json={"nome": "Bruenor"}, headers=auth(token_jogador)
    ).get_json()["data"]
    client.post(
        f"{URL}/{mesa['id']}/personagens",
        json={"personagem_id": personagem["id"]},
        headers=auth(token_jogador),
    )

    # Mestre acessa a ficha do jogador da sua mesa.
    visto = client.get(f"/api/v1/characters/{personagem['id']}", headers=auth(token_mestre))
    assert visto.status_code == 200
    assert visto.get_json()["data"]["id"] == personagem["id"]
