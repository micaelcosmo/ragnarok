# Unit Spec — Motor de Regras D&D 5E (`app/rules/dnd5e.py`)

Funções **puras** (sem I/O). Base para TDD. Todas testadas em `tests/test_rules.py`.

## `modificador(valor: int) -> int`
Modificador de atributo = `floor((valor - 10) / 2)`.
| valor | 1 | 8 | 10 | 11 | 14 | 15 | 20 | 30 |
|-------|---|---|----|----|----|----|----|----|
| mod   |-5 |-1 | 0  | 0  | +2 | +2 | +5 | +10|

## `bonus_proficiencia(nivel: int) -> int`
Por nível (1–20): níveis 1–4 → +2, 5–8 → +3, 9–12 → +4, 13–16 → +5, 17–20 → +6.
Fórmula: `2 + floor((nivel - 1) / 4)`. Clampa nível em [1, 20].

## `nivel_por_xp(xp: int) -> int`
Tabela oficial de XP→nível (0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000,
64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000).

## `valor_pericia(atributo_mod, proficiente, bonus_prof) -> int`
`atributo_mod + (bonus_prof if proficiente else 0)`.

## `valor_salvaguarda(atributo_mod, proficiente, bonus_prof) -> int`
Idem perícia.

## `percepcao_passiva(mod_sabedoria, proficiente_percepcao, bonus_prof) -> int`
`10 + valor_pericia(mod_sab, proficiente_percepcao, bonus_prof)`.

## `cd_magia(mod_conjuracao, bonus_prof) -> int`
`8 + bonus_prof + mod_conjuracao`.

## `bonus_ataque_magia(mod_conjuracao, bonus_prof) -> int`
`bonus_prof + mod_conjuracao`.

## `iniciativa(mod_destreza, bonus_extra=0) -> int`
`mod_destreza + bonus_extra`.

## `PERICIAS` (constante)
Mapa perícia→atributo (pt-BR). Ex.: `"Atletismo": "for"`, `"Furtividade": "des"`,
`"Percepção": "sab"`, `"Persuasão": "car"`, etc. (18 perícias do 5E).

## `ATRIBUTOS` (constante)
`["for","des","con","int","sab","car"]`.

## Critérios de aceite
- `modificador(15) == 2`; `modificador(8) == -1`; `modificador(30) == 10`.
- `bonus_proficiencia(1)==2`; `bonus_proficiencia(5)==3`; `bonus_proficiencia(20)==6`.
- `nivel_por_xp(0)==1`; `nivel_por_xp(300)==2`; `nivel_por_xp(355000)==20`.
- `cd_magia(3, 2) == 13`; `percepcao_passiva(2, True, 2) == 14`.
