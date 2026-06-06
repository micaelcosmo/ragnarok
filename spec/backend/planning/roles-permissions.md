# Backend — Papéis & Permissões (RBAC)

## Papéis
- **ADMIN** — **gerente da plataforma** (governança), NÃO um super-mestre de jogo. Cuida de:
  gestão de **contas** (listar/promover/rebaixar/remover usuários), **moderação de mesas**
  ("desbugar": ver/remover qualquer mesa, tirar membro preso), curadoria do **catálogo de
  conteúdo** (SRD + ingestões via pipeline) e **métricas** da plataforma.
  > O admin tem override técnico (passa em `@role_required`) para poder moderar, mas o papel
  > **não é de jogo**: ele não "mestra" mesas nem é jogador por definição. Foco = administrar.
- **MESTRE** — papel de **jogo**: cria/gerencia mesas, gerencia jogadores, CRUD de bestiário
  (monstros/PDMs). Também pode ter personagens (um mestre pode jogar).
- **JOGADOR** — cria/edita os próprios personagens; entra em mesas por código.

> Papéis são **exclusivos** (um usuário tem 1 papel). ADMIN ≠ MESTRE: separamos governança
> da plataforma (admin) das mecânicas de jogo (mestre). O override do admin existe só para
> moderação/suporte, não para "ser mestre".

## Matriz de permissões

| Ação | ADMIN | MESTRE | JOGADOR |
|------|:-----:|:------:|:-------:|
| Registrar/login | ✓ | ✓ | ✓ |
| Ver catálogo SRD | ✓ | ✓ | ✓ |
| Criar/editar conteúdo do compêndio | ✓ | ✓ | ✗ |
| Editar conteúdo **oficial** | ✓ (no lugar) | ✓ (cria variante homebrew) | ✗ |
| Excluir conteúdo oficial | ✓ | ✗ | ✗ |
| Aceitar fonte homebrew na própria mesa | ✓ | ✓ | ✗ |
| Criar/editar personagem próprio | ✓ | ✓ | ✓ |
| Ver personagem de outro | ✓ | só da sua mesa | ✗ |
| Criar mesa | ✓ | ✓ | ✗ |
| Gerenciar membros da mesa | ✓ | só as suas | ✗ |
| Entrar em mesa por código | ✓ | ✓ | ✓ |
| CRUD bestiário (mesa) | ✓ | só as suas | ✗ |
| CRUD bestiário SRD global | ✓ | ✗ | ✗ |
| Gerenciar usuários / promover papel | ✓ | ✗ | ✗ |
| Ver métricas da plataforma | ✓ | ✗ | ✗ |
| **Moderar mesas** (listar todas / desbugar / remover qualquer) | ✓ | ✗ | ✗ |
| Curar catálogo de conteúdo (ingestão/edição) | ✓ | ✗ | ✗ |

## Implementação
- Decorator `@role_required(*roles)` — checa `current_user.role in roles` (ADMIN sempre passa).
- Checagem de **ownership** dentro do handler (ex.: `personagem.user_id == current_user.id`).
- Mestre acessa personagem de jogador apenas se `personagem.mesa_id` pertence a uma mesa
  cujo `mestre_id == current_user.id`.

## Critérios de aceite (testáveis)
1. JOGADOR recebe 403 ao tentar `POST /campaigns`.
2. JOGADOR recebe 403 ao acessar personagem de outro jogador.
3. MESTRE acessa (200) o personagem de um jogador da sua mesa.
4. MESTRE recebe 403 ao editar catálogo SRD.
5. Não-ADMIN recebe 403 em qualquer `/admin/*`.
6. Registro nunca cria ADMIN (mesmo enviando `role:"ADMIN"`).
