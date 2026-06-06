"""Testes do fluxo de redefinição de senha via link gerado pelo admin."""

URL_LOGIN = "/api/v1/auth/login"
URL_RESET = "/api/v1/auth/reset-password"


def _link(client, auth, token_admin, user_id):
    return client.post(f"/api/v1/admin/users/{user_id}/reset-link", headers=auth(token_admin))


def test_admin_gera_link_e_usuario_redefine(client, make_user, auth):
    _admin, token_admin = make_user(role="ADMIN")
    alvo, _t = make_user(role="JOGADOR", password="senhaAntiga")

    resposta = _link(client, auth, token_admin, alvo.id)
    assert resposta.status_code == 200
    token_reset = resposta.get_json()["data"]["token"]
    assert resposta.get_json()["data"]["caminho"].startswith("/#/reset?token=")

    # Redefine sem a senha antiga.
    redefinir = client.post(URL_RESET, json={"token": token_reset, "nova_senha": "novaSenha123"})
    assert redefinir.status_code == 200
    assert "access_token" in redefinir.get_json()["data"]

    # Login com a nova senha funciona; com a antiga, não.
    assert client.post(URL_LOGIN, json={"email": alvo.email, "password": "novaSenha123"}).status_code == 200
    assert client.post(URL_LOGIN, json={"email": alvo.email, "password": "senhaAntiga"}).status_code == 401


def test_nao_admin_nao_gera_link(client, make_user, auth):
    _mestre, token_mestre = make_user(role="MESTRE")
    alvo, _t = make_user(role="JOGADOR")
    assert _link(client, auth, token_mestre, alvo.id).status_code == 403


def test_link_invalida_apos_uso(client, make_user, auth):
    _admin, token_admin = make_user(role="ADMIN")
    alvo, _t = make_user(role="JOGADOR")
    token_reset = _link(client, auth, token_admin, alvo.id).get_json()["data"]["token"]

    primeiro = client.post(URL_RESET, json={"token": token_reset, "nova_senha": "primeira123"})
    assert primeiro.status_code == 200
    # Reusar o mesmo link após a senha mudar deve falhar (ph não confere mais).
    segundo = client.post(URL_RESET, json={"token": token_reset, "nova_senha": "outra123"})
    assert segundo.status_code == 401


def test_reset_senha_curta(client, make_user, auth):
    _admin, token_admin = make_user(role="ADMIN")
    alvo, _t = make_user(role="JOGADOR")
    token_reset = _link(client, auth, token_admin, alvo.id).get_json()["data"]["token"]
    assert client.post(URL_RESET, json={"token": token_reset, "nova_senha": "123"}).status_code == 400


def test_reset_token_invalido(client):
    assert client.post(URL_RESET, json={"token": "lixo", "nova_senha": "valida123"}).status_code == 401
