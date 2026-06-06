# Conteúdo Base — Visão Geral

> Spec dedicada à **gestão do conteúdo de jogo** do Ragnarok: raças, classes, antecedentes,
> perícias, talentos, magias e monstros — registrados no banco e **incrementáveis** por uma
> linha de processamento (pipeline) que ingere conteúdo de fontes externas.

## Objetivo
Sair do conjunto curado embutido (`backend/data/*.json`) para um catálogo **rico e expansível**,
mantendo tudo **registrado no DB** e rastreável por **fonte/livro** (ex.: SRD, e — quando
disponível sob licença aberta — material de livros como *Guia do Aventureiro para a Costa da
Espada*). A meta é aumentar as opções de **classe, raça, antecedente, talento, magia e monstro**.

## Princípios
1. **Tudo no banco**: o catálogo vive no Postgres; os JSON locais são apenas o *seed* inicial.
2. **Rastreabilidade de fonte**: cada registro guarda `fonte` (ex.: `"SRD 5.1"`, `"Tome of Beasts"`).
   Isso permite filtrar por livro na UI e saber a procedência.
3. **Idempotência**: reimportar não duplica (chave = `slug`); atualiza campos vazios sem
   sobrescrever edições manuais marcadas.
4. **Licenciamento explícito (importante)**:
   - Só ingerimos conteúdo sob **licença aberta** (OGL 1.0a / CC-BY) — SRD da Wizards e fontes
     OGL de terceiros (ex.: *Tome of Beasts* da Kobold Press).
   - Conteúdo **proprietário** de livros oficiais não-SRD (textos de fluff, subclasses exclusivas)
     **não é redistribuído**. Quando uma fonte aberta expõe a porção OGL de um livro, usamos
     apenas essa porção e creditamos a fonte. Projeto **acadêmico**, sem fins comerciais.

## Fontes suportadas (adapters)
```yaml
fontes:
  local:                       # seed embutido (offline) — sempre disponível
    tipo: arquivos JSON em backend/data/
    fonte_padrao: "SRD 5.1"
  open5e:                      # https://api.open5e.com — agregador OGL
    tipos: [races, classes, backgrounds, feats, spells, monsters]
    licenca: OGL 1.0a / documentos tagueados (document__slug)
  dnd5eapi:                    # https://www.dnd5eapi.co — SRD oficial
    tipos: [races, classes, spells, feats, monsters]
    licenca: SRD (OGL)
```

## Tipos de conteúdo no escopo
| Tipo | Modelo | Observação |
|------|--------|------------|
| Raça | `Raca` | + subraças |
| Classe | `Classe` | sem subclasses proprietárias |
| Antecedente | `Antecedente` | |
| Perícia | `Pericia` | 18 fixas do 5E (novas perícias são raras; tabela de referência) |
| **Talento** | `Talento` (novo) | feats — vêm majoritariamente do pipeline (SRD só tem "Grappler") |
| Magia | `Magia` | |
| Monstro | `Monstro` | bestiário SRD global |

## Não-objetivos
- Não reproduzir livros inteiros nem texto protegido por direitos autorais.
- Não automatizar regras de subclasses proprietárias.
