# Unit Spec — Cliente de API & Sessão (frontend)

## `api.js`
- `API_BASE` = `/api/v1` (nginx faz proxy para o backend).
- `apiFetch(path, {method='GET', body, auth=true})`:
  - injeta `Authorization: Bearer <token>` quando `auth` e há token.
  - serializa `body` como JSON; header `Content-Type: application/json`.
  - em `!res.ok`, lança `ApiError(status, payload.error)`.
  - em 401, dispara logout + redireciona p/ `#/login`.
  - retorna `payload.data`.

## `auth.js`
- `setSession({access_token, user})` → salva em `localStorage`.
- `getToken()`, `getUser()`, `isLogged()`, `logout()`.
- `requireRole(...roles)` → boolean p/ guarda de rota (ADMIN sempre true).

## Critérios de aceite (smoke manual + futuros testes)
1. Chamada autenticada inclui o header Bearer.
2. 401 limpa sessão e volta ao login.
3. `getUser().role` controla itens de menu exibidos.
