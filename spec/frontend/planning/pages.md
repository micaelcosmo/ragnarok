# Frontend — Páginas & Módulos

SPA *vanilla* com **hash router** (`js/router.js`). Cada página é um módulo que renderiza
HTML no `#app` e liga eventos. Estado de sessão em `js/auth.js`; chamadas em `js/api.js`.

## Módulos JS
| Arquivo | Responsabilidade |
|---------|------------------|
| `js/api.js` | `apiFetch(path, {method,body,auth})` — base URL, token, erros JSON. |
| `js/auth.js` | login/logout, guarda token, `getUser()`, guarda de rota por papel. |
| `js/router.js` | hash router minimalista + middlewares (auth/role). |
| `js/ui.js` | helpers: `el()`, `toast()`, `modal()`, `tabs()`, formatadores. |
| `js/rules.js` | espelho leve do motor (modificador) p/ preview no wizard. |
| `js/pages/login.js` | login + registro. |
| `js/pages/dashboard.js` | personagens + mesas do usuário. |
| `js/pages/character.js` | ficha (leitura/edição) estilo D&D Beyond. |
| `js/pages/character_new.js` | wizard de criação. |
| `js/pages/campaigns.js` | lista/detalhe de mesas; gestão (mestre). |
| `js/pages/bestiary.js` | lista/detalhe/CRUD de monstros e PDMs. |
| `js/pages/compendium.js` | magias/raças/classes (referência). |
| `js/pages/admin.js` | usuários + métricas. |

## Páginas (telas)
1. **Login/Registro** — formulário único com toggle.
2. **Dashboard** — saudação por papel; grid de cards de personagens; lista de mesas; CTAs.
3. **Ficha** — layout 3 colunas (stat-blocks, combate/PV, abas).
4. **Novo Personagem** — wizard de 5 passos com preview de modificadores.
5. **Mesas** — lista; detalhe com membros/personagens; ações de mestre.
6. **Bestiário** — busca + cards; modal de detalhe; form de criação (mestre).
7. **Compêndio** — busca de magias (filtro por nível/classe), raças, classes.
8. **Admin** — cards de stats + tabela de usuários com select de papel.

## Critérios de aceite (frontend/tests)
- Sem token, rota protegida redireciona para `#/login`.
- Dashboard de JOGADOR não mostra ações de mestre/admin.
- Criar personagem pelo wizard resulta em ficha aberta com modificadores corretos.
- A ficha reflete os `derivados` vindos da API (não recalcula no cliente, exceto preview).
