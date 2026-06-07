# Unit — Defesa sem Armadura automática (E30)

> Gap do roadmap: a CA sem armadura é manual. Bárbaro e Monge têm **Defesa sem Armadura**
> (fórmula que usa CON/SAB) que deveria ser calculada automaticamente quando sem armadura.

## Regra (SRD 5E)
```yaml
sem_armadura:
  barbarian: CA = 10 + mod(DES) + mod(CON)
  monk:      CA = 10 + mod(DES) + mod(SAB)
  outras:    CA = valor manual (personagem.ca, default 10)
observacao:
  - só vale SEM armadura equipada (com escudo o +2 ainda se aplica via ajuste, fora deste escopo)
  - usa-se max(manual, formula) para nunca reduzir uma CA que o jogador setou à mão
  - detecção por classe_slug ("barbarian"/"monk"); robusto a maiúsculas/acentos
```

## Componentes
```yaml
regras (app/rules/dnd5e.py):
  ca_sem_armadura(classe_slug, mods) -> int | None   # None se a classe não tem a feature
construtor (_calcular_ca):
  - sem armadura: ca_base = max(ca manual, ca_sem_armadura(classe, mods) ou 0) + ajuste
  - derivado["ca_detalhe"] = "Defesa sem Armadura (Bárbaro/Monge)" | "CA base" | "Armadura: <nome>"
```

## Critérios de aceite
```yaml
- barbarian sem armadura, DES 14(+2)/CON 16(+3), ca manual 10 -> CA 15
- monk sem armadura, DES 16(+3)/SAB 14(+2) -> CA 15
- com armadura equipada -> usa a armadura (inalterado)
- classe comum -> usa a CA manual (inalterado)
- ca_detalhe descreve a origem do cálculo
- sem migração; sem regressão
```

## Fora de escopo
- escudo automático, Defesa com Armadura de Draconato, estilos de luta que mexem na CA.
