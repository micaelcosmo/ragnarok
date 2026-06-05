# Backend — Arquitetura

## Stack
- **Linguagem**: Python 3.11
- **Framework**: Flask (app factory pattern)
- **ORM**: Flask-SQLAlchemy (SQLAlchemy 2.x)
- **Auth**: Flask-JWT-Extended (access tokens JWT, Bearer)
- **CORS**: Flask-CORS (libera o frontend)
- **Servidor**: gunicorn (produção/Docker)
- **Testes**: pytest + SQLite em memória
- **DB runtime**: PostgreSQL

## Camadas
```
app/
├── __init__.py        # create_app(config) — app factory
├── config.py          # Config base / Dev / Test / Prod (via env)
├── extensions.py      # db, jwt, cors, migrate — instâncias únicas
├── models/            # entidades SQLAlchemy (sem lógica de regra de jogo)
├── rules/             # FUNÇÕES PURAS de regras D&D 5E (testáveis isoladas)
├── schemas/           # (de)serialização + validação de entrada
├── api/               # blueprints REST (orquestram models + rules)
│   └── v1/ ...
├── utils/             # decorators (role_required), erros, paginação
└── seed.py            # popula admin + conteúdo SRD (idempotente)
```

### Princípio chave
`app/rules/dnd5e.py` **não importa Flask nem o DB**. São funções puras
(`modificador(valor) -> int`, `bonus_proficiencia(nivel) -> int`, etc.).
Isso permite TDD rápido e mantém as regras de jogo desacopladas da infraestrutura.

## Padrão de resposta da API
```yaml
sucesso_objeto:
  data: { ... }
sucesso_lista:
  data: [ ... ]
  meta: { total: N }
erro:                       # sempre JSON, com status HTTP coerente
  error:
    code: VALIDATION
    message: "mensagem legível"
    details: { campo: "motivo" }
```

## Versionamento
Todos os endpoints sob `/api/v1`. Healthcheck em `/api/v1/health`.

## Segurança
- Senhas com `werkzeug.security` (pbkdf2/scrypt).
- JWT no header `Authorization: Bearer <token>`.
- RBAC via decorator `@role_required("ADMIN", ...)`.
- Ownership: jogador só acessa os próprios personagens; mestre só as próprias mesas.

## Configuração por ambiente (env vars)
| Var | Default (dev) | Descrição |
|-----|---------------|-----------|
| `FLASK_CONFIG` | `dev` | dev/test/prod |
| `DATABASE_URL` | sqlite/postgres | conexão SQLAlchemy |
| `JWT_SECRET_KEY` | dev key | assinatura dos tokens |
| `SEED_ADMIN_EMAIL` | admin@ragnarok.local | admin inicial |
| `SEED_ADMIN_PASSWORD` | admin123 | senha do admin inicial |
