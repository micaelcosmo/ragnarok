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

<!-- Próximos itens entram abaixo conforme forem aparecendo -->
