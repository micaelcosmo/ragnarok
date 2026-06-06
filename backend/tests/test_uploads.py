"""Testes do upload seguro de imagens."""
import io

URL = "/api/v1/uploads"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64   # assinatura PNG válida + corpo


def _enviar(client, headers, conteudo, nome):
    return client.post(
        URL,
        data={"arquivo": (io.BytesIO(conteudo), nome)},
        content_type="multipart/form-data",
        headers=headers,
    )


def test_upload_png_valido(client, make_user, auth):
    _u, token = make_user()
    resp = _enviar(client, auth(token), PNG, "retrato.png")
    assert resp.status_code == 200
    url = resp.get_json()["data"]["url"]
    assert url.startswith("/api/v1/uploads/") and url.endswith(".png")
    # E o arquivo é servível.
    assert client.get(url, headers=auth(token)).status_code == 200


def test_upload_recusa_extensao(client, make_user, auth):
    _u, token = make_user()
    resp = _enviar(client, auth(token), b"qualquer coisa", "nota.txt")
    assert resp.status_code == 400


def test_upload_recusa_conteudo_falso(client, make_user, auth):
    """Extensão .png mas conteúdo não-imagem -> rejeita (magic bytes)."""
    _u, token = make_user()
    resp = _enviar(client, auth(token), b"<html>nao sou imagem</html>", "fake.png")
    assert resp.status_code == 400


def test_upload_exige_autenticacao(client):
    resp = _enviar(client, {}, PNG, "x.png")
    assert resp.status_code == 401


def test_upload_recusa_grande(client, make_user, auth):
    _u, token = make_user()
    grande = b"\x89PNG\r\n\x1a\n" + b"\x00" * (2 * 1024 * 1024 + 200 * 1024)  # > 2MB
    resp = _enviar(client, auth(token), grande, "grande.png")
    assert resp.status_code in (400, 413)
