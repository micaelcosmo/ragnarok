# Conteúdo Base — Arquitetura da Pipeline

Linha de processamento **orientada a objetos** (POO) em `backend/app/content/`.

## Estágios
```yaml
pipeline:
  - fetch:      # adapter busca registros brutos da fonte (HTTP ou arquivo)
  - normalize:  # converte o formato da fonte no nosso schema canônico (pt-BR keys, slug)
  - filter:     # descarta itens fora de licença/escopo (document permitido, tipo válido)
  - upsert:     # persiste no DB por slug (insere ausente; atualiza campos vazios)
  - report:     # devolve resumo {inseridos, atualizados, ignorados} por tipo
```

## Componentes (classes)
```yaml
classes:
  ContentSource (ABC):
    metodos: [nome, buscar(tipo) -> list[dict-bruto]]
  LocalSource(ContentSource):       # lê backend/data/*.json
  Open5eSource(ContentSource):      # HTTP api.open5e.com (paginação seguida)
  Dnd5eApiSource(ContentSource):    # HTTP www.dnd5eapi.co
  Normalizer:                       # mapeia bruto->canônico por tipo (estáticos por fonte)
  ContentPipeline:                  # orquestra fetch->normalize->filter->upsert->report
    construtor: (source, modelos_por_tipo, fonte_label)
    metodo: executar(tipos) -> Relatorio
  Relatorio:                        # acumula contagens e mensagens
```

## Schema canônico (chaves internas)
Cada tipo tem um conjunto de campos canônicos (os mesmos do modelo SQLAlchemy). O `Normalizer`
preenche `slug`, `nome`, ... e injeta `fonte`. Atributos sempre em `for/des/con/int/sab/car`.

## Idempotência
- Chave natural: `slug` (único por tipo).
- Inserção: cria se ausente.
- Atualização: por padrão **não sobrescreve** campos já preenchidos (preserva edições do admin);
  pode rodar em modo `--force` para sobrescrever.

## Interfaces de uso
```yaml
cli:
  comando: "python -m app.content.cli --source open5e --types feats,races,spells [--limit N] [--force]"
  efeito: roda a pipeline e imprime o relatório
seed:
  local: "python -m app.seed"   # usa LocalSource implicitamente (conteúdo offline)
api_admin:
  futuro: "POST /admin/content/import {source, types}"  # disparar ingestão pela UI (ADMIN)
```

## Rede e testes
- A pipeline com fontes HTTP precisa de internet (operação on-demand do admin, **não** no boot).
- **Testes não acessam a rede**: usam uma `FakeSource` em memória para validar
  normalize/filter/upsert/idempotência.

## Critérios de aceite
1. `ContentPipeline` com `FakeSource` insere N registros e, ao rodar de novo, insere 0 (idempotente).
2. Campo `fonte` é gravado em cada registro importado.
3. `LocalSource` carrega os JSON de `backend/data/` e popula os modelos.
4. CLI executa e imprime relatório com contagens por tipo.
