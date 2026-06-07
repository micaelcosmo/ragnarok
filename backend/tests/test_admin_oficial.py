"""E32: ADMIN promove conteúdo homebrew a OFICIAL (curadoria do compêndio)."""
from app.extensions import db
from app.models.reference import Talento

URL = "/api/v1/reference/feats"


def _homebrew(app):
    with app.app_context():
        t = Talento(slug="meio-talento-teste", nome="Meio-Talento", descricao="x",
                    fonte="Homebrew da Mesa", homebrew=True)
        db.session.add(t)
        db.session.commit()


def test_admin_oficializa(client, app, make_user, auth):
    _homebrew(app)
    _admin, token = make_user(role="ADMIN")
    r = client.post(f"{URL}/meio-talento-teste/oficializar", json={"fonte": "SRD 5.1"},
                    headers=auth(token))
    assert r.status_code == 200
    d = r.get_json()["data"]
    assert d["homebrew"] is False and d["oficial"] is True and d["fonte"] == "SRD 5.1"


def test_mestre_nao_pode_oficializar(client, app, make_user, auth):
    _homebrew(app)
    _mestre, token = make_user(role="MESTRE")
    r = client.post(f"{URL}/meio-talento-teste/oficializar", json={}, headers=auth(token))
    assert r.status_code == 403


def test_oficializar_inexistente_404(client, make_user, auth):
    _admin, token = make_user(role="ADMIN")
    assert client.post(f"{URL}/nao-existe/oficializar", json={}, headers=auth(token)).status_code == 404
