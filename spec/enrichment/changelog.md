# Changelog — Enriquecimento

## [Não lançado]

### Fase 1 — Motor de efeitos (feat)
- `app/rules/efeitos.py` (puro): `combinar`/`aplicar` — soma efeitos das fontes sobre a base.
- `ConstrutorDeFicha` (service): resolve raça/classe/antecedente/talentos do catálogo e monta a
  ficha final (base + fontes), **reversível** (remover fonte remove o bônus).
- Campo `efeitos` em Raca/Classe/Antecedente/Talento; `talentos` e `ca_ajuste` no Personagem.
- Seed deriva `efeitos`: raça→atributos, classe→salvaguardas, antecedente→perícias; Grappler→recurso.
- API: POST/PUT de personagem aceitam `talentos` e `ca_ajuste`; `derivados` agora traz
  `atributos_final`, `concedido`, `recursos`, `sentidos`, CA com ajuste manual.
- Migração Alembic `14082adb24ce` (campos novos; `ca_ajuste` com server_default p/ dados existentes).
- Testes: motor puro (4) + integração add/remove talento reversível + raça/antecedente + CA (3).
- Validado em stack Docker **isolada** (`docker-compose.dev.yml`, projeto `ragnarok-dev`).

### Fase 2 — Conteúdo (feat)
- Modelos `Arma`, `Armadura`, `Item` (separados) com procedência (`fonte`/`homebrew`/`oficial`),
  ownership (`personagem_id`/`mesa_id`/global) e i18n (`idioma`). Migração `9c6b8cab1404`.
- Pipeline ganha tipos `weapons`/`armor`/`items` (open5e, OGL, homebrew=False).
- `Open5eSource` deriva `efeitos`: arma→ataque(dano/tipo/acuidade), armadura→ca_base/ca_soma_des,
  raça→atributos, classe→salvaguardas, antecedente→perícias.
- Endpoints `GET /reference/{weapons,armor,items}` (catálogo global, `?q=`/`?fonte=`/paginação).
- +4 testes (90 no total).

### docs (planejamento)
- Visão geral, motor de efeitos (`ConstrutorDeFicha`, base+fontes reversível), modelo de dados
  (Arma/Armadura/Item separados + fontes no Personagem + aceitação homebrew por mesa),
  compêndio editável (cards clicáveis, CRUD MESTRE/ADMIN, fonte obrigatória + homebrew),
  e i18n (toggle EN/PT com tradução offline grátis).
