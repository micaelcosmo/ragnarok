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

### Fase 6 — Traços não-numéricos + idioma EN/PT (feat)
- Ficha exibe **traços concedidos** (recursos/sentidos/proficiências) das fontes, sem afetar números.
- `Traducao` (cache) + serviço `Tradutor` (Argos offline opcional, fallback gracioso);
  migração `f3fb253e632d`.
- `?idioma=pt` em `/catalog/<tipo>` e `/reference/{weapons,armor,items}` traduz conteúdo importado.
- Frontend: **toggle 🌐 PT/EN** na topbar (persistente); cliente injeta o idioma.
- +4 testes (103 no total).

### Fase 5 — Compêndio editável (feat)
- Campos `homebrew`/`criado_por` em Raca/Classe/Antecedente/Magia/Talento (+ `oficial` no to_dict).
  Modelo `MesaFonteAceita`. Migração `0ba57e6c8e18`.
- CRUD genérico `POST/PUT/DELETE /reference/<tipo>` (MESTRE/ADMIN): **fonte obrigatória**,
  conteúdo criado é **homebrew**; editar **oficial** cria **variante homebrew** (preserva o oficial);
  só ADMIN exclui oficial.
- Aceitação por mesa: `POST/DELETE /campaigns/<id>/fontes` (mestre/admin).
- RBAC atualizado (compêndio passa de só-ADMIN para MESTRE+ADMIN).
- Frontend: compêndio com **cards clicáveis** (todos os tipos), **selo de fonte 🛡️ Oficial / 🧪
  Homebrew**, busca e **Criar/Editar/Excluir** para MESTRE/ADMIN.
- Naming convention nas constraints (corrige batch-mode do Alembic em SQLite).
- +4 testes (99 no total).

### Fase 4 — Wizard enriquecido (feat)
- Novo passo **Talentos** (multi-seleção do catálogo `/reference/feats`).
- **Preview ao vivo dos bônus**: mostra o que raça (atributos), antecedente (perícias),
  classe (salvaguardas) e talentos concedem — lido dos `efeitos` do catálogo.
- Atributos passam a ser **base** (bônus racial/talento somados pelo motor, não mais "manual").
- Criação envia `talentos` (e deixa salvaguardas/atributos para o motor aplicar).

### Fase 3 — Editor de itens + equipar (feat)
- CRUD `/catalog/{weapons,armor,items}` com ownership: JOGADOR vincula ao seu personagem;
  MESTRE/ADMIN ao acervo geral; tudo homebrew + fonte obrigatória.
- Personagem: `armadura_equipada_id` + `armas_equipadas`; endpoints `/characters/<id>/equipar`
  e `/desequipar`. Migração `e8c592ad9299`.
- `ConstrutorDeFicha` calcula **CA** da armadura equipada (base+DES limitado+bônus) e os
  **ataques** das armas (acerto = mod+proficiência+mágico; DES se acuidade/à distância).
- Frontend: aba Equipamento na ficha (equipar/desequipar + criar item homebrew vinculado),
  tabela de ataques equipados.
- +5 testes (95 no total).

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
