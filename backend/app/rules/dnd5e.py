"""
Motor de regras do D&D 5E (SRD 5.1).

Funções PURAS: recebem números, devolvem números. Sem I/O, sem Flask, sem DB.
São a base do TDD (ver spec/backend/units/rules-engine.spec.md).
"""
from __future__ import annotations

import math

# Os seis atributos, na ordem canônica.
ATRIBUTOS = ["for", "des", "con", "int", "sab", "car"]

NOMES_ATRIBUTOS = {
    "for": "Força",
    "des": "Destreza",
    "con": "Constituição",
    "int": "Inteligência",
    "sab": "Sabedoria",
    "car": "Carisma",
}

# Perícia -> atributo regente (18 perícias do 5E, nomes pt-BR).
PERICIAS = {
    "Acrobacia": "des",
    "Adestrar Animais": "sab",
    "Arcanismo": "int",
    "Atletismo": "for",
    "Atuação": "car",
    "Enganação": "car",
    "Furtividade": "des",
    "História": "int",
    "Intimidação": "car",
    "Intuição": "sab",
    "Investigação": "int",
    "Medicina": "sab",
    "Natureza": "int",
    "Percepção": "sab",
    "Persuasão": "car",
    "Prestidigitação": "des",
    "Religião": "int",
    "Sobrevivência": "sab",
}

# Tabela oficial de XP acumulado para alcançar cada nível (índice 0 = nível 1).
_XP_NIVEL = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000,
]


def _clamp(valor: int, minimo: int, maximo: int) -> int:
    return max(minimo, min(maximo, valor))


def modificador(valor: int) -> int:
    """Modificador de atributo: floor((valor - 10) / 2)."""
    return math.floor((int(valor) - 10) / 2)


def bonus_proficiencia(nivel: int) -> int:
    """Bônus de proficiência por nível (1..20): 2 + floor((nivel-1)/4)."""
    nivel = _clamp(int(nivel), 1, 20)
    return 2 + (nivel - 1) // 4


# Níveis que concedem um Aumento de Habilidade (cada um vale +2 pontos para distribuir).
_NIVEIS_ASI = (4, 8, 12, 16, 19)
_PONTOS_POR_ASI = 2
TETO_ATRIBUTO = 20


def asi_pontos_por_nivel(nivel: int) -> int:
    """Orçamento de pontos de Aumento de Habilidade acumulado até o nível (SRD 5E)."""
    nivel = int(nivel or 1)
    return _PONTOS_POR_ASI * sum(1 for marco in _NIVEIS_ASI if nivel >= marco)


def sanear_asi(pedido: dict, pontos_total: int, atributos_base: dict) -> dict:
    """
    Filtra/clampa uma pool de ASI manual: apenas chaves `for..car` com inteiros > 0, respeitando o
    orçamento (`pontos_total`) em ordem determinística e o teto final 20 por atributo (base + ASI).
    """
    pedido = pedido or {}
    base = atributos_base or {}
    resultado = {}
    gasto = 0
    for chave in ATRIBUTOS:
        try:
            valor = int(pedido.get(chave, 0) or 0)
        except (TypeError, ValueError):
            valor = 0
        if valor <= 0:
            continue
        teto = max(0, TETO_ATRIBUTO - int(base.get(chave, 10)))   # não passa de 20 no final
        valor = min(valor, teto, pontos_total - gasto)            # nem do orçamento
        if valor <= 0:
            continue
        resultado[chave] = valor
        gasto += valor
    return resultado


_RECARGAS_VALIDAS = ("curto", "longo", "nenhum")


# Efeitos de exaustão por nível (SRD 5E), acumulativos na narrativa.
NIVEIS_EXAUSTAO = [
    "",                                                  # 0 — sem exaustão
    "Desvantagem em testes de habilidade",               # 1
    "Velocidade reduzida à metade",                      # 2
    "Desvantagem em ataques e testes de resistência",    # 3
    "PV máximo reduzido à metade",                       # 4
    "Velocidade reduzida a 0",                           # 5
    "Morte",                                             # 6
]


def clamp_morte(valor):
    """Sucessos/falhas de morte ficam em [0, 3]."""
    return _clamp(int(valor or 0), 0, 3)


def clamp_exaustao(valor):
    """Nível de exaustão fica em [0, 6]."""
    return _clamp(int(valor or 0), 0, 6)


def efeito_exaustao(nivel):
    """Descrição do efeito do nível de exaustão atual (vazio no nível 0)."""
    return NIVEIS_EXAUSTAO[clamp_exaustao(nivel)]


# Moedas (E33): valor de cada tipo em PO. 1 PO = 100 PC = 10 PP = 2 PE = 0,1 PL.
_MOEDAS_EM_PO = {"pc": 0.01, "pp": 0.1, "pe": 0.5, "po": 1.0, "pl": 10.0}


def sanear_moedas(d):
    """Filtra a bolsa de moedas: só pc/pp/pe/po/pl, inteiros >= 0 (negativos viram 0)."""
    limpo = {}
    for chave in _MOEDAS_EM_PO:
        if chave in (d or {}):
            try:
                limpo[chave] = max(0, int(d[chave] or 0))
            except (TypeError, ValueError):
                continue
    return limpo


def moedas_total_po(d):
    """Total das moedas convertido em PO (peças de ouro)."""
    total = sum(_MOEDAS_EM_PO[k] * int((d or {}).get(k, 0) or 0) for k in _MOEDAS_EM_PO)
    return round(total, 2)


def ca_sem_armadura(classe_slug, mods):
    """
    CA da Defesa sem Armadura por classe (None se a classe não tem a feature):
    Bárbaro = 10 + DES + CON; Monge = 10 + DES + SAB.
    """
    slug = (classe_slug or "").strip().lower()
    if slug == "barbarian":
        return 10 + int(mods.get("des", 0)) + int(mods.get("con", 0))
    if slug == "monk":
        return 10 + int(mods.get("des", 0)) + int(mods.get("sab", 0))
    return None


def sanear_recursos(lista) -> list:
    """Valida/clampa uma lista de recursos de classe: nome não-vazio, max>=0, atual em [0,max]."""
    limpos = []
    for item in (lista or []):
        if not isinstance(item, dict):
            continue
        nome = str(item.get("nome") or "").strip()
        recarga = item.get("recarga")
        if not nome or recarga not in _RECARGAS_VALIDAS:
            continue
        try:
            maximo = max(0, int(item.get("max", 0) or 0))
            atual = int(item.get("atual", 0) or 0)
        except (TypeError, ValueError):
            continue
        limpos.append({
            "nome": nome,
            "max": maximo,
            "atual": _clamp(atual, 0, maximo),
            "recarga": recarga,
            "descricao": str(item.get("descricao") or ""),
        })
    return limpos


def aplicar_descanso(recursos, tipo: str) -> list:
    """Recarrega (atual:=max) os recursos cujo tipo de recarga é coberto pelo descanso."""
    recarregaveis = {"curto"} if tipo == "curto" else {"curto", "longo"}
    novos = []
    for recurso in (recursos or []):
        copia = dict(recurso)
        if copia.get("recarga") in recarregaveis:
            copia["atual"] = int(copia.get("max", 0) or 0)
        novos.append(copia)
    return novos


def nivel_por_xp(xp: int) -> int:
    """Nível (1..20) correspondente a um total de XP acumulado."""
    xp = max(0, int(xp))
    nivel = 1
    for indice, xp_limite in enumerate(_XP_NIVEL):
        if xp >= xp_limite:
            nivel = indice + 1
        else:
            break
    return nivel


def valor_pericia(atributo_mod: int, proficiente: bool, bonus_prof: int) -> int:
    """Valor de uma perícia: mod do atributo + (proficiência se aplicável)."""
    return int(atributo_mod) + (int(bonus_prof) if proficiente else 0)


def valor_salvaguarda(atributo_mod: int, proficiente: bool, bonus_prof: int) -> int:
    """Valor de uma salvaguarda: idêntico à perícia."""
    return valor_pericia(atributo_mod, proficiente, bonus_prof)


def percepcao_passiva(mod_sabedoria: int, proficiente_percepcao: bool, bonus_prof: int) -> int:
    """Percepção passiva: 10 + valor da perícia Percepção."""
    return 10 + valor_pericia(mod_sabedoria, proficiente_percepcao, bonus_prof)


def cd_magia(mod_conjuracao: int, bonus_prof: int) -> int:
    """CD de salvaguarda das magias: 8 + bônus de proficiência + mod de conjuração."""
    return 8 + int(bonus_prof) + int(mod_conjuracao)


def bonus_ataque_magia(mod_conjuracao: int, bonus_prof: int) -> int:
    """Bônus de ataque de magia: bônus de proficiência + mod de conjuração."""
    return int(bonus_prof) + int(mod_conjuracao)


def iniciativa(mod_destreza: int, bonus_extra: int = 0) -> int:
    """Bônus de iniciativa: mod de Destreza + bônus extra."""
    return int(mod_destreza) + int(bonus_extra)


def pv_maximo_sugerido(dado_vida: int, nivel: int, mod_constituicao: int) -> int:
    """
    PV máximo sugerido (média): nível 1 = dado cheio + CON;
    níveis seguintes usam a média do dado (dado/2 + 1) + CON por nível.
    """
    nivel = max(1, int(nivel))
    media_por_nivel = dado_vida // 2 + 1
    total = dado_vida + mod_constituicao
    total += (nivel - 1) * (media_por_nivel + mod_constituicao)
    return max(1, total)


def ficha_derivada(atributos: dict, nivel: int, *,
                   pericias_proficientes=None,
                   salvaguardas_proficientes=None,
                   atributo_conjuracao=None,
                   iniciativa_bonus_extra=0) -> dict:
    """
    Monta o bloco de campos derivados de uma ficha a partir dos atributos base
    e do nível. Usado na serialização de Personagem (não persistido).
    """
    pericias_proficientes = set(pericias_proficientes or [])
    salvaguardas_proficientes = set(salvaguardas_proficientes or [])

    mods = {atributo: modificador(atributos.get(atributo, 10)) for atributo in ATRIBUTOS}
    bp = bonus_proficiencia(nivel)

    pericias = []
    for nome_pericia, atributo in PERICIAS.items():
        proficiente = nome_pericia in pericias_proficientes
        pericias.append({
            "nome": nome_pericia,
            "atributo": atributo,
            "proficiente": proficiente,
            "valor": valor_pericia(mods[atributo], proficiente, bp),
        })

    salvaguardas = []
    for atributo in ATRIBUTOS:
        proficiente = atributo in salvaguardas_proficientes
        salvaguardas.append({
            "atributo": atributo,
            "proficiente": proficiente,
            "valor": valor_salvaguarda(mods[atributo], proficiente, bp),
        })

    derivado = {
        "modificadores": mods,
        "bonus_proficiencia": bp,
        "iniciativa": iniciativa(mods["des"], iniciativa_bonus_extra),
        "percepcao_passiva": percepcao_passiva(
            mods["sab"], "Percepção" in pericias_proficientes, bp
        ),
        "pericias": pericias,
        "salvaguardas": salvaguardas,
    }

    if atributo_conjuracao in ATRIBUTOS:
        mc = mods[atributo_conjuracao]
        derivado["cd_magia"] = cd_magia(mc, bp)
        derivado["bonus_ataque_magia"] = bonus_ataque_magia(mc, bp)
    else:
        derivado["cd_magia"] = None
        derivado["bonus_ataque_magia"] = None

    return derivado
