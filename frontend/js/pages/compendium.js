// Compêndio: referência de magias, raças e classes (somente leitura).
import { api } from '../api.js';
import { montarShell } from '../app.js';
import { emptyState, esc, html, ligarTabs, modal, toast } from '../ui.js';

export async function renderCompendium() {
  const view = montarShell('Compêndio', '#/compendium');
  view.innerHTML = `
    <h2>Compêndio do SRD</h2>
    <div class="tabs">
      <div class="tab active" data-tab="magias">📜 Magias</div>
      <div class="tab" data-tab="racas">🧬 Raças</div>
      <div class="tab" data-tab="classes">⚔️ Classes</div>
    </div>
    <div data-panel="magias">
      <div class="row" style="margin-bottom:12px">
        <input class="input" id="busca-magia" placeholder="🔎 Buscar magia..." style="max-width:280px">
        <select class="select" id="filtro-nivel" style="max-width:160px">
          <option value="">Todos os níveis</option>
          ${Array.from({ length: 10 }, (_, n) => `<option value="${n}">${n === 0 ? 'Truque' : 'Nível ' + n}</option>`).join('')}
        </select>
      </div>
      <div id="lista-magias"><div class="spinner"></div></div>
    </div>
    <div data-panel="racas" style="display:none"><div id="lista-racas"><div class="spinner"></div></div></div>
    <div data-panel="classes" style="display:none"><div id="lista-classes"><div class="spinner"></div></div></div>`;
  ligarTabs(view);

  async function carregarMagias() {
    const alvo = view.querySelector('#lista-magias');
    const nivel = view.querySelector('#filtro-nivel').value;
    const busca = view.querySelector('#busca-magia').value.trim();
    alvo.innerHTML = '<div class="spinner"></div>';
    try {
      const magias = await api.reference.spells({ nivel, q: busca });
      alvo.innerHTML = magias.length ? `<div class="grid grid--cards">${magias.map(cardMagia).join('')}</div>`
        : emptyState('📜', 'Nada encontrado', 'Ajuste os filtros.');
      alvo.querySelectorAll('[data-magia]').forEach((no, indice) =>
        no.addEventListener('click', () => detalheMagia(magias[indice])));
    } catch (erro) { toast(erro.message, 'err'); }
  }

  let timer = null;
  view.querySelector('#busca-magia').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(carregarMagias, 250); });
  view.querySelector('#filtro-nivel').addEventListener('change', carregarMagias);
  carregarMagias();

  try {
    const racas = await api.reference.races();
    view.querySelector('#lista-racas').innerHTML = `<div class="grid grid--cards">${racas.map((raca) => `
      <div class="card"><h3>${esc(raca.nome)}</h3>
        <div class="muted">${esc(raca.tamanho || '')} · ${raca.deslocamento} m</div>
        <p style="font-size:.88rem">${esc(raca.descricao || '')}</p>
        ${(raca.subracas || []).length ? `<div>${raca.subracas.map((s) => `<span class="chip">${esc(s.nome)}</span>`).join('')}</div>` : ''}
      </div>`).join('')}</div>`;
  } catch (_) { /* aba carregada sob demanda */ }

  try {
    const classes = await api.reference.classes();
    view.querySelector('#lista-classes').innerHTML = `<div class="grid grid--cards">${classes.map((classe) => `
      <div class="card"><h3>${esc(classe.nome)}</h3>
        <div class="row"><span class="chip">d${classe.dado_vida}</span>
          ${classe.conjurador ? '<span class="chip">conjurador</span>' : '<span class="chip">marcial</span>'}</div>
        <p style="font-size:.88rem">${esc(classe.descricao || '')}</p>
        <div class="muted" style="font-size:.82rem">Salvaguardas: ${(classe.salvaguardas || []).map((s) => s.toUpperCase()).join(', ')}</div>
      </div>`).join('')}</div>`;
  } catch (_) { /* idem */ }
}

function cardMagia(magia) {
  return `<div class="card char-card" data-magia="${magia.slug}">
    <div class="spread"><div class="ccard-name" style="font-size:1rem">${esc(magia.nome)}</div>
      <span class="badge">${magia.nivel === 0 ? 'Truque' : 'Nv ' + magia.nivel}</span></div>
    <div class="ccard-sub">${esc(magia.escola || '')} ${magia.concentracao ? '· conc.' : ''} ${magia.ritual ? '· ritual' : ''}</div>
    <div class="muted" style="font-size:.78rem">${(magia.classes || []).join(', ')}</div>
  </div>`;
}

function detalheMagia(magia) {
  const conteudo = html(`<div>
    <div class="spread"><h2 style="margin:0">${esc(magia.nome)}</h2>
      <span class="badge">${magia.nivel === 0 ? 'Truque' : 'Nível ' + magia.nivel}</span></div>
    <div class="muted">${esc(magia.escola || '')}</div>
    <div class="row" style="margin:12px 0">
      <span class="chip">⏱️ ${esc(magia.tempo_conjuracao || '—')}</span>
      <span class="chip">🎯 ${esc(magia.alcance || '—')}</span>
      <span class="chip">🧩 ${esc(magia.componentes || '—')}</span>
      <span class="chip">⌛ ${esc(magia.duracao || '—')}</span>
    </div>
    <p style="white-space:pre-wrap">${esc(magia.descricao || '')}</p>
    <div>${(magia.classes || []).map((c) => `<span class="chip">${esc(c)}</span>`).join('')}</div>
    <div class="row" style="justify-content:flex-end; margin-top:12px">
      <button class="btn btn--ghost" id="fechar">Fechar</button></div>
  </div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#fechar').addEventListener('click', fechar);
}
