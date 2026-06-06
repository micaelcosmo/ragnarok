# Roadmap de Gaps — revelados ao importar a ficha do Kzen (Bárbaro 9 Halfling)

> Importar uma ficha oficial de nível alto expôs o que a plataforma ainda **não modela**.
> Cada item vira candidato a feature futura. Prioridade: 🔴 alta · 🟡 média · ⚪ baixa.

## Mecânicas de personagem
- 🔴 **Aumentos de Habilidade (ASI)**: não há mecanismo de ASI por nível (4/8/12/16/19). Hoje
  são "embutidos" no atributo base na importação. Futuro: trilha de progressão por nível.
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

## Observações de qualidade detectadas na ficha de origem
- Sabedoria Passiva no PDF (12) estava **incorreta**; o correto com Percepção proficiente é **14**
  (nossa engine calcula 14 — importação "corrigida").
- "Dados de Vida: 8" no PDF; nível 9 = **9d12** (corrigido).
