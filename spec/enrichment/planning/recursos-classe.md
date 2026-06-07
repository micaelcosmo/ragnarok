# Unit — Recursos de classe com usos (E27)

> Atende o gap "Recursos de classe (Fúria/Dados de Vida/Inspiração) sem rastreio de usos" do roadmap.

## Objetivo
Rastrear **recursos com usos limitados** que recarregam por descanso (Fúria, Dados de Vida,
Inspiração de Bardo, etc.): cada recurso tem **máximo**, **atual** e **tipo de recarga**.

## Modelo
```yaml
Personagem.recursos: JSON (lista), default []
  item:
    nome: str                # "Fúria", "Dados de Vida"
    max: int >= 0
    atual: int em [0, max]
    recarga: "curto" | "longo" | "nenhum"   # descanso que restaura
    descricao: str (opcional)
migracao: alembic (coluna JSON nullable)
```

## Regras (puras, `app/rules/dnd5e.py`)
```yaml
aplicar_descanso(recursos, tipo):
  - tipo "curto"  -> recarrega recursos com recarga == "curto"
  - tipo "longo"  -> recarrega recarga in {"curto","longo"}
  - "nenhum"      -> nunca recarrega automaticamente
  - recarregar = atual := max
sanear_recursos(lista):
  - nome str não-vazio; max int >= 0; atual clampado a [0, max]; recarga in {curto,longo,nenhum}
  - descarta itens inválidos
```

## API
```yaml
- PUT /characters/<id>  aceita `recursos` (lista) -> sanear_recursos
- POST /characters/<id>/recursos/ajustar { indice, delta }  -> atual += delta, clampado [0, max]
- POST /characters/<id>/descanso { tipo: "curto"|"longo" }  -> aplicar_descanso;
    descanso "longo" também restaura pv_atual := pv_max
  (todas exigem dono ou ADMIN; retornam a ficha atualizada)
```

## Frontend
```yaml
- painel "Recursos" na ficha: cada recurso com nome, atual/max (pips ou número) e botões − / +
- botões "Descanso curto" / "Descanso longo" no topo do painel
- criar/editar/remover recurso (modal simples), análogo aos traços
- reflete ao vivo (polling já existente)
```

## Critérios de aceite
```yaml
- definir recursos via PUT salva sanitizado (atual clampado a [0,max])
- ajustar delta -1 reduz atual (não passa de 0); +1 não passa de max
- descanso curto restaura só os de recarga "curto"; longo restaura curto+longo e PV
- recarga "nenhum" nunca é restaurada por descanso
- sem regressão na suíte
```

## Fora de escopo (futuro)
- auto-sugestão de recursos por classe/nível (Fúria N usos, Dados de Vida = nível), gasto parcial de
  Dados de Vida com cura no descanso curto, recursos com recarga por "dado" (ex.: 1/dia em amanhecer).
