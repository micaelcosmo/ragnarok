# ADR-0002 — Adoção do Alembic (Flask-Migrate) para evolução de schema

- **Status**: Aceito
- **Data**: 2026-06-06

## Contexto
O schema era criado por `db.create_all()`, que **só cria tabelas ausentes** e **não altera**
tabelas existentes. Na prática, adicionar colunas (ex.: `fonte`) ou tabelas (`talentos`) exigiu
recriar o banco (`docker compose down -v`) — **destrutivo**. Com a plataforma já online e com
dados reais (contas de jogadores, ~3.200 monstros ingeridos), isso era um risco inaceitável.

## Decisão
Adotar **Flask-Migrate/Alembic** para versionar o schema, mantendo os dados existentes:
1. Adicionada a extensão `Migrate` (`app/extensions.py`, inicializada no app factory).
2. Gerada a **migração baseline** (autogenerate contra um banco vazio) representando o schema atual.
3. O banco **já existente em produção** foi marcado com `flask db stamp head` — registra a revisão
   atual **sem reexecutar** os `CREATE`, preservando 100% dos dados.
4. O `entrypoint.sh` passou a rodar `flask db upgrade` no boot (idempotente: cria o schema em
   banco vazio; no-op em banco já no head).
5. Adicionados scripts `scripts/backup.ps1` e `scripts/restore.ps1` (pg_dump/psql) como rede de
   segurança.

## Fluxo daqui em diante
```yaml
mudanca_de_schema:
  - editar models
  - "flask db migrate -m 'descreve a mudança'"   # gera ALTER não-destrutivo
  - "flask db upgrade"                            # aplica preservando dados
boot_em_producao:
  - entrypoint: "flask db upgrade" -> seed idempotente -> gunicorn
seguranca:
  - "scripts/backup.ps1 antes de qualquer migração relevante"
```

## Consequências
- (+) Schema evolui sem perder dados; fim do `down -v` para aplicar colunas novas.
- (+) Histórico de migrações versionado em `backend/migrations/versions/`.
- (−) Exige disciplina: gerar/migrar a cada mudança de model. Revisar o autogenerate (ele não
  detecta tudo, ex.: renomeações são vistas como drop+add).

## Notas
- Testes continuam usando `db.create_all()` em SQLite em memória (rápido, sem migrações) — as
  migrações cobrem o runtime (Postgres).
- A baseline foi gerada contra um banco vazio para capturar o schema completo; o banco vivo foi
  apenas carimbado (stamp), nunca recriado.
