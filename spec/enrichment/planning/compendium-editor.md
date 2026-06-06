# Compêndio Editável — cards clicáveis, CRUD e procedência

## Requisitos (do dono)
- **Cards clicáveis** para TODOS os tipos (magias, talentos, raças, classes, antecedentes,
  armas, armaduras, itens) — abrem um **detalhe** (como as magias já fazem).
- **CRUD por MESTRE/ADMIN**: criam, editam e excluem qualquer card.
- **Fonte obrigatória e visível** em todo card (procedência da informação).
- **Anti-"homebrew vendido como oficial"**: conteúdo criado por usuário é marcado **homebrew**
  e nunca rotulado como oficial. O **mestre aceita ou não** o homebrew na mesa dele.

## Procedência (`fonte`) — obrigatória
Todo modelo de conteúdo já tem `fonte`. Agora:
```yaml
fonte: "obrigatória (exibida no card; required ao criar/editar)"
oficial: "bool derivado da licença da fonte (SRD/OGL = oficial; criado por usuário = homebrew)"
homebrew: "bool — true quando criado por MESTRE/JOGADOR/ADMIN como conteúdo próprio"
criado_por: "user_id (quando homebrew)"
```
- Conteúdo importado do pipeline (open5e/SRD) → `homebrew=false`, `fonte` = documento de origem.
- Conteúdo criado na UI → `homebrew=true`, `fonte` = `"Homebrew — <nome do criador>"`
  (ou rótulo informado), **nunca** marcado como oficial.
- O card exibe um selo: **🛡️ Oficial (fonte)** ou **🧪 Homebrew (fonte/criador)**.

## Aceitação por mesa ("o mestre aceita ou não")
- Conteúdo **oficial** é visível para todos por padrão.
- Conteúdo **homebrew** não é "confiável" automaticamente. Um **mestre** pode marcar fontes/itens
  homebrew como **aceitos na sua mesa** → ficam disponíveis para os jogadores daquela mesa.
- Modelo: `MesaFonteAceita {mesa_id, fonte}` (ou aceitação por item). Listagens em contexto de
  mesa incluem: oficiais + homebrew do próprio usuário + homebrew **aceito** pela mesa.

## Permissões (atualiza RBAC)
| Ação no compêndio | ADMIN | MESTRE | JOGADOR |
|---|:---:|:---:|:---:|
| Ver cards (detalhe) | ✓ | ✓ | ✓ |
| Criar/editar/excluir card | ✓ | ✓ | ✗ |
| Editar conteúdo **oficial** importado | ✓ | ✓* | ✗ |
| Aceitar homebrew na própria mesa | ✓ | ✓ | ✗ |

\* Mestre pode editar, mas a edição de um item **oficial** o transforma em variante homebrew
(ou cria uma cópia homebrew) para preservar a procedência original — **decisão a confirmar na Fase 5**.

## API (Fase 5)
```yaml
# leitura: qualquer autenticado (com filtro de mesa/aceitação)
GET /reference/<tipo>            # ?fonte= &homebrew= &mesa_id=
GET /reference/<tipo>/<slug>
# escrita: MESTRE/ADMIN
POST   /reference/<tipo>         # cria homebrew (fonte obrigatória)
PUT    /reference/<tipo>/<slug>
DELETE /reference/<tipo>/<slug>
# aceitação de homebrew por mesa (MESTRE/ADMIN)
POST   /campaigns/<id>/fontes    # {fonte} aceita
DELETE /campaigns/<id>/fontes    # {fonte} remove
```
tipo ∈ {races, classes, backgrounds, feats, spells, weapons, armor, items}

## Frontend
- Compêndio: todos os cards clicáveis → modal de detalhe; selo de procedência sempre visível.
- Botões **+ Criar** e **✏️ Editar/🗑️** para MESTRE/ADMIN em cada aba.
- Formulário exige **fonte** (default "Homebrew — <eu>") e mostra aviso de que será homebrew.

## Critérios de aceite
1. Card sem `fonte` não existe (required no create; exibido sempre).
2. JOGADOR não vê botões de criar/editar; recebe 403 se tentar via API.
3. MESTRE cria card → marcado homebrew + fonte do criador (nunca "oficial").
4. Homebrew de outro mestre só aparece na minha mesa se eu **aceitar** a fonte.
5. Editar oficial não apaga a procedência original (vira variante homebrew).
