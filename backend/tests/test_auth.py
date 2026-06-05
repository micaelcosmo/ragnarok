"""Testes de autenticação e RBAC."""

URL_REGISTER = "/api/v1/auth/register"
URL_LOGIN = "/api/v1/auth/login"
URL_ME = "/api/v1/auth/me"


def test_registro_valido(client):
    resposta = client.post(URL_REGISTER, json={
        "email": "novo@teste.local", "name": "Novo", "password": "senha123",
    })
    assert resposta.status_code == 201
    corpo = resposta.get_json()["data"]
    assert corpo["email"] == "novo@teste.local"
    assert corpo["role"] == "JOGADOR"
    assert "password_hash" not in corpo


def test_registro_email_duplicado(client):
    payload = {"email": "dup@teste.local", "name": "A", "password": "senha123"}
    client.post(URL_REGISTER, json=payload)
    resposta = client.post(URL_REGISTER, json=payload)
    assert resposta.status_code == 409
    assert resposta.get_json()["error"]["code"] == "CONFLICT"


def test_registro_senha_curta(client):
    resposta = client.post(URL_REGISTER, json={
        "email": "curta@teste.local", "name": "A", "password": "123",
    })
    assert resposta.status_code == 400
    assert resposta.get_json()["error"]["code"] == "VALIDATION"


def test_registro_nunca_cria_admin(client):
    resposta = client.post(URL_REGISTER, json={
        "email": "hacker@teste.local", "name": "H", "password": "senha123", "role": "ADMIN",
    })
    assert resposta.status_code == 201
    assert resposta.get_json()["data"]["role"] == "JOGADOR"


def test_registro_pode_ser_mestre(client):
    resposta = client.post(URL_REGISTER, json={
        "email": "mestre@teste.local", "name": "M", "password": "senha123", "role": "MESTRE",
    })
    assert resposta.get_json()["data"]["role"] == "MESTRE"


def test_login_correto_e_incorreto(client):
    client.post(URL_REGISTER, json={
        "email": "log@teste.local", "name": "L", "password": "senha123",
    })
    ok = client.post(URL_LOGIN, json={"email": "log@teste.local", "password": "senha123"})
    assert ok.status_code == 200
    assert "access_token" in ok.get_json()["data"]

    ruim = client.post(URL_LOGIN, json={"email": "log@teste.local", "password": "errada"})
    assert ruim.status_code == 401


def test_me_exige_token(client, make_user, auth):
    sem = client.get(URL_ME)
    assert sem.status_code == 401

    _usuario, token = make_user(role="JOGADOR")
    com = client.get(URL_ME, headers=auth(token))
    assert com.status_code == 200
    assert com.get_json()["data"]["role"] == "JOGADOR"
