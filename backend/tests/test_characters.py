"""Testes de Personagens: CRUD, campos derivados e ownership."""

URL = "/api/v1/characters"


def _criar_personagem(client, auth, token, **extra):
    payload = {"nome": "Aelar", "atributos": {"for": 16, "des": 14, "con": 14}}
    payload.update(extra)
    return client.post(URL, json=payload, headers=auth(token))


def test_criar_personagem(client, make_user, auth):
    usuario, token = make_user()
    resposta = _criar_personagem(client, auth, token)
    assert resposta.status_code == 201
    dados = resposta.get_json()["data"]
    assert dados["user_id"] == usuario.id
    assert dados["nome"] == "Aelar"


def test_derivados_modificadores(client, make_user, auth):
    _usuario, token = make_user()
    resposta = _criar_personagem(
        client, auth, token,
        nivel=5,
        pericias_proficientes=["Atletismo"],
    )
    derivados = resposta.get_json()["data"]["derivados"]
    assert derivados["modificadores"]["for"] == 3   # FOR 16 -> +3
    assert derivados["bonus_proficiencia"] == 3     # nível 5 -> +3
    atletismo = next(p for p in derivados["pericias"] if p["nome"] == "Atletismo")
    assert atletismo["valor"] == 6                  # +3 atributo +3 proficiência


def test_jogador_nao_ve_personagem_de_outro(client, make_user, auth):
    _dono, token_dono = make_user()
    criado = _criar_personagem(client, auth, token_dono).get_json()["data"]

    _outro, token_outro = make_user()
    resposta = client.get(f"{URL}/{criado['id']}", headers=auth(token_outro))
    assert resposta.status_code == 403


def test_atualizar_muda_derivados(client, make_user, auth):
    _usuario, token = make_user()
    criado = _criar_personagem(client, auth, token).get_json()["data"]

    atualizada = client.put(
        f"{URL}/{criado['id']}",
        json={"atributos": {"for": 20}},
        headers=auth(token),
    )
    assert atualizada.status_code == 200
    assert atualizada.get_json()["data"]["derivados"]["modificadores"]["for"] == 5


def test_deletar_personagem(client, make_user, auth):
    _usuario, token = make_user()
    criado = _criar_personagem(client, auth, token).get_json()["data"]

    apagar = client.delete(f"{URL}/{criado['id']}", headers=auth(token))
    assert apagar.status_code == 200

    lista = client.get(URL, headers=auth(token)).get_json()["data"]
    assert all(item["id"] != criado["id"] for item in lista)
