# Roadmap de Gaps — revelados ao importar a ficha do Kzen (Bárbaro 9 Halfling)

> Importar uma ficha oficial de nível alto expôs o que a plataforma ainda **não modela**.
> Cada item vira candidato a feature futura. Prioridade: 🔴 alta · 🟡 média · ⚪ baixa.

## Mecânicas de personagem
- ✅ **Aumentos de Habilidade (ASI)** — FEITO (E26): pool reversível `bonus_atributos_manuais`
  (níveis 4/8/12/16/19 → +2), clampada no servidor (teto 20), seção +/- no editor.
- 🟡 **Validação de `tracos_extras`**: o campo aceita JSON livre do usuário (nome/descrição/efeitos)
  sem validar forma nem clampar a magnitude dos números (ex.: `efeitos.atributos.con: 9999`).
  (O ASI do E26 já usa esse padrão de clamp no servidor — falta aplicar o mesmo aos traços e,
  idealmente, traços incrementais sujeitos à aprovação do Mestre da mesa.)
- ✅ **Sub-raças aplicando efeitos** — FEITO (E29): `subraca_slug`; o construtor aplica
  bonus/efeitos da sub-raça como fonte reversível + traços (origem "subraca").
- 🟡 **Talentos vs ASI**: feats reais (Sortudo, Bravura) existem como conteúdo, mas a escolha
  "ASI ou talento" por nível não é guiada. (Base do E26 facilita isso.)
- ✅ **Recursos de classe** (Fúria [usos], Dados de Vida [n], Inspiração) — FEITO (E27): campo
  `recursos` (atual/máx/recarga) + `POST /recursos/ajustar` e `POST /descanso` (curto/longo,
  longo restaura PV) + painel na ficha.
- ✅ **Defesa sem Armadura** (10 + DES + CON/SAB) — FEITO (E30): `dnd5e.ca_sem_armadura`
  (Bárbaro/Monge) no construtor + `derivados.ca_detalhe`.
- ✅ **Testes contra a morte + exaustão** — FEITO (E31): `mortes_sucesso/falha` (0–3) e `exaustao`
  (0–6) + efeitos do nível + mini-painel "Estado" na ficha.
- ✅ **Multiclasse** — FEITO (E35): `classes_extras` [{slug,nivel}]; nível total dirige a
  proficiência (salvaguardas só da 1ª classe).
- ⚪ **Resistências/imunidades de dano** (ex.: fúria → concussão/cortante/perfurante): só texto.
- ⚪ **Regra Pequeno + arma Pesada** (desvantagem): não validamos compatibilidade arma×tamanho.

## Conteúdo / catálogo
- 🔴 **Antecedente Forasteiro (Outlander)** não existia → **adicionado nesta entrega** ao seed.
- 🟡 **Bênção/boon de campanha**: ganhos concedidos pelo mestre durante o jogo. Modelados como
  **talento homebrew** (ex.: "Bênção da Grande Serpente [+2 CON]"). Futuro: tipo "boon" dedicado.
- ✅ **Admin/mestre marcar conteúdo como OFICIAL** — FEITO (E32): `POST /reference/<tipo>/<slug>/
  oficializar` (ADMIN) + botão "Tornar Oficial" no compêndio.

## Ficha / campos
- ✅ **Moedas por tipo** (PC/PP/PE/PO/PL) — FEITO (E33): campo `moedas` + `derivados.total_po` +
  inputs no editor/chips na ficha/PDF (mantém `dinheiro` texto).
- ⚪ **Página de identidade** (idade, altura, peso, olhos, pele, cabelo, facção, símbolo, aliados,
  tesouro, aparência): só temos `historia`/`avatar_url`. Futuro: aba "Identidade".
- ✅ **Multiclasse** — FEITO (E35): ver acima (classes_extras + nível total).

## Imagens / mídia
- ✅ **Galeria de imagens do personagem** — FEITO (E34): campo `imagens` [{url,legenda,principal}]
  + galeria na aba Identidade (upload, principal, remover). Era: 2 slots (retrato `avatar_url` + símbolo
  `simbolo_faccao_url`); pedido de **várias imagens** (corpo inteiro, rosto,
  cenas, etc.) com legenda e uma marcada como principal. Modelo `ImagemPersonagem`
  (personagem_id, url, legenda, principal) + UI de galeria na aba Identidade.

## Exportação / saída de serviço
- 🔴 **Exportar ficha em PDF (parecida com a oficial)**: gerar um PDF da ficha o **mais próximo
  possível do layout oficial 5E** — bloco de atributos à esquerda, combate (CA/iniciativa/PV/
  ataques) ao centro, perícias/salvaguardas, traços & recursos, e 2ª página de identidade
  (retrato + símbolo da facção + aparência/aliados/tesouro). Reaproveita os mesmos `derivados`
  da ficha (atributos_final, modificadores, CA, ataques, perícias, traços, magias).
  **Motor proposto:** WeasyPrint (Python puro, ótimo com print-CSS `@page A4`) — respeita a regra
  "backend só Python", sem Node. Endpoint `GET /api/v1/characters/<id>/pdf` (auth + dono/mestre/
  admin) → `application/pdf`. Botão "Exportar PDF" na ficha (download via blob).
  **Licença:** recriamos um layout **semelhante** (design próprio inspirado no oficial), usando só
  conteúdo SRD + nossos dados — **sem embutir o formulário oficial da WotC** (evita IP do form).
  **Status:** ✅ FEITO (E25). Serviço `FichaPDF` + template `templates/pdf/ficha.{html,css}` (2 págs),
  endpoint `GET /characters/<id>/pdf`, botão na ficha. Imagens só de uploads locais (basename →
  `file://` dentro de `UPLOAD_DIR`); URLs externas ignoradas. Verificado em prod (Kzen com retrato+
  símbolo, 74 KB).
  **Hardening pendente (do review do E25):**
  - ⚪ Passar um `url_fetcher` restritivo ao WeasyPrint (defense-in-depth: só `file://` sob
    `UPLOAD_DIR`) — hoje já é seguro por basename + autoescape do Jinja, mas vale o cinto-e-suspensório.
  - ⚪ Rate-limit / cache no endpoint de PDF (render é CPU-bound; evitar abuso de spam).
  - ⚪ Tema alternativo de PDF, watermark "homebrew", export de bestiário/PDM.

## ⭐ Produtividade de ficha — features do agente (entregues no lote de 2026-06-07)
> Foco do dono: **agilizar questões de ficha**, sem virar "joguinho" dentro da plataforma.
> (A ideia anterior de "rolador de dados" foi descartada pelo dono — era gamificação, fora do objetivo.)

- ✅ **Clonar personagem** — FEITO (E36): `POST /characters/<id>/clonar` (cópia coluna a coluna p/ o
  usuário) + botão "Clonar" na ficha.
- ✅ **Exportar/Importar ficha em JSON** — FEITO (E37): `GET /characters/<id>/export` +
  `POST /characters/import` (backup/portabilidade; **não** é import por LLM).
- ✅ **Cálculo automático de PV** — FEITO (E38): `dnd5e.pv_sugerido` + botão "Calcular PV" (classe/nível/CON).
- ✅ **Revisão automática da ficha (lint)** — FEITO (E39): `dnd5e.revisar_ficha` + banner de
  inconsistências (PV/atributos/ASI/exaustão/perícias) no topo da ficha.

### Próximas ideias de produtividade (não-gamificação) — candidatas
- ⚪ **Aplicar proficiências da classe/antecedente com 1 clique** (preenche perícias proficientes a
  partir do catálogo escolhido — agiliza a criação).
- ⚪ **Validação de `tracos_extras`** com o mesmo clamp do E26 (fecha o débito de hardening).
- ⚪ **Página/preview de impressão rápida** e **export de bestiário/PDM em PDF** (reusa o FichaPDF).

## Futuro distante (ideias do dono)
- ⚪ **Importação de ficha por LLM**: jogador/mestre faz upload de uma ficha (PDF/imagem) e um
  **LLM parseia e distribui** os dados no nosso modelo de forma inteligente (mapear raça/classe/
  antecedente/talentos/atributos/itens contra o catálogo, criar homebrew quando não existir,
  aplicar efeitos). Reduz digitação manual. **Bem pra depois.** (Hoje a importação é manual via API/UI.)

## Observações de qualidade detectadas na ficha de origem
- Sabedoria Passiva no PDF (12) estava **incorreta**; o correto com Percepção proficiente é **14**
  (nossa engine calcula 14 — importação "corrigida").
- "Dados de Vida: 8" no PDF; nível 9 = **9d12** (corrigido).
