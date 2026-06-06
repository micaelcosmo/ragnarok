"""Fase 2: normalização de armas/armaduras/itens (open5e) e endpoints de catálogo."""
from app.content.open5e_source import Open5eSource
from app.extensions import db
from app.models.items import Arma, Armadura, Item


def test_norm_weapon_deriva_efeito_ataque():
    fonte = Open5eSource()
    bruto = {"slug": "longsword", "name": "Longsword", "category": "Martial Melee",
             "damage_dice": "1d8", "damage_type": "slashing",
             "properties": ["Versatile (1d10)", "Finesse"], "document__title": "SRD"}
    c = fonte._norm_weapons(bruto)
    assert c["categoria"] == "marcial"
    assert c["efeitos"]["ataque"]["dano"] == "1d8"
    assert c["efeitos"]["ataque"]["acuidade"] is True   # Finesse
    assert c["homebrew"] is False


def test_norm_armor_deriva_efeito_ca():
    fonte = Open5eSource()
    bruto = {"slug": "leather", "name": "Leather", "category": "Light",
             "base_ac": 11, "plus_dex_mod": True, "plus_max": None,
             "stealth_disadvantage": False, "document__title": "SRD"}
    c = fonte._norm_armor(bruto)
    assert c["ca_base"] == 11
    assert c["efeitos"]["ca_base"] == 11
    assert c["efeitos"]["ca_soma_des"] is True


def _seed_itens(app):
    with app.app_context():
        db.session.add(Arma(slug="adaga", nome="Adaga", dano="1d4", tipo_dano="perfurante",
                            fonte="SRD 5.1", homebrew=False))
        db.session.add(Armadura(slug="cota", nome="Cota de Malha", ca_base=16,
                               fonte="SRD 5.1", homebrew=False))
        db.session.add(Item(slug="bola-cristal", nome="Bola de Cristal", raridade="muito raro",
                           fonte="SRD 5.1", homebrew=False))
        db.session.commit()


def test_endpoints_listam_catalogo(client, app, make_user, auth):
    _seed_itens(app)
    _u, token = make_user()
    for caminho, slug in [("weapons", "adaga"), ("armor", "cota"), ("items", "bola-cristal")]:
        resp = client.get(f"/api/v1/reference/{caminho}", headers=auth(token))
        assert resp.status_code == 200
        assert any(r["slug"] == slug for r in resp.get_json()["data"])


def test_itens_exigem_autenticacao(client):
    assert client.get("/api/v1/reference/weapons").status_code == 401
