# CLAUDE.md — Guia do Agente para o Projeto Ragnarok

> Este arquivo orienta agentes de IA (Claude Code) e desenvolvedores humanos a trabalhar
> neste repositório. Leia-o antes de qualquer alteração.

## 1. O que é o Ragnarok

**Ragnarok** é uma plataforma web para criação e gerenciamento de fichas de RPG **D&D 5E**,
inspirada no [D&D Beyond](https://www.dndbeyond.com). Projeto **acadêmico/de estudo**.
Usa apenas conteúdo do **SRD 5.1 (CC-BY 4.0 / OGL)**.

A plataforma atende três perfis de usuário:

| Perfil      | Pode fazer |
|-------------|------------|
| **ADMIN**   | **Gerente da plataforma** (governança, não é papel de jogo): gere contas/papéis, **modera mesas** (lista todas, desbuga/remove, tira membro preso), cura o **catálogo de conteúdo** (SRD + ingestões) e vê métricas. |
| **MESTRE**  | Papel de jogo: monta mesas (campanhas), gerencia jogadores convidados, cria/edita/adiciona PDMs (NPCs) e monstros ao bestiário da mesa. |
| **JOGADOR** | Entra em mesas, cria e edita personagens com ficha 5E completa e automatizada. |

## 2. Arquitetura (resumo)

Separação estrita **frontend / backend**, tudo **dockerizado**.

```
┌──────────────┐   HTTP/JSON    ┌──────────────┐   SQLAlchemy   ┌──────────────┐
│  Frontend    │ ─────────────► │   Backend    │ ─────────────► │  PostgreSQL  │
│ HTML/CSS/JS  │   (REST API)   │  Python/Flask│                │   (Docker)   │
│  nginx       │ ◄───────────── │  JWT + RBAC  │ ◄───────────── │              │
└──────────────┘                └──────────────┘                └──────────────┘
```

- **Frontend**: HTML + CSS + JavaScript *vanilla* (sem framework), servido por **nginx**.
  Consome a API via `fetch`. Tema "dark fantasy / pergaminho" estilo D&D Beyond.
- **Backend**: **Python** apenas. Flask (app factory) + Flask-SQLAlchemy + Flask-JWT-Extended +
  Flask-CORS. API REST versionada em `/api/v1`.
- **Banco**: **PostgreSQL** em produção/dev (Docker); **SQLite** em memória nos testes.
- **Infra**: `docker-compose.yml` orquestra `db` (postgres), `backend` (gunicorn), `frontend` (nginx).

### Portas (para não conflitar com outros projetos da máquina)
- Frontend: **8080** → http://localhost:8080
- Backend:  **5050** → http://localhost:5050/api/v1
- Postgres: **5433** (host) → 5432 (container)

## 3. Estrutura de pastas

```
ragnarok/
├── CLAUDE.md              # este arquivo
├── status.md             # TODAS as tasks e seu estado (fonte da verdade do progresso)
├── README.md
├── docker-compose.yml
├── .env.example
├── spec/                 # Spec-Driven Development (ver §4)
│   ├── backend/{planning,units,tests,decisions,changelog.md}
│   └── frontend/{planning,units,tests,changelog.md}
├── backend/
│   ├── app/              # código da aplicação (factory, models, api, rules, utils)
│   ├── data/             # seed JSON do SRD (raças, classes, magias, monstros)
│   ├── tests/            # pytest (TDD)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html, css/, js/, pages/
│   ├── Dockerfile
│   └── nginx.conf
└── legacy/               # protótipo Flask original (server-rendered) — arquivado
```

## 4. Como trabalhamos: SDD + TDD

Este projeto segue **Spec-Driven Development** com **Test-Driven Development**.
Para CADA funcionalidade, o ciclo é:

```
planning → spec da unit → escreve teste (RED) → escreve código (GREEN) →
refatora → atualiza changelog + status.md → volta para a lista de tasks
```

- **`spec/**/planning/`** — visão, arquitetura, contratos de API, fluxos de UX.
- **`spec/**/units/`** — especificação de cada unidade (entrada/saída, regras, critérios de aceite).
- **`spec/**/tests/`** — plano de testes e critérios de aceitação.
- **`spec/**/decisions/`** — ADRs (Architecture Decision Records).
- **`spec/**/changelog.md`** — registro cronológico do que mudou (semântico).

Regra de ouro: **não escreva código sem teste**. Se a task for grande, **fragmente** em
sub-tasks no `status.md` e resolva uma de cada vez.

## 5. Comandos

### Backend (local, sem Docker)
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
pytest -q                                          # roda os testes (TDD)
flask --app wsgi run --port 5050                   # sobe a API
python -m app.seed                                 # popula o banco com SRD + admin
```

### Stack completa (Docker) — IMPORTANTE
> Sempre **derrube** a stack antes de subir de novo (evita conflito de container/porta).
```bash
docker compose down                # mata os containers do Ragnarok
docker compose up --build -d       # sobe db + backend + frontend
docker compose logs -f backend     # acompanha logs
docker compose exec backend python -m app.seed   # popula o banco
```

## 6. Convenções

- **Commits semânticos**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `style:`.
  Um commit por incremento coeso. Mensagens em pt-BR são aceitas.
- **Idioma**: domínio e UI em **pt-BR**; código (nomes de variáveis/funções) em pt-BR/en misto,
  mas `slug`s de conteúdo SRD ficam em **inglês** (estáveis para integração).
- **Atributos D&D**: chaves `for, des, con, int, sab, car` (Força, Destreza, Constituição,
  Inteligência, Sabedoria, Carisma).
- **Camadas**: regras de jogo puras ficam em `app/rules/` (sem dependência de Flask/DB) para
  serem 100% testáveis. API só orquestra.

## 7. Estado atual
Veja **`status.md`** para a lista completa de tasks e o que está pronto/pendente.
