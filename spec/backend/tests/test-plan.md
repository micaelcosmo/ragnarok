# Backend — Plano de Testes (pytest + TDD)

## Estratégia
- **TDD**: para cada unit, escreve o teste primeiro (RED), depois o código (GREEN), refatora.
- **Isolamento**: SQLite em memória, app de teste via `create_app("test")`, fixtures em `conftest.py`.
- **Pirâmide**:
  - *Unitários puros* — `test_rules.py` (motor de regras, sem DB).
  - *Integração de API* — auth, characters, campaigns, bestiary, admin (com client HTTP de teste).

## Fixtures (`conftest.py`)
- `app` — app de teste (config test, `db.create_all()`).
- `client` — `app.test_client()`.
- `db_session` — sessão limpa por teste.
- `make_user(role)` — cria usuário e retorna `(user, token)`.
- `auth(token)` — header `{"Authorization": f"Bearer {token}"}`.

## Cobertura alvo
| Arquivo | Foco | Casos mín. |
|---------|------|-----------|
| test_rules.py | regras puras | 12 |
| test_auth.py | registro/login/RBAC | 6 |
| test_characters.py | CRUD + derivados + ownership | 6 |
| test_campaigns.py | mesas/membros/permissão | 6 |
| test_bestiary.py | CRUD + escopo mesa/global | 4 |
| test_admin.py | gestão usuários/stats | 4 |

## Comando
```bash
cd backend && pytest -q
```
Critério de pronto: **todos verdes** antes de dockerizar (T12.1).
