# Frontend — Plano de Testes

O frontend é vanilla JS sem build. Estratégia pragmática:

## Níveis
1. **Smoke manual** (checklist) — fluxo principal num navegador via a stack Docker.
2. **Verificação visual** — comparar com referências do design system.
3. **Contrato com a API** — páginas consomem `data`/`error` conforme o contrato do backend.

## Checklist de smoke (E2E manual)
- [ ] Registrar usuário JOGADOR e logar.
- [ ] Criar personagem pelo wizard; ficha abre com modificadores corretos.
- [ ] Editar PV atual e salvar; persiste após reload.
- [ ] Registrar MESTRE; criar mesa; copiar código.
- [ ] JOGADOR entra na mesa pelo código; vincula personagem.
- [ ] MESTRE vê o personagem do jogador na mesa.
- [ ] MESTRE cria monstro no bestiário da mesa.
- [ ] ADMIN (seed) loga; vê stats; promove um jogador a mestre.
- [ ] Rota protegida sem token redireciona para login.

## Critério de pronto
Checklist de smoke passa na stack `docker compose up`.
