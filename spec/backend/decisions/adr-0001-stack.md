# ADR-0001 — Escolha de stack do backend

- **Status**: Aceito
- **Data**: 2026-06-05

## Contexto
O protótipo original (`legacy/`) é um monolito Flask com templates server-rendered e SQLite,
sem separação front/back, sem testes, sem papéis. O objetivo é uma plataforma estilo D&D Beyond
com 3 perfis (ADMIN/MESTRE/JOGADOR), frontend desacoplado (HTML/CSS/JS), backend só em Python,
banco PostgreSQL e tudo dockerizado, desenvolvido com SDD + TDD.

## Decisão
- **Flask** (não Django/FastAPI): leve, já familiar ao projeto, baixo atrito para API REST + JWT.
- **Flask-JWT-Extended** para autenticação stateless (token Bearer) — adequado a frontend SPA-like.
- **Flask-SQLAlchemy** mantendo continuidade do ORM já usado no legado.
- **PostgreSQL** em runtime; **SQLite em memória** nos testes (velocidade + zero setup no CI).
- **Regras de jogo como funções puras** em `app/rules/` — desacopladas de Flask/DB para TDD rápido.
- **Serialização manual** (`to_dict`) em vez de Marshmallow/Pydantic — menos dependências, controle
  total sobre campos derivados de regra.

## Consequências
- (+) Backend testável sem subir Postgres; regras de jogo 100% cobertas por testes unitários.
- (+) Frontend pode ser qualquer coisa que fale HTTP/JSON; trocável sem tocar no backend.
- (−) Sem migrations (usamos `create_all` + seed). Aceitável para projeto de estudo; ADR futuro
  pode introduzir Alembic se o schema estabilizar.

## Alternativas consideradas
- **FastAPI**: ótimo, mas adiciona curva (async, pydantic) sem ganho essencial aqui.
- **Manter templates Flask**: contraria o requisito de separação front/back.
