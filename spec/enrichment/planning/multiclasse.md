# Unit — Multiclasse (E35)

> Gap do roadmap: só uma classe por personagem. Multiclasse é comum em níveis altos.
> Escopo **consciente e correto**: rastrear classes adicionais e usar o **nível total** onde ele
> realmente importa (bônus de proficiência), sem inventar regras que exigiriam UI dedicada.

## Modelo
```yaml
Personagem.classes_extras: JSON (lista), default []
  item: { slug: str, nivel: int >= 1 }   # classes além da primária (classe_slug + nivel)
migração: Alembic (coluna JSON)
```

## Regras (app/rules/dnd5e.py)
```yaml
sanear_classes_extras(lista): só {slug não-vazio, nivel int >= 1}; descarta inválidos
nivel_total(nivel, classes_extras): nivel primário + soma dos níveis extras (clamp 1..20)
```

## Construtor
```yaml
- usa nivel_total para o ConstrutorDeFicha (bônus de proficiência, perícias, salvaguardas, etc.)
- dobra os `efeitos` de cada classe extra como fonte (ex.: proficiências), mas NÃO duplica
  salvaguardas de classe (no 5E, salvaguardas vêm só da 1ª classe) -> remove 'salvaguardas' do efeito extra
- derivado["nivel_total"] e derivado["classes"] = [{slug, nivel}] (primária + extras)
```

## API / Frontend
```yaml
- PUT aceita classes_extras -> sanear
- editor: seção "Multiclasse" (adicionar/remover classe + nível)
- ficha: cabeçalho mostra "Classe N / Outra M · nível total T"
```

## Critérios de aceite
```yaml
- primária nivel 4 + extra {wizard:1} -> nivel_total 5 -> bônus de proficiência sobe de +2 p/ +3
- salvaguardas da classe extra NÃO são concedidas automaticamente (só as da primária)
- classes_extras inválidas são descartadas
- sem regressão
```

## Fora de escopo (futuro, exige UI dedicada)
- pré-requisitos de atributo p/ multiclassear, slots de magia multiclasse, proficiências parciais
  de entrada, HP por classe. Por ora o jogador ajusta PV/proficiências à mão.
