# Unit — Testes contra a Morte + Exaustão (E31)

> Gap do roadmap: não há campos para **testes de resistência contra a morte** (sucessos/falhas)
> nem para **exaustão** (níveis 1–6). Hoje só no papel.

## Modelo
```yaml
Personagem:
  mortes_sucesso: int [0..3], default 0
  mortes_falha:   int [0..3], default 0
  exaustao:       int [0..6], default 0
migração: Alembic (3 colunas int, nullable/default 0)
```

## Regras (app/rules/dnd5e.py)
```yaml
NIVEIS_EXAUSTAO: lista de descrições dos efeitos por nível (1..6 do SRD)
  1: Desvantagem em testes de habilidade
  2: Velocidade reduzida à metade
  3: Desvantagem em ataques e testes de resistência
  4: PV máximo reduzido à metade
  5: Velocidade reduzida a 0
  6: Morte
efeito_exaustao(nivel) -> str   # descrição acumulada do nível atual (ou "" no nível 0)
clamp_morte(v) -> 0..3 ; clamp_exaustao(v) -> 0..6
```

## API
```yaml
- PUT aceita mortes_sucesso/mortes_falha/exaustao, com clamp (0..3 / 0..6)
derivados:
  - derivado["exaustao_efeito"] = efeito_exaustao(personagem.exaustao)
```

## Frontend
```yaml
- mini-painel "Estado" na ficha (perto do PV): 3 pips de sucesso + 3 de falha de morte (clicáveis),
  e exaustão 0–6 com − / + mostrando o efeito do nível atual. Salva via update; reflete ao vivo.
```

## Critérios de aceite
```yaml
- mortes_sucesso/falha clampam em [0,3]; exaustao em [0,6]
- exaustao_efeito traz a descrição do nível (vazio no 0; "Morte" no 6)
- persiste e aparece na ficha
- sem regressão
```

## Fora de escopo
- aplicar mecanicamente os efeitos de exaustão nos números (desvantagem/velocidade) — por ora é informativo.
