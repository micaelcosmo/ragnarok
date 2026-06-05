# Changelog — Backend

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/) + commits semânticos.

## [Não lançado]
### docs
- Specs de planning (arquitetura, domínio, contrato de API, RBAC).
- Specs de units (rules-engine, auth, characters, campaigns, bestiary-admin, coding-conventions).
- Plano de testes e ADR-0001 (stack).

### feat
- App factory Flask + config por ambiente (dev/test/prod) + extensions (db/jwt/cors).
- Handler de erros JSON padronizado + healthcheck `/api/v1/health`.
- Motor de regras D&D 5E puro (`app/rules/dnd5e.py`): modificadores, proficiência,
  XP→nível, perícias, salvaguardas, percepção passiva, CD/ataque de magia, PV sugerido.
- Auth JWT (registro/login/me) + RBAC (`@role_required`, `@auth_required`).
- Models: User, Personagem (ficha 5E + derivados), Mesa, MembroMesa, Monstro, e
  referência (Raca, Classe, Antecedente, Magia) — todos com `to_dict` (POO).
- API CRUD: characters (ownership), campaigns (mesas/convite/kick/vínculo),
  bestiary (escopo global/mesa), reference (catálogo + escrita ADMIN), admin (users/stats).
- Seed idempotente (`SeedRunner`) cria ADMIN + popula SRD (9 raças, 12 classes,
  8 antecedentes, 47 magias, 27 monstros).

### test
- 63 testes pytest verdes (37 unitários de regras + 26 de integração da API).

### style
- PEP8, nomes de laço descritivos, exemplos em ```yaml nas specs (convenção do projeto).
