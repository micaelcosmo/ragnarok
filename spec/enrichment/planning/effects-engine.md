# Motor de Efeitos — `ConstrutorDeFicha`

Serviço **POO**, server-side, **puro o quanto possível** (testável/TDD). Calcula a ficha final
somando os efeitos das **fontes ativas** sobre a camada **base/manual**.

## Esquema canônico de `efeitos`
Campo JSON presente em raça, classe, antecedente, talento, arma e armadura.
```yaml
efeitos:
  atributos: {for: 0, des: 0, con: 0, int: 0, sab: 0, car: 0}  # somados
  pericias: ["Persuasão", "Intuição"]        # proficiências concedidas
  salvaguardas: ["for", "con"]
  iniciativa: 0                               # bônus direto (ex.: talento Alerta +5)
  deslocamento: 0                             # delta (m)
  pv_por_nivel: 0                             # ex.: Anão da Colina / Tough +1/nível
  ca_base: null                              # armadura: define a base da CA
  ca_soma_des: false                         # armadura: soma mod DES
  ca_des_max: null                           # teto do bônus de DES (ex.: 2)
  ca_bonus: 0                                # escudo / +X mágico
  sentidos: ["Visão no escuro 18m"]
  idiomas: ["Comum"]
  proficiencias_texto: ["Armas marciais"]    # vão p/ "outras proficiências"
  recursos: ["Você nunca é surpreendido enquanto consciente."]  # TEXTO, não-número
```
Chaves ausentes = sem efeito. Magias **não** têm `efeitos` (não entram na soma).

## Fontes ativas (no Personagem)
```yaml
fontes:
  raca_slug, classe_slug, antecedente_slug   # já existem
  talentos: ["alerta", "resistente"]         # NOVO (lista de slugs)
  armadura_equipada_id: 12                    # NOVO (uma armadura)
  armas_equipadas: [3, 7]                      # NOVO (armas)
  # itens (descritivos) NÃO entram na soma
```

## Algoritmo (reversível por construção)
```yaml
construir_ficha(personagem):
  base = atributos/manuais do personagem
  fontes = resolve(raca, classe, antecedente, talentos[], armadura, armas[])
  atributos_final = base.atributos + Σ efeitos.atributos
  pericias_final  = base.pericias ∪ (Σ efeitos.pericias)
  salva_final     = base.salvaguardas ∪ (Σ efeitos.salvaguardas)
  iniciativa      = mod(des_final) + base.iniciativa_bonus + Σ efeitos.iniciativa
  ca              = calcular_ca(base.ca, base.ca_ajuste, armadura, escudo/ca_bonus, mod des)
  deslocamento    = base + Σ efeitos.deslocamento
  recursos        = base.caracteristicas (texto) ++ Σ efeitos.recursos  # exibidos como traços
  derivados       = regras 5E sobre atributos_final/pericias_final/...
  return {..., "concedido": {de_onde_veio_cada_bonus}}
```
- **Reversível**: como tudo é recomputado das fontes atuais, remover um talento/arma remove o
  bônus automaticamente. Nada é "gravado e esquecido".
- **Editável**: o jogador edita a camada **base** (atributos, CA base, `ca_ajuste`, perícias
  marcadas à mão). O `concedido` mostra o que veio das fontes (somado por cima).

## CA editável com ajuste manual
Pedido do dono: ao editar, ter um **quadrado de ajuste** (+/- pontos específicos).
```yaml
ca:
  base: 10            # ou definido pela armadura equipada
  ca_ajuste: 0        # NOVO campo manual (+/-), editável
  formula: "base(armadura ou manual) + mod_des(limitado) + ca_bonus(escudo/mágico) + ca_ajuste"
```

## Critérios de aceite (tests/test_effects.py)
1. Talento com `iniciativa:+1` na lista → iniciativa final sobe 1; removido → volta.
2. Antecedente com `pericias:[A,B]` → A e B aparecem como proficientes (concedido).
3. Raça com `atributos:{con:+2}` → CON final = base+2; modificador recalcula.
4. Armadura equipada define `ca_base` + DES limitado; `ca_ajuste:+1` soma; desequipar reverte.
5. Magia adicionada não altera nenhum número.
6. `recursos` (texto) aparecem na lista de traços, sem afetar números.
