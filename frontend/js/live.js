// Atualização "ao vivo" das telas abertas, sem F5.
// - Reativo: cada mutação já re-renderiza a partir da resposta da API.
// - Polling: enquanto a tela está aberta, refaz o fetch a cada intervalo e re-renderiza
//   SE algo mudou (inclusive mudanças feitas por OUTRO usuário). Não atrapalha quem está
//   editando (pula se há modal aberto ou um input/textarea em foco).

let poller = null;

export function pararPolling() {
  if (poller) {
    clearInterval(poller);
    poller = null;
  }
}

/**
 * @param {Function} buscar - async () => dados (estado atual do servidor)
 * @param {Function} aplicar - (dados) => re-renderiza a tela com os novos dados
 * @param {Object}   opts - { inicial?: any, ms?: number }
 */
export function iniciarPolling(buscar, aplicar, { inicial = undefined, ms = 7000 } = {}) {
  pararPolling();
  let assinatura = inicial !== undefined ? JSON.stringify(inicial) : null;
  poller = setInterval(async () => {
    // Não interrompe edição em andamento.
    if (document.querySelector('.modal-back')) return;
    const foco = document.activeElement;
    if (foco && ['INPUT', 'TEXTAREA', 'SELECT'].includes(foco.tagName)) return;
    try {
      const dados = await buscar();
      const nova = JSON.stringify(dados);
      if (assinatura !== null && nova !== assinatura) aplicar(dados);
      assinatura = nova;
    } catch (_) { /* silencioso: rede instável não deve poluir a UI */ }
  }, ms);
}
