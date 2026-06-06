"""Testes de administração: acesso restrito, troca de papel, métricas."""

URL_USERS = "/api/v1/admin/users"
URL_STATS = "/api/v1/admin/stats"


def test_nao_admin_bloqueado(client, make_user, auth):
    _jogador, token_jogador = make_user(role="JOGADOR")
    _mestre, token_mestre = make_user(role="MESTRE")
    assert client.get(URL_USERS, headers=auth(token_jogador)).status_code == 403
    assert client.get(URL_STATS, headers=auth(token_mestre)).status_code == 403


def test_admin_promove_jogador(client, make_user, auth):
    _admin, token_admin = make_user(role="ADMIN")
    jogador, _token = make_user(role="JOGADOR")

    resposta = client.put(
        f"{URL_USERS}/{jogador.id}/role", json={"role": "MESTRE"}, headers=auth(token_admin)
    )
    assert resposta.status_code == 200
    assert resposta.get_json()["data"]["role"] == "MESTRE"


def test_admin_nao_deleta_a_si_mesmo(client, make_user, auth):
    admin, token_admin = make_user(role="ADMIN")
    resposta = client.delete(f"{URL_USERS}/{admin.id}", headers=auth(token_admin))
    assert resposta.status_code == 400


def test_admin_modera_mesas(client, make_user, auth):
    # Mestre cria uma mesa.
    _mestre, token_mestre = make_user(role="MESTRE")
    mesa = client.post(
        "/api/v1/campaigns", json={"nome": "Mesa Bugada"}, headers=auth(token_mestre)
    ).get_json()["data"]

    _admin, token_admin = make_user(role="ADMIN")
    # Admin lista todas as mesas.
    listagem = client.get("/api/v1/admin/campaigns", headers=auth(token_admin))
    assert listagem.status_code == 200
    assert any(item["id"] == mesa["id"] for item in listagem.get_json()["data"])

    # Mestre comum não pode moderar.
    assert client.get("/api/v1/admin/campaigns", headers=auth(token_mestre)).status_code == 403

    # Admin desbuga (remove) a mesa.
    remocao = client.delete(f"/api/v1/admin/campaigns/{mesa['id']}", headers=auth(token_admin))
    assert remocao.status_code == 200


def test_stats_conta_corretamente(client, make_user, auth):
    _admin, token_admin = make_user(role="ADMIN")
    make_user(role="JOGADOR")
    make_user(role="MESTRE")

    dados = client.get(URL_STATS, headers=auth(token_admin)).get_json()["data"]
    assert dados["usuarios"]["ADMIN"] >= 1
    assert dados["usuarios"]["JOGADOR"] >= 1
    assert dados["usuarios"]["MESTRE"] >= 1
    assert "personagens" in dados and "mesas" in dados
