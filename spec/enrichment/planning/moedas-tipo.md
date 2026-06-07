# Unit — Moedas por tipo (E33)

> Gap do roadmap: `dinheiro` é texto único. D&D usa 5 tipos de moeda. Estruturar agiliza somar
> tesouro, comprar/vender e mostrar o total.

## Modelo
```yaml
Personagem.moedas: JSON {pc, pp, pe, po, pl} (inteiros >= 0), default {}
  pc = cobre · pp = prata · pe = electro · po = ouro · pl = platina
mantém `dinheiro` (texto livre) para anotações; `moedas` é o estruturado.
migração: Alembic (coluna JSON)
```

## Regras (app/rules/dnd5e.py)
```yaml
sanear_moedas(d): só chaves pc/pp/pe/po/pl, inteiros >= 0 (negativos viram 0, inválidos ignorados)
moedas_total_po(d): total convertido em PO -> pc*0.01 + pp*0.1 + pe*0.5 + po*1 + pl*10
  (1 PO = 100 PC = 10 PP = 2 PE = 0,1 PL)
```

## API / derivados
```yaml
- PUT aceita `moedas` (dict) -> sanear_moedas
- derivado["total_po"] = moedas_total_po(personagem.moedas) (arredondado a 2 casas)
```

## Frontend
```yaml
- editor: 5 inputs (PC/PP/PE/PO/PL) na aba Magia & Itens, perto de `dinheiro`
- ficha: chips das moedas (>0) + "≈ X PO" do total; PDF da ficha mostra as moedas
```

## Critérios de aceite
```yaml
- moedas {po:10, pp:5} salva e total_po = 10.5
- negativos -> 0; chave inválida ignorada
- sem moedas -> total_po 0
- sem regressão
```

## Fora de escopo
- conversão/“troco” automático ao comprar; peso das moedas.
