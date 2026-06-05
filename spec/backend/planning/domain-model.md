# Backend — Modelo de Domínio

## Entidades

### User
| Campo | Tipo | Notas |
|-------|------|-------|
| id | int PK | |
| email | str unique | |
| name | str | |
| password_hash | str | |
| role | enum | `ADMIN` \| `MESTRE` \| `JOGADOR` (default JOGADOR) |
| created_at | datetime | |

Relacionamentos: `personagens` (1:N), `mesas_mestradas` (1:N como mestre),
`participacoes` (N:M com Mesa via MembroMesa).

### Personagem (ficha 5E)
Identidade: `nome, raca_slug, classe_slug, antecedente_slug, nivel, xp, tendencia, nome_jogador`.
Atributos base (1–30): `for, des, con, int, sab, car`.
Combate: `ca, iniciativa_bonus, deslocamento, pv_max, pv_atual, pv_temp, dado_vida, inspiracao(bool)`.
Proficiências: `pericias_proficientes` (JSON list), `salvaguardas_proficientes` (JSON list).
Texto livre: `tracos_personalidade, ideais, vinculos, fraquezas, historia, caracteristicas, idiomas, equipamento, ataques, dinheiro`.
Magia: `classe_conjuradora, atributo_conjuracao, magias` (JSON), `truques` (JSON).
FKs: `user_id` (dono), `mesa_id` (nullable — personagem pode estar numa mesa).

**Campos derivados (calculados, não persistidos):** modificadores dos 6 atributos,
bônus de proficiência, perícias (valor), salvaguardas (valor), percepção passiva, CD de magia,
bônus de ataque de magia, iniciativa total. Calculados por `app/rules/dnd5e.py` na serialização.

### Mesa (campanha)
`id, nome, descricao, sistema(='D&D 5E'), codigo_convite(unique), mestre_id(FK User), created_at`.
Relacionamentos: `membros` (MembroMesa), `personagens` (1:N), `monstros` (bestiário da mesa).

### MembroMesa
`id, mesa_id, user_id, papel_na_mesa(='jogador'), entrou_em`. Une jogador↔mesa.

### Monstro / PDM (bestiário)
`id, slug, nome, tipo, tamanho, alinhamento, ca, pv, pv_formula, deslocamento,
atributos(JSON 6), nd(challenge rating), xp, pericias, sentidos, idiomas,
habilidades(JSON), acoes(JSON), is_pdm(bool), mesa_id(nullable=SRD global), criado_por(FK)`.

### Conteúdo de referência (read-only / seed SRD)
- **Raca**: `slug, nome, descricao, deslocamento, tamanho, bonus_atributos(JSON), tracos(JSON), subracas(JSON)`.
- **Classe**: `slug, nome, descricao, dado_vida, salvaguardas(JSON), pericias_disponiveis(JSON),
  num_pericias, conjurador(bool), atributo_conjuracao`.
- **Antecedente**: `slug, nome, descricao, pericias(JSON), idiomas, equipamento`.
- **Magia**: `slug, nome, nivel, escola, tempo_conjuracao, alcance, componentes, duracao,
  concentracao(bool), ritual(bool), classes(JSON), descricao`.

## Diagrama (texto)
```
User 1───N Personagem N───1 Mesa 1───1 User(mestre)
  │                         │
  └───N MembroMesa N────────┘
Mesa 1───N Monstro (bestiário da mesa)   Monstro(mesa_id NULL) = SRD global
Raca / Classe / Antecedente / Magia = catálogo SRD (somente leitura p/ jogador; CRUD p/ admin)
```
