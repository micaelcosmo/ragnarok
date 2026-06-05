# Unit Spec — Bestiário & Admin

## Bestiário
- `GET /bestiary` lista monstros SRD globais (`mesa_id NULL`); com `?mesa_id=` soma os da mesa.
- `POST /bestiary` (MESTRE/ADMIN): com `mesa_id` cria no bestiário da mesa (só mestre da mesa);
  sem `mesa_id` + ADMIN cria SRD global.
- PUT/DELETE: criador, mestre da mesa, ou ADMIN.
- `is_pdm=true` marca PDM (NPC) vs monstro.

### Aceite (tests/test_bestiary.py)
1. JOGADOR → 403 ao criar monstro.
2. MESTRE cria monstro na sua mesa → 201.
3. listagem da mesa inclui SRD global + o criado.
4. MESTRE não edita monstro de outra mesa → 403.

## Admin
- `GET /admin/users` (ADMIN) com filtros `q`, `role`.
- `PUT /admin/users/<id>/role {role}` (ADMIN) — valida enum.
- `DELETE /admin/users/<id>` (ADMIN) — não pode deletar a si mesmo.
- `GET /admin/stats` (ADMIN) — `{usuarios:{ADMIN,MESTRE,JOGADOR}, personagens, mesas, monstros}`.

### Aceite (tests/test_admin.py)
1. JOGADOR/MESTRE → 403 em `/admin/*`.
2. ADMIN promove jogador → MESTRE (200) e papel persiste.
3. `/admin/stats` retorna contagens corretas.
4. ADMIN não deleta a própria conta → 400.
