# Roadmap de Gaps — revelados ao importar a ficha do Kzen (Bárbaro 9 Halfling)

> Importar uma ficha oficial de nível alto expôs o que a plataforma ainda **não modela**.
> Cada item vira candidato a feature futura. Prioridade: 🔴 alta · 🟡 média · ⚪ baixa.

## Mecânicas de personagem
- 🔴 **Aumentos de Habilidade (ASI)**: não há mecanismo de ASI por nível (4/8/12/16/19). Hoje
  são "embutidos" no atributo base na importação. Futuro: trilha de progressão por nível.
- 🟡 **Validação de `tracos_extras`**: o campo aceita JSON livre do usuário (nome/descrição/efeitos)
  sem validar forma nem clampar a magnitude dos números (ex.: `efeitos.atributos.con: 9999`).
  Afeta só a própria ficha (risco de balanceamento, não de plataforma), mas vale um schema/limites
  no backend e, idealmente, traços incrementais sujeitos à aprovação do Mestre da mesa.
- 🔴 **Sub-raças aplicando efeitos**: a raça aplica `efeitos`, mas **sub-raça** (ex.: Halfling
  Robusto +1 CON, resistência a veneno) não é auto-aplicada. Hoje embutimos na base/descrição.
- 🟡 **Talentos vs ASI**: feats reais (Sortudo, Bravura) existem como conteúdo, mas a escolha
  "ASI ou talento" por nível não é guiada.
- 🔴 **Recursos de classe** (Fúria [usos], Dados de Vida [n], Inspiração como recurso):
  sem rastreio de usos/recarga. Hoje viram texto.
- 🟡 **Defesa sem Armadura** (CA = 10 + DES + CON): a CA é manual; não há fórmula automática por
  classe quando sem armadura.
- 🟡 **Testes contra a morte** (sucessos/falhas) e **exaustão**: sem campos próprios.
- ⚪ **Resistências/imunidades de dano** (ex.: fúria → concussão/cortante/perfurante): só texto.
- ⚪ **Regra Pequeno + arma Pesada** (desvantagem): não validamos compatibilidade arma×tamanho.

## Conteúdo / catálogo
- 🔴 **Antecedente Forasteiro (Outlander)** não existia → **adicionado nesta entrega** ao seed.
- 🟡 **Bênção/boon de campanha**: ganhos concedidos pelo mestre durante o jogo. Modelados como
  **talento homebrew** (ex.: "Bênção da Grande Serpente [+2 CON]"). Futuro: tipo "boon" dedicado.
- 🟡 **Admin/mestre marcar conteúdo como OFICIAL**: hoje todo conteúdo criado via API é `homebrew`.
  Falta um caminho para o ADMIN publicar conteúdo oficial (curadoria).

## Ficha / campos
- 🟡 **Moedas por tipo** (PC/PE/PP/PO/PL): hoje `dinheiro` é texto único.
- ⚪ **Página de identidade** (idade, altura, peso, olhos, pele, cabelo, facção, símbolo, aliados,
  tesouro, aparência): só temos `historia`/`avatar_url`. Futuro: aba "Identidade".
- ⚪ **Multiclasse** (ex.: Bárbaro X / Outra Y): só uma classe por personagem.

## Imagens / mídia
- 🟡 **Galeria de imagens do personagem**: hoje há 2 slots (retrato `avatar_url` + símbolo
  `simbolo_faccao_url`). Pedido: suportar **várias imagens** por personagem (corpo inteiro, rosto,
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

## Futuro distante (ideias do dono)
- ⚪ **Importação de ficha por LLM**: jogador/mestre faz upload de uma ficha (PDF/imagem) e um
  **LLM parseia e distribui** os dados no nosso modelo de forma inteligente (mapear raça/classe/
  antecedente/talentos/atributos/itens contra o catálogo, criar homebrew quando não existir,
  aplicar efeitos). Reduz digitação manual. **Bem pra depois.** (Hoje a importação é manual via API/UI.)

## Observações de qualidade detectadas na ficha de origem
- Sabedoria Passiva no PDF (12) estava **incorreta**; o correto com Percepção proficiente é **14**
  (nossa engine calcula 14 — importação "corrigida").
- "Dados de Vida: 8" no PDF; nível 9 = **9d12** (corrigido).
