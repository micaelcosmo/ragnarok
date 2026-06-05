# ⚔️ Ragnarok — Grimório Digital

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API_REST-black?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=for-the-badge&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/pytest-63_passing-4c9a5e?style=for-the-badge)

> *"Toda lenda começa com uma escolha..."*

**Ragnarok** é uma plataforma web para criação e gerenciamento de fichas de RPG **D&D 5E**,
inspirada no [D&D Beyond](https://www.dndbeyond.com). Projeto **acadêmico**, usando apenas
conteúdo do **SRD 5.1** (CC-BY/OGL).

> 🌱 Este é o estado da branch **`develop`** — reescrita com separação front/back,
> API REST, PostgreSQL e tudo dockerizado, desenvolvida com **Spec-Driven Development + TDD**.
> O protótipo Flask original foi arquivado em [`legacy/`](legacy/).

---

## ✨ Funcionalidades

### 👥 Três perfis de usuário (RBAC)
- **ADMIN** — gerencia a plataforma: usuários, papéis, catálogo SRD e métricas.
- **MESTRE** — monta mesas (campanhas), gerencia jogadores, cria/edita monstros e PDMs.
- **JOGADOR** — cria e edita personagens com ficha 5E completa e automatizada.

### 🗺️ Fichas estilo D&D Beyond
- Atributos com **modificadores calculados** automaticamente (stat-blocks).
- **Perícias e salvaguardas** derivadas (proficiência + atributo) pelo motor de regras.
- CA, iniciativa, percepção passiva, CD/ataque de magia — tudo computado no backend.
- PV com barra visual e botões de **dano/cura**; abas de ataques, equipamento, traços e história.
- **Wizard de criação** em 5 passos (raça → classe → antecedente → atributos → perícias).

### 🛡️ Mesas, Bestiário e Compêndio
- Mestre cria mesa com **código de convite**; jogadores entram e vinculam personagens.
- **Bestiário** SRD global + criaturas próprias por mesa (monstros e PDMs).
- **Compêndio** navegável: 47 magias (com filtros), 9 raças, 12 classes.

---

## 🏗️ Arquitetura

```
┌──────────────┐   HTTP/JSON    ┌──────────────┐   SQLAlchemy   ┌──────────────┐
│  Frontend    │ ─────────────► │   Backend    │ ─────────────► │  PostgreSQL  │
│ HTML/CSS/JS  │   REST /api/v1 │  Python/Flask│                │   (Docker)   │
│  (nginx)     │ ◄───────────── │  JWT + RBAC  │ ◄───────────── │              │
└──────────────┘                └──────────────┘                └──────────────┘
```

- **Frontend**: HTML + CSS + JavaScript *vanilla* (SPA com hash router), servido por **nginx**.
- **Backend**: **Python**/Flask (app factory) + SQLAlchemy + JWT + CORS. Regras de jogo puras
  em `backend/app/rules/dnd5e.py` (100% testadas).
- **Banco**: **PostgreSQL** em runtime; **SQLite em memória** nos testes.
- **Infra**: `docker-compose` orquestra `db`, `backend` (gunicorn) e `frontend` (nginx).

Documentação de design em [`spec/`](spec/) (Spec-Driven Development) e o guia do agente em
[`CLAUDE.md`](CLAUDE.md). Progresso das tasks em [`status.md`](status.md).

---

## 🚀 Como rodar

### Opção A — Docker (recomendado)
> Sempre derrube a stack antes de subir de novo.
```bash
docker compose down
docker compose up --build -d
```
Acesse:
- **Frontend**: http://localhost:8080
- **API**: http://localhost:5050/api/v1/health
- **Postgres**: localhost:5433

Login admin inicial (criado pelo seed): `admin@ragnarok.local` / `admin123`.

### Opção B — Backend local (testes/dev)
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
pytest -q                                            # 63 testes
python -m app.seed                                   # popula SRD (SQLite dev)
python wsgi.py                                        # API em :5050
```

---

## 🧪 Qualidade
- **63 testes pytest** (37 unitários do motor de regras + 26 de integração da API).
- TDD: cada funcionalidade tem teste antes do código.
- Conteúdo apenas SRD 5.1 (CC-BY/OGL).

## 📁 Estrutura
```
ragnarok/
├── backend/   # API Flask + regras + testes + seed SRD
├── frontend/  # SPA vanilla + nginx
├── spec/      # Spec-Driven Development (planning/units/tests/decisions/changelogs)
├── legacy/    # protótipo Flask original (arquivado)
├── docker-compose.yml · CLAUDE.md · status.md
```

Desenvolvido por **Micael Cosmo** · Reformulação SDD/TDD na branch `develop`.
