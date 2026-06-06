# Unit Spec — Mesas / Campanhas

## Regras
- `POST /campaigns` gera `codigo_convite` (6 chars alfanum. único). Mestre = criador.
- `POST /campaigns/join {codigo}` adiciona o usuário como MembroMesa (idempotente).
- `POST /campaigns/<id>/kick {user_id}` só pelo mestre/ADMIN.
- `POST /campaigns/<id>/personagens {personagem_id}` vincula personagem (do membro) à mesa.
- Detalhe inclui `membros[]` e `personagens[]`.

## Critérios de aceite (tests/test_campaigns.py)
1. JOGADOR → 403 ao criar mesa.
2. MESTRE cria mesa → 201 com `codigo_convite`.
3. JOGADOR entra por código → aparece em `membros`.
4. join com código inválido → 404.
5. mestre vê personagem vinculado de um jogador da mesa (200).
6. não-membro não vê a mesa (403/404).
