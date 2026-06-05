# Unit Spec — Auth & RBAC

## Endpoints
- `POST /auth/register` — valida email único + senha mín. 6 chars. `role` recebido é **ignorado**
  se for ADMIN (segurança). Default `JOGADOR`. Mestre pode ser escolhido no registro (estudo).
- `POST /auth/login` — retorna `access_token` (JWT, identity=user.id) + objeto user.
- `GET /auth/me` — retorna user atual a partir do token.

## Decorators (`app/utils/auth.py`)
- `current_user()` — resolve User a partir do `get_jwt_identity()`.
- `@role_required(*roles)` — 401 sem token, 403 se papel não permitido (ADMIN sempre passa).

## Critérios de aceite (tests/test_auth.py)
1. registro válido → 201 + user sem `password_hash` no payload.
2. registro com email duplicado → 409 CONFLICT.
3. registro com senha curta → 400 VALIDATION.
4. registro tentando `role:"ADMIN"` → cria como JOGADOR.
5. login correto → 200 + token; login errado → 401.
6. `/auth/me` sem token → 401; com token → 200 user.
