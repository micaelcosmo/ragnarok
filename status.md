# 📊 STATUS — Ragnarok

> Fonte da verdade do progresso. Toda task passa pelo ciclo:
> **planning → spec → teste (RED) → código (GREEN) → refatora → atualiza status**.
> Legenda: ✅ feito · 🔄 em andamento · ⏳ pendente · ❌ bloqueado/falhando

Última atualização: 2026-06-06 (ciclo ao vivo → #6 → #3 → #2 concluído; E21–E24 em produção)

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
| E13 | ADMIN como gerente da plataforma (não super-mestre) | ✅ |
| E14 | Pipeline de Conteúdo Base (talentos, fontes, ingestão OGL) | ✅ |
| E15 | Exposição online (hardening + túnel Cloudflare) | ✅ |
| E16 | Ficha 100% editável + tooltips no hover | ✅ |
| E17 | Auth: auto-login no registro + reset de senha por link (admin) | ✅ |
| E18 | Banco: Alembic/Flask-Migrate (sem perder dados) + backup | ✅ |
| E19 | Enriquecimento da ficha (efeitos, itens, wizard, compêndio, i18n) | ✅ (em prod) |
| E20 | Identidade & Imagens do Personagem (retrato, símbolo, página de identidade) | ✅ (em prod) |
| E21 | Atualização ao vivo (sem F5): reativo + polling | ✅ (em prod) |
| E22 | Traços/recursos como cards incrementais (descritivo × numérico, reversível) + Aumentos de Habilidade | ✅ (em prod) |
| E23 | Equipamento mundano no catálogo (gear + pacotes SRD) | ✅ (em prod) |
| E24 | Tradução PT de armas/armaduras (de-para curado offline + cache) | ✅ (em prod) |
| E25 | Exportar ficha em PDF (estilo oficial 5E, WeasyPrint) | ✅ (em prod) |
| E26 | Aumentos de Habilidade (ASI) por nível — pool reversível | ✅ (em prod) |
| E27 | Recursos de classe com usos (Fúria/Dados de Vida) + descanso | ✅ (em prod) |
| E28 | Toggle EN/PT na UI (i18n visual do compêndio) | 🔄 em andamento |

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

### E13 — ADMIN = gerente da plataforma
- [x] T13.1 Reescrever specs RBAC/API/CLAUDE.md (governança ≠ jogo)
- [x] T13.2 Renomear admin do seed (Administrador)
- [x] T13.3 Endpoints de moderação: GET/DELETE /admin/campaigns, kick (desbugar)
- [x] T13.4 Aba de moderação de mesas no painel admin (front) + teste

### E14 — Pipeline de Conteúdo Base
- [x] T14.1 Spec dedicada spec/content/ (overview, pipeline, importers)
- [x] T14.2 Modelo Talento + campo `fonte` em todas as referências
- [x] T14.3 Pipeline POO: ContentSource, LocalSource, Open5eSource, ContentPipeline, CLI
- [x] T14.4 Endpoints /reference/feats, /reference/sources, filtro ?fonte=
- [x] T14.5 Testes offline (FakeSource, idempotência, fonte, truncamento) — +9
- [x] T14.6 Ingestão real open5e: +73 talentos, +1389 magias, +3181 monstros, +11 raças
- [x] T14.7 Limite/paginação nas listas grandes (bestiário/magias)

### E15 — Exposição online
- [x] T15.1 Hardening: segredos fortes (.env) + senha admin
- [x] T15.2 cloudflared (binário) + túnel para :8080
- [x] T15.3 URL pública validada (frontend + API)
- [ ] T15.4 (futuro/opcional) DNS estável via named tunnel — requer login Cloudflare do dono

### E16 — Ficha editável + tooltips
- [x] T16.1 Edição COMPLETA do personagem (todos os campos, proficiências como toggles)
- [x] T16.2 Monstro/PDM editável (PUT) pelo dono/mestre/admin
- [x] T16.3 Tooltips no hover (atributos/perícias/salvaguardas/combate) sem afetar inputs
- [x] T16.4 Compêndio: aba de Talentos + filtro por fonte

---

### E17 — Auth (auto-login + reset por link)
- [x] T17.1 Registro devolve {access_token, user} (auto-login) — corrige "credenciais inválidas"
- [x] T17.2 Frontend: entra direto no registro + mostrar senha + feedback
- [x] T17.3 ADMIN gera link de reset; usuário define só a senha nova (token uso único/validade)
- [x] T17.4 Página pública #/reset + botão no painel admin + 7 testes (auth+reset)

### E18 — Banco (Alembic)
- [x] T18.1 Flask-Migrate nas extensions/app factory
- [x] T18.2 Baseline (autogenerate) + stamp head no banco vivo (dados preservados)
- [x] T18.3 entrypoint roda flask db upgrade no boot; ADR-0002
- [x] T18.4 scripts/backup.ps1 e restore.ps1 + docs

### E19 — Enriquecimento (✅ em produção; spec em `spec/enrichment/`)
- [x] F1 Motor de efeitos (`efeitos` em raça/classe/antec./talento + `ConstrutorDeFicha` base+fontes reversível) + testes
- [x] F2 Conteúdo: ingestão weapons/armor/(magic)items + derivar efeitos + curar talentos
- [x] F3 Modelos Arma/Armadura/Item + editor + ownership + equipar (CA/ataque; CA com ajuste manual)
- [x] F4 Wizard enriquecido (seletores reais + preview ao vivo dos bônus)
- [x] F5 Compêndio editável: cards clicáveis + CRUD MESTRE/ADMIN + fonte obrigatória + homebrew + aceitação por mesa
- [x] F6 Traços não-numéricos exibidos + toggle de idioma EN/PT (tradução offline grátis + cache)

### E20 — Identidade & Imagens (✅ em produção)
- [x] T20.1 Campos de identidade no `Personagem` (idade/altura/peso/olhos/pele/cabelo/facção/aparência/aliados/tesouro) + `simbolo_faccao_url`; migração `18f5cd8545e6`
- [x] T20.2 Upload seguro `POST /uploads` (allowlist + magic-bytes + uuid + limite 2MB + servir sem execução) + 5 testes
- [x] T20.3 Fix #1: stat block mostra o valor FINAL do atributo (bate com o modificador)
- [x] T20.4 Frontend: retrato no cabeçalho + aba Identidade editável + upload (retrato/símbolo)
- [x] T20.5 Infra: volume `ragnarok_uploads` + nginx `client_max_body_size 4m` + `^~ /api/` (fix 404 de imagem)
- [x] T20.6 Backup + deploy (sem -v) + smoke público; `progresso.html` no Dockerfile (não some em rebuild)

> Backlog de ideias/pendências fica em `spec/enrichment/planning/ajustes-pendentes.md`
> (correções pedidas) e `spec/enrichment/planning/roadmap-gaps.md` (gaps de mecânica/conteúdo).

---

## 📝 Notas / decisões rápidas
- Portas escolhidas: 8080 (front), 5050 (api), 5433 (postgres host) para evitar conflito.
- SQLite em memória nos testes para velocidade; Postgres em runtime.
- Conteúdo SRD 5.1 + ingestões OGL (open5e: Kobold Press, Level Up A5e, etc.) com `fonte` rastreável.
- ADMIN é governança (contas/moderação/conteúdo), NÃO um super-mestre de jogo.
- Online via túnel Cloudflare (URL trycloudflare). DNS estável fica para quando o dono logar.
- Testes: **108 pytest verdes**. Conteúdo: ~20 raças, 12 classes, 74 talentos, ~1436 magias,
  3208 monstros, 68 armas, 23 armaduras, 1618 itens. 12 migrações Alembic.
- Personagem-exemplo **Kzen** (Bárbaro 9 Halfling) importado na conta admin com retrato + símbolo.
