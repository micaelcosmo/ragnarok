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
- `POST /auth/reset-password` *(público)* — `{token,nova_senha}` → redefine a senha via link
  (sem senha antiga) e devolve `{access_token,user}` (auto-login). Token de uso único (invalida
  ao trocar a senha) e com validade.
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

## Catálogo de itens (Armas/Armaduras/Itens) — `tipo ∈ {weapons, armor, items}`
- `GET /catalog/<tipo>?personagem_id=&q=` — catálogo global + itens próprios do personagem.
- `GET /catalog/<tipo>/<id>`.
- `POST /catalog/<tipo>` — cria. **JOGADOR** exige `personagem_id` (vincula ao seu personagem,
  só ele usa); **MESTRE/ADMIN** cria global (ou `mesa_id`). Sempre `homebrew=true`, `fonte` obrigatória.
- `PUT /catalog/<tipo>/<id>` · `DELETE /catalog/<tipo>/<id>` — criador/mestre da mesa/ADMIN.

## Equipar (personagem)
- `POST /characters/<id>/equipar` *(owner/A)* — `{tipo:"arma"|"armadura", item_id}`. Aplica CA
  (armadura) e ataques (armas) nos `derivados`.
- `POST /characters/<id>/desequipar` *(owner/A)* — `{tipo, item_id?}`.

Catálogo SRD/OGL global também via leitura em `GET /reference/{weapons,armor,items}`.

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
- `POST /admin/users/<id>/reset-link` *(A)* — gera um link de redefinição de senha para o usuário
  (devolve `{token, caminho:"/#/reset?token=...", expira_em_horas}`).
- `GET /admin/stats` *(A)* — contagens (usuários por papel, personagens, mesas, monstros).
- `GET /admin/campaigns?q=` *(A)* — lista **todas** as mesas (moderação).
- `DELETE /admin/campaigns/<id>` *(A)* — remove qualquer mesa ("desbugar").
- `POST /admin/campaigns/<id>/kick` *(A)* — `{user_id}` — tira um membro preso de qualquer mesa.

## Códigos de erro
`VALIDATION` (400), `UNAUTHORIZED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404),
`CONFLICT` (409), `INTERNAL` (500).
