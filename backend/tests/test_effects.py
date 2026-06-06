"""Testes do motor de efeitos puro (app/rules/efeitos.py)."""
from app.rules import efeitos as ef


def test_combinar_soma_atributos_e_unifica_listas():
    a = {"atributos": {"for": 2}, "pericias": ["Atletismo"], "iniciativa": 1}
    b = {"atributos": {"for": 1, "con": 2}, "pericias": ["Atletismo", "Furtividade"], "iniciativa": 5}
    total = ef.combinar([a, b])
    assert total["atributos"] == {"for": 3, "con": 2}
    assert total["pericias"] == ["Atletismo", "Furtividade"]  # sem duplicar
    assert total["iniciativa"] == 6


def test_aplicar_soma_sobre_base():
    base = {
        "atributos": {"for": 15, "des": 14, "con": 13, "int": 10, "sab": 10, "car": 10},
        "pericias_proficientes": ["Intuição"],
        "salvaguardas_proficientes": [],
        "iniciativa_bonus": 0,
    }
    fontes = [
        {"atributos": {"for": 2}, "salvaguardas": ["for", "con"]},   # ex.: classe
        {"pericias": ["Atletismo", "Intimidação"]},                   # ex.: antecedente
        {"iniciativa": 1, "recursos": ["Você nunca é surpreendido."]},  # ex.: talento
    ]
    final = ef.aplicar(base, fontes)
    assert final["atributos"]["for"] == 17          # 15 + 2
    assert "Atletismo" in final["pericias_proficientes"]
    assert "Intuição" in final["pericias_proficientes"]   # manual preservado
    assert final["salvaguardas_proficientes"] == ["for", "con"]
    assert final["iniciativa_extra"] == 1
    assert "Você nunca é surpreendido." in final["recursos"]
    assert final["concedido"]["atributos"] == {"for": 2}


def test_remover_fonte_reverte_bonus():
    base = {"atributos": {"for": 10, "des": 10, "con": 10, "int": 10, "sab": 10, "car": 10},
            "pericias_proficientes": [], "salvaguardas_proficientes": [], "iniciativa_bonus": 0}
    talento = {"iniciativa": 1}
    com = ef.aplicar(base, [talento])
    sem = ef.aplicar(base, [])
    assert com["iniciativa_extra"] == 1
    assert sem["iniciativa_extra"] == 0   # removida a fonte, bônus some


def test_efeito_vazio_e_none_sao_ignorados():
    total = ef.combinar([None, {}, ef.efeito_vazio()])
    assert total["atributos"] == {}
    assert total["iniciativa"] == 0
