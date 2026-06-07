# Unit — Galeria de imagens do personagem (E34)

> Gap do roadmap: hoje há 2 slots (retrato + símbolo). Pedido: **várias imagens** por personagem
> (corpo inteiro, rosto, cenas), com legenda e uma marcada como **principal**.

## Modelo
```yaml
Personagem.imagens: JSON (lista), default []
  item: { url: str, legenda: str, principal: bool }
migração: Alembic (coluna JSON)
reuso: upload via POST /uploads (já existente, validado por magic-bytes)
```

## Regras (app/rules/dnd5e.py)
```yaml
sanear_imagens(lista):
  - cada item precisa de `url` não-vazia; legenda str; principal bool
  - normaliza: no máximo UMA principal (a primeira marcada vence); descarta itens sem url
```

## API
```yaml
- PUT /characters/<id> aceita `imagens` -> sanear_imagens
derivados:
  - derivado["imagem_principal"] = url da principal (ou avatar_url como fallback)
```

## Frontend
```yaml
- aba Identidade: galeria de miniaturas (principal destacada com ★)
- botão "＋ Imagem" (upload), por imagem: definir principal (★), legenda, remover
- usa api.upload + api.characters.update; reflete ao vivo
```

## Critérios de aceite
```yaml
- adicionar imagens salva a lista; só uma principal
- item sem url é descartado
- derivado.imagem_principal retorna a principal (ou avatar_url se nenhuma)
- sem regressão
```

## Fora de escopo
- mostrar a galeria no PDF; limpeza de imagens órfãs no servidor (já no roadmap).
