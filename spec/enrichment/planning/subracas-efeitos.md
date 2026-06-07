# Unit — Sub-raças aplicando efeitos (E29)

> Gap do roadmap: a raça aplica `efeitos`, mas a **sub-raça** (ex.: Halfling Robusto +1 CON,
> resistência a veneno) não era auto-aplicada. Hoje só existe no texto.

## Objetivo
Ao escolher uma **sub-raça**, aplicar automaticamente seus bônus (base + fontes, reversível) e
expor seus traços descritivos — reusando o motor de efeitos do `ConstrutorDeFicha`.

## Modelo
```yaml
Personagem.subraca_slug: str nullable  (migração Alembic)
Raca.subracas: já existe (JSON) -> [{slug, nome, bonus_atributos, tracos:[{nome,descricao}], efeitos?}]
```

## Regras / construtor
```yaml
ConstrutorDeFicha._fontes_efeitos:
  - se raca_slug e subraca_slug: localizar a sub-raça em raca.subracas (por slug)
  - fonte = subraca.efeitos OU {"atributos": subraca.bonus_atributos}
derivados:
  - derivado["subraca"] = {slug, nome, tracos} para exibição (None se não houver)
  - os tracos da sub-raça entram como cards descritivos em tracos_ativos (origem "subraca")
```

## API
```yaml
- PUT/POST aceita `subraca_slug` (campo texto). Se a sub-raça não existir na raça, é ignorada no cálculo.
```

## Frontend
```yaml
- editor: campo "Sub-raça" (slug) ao lado de Raça, com dica das sub-raças disponíveis
- ficha: chip da sub-raça no cabeçalho; traços da sub-raça aparecem no painel Traços
```

## Critérios de aceite
```yaml
- raça com bonus {for:2} + sub-raça com bonus {con:1} -> atributos_final soma ambos (reversível)
- limpar subraca_slug remove o efeito da sub-raça
- sub-raça inexistente é ignorada (sem erro)
- derivados.subraca traz nome + tracos; tracos entram em tracos_ativos (origem subraca)
- sem regressão
```

## Fora de escopo (futuro)
- escolha de idioma/perícia concedidos pela sub-raça com UI dedicada; sub-raças homebrew.
