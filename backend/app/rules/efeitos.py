"""
Combinação de efeitos (bônus) de fontes sobre a ficha — funções PURAS (sem DB/Flask).

Modelo "base + fontes": a ficha final = camada base/manual + soma dos `efeitos` das fontes
ativas (raça, classe, antecedente, talentos, arma/armadura). Como tudo é recomputado das
fontes atuais, remover uma fonte remove o bônus automaticamente (reversível por construção).

Magias NÃO entram aqui (não concedem bônus numérico).
"""
from __future__ import annotations

from app.rules.dnd5e import ATRIBUTOS

# Esquema canônico de um efeito (todas as chaves opcionais).
CHAVES_LISTA = ("pericias", "salvaguardas", "sentidos", "idiomas", "proficiencias_texto", "recursos")
CHAVES_NUMERO = ("iniciativa", "deslocamento", "pv_por_nivel", "ca_bonus")


def efeito_vazio() -> dict:
    base = {chave: [] for chave in CHAVES_LISTA}
    base["atributos"] = {}
    for chave in CHAVES_NUMERO:
        base[chave] = 0
    return base


def combinar(efeitos: list[dict]) -> dict:
    """Soma uma lista de efeitos num efeito agregado (sem duplicar listas)."""
    total = efeito_vazio()
    for efeito in efeitos:
        if not efeito:
            continue
        for atributo, valor in (efeito.get("atributos") or {}).items():
            if atributo in ATRIBUTOS:
                total["atributos"][atributo] = total["atributos"].get(atributo, 0) + int(valor or 0)
        for chave in CHAVES_LISTA:
            for item in (efeito.get(chave) or []):
                if item not in total[chave]:
                    total[chave].append(item)
        for chave in CHAVES_NUMERO:
            total[chave] += int(efeito.get(chave) or 0)
    return total


def aplicar(base: dict, efeitos: list[dict]) -> dict:
    """
    Aplica os efeitos das fontes sobre a camada base/manual e devolve a ficha resolvida.

    `base` esperado:
      atributos: {for..car} (valores base/manuais)
      pericias_proficientes: [..]      (marcadas à mão)
      salvaguardas_proficientes: [..]
      iniciativa_bonus: int            (manual)
      caracteristicas: str|None        (texto manual)
    """
    agregado = combinar(efeitos)

    atributos_final = {}
    for atributo in ATRIBUTOS:
        atributos_final[atributo] = int(base.get("atributos", {}).get(atributo, 10)) \
            + agregado["atributos"].get(atributo, 0)

    pericias_base = list(base.get("pericias_proficientes") or [])
    pericias_final = pericias_base + [p for p in agregado["pericias"] if p not in pericias_base]

    salva_base = list(base.get("salvaguardas_proficientes") or [])
    salva_final = salva_base + [s for s in agregado["salvaguardas"] if s not in salva_base]

    return {
        "atributos": atributos_final,
        "pericias_proficientes": pericias_final,
        "salvaguardas_proficientes": salva_final,
        "iniciativa_extra": int(base.get("iniciativa_bonus") or 0) + agregado["iniciativa"],
        "deslocamento_extra": agregado["deslocamento"],
        "pv_por_nivel_extra": agregado["pv_por_nivel"],
        "ca_bonus": agregado["ca_bonus"],
        "sentidos": agregado["sentidos"],
        "idiomas": agregado["idiomas"],
        "proficiencias_texto": agregado["proficiencias_texto"],
        "recursos": agregado["recursos"],
        # Marca quais perícias/salvaguardas vieram de fontes (para a UI distinguir do manual).
        "concedido": {
            "pericias": list(agregado["pericias"]),
            "salvaguardas": list(agregado["salvaguardas"]),
            "atributos": dict(agregado["atributos"]),
        },
    }
