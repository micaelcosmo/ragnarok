# Unit — Admin marca conteúdo como OFICIAL (E32)

> Gap do roadmap: todo conteúdo criado via API é `homebrew`. Falta um caminho para o **ADMIN**
> promover um conteúdo a **oficial** (curadoria do catálogo).

## Objetivo
Permitir que o **ADMIN** promova um conteúdo homebrew do compêndio a oficial (`homebrew=False`),
opcionalmente ajustando a `fonte`. Operação de **governança** (não é papel de jogo).

## API
```yaml
- POST /reference/<tipo>/<slug>/oficializar   (ADMIN apenas)
    body opcional: { fonte?: str }
    efeito: homebrew=False; se fonte vier, atualiza; senão mantém
    resposta: o registro atualizado (oficial=true)
  tipos: races|classes|backgrounds|feats|spells
  - MESTRE/JOGADOR -> 403 ; tipo/slug inválido -> 404 ; idempotente (já oficial -> ok)
```

## Frontend
```yaml
- compêndio (modal de detalhe): se o usuário é ADMIN e o item é homebrew,
  botão "✔️ Tornar Oficial" (com prompt opcional de fonte). Recarrega a lista.
```

## Critérios de aceite
```yaml
- ADMIN oficializa homebrew -> homebrew=false / oficial=true (e fonte se enviada)
- MESTRE recebe 403
- slug inexistente -> 404
- idempotente: oficializar um já-oficial mantém oficial
- sem migração (usa o campo homebrew existente); sem regressão
```

## Fora de escopo
- oficializar itens de equipamento (weapons/armor/items vivem em outra rota) — fica para depois;
  reverter oficial -> homebrew (não é necessário hoje).
