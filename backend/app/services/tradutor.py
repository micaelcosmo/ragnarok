"""
Tradutor offline (en->pt) com cache em banco. POO.

Backend de MT: usa **Argos Translate** (offline, gratuito, MIT) se estiver instalado e com o
modelo en->pt baixado; caso contrário, faz fallback (devolve o original marcando traduzido=False).
Assim a UI nunca quebra — mostra o original com um aviso de "sem tradução".
"""
from app.extensions import db
from app.models.translation import Traducao

_ARGOS_OK = None  # cache do estado do motor


def _argos_disponivel():
    global _ARGOS_OK
    if _ARGOS_OK is None:
        try:
            import argostranslate.translate  # noqa: F401
            _ARGOS_OK = True
        except Exception:
            _ARGOS_OK = False
    return _ARGOS_OK


class Tradutor:
    """Traduz textos en->pt com cache; degrada graciosamente sem o motor."""

    def __init__(self, idioma="pt"):
        self.idioma = idioma

    def _motor(self, texto):
        """Traduz via Argos se disponível; senão None."""
        if not texto or not _argos_disponivel():
            return None
        try:
            import argostranslate.translate as t
            return t.translate(texto, "en", "pt")
        except Exception:
            return None

    def campo(self, tipo, slug, campo, texto_original):
        """Devolve a tradução cacheada/gerada do campo, ou o original (fallback)."""
        if not texto_original:
            return texto_original, False
        cache = Traducao.query.filter_by(
            tipo=tipo, slug=slug, campo=campo, idioma=self.idioma
        ).first()
        if cache:
            return cache.texto, True
        traduzido = self._motor(texto_original)
        if traduzido and traduzido != texto_original:
            db.session.add(Traducao(tipo=tipo, slug=slug, campo=campo,
                                    idioma=self.idioma, texto=traduzido))
            db.session.commit()
            return traduzido, True
        return texto_original, False

    def aplicar(self, tipo, registro_dict, campos=("nome", "descricao")):
        """
        Aplica tradução nos campos de um dict serializado (somente se idioma do registro != pt).
        Anota `traduzido` (bool) no dict. Não traduz conteúdo já em pt.
        """
        if registro_dict.get("idioma") == "pt":
            return registro_dict
        algum = False
        for campo in campos:
            if campo in registro_dict and registro_dict[campo]:
                texto, ok = self.campo(tipo, registro_dict.get("slug", ""), campo, registro_dict[campo])
                registro_dict[campo] = texto
                algum = algum or ok
        registro_dict["traduzido"] = algum
        return registro_dict
