# Unit Spec — Importers & Pipeline de Conteúdo

## `Talento` (novo modelo)
| Campo | Tipo | Notas |
|-------|------|-------|
| slug | str unique | chave natural |
| nome | str | pt-BR |
| descricao | text | efeito do talento |
| pre_requisito | str | ex.: "Força 13+" (nullable) |
| fonte | str | ex.: "SRD 5.1", "Open5e: tome-of-beasts" |

## Campo `fonte`
Adicionado a `Raca`, `Classe`, `Antecedente`, `Magia`, `Monstro`, `Talento`.
Default `"SRD 5.1"` para o seed local.

## `ContentSource` (interface)
```yaml
ContentSource:
  nome: -> str
  buscar(tipo): -> list[dict]   # registros brutos; tipo in [races,classes,backgrounds,feats,spells,monsters]
```

## `Normalizer`
Para cada (fonte, tipo), converte o dict bruto no schema canônico do modelo. Garante `slug`
e injeta `fonte`. Campos desconhecidos são ignorados.

## `ContentPipeline.executar(tipos)`
```yaml
para_cada tipo em tipos:
  brutos = source.buscar(tipo)
  para_cada bruto em brutos:
    canonico = normalizer.normalizar(tipo, bruto, fonte)
    se invalido (sem slug/nome): ignora
    se ja existe (slug): atualiza campos vazios (ou tudo se force) -> conta "atualizado"
    senao: insere -> conta "inserido"
retorna Relatorio(por_tipo={inseridos, atualizados, ignorados})
```

## Critérios de aceite (tests/test_content.py — sem rede)
1. `FakeSource` com 3 talentos → pipeline insere 3; segunda execução insere 0 (idempotente).
2. Registro importado tem `fonte` == rótulo da pipeline.
3. `Normalizer` mapeia atributos para `for/des/con/int/sab/car`.
4. Item sem `slug` é ignorado (entra em "ignorados").
5. Modo `force=True` sobrescreve campo já preenchido; sem force, preserva.
