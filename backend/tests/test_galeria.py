"""E34: galeria de imagens do personagem (várias + uma principal)."""
from app.rules import dnd5e

URL = "/api/v1/characters"


def test_sanear_imagens():
    bruto = [
        {"url": "/api/v1/uploads/a.png", "legenda": "Rosto", "principal": True},
        {"url": "/api/v1/uploads/b.png", "principal": True},   # 2ª principal -> vira False
        {"legenda": "sem url"},                                 # descartada
        {"url": "  ", "legenda": "vazia"},                      # url vazia -> descartada
    ]
    limpo = dnd5e.sanear_imagens(bruto)
    assert len(limpo) == 2
    assert limpo[0] == {"url": "/api/v1/uploads/a.png", "legenda": "Rosto", "principal": True}
    assert limpo[1]["principal"] is False


def test_api_imagens_e_principal(client, make_user, auth):
    _u, token = make_user()
    pid = client.post(URL, json={"nome": "Modelo", "avatar_url": "/api/v1/uploads/av.png"},
                      headers=auth(token)).get_json()["data"]["id"]
    # sem galeria: principal cai no avatar
    d0 = client.get(f"{URL}/{pid}", headers=auth(token)).get_json()["data"]["derivados"]
    assert d0["imagem_principal"] == "/api/v1/uploads/av.png"

    d = client.put(f"{URL}/{pid}", json={"imagens": [
        {"url": "/api/v1/uploads/corpo.png", "legenda": "Corpo", "principal": False},
        {"url": "/api/v1/uploads/rosto.png", "legenda": "Rosto", "principal": True},
    ]}, headers=auth(token)).get_json()["data"]
    assert len(d["imagens"]) == 2
    assert d["derivados"]["imagem_principal"] == "/api/v1/uploads/rosto.png"
