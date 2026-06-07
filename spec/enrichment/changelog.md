# Changelog — Enriquecimento

## [E28 — Toggle EN/PT na UI]
### feat
- Compêndio: botão **🌐 PT | EN** que alterna o idioma (localStorage) e re-renderiza as listas —
  fecha o i18n visual em cima do `?idioma=pt` já existente (E24). Afeta armas/armaduras/itens
  (conteúdo open5e em inglês): EN mostra "Greataxe", PT mostra "Machado Grande".
- `api.reference` (spells/feats/races/classes/backgrounds) passa a anexar `?idioma` também, para
  traduzir esses tipos quando houver conteúdo importado em inglês.
- +teste cobrindo `/reference/armor?idioma=pt`. Unit: `planning/toggle-idioma.md`. Sem migração.

## [E27 — Recursos de classe com usos]
### feat
- Personagem: campo `recursos` (JSON lista: {nome, max, atual, recarga, descricao}). Migração Alembic.
- `app/rules/dnd5e`: `sanear_recursos()` (valida/clampa) e `aplicar_descanso(recursos, tipo)`
  (curto recarrega "curto"; longo recarrega curto+longo; "nenhum" nunca).
- API: PUT aceita `recursos`; `POST /characters/<id>/recursos/ajustar` ({indice, delta}, clamp [0,max])
  e `POST /characters/<id>/descanso` ({tipo}; longo também restaura PV).
- Frontend: painel **Recursos** na ficha (atual/max, − / +, criar/editar/remover) + botões de
  **Descanso curto/longo**; reflete ao vivo. Unit: `planning/recursos-classe.md`.
- +N testes (sanear/descanso + endpoints).

## [E26 — Aumentos de Habilidade (ASI) por nível]
### feat
- Personagem: campo `bonus_atributos_manuais` (JSON {for..car}). Migração Alembic.
- `app/rules/dnd5e.asi_pontos_por_nivel(nivel)` — orçamento 5E (níveis 4/8/12/16/19 → +2 cada).
- `ConstrutorDeFicha` dobra a pool como **fonte** (final = base + fontes + ASI manual, reversível) e
  expõe `derivados.asi` = {pontos_total, pontos_usados, pontos_restantes}.
- API valida/clampa a pool (só chaves for..car, inteiros ≥ 0, não excede o orçamento, teto final 20).
- Frontend: seção **Aumentos de Habilidade** no editor (+/- por atributo, mostra pontos restantes); o
  stat block já mostra o ▲ (final > base). Unit: `planning/asi-por-nivel.md`.
- +N testes (regras + construtor reversível + clamp da API).

## [E25 — Exportar ficha em PDF (estilo oficial 5E)]
### feat
- Serviço `FichaPDF` (POO): monta o contexto a partir do `ConstrutorDeFicha` (mesmos derivados
  da ficha web) e renderiza um template Jinja (HTML + print-CSS) convertido por **WeasyPrint**.
- Template `app/templates/pdf/ficha.{html,css}` — **2 páginas**: pág.1 atributos/salvaguardas/
  perícias + combate/ataques + traços & recursos (selo números/descritivo) + personalidade;
  pág.2 identidade (características/aparência/aliados/tesouro/equipamento/história) + retrato e símbolo.
- Endpoint `GET /api/v1/characters/<id>/pdf` (auth; dono/ADMIN/mestre) → `application/pdf` (attachment).
- Imagens só de uploads locais (basename → `file://` em `UPLOAD_DIR`); URLs externas ignoradas (anti-SSRF).
- Frontend: botão **🖨️ Exportar PDF** + `baixarArquivo()` (fetch blob autenticado → download).
- Infra: `weasyprint` no requirements; libs nativas (pango/cairo/gdk-pixbuf/dejavu) no Dockerfile.
  Sem migração (feature só-leitura). ADR-0003 + unit `planning/export-pdf.md`.
- +4 testes (**115 no total**). Verificado em prod (Kzen 74 KB, retrato+símbolo embutidos).

## [E24 — Tradução PT de armas/armaduras (de-para curado)]
### feat
- `backend/data/traducoes_pt.json` (47 nomes PT de weapons/armor do SRD) semeado de forma
  idempotente por `SeedRunner.semear_traducoes()` no cache `Traducao`.
- `/reference|catalog/weapons?idioma=pt` aplica via `Tradutor` (ex.: greataxe → "Machado Grande");
  **fallback gracioso** mantém o original quando não há tradução. Argos segue opcional.
- +1 teste (seed idempotente). Opção (c) do roadmap (offline, sem instalar o Argos).

## [E23 — Equipamento mundano no catálogo]
### feat
- `backend/data/gear.json` (30 itens SRD: mochila, corda, tochas, rações, kits, pacotes)
  semeado como `Item` global oficial via `SeedRunner.semear_equipamento` (homebrew=False, idioma=pt).
- Fecha o gap de "adventuring gear" que só existia no campo de texto `equipamento` da ficha.

## [E22 — Traços/Recursos como cards incrementais + Aumentos de Habilidade]
### feat
- Personagem: campo `tracos_extras` (JSON). Migração `7ed254ff640a`.
- `ConstrutorDeFicha`: `_tracos_ativos()` lista talentos + traços extras como **cards**, marcando
  `tipo` **numérico** (altera atributos/iniciativa/CA/etc., reversível) × **descritivo**; os efeitos
  numéricos entram como fonte (base + fontes), somando e revertendo.
- Frontend: painel **Traços & Recursos** na ficha (criar/editar/remover traço, alocar +atributo
  "tipo joguinho"). Bênção do Kzen (+2 CON, "StormKing - Mestre Atila") migrada de talento → card.
- +2 testes (numérico soma/reverte; descritivo não muda número). Hardening de validação no roadmap.

## [E21 — Atualização ao vivo (sem F5)]
### feat
- `frontend/js/live.js`: `iniciarPolling`/`pararPolling` — um poller por view, re-render só quando a
  assinatura JSON muda; pula se há modal aberto ou input/textarea/select focado; router para o poller
  ao navegar. Aplicado na ficha (7s) e na mesa (8s) → reflete mudanças entre usuários sem refresh.

## [E20 — Identidade & Imagens]
### feat
- Personagem: campos de identidade (idade/altura/peso/olhos/pele/cabelo/facção/aparência/
  aliados/tesouro) + `simbolo_faccao_url`; `avatar_url` vira o retrato. Migração `18f5cd8545e6`.
- **Upload seguro** `POST /api/v1/uploads` (allowlist + magic-bytes + uuid + limite 2 MB +
  servir sem execução); volume `ragnarok_uploads`; nginx `client_max_body_size 4m`.
- Frontend: retrato no cabeçalho da ficha + **aba Identidade** (editável, com símbolo da facção)
  + botões de **upload** (retrato/símbolo) no formulário.
- **Fix #1**: stat block passa a exibir o **valor final** do atributo (DES 18/+4), batendo com o mod.
- +5 testes de upload (108 no total). Planning: `planning/identidade-imagens.md`.

## [Pós-lançamento]
### content/docs
- **Roadmap de gaps** (`planning/roadmap-gaps.md`) gerado a partir da importação da ficha do
  Kzen (Bárbaro 9 Halfling): ASI, sub-raça automática, recursos de classe, moedas, testes de
  morte, oficial-vs-homebrew para admin, etc.
- Antecedente **Forasteiro (Outlander)** adicionado ao seed (`backgrounds.json`) + efeitos
  (perícias Atletismo/Sobrevivência) — gap que a ficha revelou.
- Personagem de exemplo **Kzen** importado (corrigido) e **Bênção da Grande Serpente [+2 CON]**
  modelada como talento homebrew de campanha (in-game → out-game).

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
