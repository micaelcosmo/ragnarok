# Unit — Revisão automática da ficha (E39, nova)

> Agiliza a ficha: um "lint" que aponta **inconsistências** automaticamente — o jogador/mestre
> revisa rápido em vez de caçar erro a olho. Alinhado a "agilizar questões de ficha".

## Regras (pura, `app/rules/dnd5e.py`)
```yaml
revisar_ficha(p, d) -> [ {nivel: "alerta"|"info", msg} ]
  alertas (erros prováveis):
    - PV máximo <= 0
    - PV atual > PV máximo
    - atributo FINAL fora de 1..30
    - Aumentos de Habilidade acima do orçamento do nível (asi.usados > asi.total)
    - exaustão >= 6 (morte)
    - atributo de conjuração inválido
    - perícias proficientes desconhecidas (fora das 18 do 5E)
  infos (confira se é intencional):
    - sem classe / sem raça
    - atributo final > 20
```

## Construtor / derivados
```yaml
- derivado["revisao"] = revisar_ficha(<subset do personagem>, derivado)
  (chamado ao final de construir(), com os derivados já calculados)
```

## Frontend
```yaml
- ficha: se houver itens, um aviso "🔍 Revisão (N)" no topo, expansível, listando alertas (vermelho)
  e infos (âmbar). Sem itens -> nada.
```

## Critérios de aceite
```yaml
- pv_atual > pv_max -> alerta ; perícia inválida -> alerta ; exaustão 6 -> alerta
- sem classe/raça -> info
- ficha consistente -> sem alertas (no máximo infos)
- sem migração; sem regressão
```

## Fora de escopo
- corrigir automaticamente; validar pré-requisitos de talentos/multiclasse.
