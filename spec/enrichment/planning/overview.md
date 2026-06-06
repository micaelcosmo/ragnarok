# Enriquecimento da Ficha — Visão Geral

> Branch `enrichment`. Objetivo: enriquecer a **criação/preenchimento da ficha** com um acervo
> robusto (raças, classes, antecedentes, talentos, **armas**, **armaduras**, **itens**) e fazer
> as escolhas **aplicarem bônus automaticamente** — de forma **reversível**.

## Decisões (definidas com o dono)
```yaml
bonus:
  modelo: "base + fontes computadas"   # NÃO snapshot
  reversivel: true                     # add fonte soma; remove fonte subtrai (automático)
  magias: "não aplicam nada automático (apenas listadas)"
itens:
  modelos_separados: [Arma, Armadura, Item]   # não unificado
  arma: "dano, acerto/ataque, propriedades"
  armadura: "agrega à CA; CA editável com caixa de AJUSTE manual (+/- pontos)"
  item: "descritivo apenas (bola de cristal, capa do voo...) — nunca muda número"
ownership:
  jogador_cria: "vincula ao personagem (só ele usa)"
  mestre_ou_admin_cria: "acervo geral (global; ou da mesa, p/ mestre)"
idioma:
  toggle_topo: "EN original <-> PT"
  traducao: "offline, gratuita (sem ferramenta paga) + cache no DB"
compendio:
  cards_clicaveis: "todos (magias, talentos, raças, classes, antecedentes, armas, armaduras, itens) abrem detalhe"
  crud: "MESTRE e ADMIN criam/editam/excluem qualquer card"   # antes era só ADMIN
entrega:
  ritmo: "por fase, com commit semântico + push ao fim de cada fase"
```

> **Mudança de RBAC:** a curadoria do catálogo passa de "só ADMIN" para **MESTRE + ADMIN**
> (mestres podem adicionar/editar conteúdo, ex.: homebrew). Atualiza
> `spec/backend/planning/roles-permissions.md`.

## O modelo "base + fontes" (chave de tudo)
A ficha tem dois planos:
1. **Base/manual** — o que o jogador digita (atributos, CA base, perícias marcadas à mão, etc.).
   Continua **100% editável**.
2. **Fontes** — listas de origens ativas: raça, classe, antecedente, **talentos**, **arma(s)
   equipada(s)**, **armadura equipada**. Cada origem carrega um `efeitos` estruturado.

A ficha **final** é calculada por um serviço **`ConstrutorDeFicha`**:
```
final = base + Σ efeitos(fontes ativas)
```
Como as fontes são recomputadas a cada leitura, **remover uma fonte remove o bônus
automaticamente** (sem mutação destrutiva). Ex.: talento "+1 iniciativa" entra na lista de
talentos → soma; tirou da lista → some. Magias ficam de fora dessa soma.

## Fases (incremental — commit+push por fase)
1. **Motor de efeitos**: campo `efeitos` em raça/classe/antecedente/talento; personagem passa a
   rastrear `talentos`; `ConstrutorDeFicha` computa final (base+fontes); testes. Demonstra o
   add/remove automático.
2. **Conteúdo**: ingestão de weapons/armor/(magic)items (open5e) + derivar `efeitos` de
   raça/classe/antecedente; **curar talentos populares** (efeitos numéricos).
3. **Armas/Armaduras/Itens**: 3 modelos + editor + ownership + equipar na ficha (CA/ataque
   automáticos; CA com caixa de ajuste manual).
4. **Wizard enriquecido**: seletores reais + **preview ao vivo** dos bônus na criação.
5. **Compêndio editável**: cards clicáveis (detalhe) para TODOS os tipos + **CRUD por
   MESTRE/ADMIN** (criar/editar/excluir qualquer card). Inclui o ajuste de RBAC.
6. **Traços não-numéricos** ("nunca surpreendido", "vantagem em…") exibidos como features +
   **toggle de idioma EN/PT** (tradução offline grátis + cache).

## Não-objetivos
- Magias não concedem bônus numérico automático.
- Sem subclasses proprietárias; só conteúdo OGL/SRD.
- Tradução é "boa o suficiente" (offline grátis), não profissional.

Detalhes: [effects-engine.md](effects-engine.md), [data-model.md](data-model.md), [i18n.md](i18n.md).
