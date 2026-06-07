# Unit — Aumentos de Habilidade (ASI) por nível (E26)

> Atende o item #6 do `ajustes-pendentes.md` (parte ASI). Estende o motor base+fontes do E22.

## Objetivo
Permitir alocar **Aumentos de Habilidade** de forma **mecânica e reversível** (uma "pool" de pontos),
em vez de embutir no atributo base. O total final continua = base + fontes (raça/classe/antec/
talentos/traços) **+ ASI manual**, mantendo o indicador ▲ e a reversibilidade.

## Regra (SRD 5E)
```yaml
asi:
  niveis_que_concedem: [4, 8, 12, 16, 19]   # cada um = +2 pontos para distribuir
  pontos_por_asi: 2
  pontos_totais(nivel): "2 * (quantos níveis de niveis_que_concedem <= nivel)"
  exemplos:
    nivel_3: 0
    nivel_4: 2
    nivel_8: 4
    nivel_9: 4
    nivel_12: 6
    nivel_19: 10
  limite_por_atributo: 20            # teto duro 5E (clamp do valor FINAL, defensivo)
  observacao: "Classes com ASI extra (Guerreiro 6/14, Ladino 10) ficam para o futuro."
```

## Componentes
```yaml
model:
  campo: Personagem.bonus_atributos_manuais  # JSON {for..car: int}, default {}
  migracao: alembic (nullable / default {})
regras:
  arquivo: app/rules/dnd5e.py
  add: asi_pontos_por_nivel(nivel) -> int
construtor:
  - dobra bonus_atributos_manuais como fonte de efeitos {"atributos": {...}} -> entra no final
  - derivado["asi"] = {pontos_total, pontos_usados, pontos_restantes}
api:
  - aceita bonus_atributos_manuais (dict) com validação: só chaves for..car, inteiros >= 0,
    clamp por atributo e respeitando pontos_total (não deixa alocar além do orçamento)
frontend:
  - seção "Aumentos de Habilidade" no editor: +/- por atributo, mostra pontos restantes,
    bloqueia quando acabam; salva no update. Stat block já mostra ▲ (final > base).
```

## Critérios de aceite
```yaml
- asi_pontos_por_nivel: 3->0, 4->2, 9->4, 12->6, 19->10
- alocar {for:2} num personagem nivel 4 -> atributos_final.for = base+2, asi.pontos_usados=2, restantes=0
- zerar bonus_atributos_manuais -> final volta ao base (reversível)
- API recusa/clampa: chave inválida ignorada; soma > pontos_total é cortada; valor final > 20 é limitado
- derivados expõem asi {pontos_total, pontos_usados, pontos_restantes}
- sem regressão na suíte
```

## Fora de escopo (futuro)
- ASI extra por classe (Guerreiro/Ladino), escolha "ASI ou talento" guiada por nível, half-feats com escolha de atributo.
