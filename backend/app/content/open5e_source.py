"""
Fonte open5e (https://api.open5e.com) — agregador de conteúdo OGL 1.0a.

Normaliza o formato da API para o schema canônico do Ragnarok. Cada registro recebe
`fonte` com o título do documento de origem (ex.: 'Systems Reference Document', 'Tome of Beasts').
Conteúdo em inglês (a API é em inglês); a tradução não faz parte desta etapa.
"""
import json
import urllib.request

from app.content.base import ContentSource

BASE_URL = "https://api.open5e.com/v1"

# Nome de atributo (inglês) -> chave interna.
_ATRIBUTO = {
    "strength": "for", "dexterity": "des", "constitution": "con",
    "intelligence": "int", "wisdom": "sab", "charisma": "car",
    "str": "for", "dex": "des", "con": "con", "int": "int", "wis": "sab", "cha": "car",
}


def _para_chave_atributo(nome):
    return _ATRIBUTO.get((nome or "").strip().lower())


def _pes_para_metros(pes):
    """Converte pés (D&D US) para metros no padrão 5ft = 1,5 m."""
    try:
        metros = (int(pes) / 5) * 1.5
        return f"{metros:g} m"
    except (TypeError, ValueError):
        return None


class Open5eSource(ContentSource):
    """Adapter HTTP para a API open5e (paginada)."""

    def __init__(self, limite=None, timeout=20):
        self.limite = limite
        self.timeout = timeout

    @property
    def nome(self) -> str:
        return "Open5e (OGL)"

    def buscar(self, tipo: str) -> list[dict]:
        normalizador = getattr(self, f"_norm_{tipo}", None)
        if normalizador is None:
            return []
        brutos = self._paginar(tipo)
        registros = []
        for bruto in brutos:
            try:
                canonico = normalizador(bruto)
            except Exception:  # registro malformado: ignora, não derruba a ingestão
                canonico = None
            if canonico:
                registros.append(canonico)
        return registros

    # ---- transporte ----
    def _paginar(self, recurso):
        resultados = []
        url = f"{BASE_URL}/{recurso}/?limit=50"
        while url:
            # Alguns servidores bloqueiam o User-Agent padrão do urllib; identificamos a app.
            requisicao = urllib.request.Request(
                url, headers={"User-Agent": "Ragnarok/1.0 (projeto acadêmico)"}
            )
            with urllib.request.urlopen(requisicao, timeout=self.timeout) as resposta:
                pagina = json.loads(resposta.read().decode())
            resultados.extend(pagina.get("results", []))
            if self.limite and len(resultados) >= self.limite:
                return resultados[: self.limite]
            url = pagina.get("next")
        return resultados

    # ---- normalizadores por tipo ----
    def _fonte(self, bruto):
        return bruto.get("document__title") or self.nome

    def _norm_feats(self, bruto):
        pre = (bruto.get("prerequisite") or "").strip()
        if not pre or pre.lower() == "none":
            pre = None
        elif len(pre) > 155:  # o campo é curto; metadados longos vão pra descrição
            pre = pre[:152] + "…"
        return {
            "slug": (bruto.get("slug") or "")[:80],
            "nome": (bruto.get("name") or "")[:120],
            "descricao": (bruto.get("desc") or "").strip(),
            "pre_requisito": pre,
            "fonte": self._fonte(bruto)[:120],
        }

    def _norm_races(self, bruto):
        bonus = {}
        for asi in bruto.get("asi", []) or []:
            valor = asi.get("value")
            for atributo in asi.get("attributes", []) or []:
                chave = _para_chave_atributo(atributo)
                if chave and valor:
                    bonus[chave] = valor
        tracos = []
        if bruto.get("traits"):
            tracos = [{"nome": "Traços Raciais", "descricao": bruto["traits"].strip()}]
        subracas = [
            {"slug": sub.get("slug"), "nome": sub.get("name"),
             "descricao": (sub.get("desc") or "").strip()}
            for sub in bruto.get("subraces", []) or []
        ]
        return {
            "slug": bruto.get("slug"),
            "nome": bruto.get("name"),
            "descricao": (bruto.get("desc") or "").strip(),
            "deslocamento": (bruto.get("speed") or {}).get("walk"),
            "tamanho": bruto.get("size"),
            "bonus_atributos": bonus,
            "tracos": tracos,
            "subracas": subracas,
            "fonte": self._fonte(bruto),
        }

    def _norm_backgrounds(self, bruto):
        pericias = [
            parte.strip()
            for parte in (bruto.get("skill_proficiencies") or "").split(",")
            if parte.strip()
        ]
        return {
            "slug": bruto.get("slug"),
            "nome": bruto.get("name"),
            "descricao": (bruto.get("desc") or "").strip(),
            "pericias": pericias,
            "equipamento": bruto.get("equipment"),
            "fonte": self._fonte(bruto),
        }

    def _norm_classes(self, bruto):
        salvaguardas = [
            chave for chave in (
                _para_chave_atributo(parte)
                for parte in (bruto.get("prof_saving_throws") or "").split(",")
            ) if chave
        ]
        dado = bruto.get("hit_dice") or ""
        try:
            dado_vida = int(dado.lower().replace("d", "").strip())
        except (ValueError, AttributeError):
            dado_vida = 8
        atributo_conj = _para_chave_atributo(bruto.get("spellcasting_ability"))
        return {
            "slug": bruto.get("slug"),
            "nome": bruto.get("name"),
            "descricao": (bruto.get("desc") or "").strip()[:4000],
            "dado_vida": dado_vida,
            "salvaguardas": salvaguardas,
            "conjurador": bool(atributo_conj),
            "atributo_conjuracao": atributo_conj,
            "fonte": self._fonte(bruto),
        }

    def _norm_spells(self, bruto):
        classes = [
            parte.strip().lower()
            for parte in (bruto.get("dnd_class") or "").split(",")
            if parte.strip()
        ]
        descricao = (bruto.get("desc") or "").strip()
        if bruto.get("higher_level"):
            descricao += "\n\nEm níveis superiores: " + bruto["higher_level"].strip()
        return {
            "slug": bruto.get("slug"),
            "nome": bruto.get("name"),
            "nivel": bruto.get("level_int", 0),
            "escola": bruto.get("school"),
            "tempo_conjuracao": bruto.get("casting_time"),
            "alcance": bruto.get("range"),
            "componentes": bruto.get("components"),
            "duracao": bruto.get("duration"),
            "concentracao": str(bruto.get("concentration")).lower() == "yes",
            "ritual": str(bruto.get("ritual")).lower() == "yes",
            "classes": classes,
            "descricao": descricao,
            "fonte": self._fonte(bruto),
        }

    def _norm_monsters(self, bruto):
        atributos = {}
        for nome_en, chave in (("strength", "for"), ("dexterity", "des"),
                               ("constitution", "con"), ("intelligence", "int"),
                               ("wisdom", "sab"), ("charisma", "car")):
            if bruto.get(nome_en) is not None:
                atributos[chave] = bruto[nome_en]
        habilidades = [
            {"nome": item.get("name"), "descricao": item.get("desc")}
            for item in bruto.get("special_abilities", []) or []
        ]
        acoes = [
            {"nome": item.get("name"), "descricao": item.get("desc")}
            for item in bruto.get("actions", []) or []
        ]
        pericias = bruto.get("skills")
        if isinstance(pericias, dict):
            pericias = ", ".join(f"{nome} {valor}" for nome, valor in pericias.items())
        return {
            "slug": bruto.get("slug"),
            "nome": bruto.get("name"),
            "tipo": bruto.get("type"),
            "tamanho": bruto.get("size"),
            "alinhamento": bruto.get("alignment"),
            "ca": bruto.get("armor_class") or 10,
            "pv": bruto.get("hit_points") or 1,
            "pv_formula": bruto.get("hit_dice"),
            "deslocamento": _pes_para_metros((bruto.get("speed") or {}).get("walk")),
            "atributos": atributos,
            "nd": str(bruto.get("challenge_rating")) if bruto.get("challenge_rating") else None,
            "pericias": pericias,
            "sentidos": bruto.get("senses"),
            "idiomas": bruto.get("languages"),
            "habilidades": habilidades,
            "acoes": acoes,
            "fonte": self._fonte(bruto),
        }
