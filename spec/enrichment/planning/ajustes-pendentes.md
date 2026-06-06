# Ajustes Pendentes (a iniciar quando o Micael startar a planning)

> Lista acumulada de correções/melhorias observadas. **NÃO implementar ainda** — só registrar.
> Quando aprovado, cada item vira task com ciclo SDD/TDD normal.

## 1. Stat block da ficha: valor BASE com modificador FINAL (inconsistente) 🔴
**Sintoma:** o bloco de atributo mostra o **modificador do valor final** mas exibe embaixo o
**valor base**, então a conta "não fecha".
- Evidência (Kzen): `DES +4` exibindo **16** (deveria ser 18 para +4); `CON +3` exibindo **14**
  (deveria ser 16 para +3). FOR/INT/SAB/CAR batem porque não têm bônus de fonte.
**Causa provável:** em `frontend/js/pages/character.js` `renderStats()` usa
`personagem.atributos[chave]` (base) no número, e `derivados.modificadores[chave]` (final) no mod.
**Modificador (confirmado, fórmula oficial):** `floor((valor_total - 10) / 2)`.
Ex.: 13 → +1, 14 → +2, 8 → −1, 9 → −1. (Nossa engine `app/rules/dnd5e.modificador` já está correta.)
**Correção proposta (não aplicar ainda):** exibir `derivados.atributos_final[chave]` como o número
do stat block (mantendo o valor **base** editável no formulário de edição). Assim número e
modificador batem (DES 18/+4, CON 16/+3). Avaliar mostrar um "(base 16 +2)" discreto p/ transparência.

## 2. Nomes de armas/itens em inglês (catálogo open5e) 🟡
**Sintoma:** as armas equipadas no Kzen aparecem como "Greataxe/Handaxe/Javelin" (open5e em
inglês), enquanto a ficha-fonte usa PT (Machado Grande/Machadinha/Azagaia).
**Opções:** (a) ativar tradução real (Argos) e exibir em PT via toggle; (b) criar **aliases/
homebrew PT** dos itens comuns; (c) curar um de-para PT para armas/armaduras básicas do SRD.
**Status:** Greataxe/Javelin/Handaxe equipados (id 95/101/100); ataque/dano corretos (+8, 1d12+4 etc.).

## 3. Equipamento mundano não está no catálogo 🟡
**Sintoma:** Pacote de Explorador, Roupas de Viajante, Armadilha de Caça, Tatuagens, Bolsa,
Corda 30 m — não existem como itens cadastráveis (open5e só trouxe weapons/armor/magicitems).
Hoje ficam no campo de texto `equipamento` do Kzen.
**Correção proposta:** ingerir "adventuring gear" + pacotes de equipamento (equipment packs) do SRD
para um tipo de item "equipamento comum" (ou estender o tipo `Item`).

## 4. Imagens do personagem (retrato + símbolo da facção) 🔴 — FEATURE
**Pedido:** a ficha oficial tem **arte de aparência** (retrato do Kzen) e **símbolo da facção**.
Queremos exibir/anexar imagens ao personagem.
**Proposta:** upload de imagem (validado) OU URL; campos `retrato_url`/`avatar_url` e
`simbolo_faccao_url`; volume Docker p/ uploads; nginx servindo. (ver planning "identidade-imagens").

## 5. Página de Identidade (página 2 da ficha oficial) 🟡 — FEATURE
**Pedido implícito:** dados de identidade/história — idade, altura, peso, olhos, pele, cabelo,
facção, **aparência**, **aliados & organizações**, **tesouro** (além de história, que já existe).
**Proposta:** novos campos no `Personagem` + aba "Identidade" na ficha (editável).

