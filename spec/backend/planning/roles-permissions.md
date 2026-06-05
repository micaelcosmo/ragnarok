# Backend — Papéis & Permissões (RBAC)

## Papéis
- **ADMIN** — superusuário da plataforma. Faz tudo. Gerencia usuários e catálogo SRD.
- **MESTRE** — cria/gerencia mesas, gerencia jogadores, CRUD de bestiário (monstros/PDMs).
  Também pode ter personagens (um mestre pode jogar).
- **JOGADOR** — cria/edita os próprios personagens; entra em mesas por código.

> Hierarquia: ADMIN ⊇ MESTRE ⊇ JOGADOR em capacidade, **mas papéis são exclusivos**
> (um usuário tem 1 papel). ADMIN consegue agir como qualquer um via permissões explícitas.

## Matriz de permissões

| Ação | ADMIN | MESTRE | JOGADOR |
|------|:-----:|:------:|:-------:|
| Registrar/login | ✓ | ✓ | ✓ |
| Ver catálogo SRD | ✓ | ✓ | ✓ |
| Editar catálogo SRD | ✓ | ✗ | ✗ |
| Criar/editar personagem próprio | ✓ | ✓ | ✓ |
| Ver personagem de outro | ✓ | só da sua mesa | ✗ |
| Criar mesa | ✓ | ✓ | ✗ |
| Gerenciar membros da mesa | ✓ | só as suas | ✗ |
| Entrar em mesa por código | ✓ | ✓ | ✓ |
| CRUD bestiário (mesa) | ✓ | só as suas | ✗ |
| CRUD bestiário SRD global | ✓ | ✗ | ✗ |
| Gerenciar usuários / promover papel | ✓ | ✗ | ✗ |
| Ver métricas da plataforma | ✓ | ✗ | ✗ |

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
