"""Testes unitários do motor de regras D&D 5E (funções puras)."""
import pytest

from app.rules import dnd5e as r


@pytest.mark.parametrize("valor,esperado", [
    (1, -5), (8, -1), (9, -1), (10, 0), (11, 0),
    (14, 2), (15, 2), (16, 3), (20, 5), (30, 10),
])
def test_modificador(valor, esperado):
    assert r.modificador(valor) == esperado


@pytest.mark.parametrize("nivel,esperado", [
    (1, 2), (4, 2), (5, 3), (8, 3), (9, 4),
    (12, 4), (13, 5), (16, 5), (17, 6), (20, 6),
])
def test_bonus_proficiencia(nivel, esperado):
    assert r.bonus_proficiencia(nivel) == esperado


def test_bonus_proficiencia_clamp():
    assert r.bonus_proficiencia(0) == 2
    assert r.bonus_proficiencia(99) == 6


@pytest.mark.parametrize("xp,nivel", [
    (0, 1), (299, 1), (300, 2), (900, 3),
    (6500, 5), (47999, 8), (48000, 9), (355000, 20), (999999, 20),
])
def test_nivel_por_xp(xp, nivel):
    assert r.nivel_por_xp(xp) == nivel


def test_valor_pericia():
    assert r.valor_pericia(2, True, 3) == 5
    assert r.valor_pericia(2, False, 3) == 2


def test_salvaguarda_e_passiva():
    assert r.valor_salvaguarda(1, True, 2) == 3
    assert r.percepcao_passiva(2, True, 2) == 14
    assert r.percepcao_passiva(2, False, 2) == 12


def test_magia():
    assert r.cd_magia(3, 2) == 13
    assert r.bonus_ataque_magia(3, 2) == 5


def test_iniciativa():
    assert r.iniciativa(3) == 3
    assert r.iniciativa(3, 1) == 4


def test_pv_maximo_sugerido():
    # Guerreiro nível 1, d10, CON +2 -> 12
    assert r.pv_maximo_sugerido(10, 1, 2) == 12
    # nível 2 acrescenta média (6) + CON (2) -> 20
    assert r.pv_maximo_sugerido(10, 2, 2) == 20


def test_ficha_derivada():
    atributos = {"for": 16, "des": 14, "con": 14, "int": 8, "sab": 12, "car": 10}
    d = r.ficha_derivada(
        atributos, nivel=5,
        pericias_proficientes=["Atletismo", "Percepção"],
        salvaguardas_proficientes=["for", "con"],
        atributo_conjuracao=None,
    )
    assert d["modificadores"]["for"] == 3
    assert d["bonus_proficiencia"] == 3
    assert d["iniciativa"] == 2  # mod des = +2
    # Atletismo (for +3) proficiente -> 3 + 3 = 6
    atletismo = next(p for p in d["pericias"] if p["nome"] == "Atletismo")
    assert atletismo["valor"] == 6 and atletismo["proficiente"]
    # Percepção (sab +1) proficiente -> 1 + 3 = 4 ; passiva = 14
    assert d["percepcao_passiva"] == 14
    # salvaguarda de Força proficiente -> 3 + 3 = 6
    salv_for = next(s for s in d["salvaguardas"] if s["atributo"] == "for")
    assert salv_for["valor"] == 6
    assert d["cd_magia"] is None


def test_ficha_derivada_conjurador():
    atributos = {"for": 8, "des": 14, "con": 12, "int": 16, "sab": 10, "car": 10}
    d = r.ficha_derivada(atributos, nivel=1, atributo_conjuracao="int")
    # mago nível 1: CD = 8 + 2 + 3 = 13 ; ataque = 2 + 3 = 5
    assert d["cd_magia"] == 13
    assert d["bonus_ataque_magia"] == 5
