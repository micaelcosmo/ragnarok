# Backend — Contrato da API (`/api/v1`)

Autenticação: `Authorization: Bearer <access_token>` (exceto onde marcado público).
Papéis: `A`=ADMIN, `M`=MESTRE, `J`=JOGADOR. "owner" = dono do recurso.

## Health
```yaml
GET /health:           # público
  resposta:
    data: { status: ok }
```

## Auth
- `POST /auth/register` *(público)* — `{email,name,password,role?}` → cria usuário (role default JOGADOR; ADMIN não é auto-atribuível). 201.
- `POST /auth/login` *(público)* — `{email,password}` → `{data:{access_token,user}}`.
- `GET /auth/me` — usuário atual.

## Reference (catálogo SRD) — leitura: qualquer autenticado
- `GET /reference/races` · `GET /reference/races/<slug>`
- `GET /reference/classes` · `GET /reference/classes/<slug>`
- `GET /reference/backgrounds`
- `GET /reference/spells?nivel=&classe=&q=` · `GET /reference/spells/<slug>`
- CRUD (POST/PUT/DELETE) dessas rotas: **somente A**.

## Characters
- `GET /characters` — lista do usuário atual (M/J: os seus; um mestre vê os da sua mesa via `?mesa_id=`).
- `POST /characters` *(J/M/A)* — cria ficha. Body = identidade + atributos.
- `GET /characters/<id>` *(owner ou mestre da mesa ou A)* — ficha **com campos derivados**.
- `PUT /characters/<id>` *(owner ou A)* — atualiza.
- `DELETE /characters/<id>` *(owner ou A)*.

## Campaigns (mesas)
- `GET /campaigns` — mesas onde sou mestre OU membro.
- `POST /campaigns` *(M/A)* — cria mesa (gera `codigo_convite`).
- `GET /campaigns/<id>` *(mestre/membro/A)* — detalhe + membros + personagens.
- `PUT /campaigns/<id>` *(mestre/A)*.
- `DELETE /campaigns/<id>` *(mestre/A)*.
- `POST /campaigns/join` *(J/M/A)* — `{codigo}` → entra na mesa.
- `POST /campaigns/<id>/kick` *(mestre/A)* — `{user_id}`.
- `POST /campaigns/<id>/personagens` *(membro)* — vincula um personagem meu à mesa.

## Bestiary
- `GET /bestiary?mesa_id=&q=&nd=` — SRD global + (se mesa_id) bestiário da mesa.
- `GET /bestiary/<id>`.
- `POST /bestiary` *(M/A)* — cria monstro/PDM (`mesa_id` opcional; sem ela e A = SRD global).
- `PUT /bestiary/<id>` *(criador/mestre da mesa/A)*.
- `DELETE /bestiary/<id>` *(criador/mestre da mesa/A)*.

## Admin (governança da plataforma)
- `GET /admin/users?q=&role=` *(A)*.
- `PUT /admin/users/<id>/role` *(A)* — `{role}`.
- `DELETE /admin/users/<id>` *(A)*.
- `GET /admin/stats` *(A)* — contagens (usuários por papel, personagens, mesas, monstros).
- `GET /admin/campaigns?q=` *(A)* — lista **todas** as mesas (moderação).
- `DELETE /admin/campaigns/<id>` *(A)* — remove qualquer mesa ("desbugar").
- `POST /admin/campaigns/<id>/kick` *(A)* — `{user_id}` — tira um membro preso de qualquer mesa.

## Códigos de erro
`VALIDATION` (400), `UNAUTHORIZED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404),
`CONFLICT` (409), `INTERNAL` (500).
