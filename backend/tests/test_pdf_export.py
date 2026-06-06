"""E25: exportar a ficha em PDF (estilo oficial 5E) via GET /characters/<id>/pdf.

A geração de bytes do PDF depende do WeasyPrint (+ libs nativas), presente no container.
Onde ele não estiver instalado, os testes de bytes são pulados; permissão e HTML rodam sempre.
"""
import pytest

URL = "/api/v1/characters"


def _criar_kzen(client, auth, token):
    payload = {
        "nome": "Kzen, o Impetuoso",
        "classe_slug": "barbarian",
        "nivel": 9,
        "atributos": {"for": 18, "des": 14, "con": 16, "int": 8, "sab": 12, "car": 10},
        "ca": 15, "pv_max": 95, "pv_atual": 95,
        "pericias_proficientes": ["Atletismo", "Percepção"],
        "salvaguardas_proficientes": ["for", "con"],
        "tracos_extras": [{"nome": "Fúria", "descricao": "Entra em fúria por bônus de dano."}],
    }
    return client.post(URL, json=payload, headers=auth(token)).get_json()["data"]["id"]


def test_pdf_403_para_outro_usuario(client, make_user, auth):
    """A permissão é checada antes de renderizar — não depende do WeasyPrint."""
    _dono, token_dono = make_user()
    pid = _criar_kzen(client, auth, token_dono)
    _intruso, token_intruso = make_user()
    resp = client.get(f"{URL}/{pid}/pdf", headers=auth(token_intruso))
    assert resp.status_code == 403


def test_pdf_404_para_inexistente(client, make_user, auth):
    _u, token = make_user()
    assert client.get(f"{URL}/999999/pdf", headers=auth(token)).status_code == 404


def test_html_intermediario_tem_campos_chave(client, app, make_user, auth):
    """O HTML que vira PDF deve conter os campos da ficha (sem precisar do motor)."""
    from app.models.character import Personagem
    from app.services.ficha_pdf import FichaPDF

    _u, token = make_user()
    pid = _criar_kzen(client, auth, token)
    with app.app_context():
        personagem = Personagem.query.get(pid)
        html = FichaPDF(personagem).render_html()
    assert "Kzen, o Impetuoso" in html
    assert "Força" in html and "Constituição" in html
    assert "Fúria" in html          # traço incremental aparece
    assert "CA" in html or "Classe de Armadura" in html


def test_endpoint_gera_pdf_valido(client, make_user, auth):
    """Baixa um PDF de verdade — pulado se o WeasyPrint não estiver disponível."""
    pytest.importorskip("weasyprint")
    _u, token = make_user()
    pid = _criar_kzen(client, auth, token)
    resp = client.get(f"{URL}/{pid}/pdf", headers=auth(token))
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert resp.data[:4] == b"%PDF"
    assert "attachment" in resp.headers.get("Content-Disposition", "")
    assert len(resp.data) > 1000
