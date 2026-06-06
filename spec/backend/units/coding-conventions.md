# Unit Spec — Convenções de Código (Backend Python)

> Regras obrigatórias para todo código Python do Ragnarok. Definidas pelo dono do projeto.

## 1. PEP 8 (sempre)
- Indentação de 4 espaços; máx. ~99 colunas.
- **Imports** agrupados e ordenados: (1) stdlib, (2) terceiros, (3) locais (`app.*`),
  com uma linha em branco entre os grupos.
- 2 linhas em branco entre funções/classes de nível de módulo; 1 entre métodos.
- `snake_case` para funções/variáveis, `PascalCase` para classes, `MAIÚSCULAS` para constantes.
- Sem imports não usados; sem espaços supérfluos.

## 2. Nomes de laços descritivos
Use nomes que digam o que é o item — nunca `x`, `i`, `l` soltos.

```yaml
# RUIM
ruim: "for x in i: ..."
# BOM
bom: "for produto in produtos: ..."
exemplos_bons:
  - "for atributo in ATRIBUTOS"
  - "for indice, magia in enumerate(magias)"
  - "for nome_pericia, atributo in PERICIAS.items()"
```
Exceção tolerada: `_` para valores deliberadamente ignorados.

## 3. POO (orientação a objetos)
- Inicializações e composições devem ser **orientadas a objetos**: services como classes
  (`SeedRunner`, `CharacterService`), métodos coesos nos models (`to_dict`, `set_password`),
  e construtores explícitos (`__init__`) quando fizer sentido.
- Evitar funções soltas que manipulam estado global; preferir encapsular em classes.
- Exceção: o **motor de regras** (`app/rules/dnd5e.py`) é deliberadamente funcional/puro
  (funções sem estado) para máxima testabilidade — isso é uma escolha de design documentada.

## 4. Exemplos em documentação
- Blocos de exemplo em specs/docs usam **```yaml** (mais estruturado e legível) sempre que
  representarem estrutura de dados/configuração.

## 5. Docstrings
- Toda função/classe pública tem docstring curta em pt-BR descrevendo o propósito.

## Critério de aceite
- Código novo passa numa leitura PEP8 (sem nomes de laço genéricos) e usa POO nos
  pontos de composição/serviço.
