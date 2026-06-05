# Changelog — Frontend

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/) + commits semânticos.

## [Não lançado]
### docs
- Design system (paleta, tipografia, componentes, padrão de ficha estilo D&D Beyond).
- Fluxos de UX por papel (JOGADOR/MESTRE/ADMIN).
- Mapa de páginas e módulos JS; spec do cliente de API/sessão; plano de testes.

### feat
- SPA vanilla (ES modules) com hash router e guardas por papel.
- Design system CSS completo (tema dark fantasy + dourado/vermelho, stat-blocks, abas, modais, toasts).
- Núcleo: `api.js` (cliente fetch + atalhos por recurso), `auth.js` (sessão/RBAC),
  `router.js`, `ui.js` (helpers), `rules.js` (preview de modificadores).
- Páginas: login/registro, dashboard por papel, ficha estilo D&D Beyond (leitura/edição,
  stat-blocks, perícias, salvaguardas, PV com barra e dano/cura), wizard de criação (5 passos),
  mesas (criar/entrar por código/gerenciar/vincular personagem), bestiário (lista/detalhe/CRUD),
  compêndio (magias com filtro, raças, classes), painel admin (stats + gestão de usuários).

### style
- PEP8-equivalente em JS: nomes descritivos, módulos coesos, sem variáveis de laço genéricas.
