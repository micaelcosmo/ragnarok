"""
FichaPDF — renderiza a ficha de um personagem em PDF com layout estilo oficial 5E.

POO: monta o contexto a partir do `Personagem` + derivados já calculados (mesma fonte da
verdade da ficha web), renderiza um template Jinja (HTML + print-CSS) e converte via WeasyPrint.
Ver ADR-0003. O import do WeasyPrint é lazy (só na hora de gerar bytes) para manter o serviço
testável sem as libs nativas.
"""
import re
from pathlib import Path

from flask import current_app
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.rules import dnd5e

TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "pdf"


class FichaPDF:
    """Gera o HTML/PDF da ficha de um personagem."""

    def __init__(self, personagem):
        self.personagem = personagem
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.env.filters["sinal"] = self._com_sinal

    @staticmethod
    def _com_sinal(valor):
        """Formata um modificador com sinal explícito (+3, -1, +0)."""
        numero = int(valor or 0)
        return f"+{numero}" if numero >= 0 else str(numero)

    def _imagem_local(self, url):
        """
        Resolve uma imagem para um caminho de arquivo (file://) **apenas** se for um upload
        nosso (em UPLOAD_DIR). URLs externas são ignoradas — evita SSRF/timeout no renderizador.
        """
        if not url:
            return None
        if "/uploads/" in url or url.startswith("/api/v1/uploads/"):
            nome = url.rsplit("/", 1)[-1]
        elif "://" not in url and "/" not in url:
            nome = url
        else:
            return None  # URL externa: não busca
        nome = nome.split("?")[0]
        caminho = Path(current_app.config["UPLOAD_DIR"]) / nome
        return caminho.as_uri() if caminho.exists() else None

    def _contexto(self):
        p = self.personagem.to_dict()           # já inclui o bloco "derivados"
        d = p.get("derivados") or {}
        return {
            "p": p,
            "d": d,
            "nomes_atributos": dnd5e.NOMES_ATRIBUTOS,
            "atributos_ordem": dnd5e.ATRIBUTOS,
            "css": (TEMPLATES / "ficha.css").read_text(encoding="utf-8"),
            "retrato": self._imagem_local(p.get("avatar_url")),
            "simbolo": self._imagem_local(p.get("simbolo_faccao_url")),
        }

    def render_html(self):
        """HTML intermediário (também útil para testes/depuração)."""
        return self.env.get_template("ficha.html").render(**self._contexto())

    def render_pdf(self):
        """Bytes do PDF. Import lazy do WeasyPrint (libs nativas só em runtime)."""
        from weasyprint import HTML

        return HTML(string=self.render_html()).write_pdf()

    def nome_arquivo(self):
        slug = re.sub(r"[^a-z0-9]+", "-", (self.personagem.nome or "ficha").lower()).strip("-")
        return f"ficha-{slug or 'personagem'}.pdf"
