// Helpers de UI: criação de elementos, toasts, modais, abas e formatadores.

// Cria elemento a partir de uma string HTML (primeiro nó).
export function html(stringHtml) {
  const molde = document.createElement('template');
  molde.innerHTML = stringHtml.trim();
  return molde.content.firstElementChild;
}

// Escapa texto para inserção segura em HTML.
export function esc(valor) {
  if (valor === null || valor === undefined) return '';
  return String(valor)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Formata um modificador com sinal (+3, -1, +0).
export function sinal(valor) {
  const numero = Number(valor) || 0;
  return numero >= 0 ? `+${numero}` : `${numero}`;
}

// Iniciais para avatar.
export function iniciais(nome) {
  if (!nome) return '?';
  return nome.trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]).join('').toUpperCase();
}

let contadorToast = 0;
export function toast(mensagem, tipo = 'ok') {
  const raiz = document.getElementById('toasts');
  const id = `toast-${++contadorToast}`;
  const elemento = html(`<div class="toast ${tipo === 'err' ? 'err' : tipo === 'ok' ? 'ok' : ''}" id="${id}">${esc(mensagem)}</div>`);
  raiz.appendChild(elemento);
  setTimeout(() => elemento.remove(), 3800);
}

// Abre um modal com conteúdo (elemento) e retorna função de fechar.
export function modal(conteudo) {
  const raiz = document.getElementById('modal-root');
  const fundo = html('<div class="modal-back"></div>');
  const caixa = html('<div class="card modal"></div>');
  caixa.appendChild(conteudo);
  fundo.appendChild(caixa);
  raiz.appendChild(fundo);
  const fechar = () => fundo.remove();
  fundo.addEventListener('click', (evento) => { if (evento.target === fundo) fechar(); });
  return fechar;
}

// Ativa um conjunto de abas: liga cliques em .tab[data-tab] a painéis [data-panel].
export function ligarTabs(container) {
  const abas = container.querySelectorAll('.tab[data-tab]');
  const paineis = container.querySelectorAll('[data-panel]');
  abas.forEach((aba) => {
    aba.addEventListener('click', () => {
      const alvo = aba.dataset.tab;
      abas.forEach((outra) => outra.classList.toggle('active', outra === aba));
      paineis.forEach((painel) => {
        painel.style.display = painel.dataset.panel === alvo ? '' : 'none';
      });
    });
  });
}

export function loading() {
  return html('<div class="spinner"></div>');
}

export function emptyState(icone, titulo, descricao) {
  return `<div class="empty-state"><div class="es-ico">${icone}</div>
    <h3>${esc(titulo)}</h3><p class="muted">${esc(descricao || '')}</p></div>`;
}
