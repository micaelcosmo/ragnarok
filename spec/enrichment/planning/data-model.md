# Modelo de Dados — Enriquecimento

Modelos **separados** (decisão do dono): `Arma`, `Armadura`, `Item`. Todos com `fonte`
(obrigatória), `homebrew`, `oficial`, `criado_por`, e escopo de ownership.

## Campos comuns de conteúdo
```yaml
comum:
  slug, nome, descricao
  fonte: "obrigatória"          # procedência (oficial ou homebrew)
  homebrew: bool                # true se criado por usuário
  criado_por: user_id|null
  idioma: "en|pt"               # idioma do registro (p/ toggle EN/PT)
  # escopo (ownership)
  personagem_id: null           # se setado -> só aquele personagem usa (criado por jogador)
  mesa_id: null                 # homebrew de mesa (mestre)
  # global = personagem_id e mesa_id nulos
```

## Arma
```yaml
Arma(comum):
  categoria: "simples|marcial"
  alcance: "corpo a corpo|à distância"
  dano: "1d8"
  tipo_dano: "cortante|perfurante|concussão"
  propriedades: ["versátil(1d10)", "leve", "acuidade", ...]
  bonus_magico: 0               # +X mágico (acerto/dano)
  efeitos: {...}                # ex.: acuidade muda atributo de ataque; +X soma
```
Ao **equipar**: contribui `ataque` (mod do atributo + proficiência + bônus mágico) e `dano`.

## Armadura
```yaml
Armadura(comum):
  categoria: "leve|média|pesada|escudo"
  ca_base: 14                   # null p/ escudo
  ca_soma_des: true
  ca_des_max: 2|null
  ca_bonus: 0                   # escudo (+2) / +X mágico
  requisito_forca: 0
  furtividade_desvantagem: bool
  bonus_magico: 0
  efeitos: {ca_base, ca_soma_des, ca_des_max, ca_bonus}
```
Ao **equipar**: define a fórmula de CA (ver effects-engine). **CA também editável** com
`ca_ajuste` manual no personagem.

## Item (não-arma/armadura)
```yaml
Item(comum):
  tipo_item: "maravilhoso|poção|pergaminho|anel|varinha|..."   # campo real (evita colidir c/ discriminador 'tipo')
  raridade: "comum|incomum|raro|muito raro|lendário"
  requer_sintonia: bool
  # SEM efeitos numéricos -> apenas DESCRITIVO (editável)
```

## Implementação (as-built, Fase 2) — fiel ao código
`backend/app/models/items.py`. Mixin `ConteudoItemMixin(TimestampMixin)` com campos comuns:
`id, slug(index, NÃO único — permite homebrew repetido), nome, descricao, fonte(NOT NULL,
default 'Homebrew'), homebrew(default True), idioma('pt'), criado_por(FK), personagem_id(FK),
mesa_id(FK)`. `to_dict()` adiciona `oficial = not homebrew`, `global = (sem personagem e sem mesa)`
e `tipo` ('arma'|'armadura'|'item'). `pode_editar(user)` = criador, ADMIN ou mestre da mesa.
Tabelas `armas`/`armaduras`/`itens`; migração Alembic `9c6b8cab1404`.
Endpoints de catálogo global (leitura): `GET /reference/{weapons,armor,items}` com `?q=`, `?fonte=`
e paginação (`limit`, default 80). Pipeline open5e: tipos `weapons/armor/items` (homebrew=False).

## Personagem — novas fontes e inventário
```yaml
Personagem (acréscimos):
  talentos: ["alerta", ...]            # slugs (fonte de efeitos)
  ca_ajuste: 0                         # ajuste manual de CA (+/-)
  inventario_armas: [arma_id, ...]
  inventario_armaduras: [armadura_id, ...]
  inventario_itens: [item_id, ...]
  armas_equipadas: [arma_id, ...]
  armadura_equipada_id: armadura_id|null
```
"Armas que o personagem pode usar" = acervo geral (oficial + homebrew aceito) ∪ itens com
`personagem_id == este`.

## Aceitação de homebrew por mesa
```yaml
MesaFonteAceita:
  mesa_id, fonte                       # mestre aceita uma fonte homebrew na mesa
```

## Reuso de `efeitos`
O mesmo esquema `efeitos` (ver effects-engine.md) é usado por raça, classe, antecedente,
talento, **arma** e **armadura**. `Item` e **magia** não entram na soma numérica.

## Migrações (Alembic)
Cada fase que toca o schema gera sua migração (`flask db migrate` + `upgrade`), preservando dados
(ADR-0002). Campos novos são nullable/com default para não quebrar registros existentes.
