# Unit Spec — Personagens

## Regras
- Criação exige `nome`. Atributos default 10 se ausentes. `nivel` derivado de `xp` se enviado,
  senão usa `nivel` informado (default 1).
- Serialização inclui bloco `derivados`:
  `modificadores{for..car}, bonus_proficiencia, iniciativa, percepcao_passiva,
   cd_magia, bonus_ataque_magia, pericias[{nome,atributo,valor,proficiente}],
   salvaguardas[{atributo,valor,proficiente}]`.
- Ownership: só o dono (ou ADMIN, ou mestre da mesa do personagem) lê/edita.

## Critérios de aceite (tests/test_characters.py)
1. POST cria personagem → 201, `user_id` = atual.
2. GET retorna `derivados.modificadores.for` coerente com o atributo `for`.
3. perícia proficiente reflete `+bonus_proficiencia` no valor.
4. JOGADOR A não acessa (403/404) personagem de JOGADOR B.
5. PUT atualiza atributo e os derivados mudam.
6. DELETE remove (200) e some da listagem.
