# 📊 STATUS — Ragnarok

> Fonte da verdade do progresso. Toda task passa pelo ciclo:
> **planning → spec → teste (RED) → código (GREEN) → refatora → atualiza status**.
> Legenda: ✅ feito · 🔄 em andamento · ⏳ pendente · ❌ bloqueado/falhando

Última atualização: 2026-06-05 (stack verificada E2E)

---

## 🧭 Épicos

| # | Épico | Estado |
|---|-------|--------|
| E1 | Fundação: specs, docs, estrutura | ✅ |
| E2 | Backend — fundação (app factory, config, DB) | ✅ |
| E3 | Backend — Auth & RBAC (ADMIN/MESTRE/JOGADOR) | ✅ |
| E4 | Backend — Motor de regras D&D 5E | ✅ |
| E5 | Backend — Personagens (ficha 5E) | ✅ |
| E6 | Backend — Mesas/Campanhas | ✅ |
| E7 | Backend — Bestiário (monstros/PDMs) | ✅ |
| E8 | Backend — Conteúdo de referência + seed SRD | ✅ |
| E9 | Backend — Admin (gestão da plataforma) | ✅ |
| E10 | Frontend — UI estilo D&D Beyond | ✅ |
| E11 | Infra — Docker (backend/frontend/postgres) | ✅ |
| E12 | Integração & verificação end-to-end | ✅ |

---

## ✅ Lista detalhada de tasks

### E1 — Fundação
- [x] T1.1 Estudar projeto legado e decidir arquitetura
- [x] T1.2 Criar branch `develop`
- [x] T1.3 Arquivar app legado em `legacy/`
- [x] T1.4 Criar `CLAUDE.md`
- [x] T1.5 Criar `status.md`
- [x] T1.6 Criar specs de planning (backend): arquitetura, domínio, API, RBAC
- [x] T1.7 Criar specs de planning (frontend): design system, fluxos UX, páginas
- [x] T1.8 Criar specs de units (backend e frontend)
- [x] T1.9 Criar plano de testes (backend e frontend)
- [x] T1.10 Criar ADR-0001 (stack) e changelogs iniciais

### E2 — Backend fundação
- [x] T2.1 `requirements.txt` + `pytest.ini` + estrutura `app/`
- [x] T2.2 App factory + config (Postgres/SQLite) + extensions
- [x] T2.3 Handler de erros JSON padronizado + healthcheck `/api/v1/health`
- [x] T2.4 `conftest.py` (app de teste, client, db em memória)

### E3 — Auth & RBAC
- [x] T3.1 Model `User` com papel (enum) + hash de senha
- [x] T3.2 (RED) testes de registro/login/JWT/me
- [x] T3.3 (GREEN) endpoints `/auth/register`, `/auth/login`, `/auth/me`
- [x] T3.4 Decorators `@jwt_required` + `@role_required(...)`
- [x] T3.5 (RED/GREEN) testes de autorização por papel

### E4 — Motor de regras D&D 5E
- [x] T4.1 (RED) testes: modificador de atributo, bônus de proficiência por nível
- [x] T4.2 (GREEN) `rules/dnd5e.py`: modificador, proficiência, CD, iniciativa
- [x] T4.3 (RED/GREEN) perícias e salvaguardas calculadas (proficiência + atributo)
- [x] T4.4 (RED/GREEN) PV por dado de vida + CON, percepção passiva, XP→nível

### E5 — Personagens
- [x] T5.1 Models `Personagem` (ficha 5E: atributos, perícias, combate, magias)
- [x] T5.2 (RED) testes CRUD + cálculo derivado servido na API
- [x] T5.3 (GREEN) endpoints CRUD `/characters` (somente dono/mestre acessam)
- [x] T5.4 Serialização com campos derivados (modificadores, CA, etc.)

### E6 — Mesas/Campanhas
- [x] T6.1 Models `Mesa`, `MembroMesa` (mestre + jogadores)
- [x] T6.2 (RED) testes: mestre cria mesa, convida por código, jogador entra
- [x] T6.3 (GREEN) endpoints `/campaigns` + membros + vincular personagem
- [x] T6.4 Regras de permissão (só mestre gerencia; jogador vê a sua)

### E7 — Bestiário
- [x] T7.1 Models `Monstro`/`PDM` (estatísticas 5E)
- [x] T7.2 (RED) testes CRUD bestiário (mestre/admin)
- [x] T7.3 (GREEN) endpoints `/bestiary` (global SRD + por mesa)

### E8 — Conteúdo de referência + seed
- [x] T8.1 Models de referência: `Raca`, `Classe`, `Antecedente`, `Magia`
- [x] T8.2 Seed JSON do SRD (raças, classes, antecedentes, magias, monstros)
- [x] T8.3 (GREEN) endpoints read-only `/reference/*`
- [x] T8.4 Script `python -m app.seed` (cria admin + popula SRD, idempotente)

### E9 — Admin
- [x] T9.1 (RED) testes: listar/promover/banir usuários (só ADMIN)
- [x] T9.2 (GREEN) endpoints `/admin/users`, `/admin/stats`
- [x] T9.3 CRUD de conteúdo de referência por ADMIN

### E10 — Frontend
- [x] T10.1 Design system (CSS): tema, componentes, layout
- [x] T10.2 `api.js` (cliente fetch + token) + `auth.js` (sessão)
- [x] T10.3 Páginas auth (login/registro)
- [x] T10.4 Dashboard (lista de personagens + mesas) por papel
- [x] T10.5 Ficha de personagem estilo D&D Beyond (visual + edição)
- [x] T10.6 Criação de personagem (wizard: raça→classe→atributos→perícias)
- [x] T10.7 Mesas (mestre gerencia; jogador entra por código)
- [x] T10.8 Bestiário (lista/detalhe/CRUD)
- [x] T10.9 Compêndio (magias/raças/classes — referência)
- [x] T10.10 Painel ADMIN (usuários/stats)

### E11 — Infra Docker
- [x] T11.1 `backend/Dockerfile` (gunicorn)
- [x] T11.2 `frontend/Dockerfile` + `nginx.conf` (proxy `/api`)
- [x] T11.3 `docker-compose.yml` (db/backend/frontend) + `.env.example`
- [x] T11.4 Entrypoint que espera o DB e roda seed

### E12 — Integração & verificação
- [x] T12.1 `pytest` verde (todos os testes)
- [x] T12.2 `docker compose up` sobe a stack
- [x] T12.3 Fluxo E2E: registrar → login → criar personagem → ver ficha
- [x] T12.4 Relatório final

---

## 📝 Notas / decisões rápidas
- Portas escolhidas: 8080 (front), 5050 (api), 5433 (postgres host) para evitar conflito.
- SQLite em memória nos testes para velocidade; Postgres em runtime.
- Conteúdo apenas SRD 5.1 (CC-BY/OGL).
