# Planning — E21: Atualização "ao vivo" (sem F5)

Aprovado: **(A) reativo + (B) polling** (tempo real entre usuários/abas).

## Como funciona
- **Reativo (A):** toda mutação já re-renderiza a partir da resposta da API (sem reload).
- **Polling (B):** `frontend/js/live.js` mantém um único poller ativo por tela. Enquanto a tela
  está aberta, refaz o `fetch` a cada intervalo e **re-renderiza só se o conteúdo mudou**
  (inclusive mudanças feitas por OUTRO usuário).
  - Não atrapalha edição: **pula** se há `.modal-back` aberto ou um `input/textarea/select` em foco.
  - O router (`resolver()`) chama `pararPolling()` ao trocar de rota (sem vazar pollers).

## Telas com polling
- **Ficha do personagem** (`renderCharacter`): `GET /characters/:id` a cada 7s →
  `pintarFicha` se mudou. Ex.: o mestre edita a ficha do jogador e ele vê na hora.
- **Detalhe da mesa** (`renderCampaignDetail`): `GET /campaigns/:id` a cada 8s → re-render.
  Ex.: jogador entra/vincula personagem e o mestre vê sem F5.

## Não-objetivos / decisões
- Sem WebSocket/SSE (exigiria mudar o gunicorn). **Polling** é suficiente para a escala atual.
- Intervalos curtos (7–8s) mantêm "ao vivo" sem martelar o servidor; só re-renderiza on-change.

## Critérios de aceite
- Editar a ficha (mesmo por outro usuário) reflete na tela aberta em ≤ ~8s, sem F5.
- Polling não recarrega/zera enquanto você digita ou com um modal aberto.
- Ao sair da tela, o polling para (sem requests órfãos).
