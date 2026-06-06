# Changelog — Conteúdo Base

## [Não lançado]
### docs
- Spec dedicada: visão geral (objetivos, fontes, licenças), arquitetura da pipeline e
  spec de importers/modelo `Talento`.

### feat
- Pipeline POO (`app/content/`): `ContentSource` (ABC), `LocalSource`, `Open5eSource`,
  `ContentPipeline`, `Relatorio` e CLI (`python -m app.content.cli`).
- `Open5eSource` (OGL): User-Agent próprio, paginação, normalização por tipo
  (feats/races/classes/backgrounds/spells/monsters), atributos EN→`for/des/con/int/sab/car`,
  pés→metros.
- Truncamento automático de strings ao tamanho da coluna (robustez na ingestão).
- Idempotência por `slug`; modo `--force` para sobrescrever.

### data
- Ingestão real open5e: +73 talentos, +1389 magias, +3181 monstros, +11 raças,
  taggeados por fonte (SRD 5.1, Kobold Press, Level Up A5e, Deep Magic, etc.).

### test
- Testes offline (FakeSource): inserção, idempotência, gravação de `fonte`, `--force`,
  carga do LocalSource e normalização de atributos do open5e.
