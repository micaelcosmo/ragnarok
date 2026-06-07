# Unit — Cálculo automático de PV (E38, nova)

> Agiliza a ficha: sugerir o PV máximo a partir de classe + nível + mod de CON, com um clique
> (regra fixa do 5E). Continua editável à mão — é uma conveniência, não automação obrigatória.

## Regra (SRD 5E, "PV fixo")
```yaml
pv_sugerido(dado, nivel, con_mod):
  nivel 1: dado + con_mod
  cada nível seguinte: (dado/2 + 1) + con_mod
  total = (dado + con) + (nivel-1) * (dado//2 + 1 + con)   ; mínimo 1
dado: dado de vida da CLASSE primária (Classe.dado_vida); fallback: parse de personagem.dado_vida ("9d12") ou 8
nivel: nível total (multiclasse usa o total como aproximação — HP por classe fica como futuro)
```

## Construtor / derivados
```yaml
- derivado["dado_vida_classe"] = dado da classe primária (int)
- derivado["pv_sugerido"] = pv_sugerido(dado, nivel_total, mod CON)
```

## Frontend
```yaml
- ficha: botão "🎲 Calcular PV" perto do PV -> define pv_max := pv_sugerido
  (e pv_atual := pv_sugerido se estava 0 ou igual ao antigo máximo). Confirma antes de sobrescrever.
```

## Critérios de aceite
```yaml
- pv_sugerido(12,1,3)=15 ; pv_sugerido(12,3,3)=35 ; mínimo 1
- derivados expõem dado_vida_classe e pv_sugerido
- sem classe -> usa fallback (parse de dado_vida ou 8)
- sem migração; sem regressão
```

## Fora de escopo
- HP por classe no multiclasse; rolar os dados (este usa o valor fixo/médio).
