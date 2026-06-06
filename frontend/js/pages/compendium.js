// Compêndio: magias, talentos, raças, classes — cards clicáveis com procedência (fonte),
// e CRUD (criar/editar/excluir) para MESTRE/ADMIN. Conteúdo criado é sempre homebrew.
import { api } from '../api.js';
import { getUser } from '../auth.js';
import { montarShell } from '../app.js';
import { emptyState, esc, html, ligarTabs, modal, toast } from '../ui.js';

const TABS = [
  { tipo: 'spells', icone: '📜', titulo: 'Magias' },
  { tipo: 'feats', icone: '⭐', titulo: 'Talentos' },
  { tipo: 'races', icone: '🧬', titulo: 'Raças' },
  { tipo: 'classes', icone: '⚔️', titulo: 'Classes' },
];

function selo(item) {
  if (item.homebrew) return `<span class="chip" title="Conteúdo de usuário">🧪 ${esc(item.fonte || 'Homebrew')}</span>`;
  return `<span class="chip" title="Conteúdo oficial/licenciado">🛡️ ${esc(item.fonte || 'Oficial')}</span>`;
}

function podeEditar() {
  const u = getUser();
  return u && (u.role === 'MESTRE' || u.role === 'ADMIN');
}

async function carregar(tipo) {
  if (tipo === 'spells') return api.reference.spells({});
  if (tipo === 'feats') return api.reference.feats({});
  if (tipo === 'races') return api.reference.races();
  if (tipo === 'classes') return api.reference.classes();
  return [];
}

export async function renderCompendium() {
  const view = montarShell('Compêndio', '#/compendium');
  view.innerHTML = `
    <div class="section-title">
      <h2>Compêndio do SRD <span class="muted" style="font-size:.8rem">· toda informação mostra a fonte</span></h2>
    </div>
    <div class="tabs">
      ${TABS.map((t, i) => `<div class="tab ${i === 0 ? 'active' : ''}" data-tab="${t.tipo}">${t.icone} ${t.titulo}</div>`).join('')}
    </div>
    ${TABS.map((t, i) => `<div data-panel="${t.tipo}" ${i === 0 ? '' : 'style="display:none"'}>
      <div class="row" style="margin-bottom:12px">
        <input class="input" data-busca="${t.tipo}" placeholder="🔎 Buscar ${t.titulo.toLowerCase()}..." style="max-width:280px">
        ${podeEditar() ? `<button class="btn btn--gold btn--sm" data-criar="${t.tipo}">+ Criar (homebrew)</button>` : ''}
      </div>
      <div data-lista="${t.tipo}"><div class="spinner"></div></div>
    </div>`).join('')}`;
  ligarTabs(view);

  for (const t of TABS) {
    const pintarLista = async (filtro = '') => {
      const alvo = view.querySelector(`[data-lista="${t.tipo}"]`);
      alvo.innerHTML = '<div class="spinner"></div>';
      try {
        let itens = await carregar(t.tipo);
        if (filtro) itens = itens.filter((it) => (it.nome || '').toLowerCase().includes(filtro.toLowerCase()));
        alvo.innerHTML = itens.length
          ? `<div class="grid grid--cards">${itens.map((it) => cardGenerico(t, it)).join('')}</div>`
          : emptyState(t.icone, 'Nada encontrado', 'Ajuste a busca ou crie um (homebrew).');
        alvo.querySelectorAll('[data-slug]').forEach((no) => {
          const item = itens.find((x) => x.slug === no.dataset.slug);
          no.addEventListener('click', () => detalhe(t, item, () => pintarLista(filtro)));
        });
      } catch (erro) { toast(erro.message, 'err'); }
    };

    let timer = null;
    view.querySelector(`[data-busca="${t.tipo}"]`).addEventListener('input', (e) => {
      clearTimeout(timer); timer = setTimeout(() => pintarLista(e.target.value.trim()), 250);
    });
    const criar = view.querySelector(`[data-criar="${t.tipo}"]`);
    if (criar) criar.addEventListener('click', () => formulario(t, null, () => pintarLista()));
    pintarLista();
  }
}

function cardGenerico(t, item) {
  const meta = t.tipo === 'spells' ? (item.nivel === 0 ? 'Truque' : 'Nível ' + item.nivel)
    : t.tipo === 'classes' ? `d${item.dado_vida}`
    : t.tipo === 'races' ? (item.tamanho || '')
    : (item.pre_requisito || '');
  return `<div class="card char-card" data-slug="${esc(item.slug)}">
    <div class="spread"><div class="ccard-name" style="font-size:1rem">${esc(item.nome)}</div>
      ${meta ? `<span class="badge">${esc(meta)}</span>` : ''}</div>
    <div style="margin-top:6px">${selo(item)}</div>
  </div>`;
}

function detalhe(t, item, aoMudar) {
  const corpo = corpoDetalhe(t, item);
  const editavel = podeEditar();
  const conteudo = html(`<div>
    <div class="spread"><h2 style="margin:0">${esc(item.nome)}</h2>${selo(item)}</div>
    <div style="margin-top:10px">${corpo}</div>
    <div class="row" style="justify-content:flex-end;margin-top:14px">
      ${editavel ? `<button class="btn btn--gold btn--sm" id="editar">✏️ ${item.homebrew ? 'Editar' : 'Criar variante'}</button>` : ''}
      ${editavel && item.homebrew ? '<button class="btn btn--danger btn--sm" id="excluir">🗑️ Excluir</button>' : ''}
      <button class="btn btn--ghost" id="fechar">Fechar</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#fechar').addEventListener('click', fechar);
  const ed = conteudo.querySelector('#editar');
  if (ed) ed.addEventListener('click', () => { fechar(); formulario(t, item, aoMudar); });
  const ex = conteudo.querySelector('#excluir');
  if (ex) ex.addEventListener('click', async () => {
    try { await api.reference.remove(t.tipo, item.slug); toast('Removido.'); fechar(); aoMudar(); }
    catch (erro) { toast(erro.message, 'err'); }
  });
}

function corpoDetalhe(t, item) {
  if (t.tipo === 'spells') return `<div class="muted">${esc(item.escola || '')}</div>
    <div class="row" style="margin:10px 0"><span class="chip">⏱️ ${esc(item.tempo_conjuracao || '—')}</span>
      <span class="chip">🎯 ${esc(item.alcance || '—')}</span><span class="chip">⌛ ${esc(item.duracao || '—')}</span></div>
    <p style="white-space:pre-wrap">${esc(item.descricao || '')}</p>`;
  if (t.tipo === 'classes') return `<div class="row"><span class="chip">d${item.dado_vida}</span>
    <span class="chip">${item.conjurador ? 'conjurador' : 'marcial'}</span></div>
    <p style="white-space:pre-wrap">${esc(item.descricao || '')}</p>
    <div class="muted">Salvaguardas: ${(item.salvaguardas || []).map((s) => s.toUpperCase()).join(', ') || '—'}</div>`;
  if (t.tipo === 'races') return `<div class="muted">${esc(item.tamanho || '')} · ${item.deslocamento} m</div>
    <p style="white-space:pre-wrap">${esc(item.descricao || '')}</p>
    <div class="muted">Bônus: ${Object.entries(item.bonus_atributos || {}).map(([k, v]) => k.toUpperCase() + ' +' + v).join(', ') || '—'}</div>`;
  return `${item.pre_requisito ? `<div class="muted">Pré-requisito: ${esc(item.pre_requisito)}</div>` : ''}
    <p style="white-space:pre-wrap">${esc(item.descricao || '')}</p>`;
}

// Formulário de criação/edição (homebrew). Campos mínimos por tipo + fonte obrigatória.
function formulario(t, item, aoMudar) {
  const ed = Boolean(item);
  const v = (campo, def = '') => esc(item && item[campo] != null ? item[campo] : def);
  const extra = t.tipo === 'spells'
    ? `<div class="row" style="gap:8px"><div class="field" style="flex:1"><label>Nível</label><input class="input" id="nivel" type="number" value="${v('nivel', 0)}"></div>
       <div class="field" style="flex:2"><label>Escola</label><input class="input" id="escola" value="${v('escola')}"></div></div>`
    : t.tipo === 'classes'
    ? `<div class="field"><label>Dado de vida (d?)</label><input class="input" id="dado_vida" type="number" value="${v('dado_vida', 8)}"></div>`
    : t.tipo === 'races'
    ? `<div class="field"><label>Deslocamento (m)</label><input class="input" id="deslocamento" type="number" value="${v('deslocamento', 9)}"></div>`
    : `<div class="field"><label>Pré-requisito</label><input class="input" id="pre_requisito" value="${v('pre_requisito')}"></div>`;
  const conteudo = html(`<div>
    <h3>${ed ? (item.homebrew ? 'Editar' : 'Criar variante de') + ' ' + esc(item.nome) : 'Novo ' + t.titulo.toLowerCase()} (homebrew)</h3>
    <div class="field"><label>Nome</label><input class="input" id="nome" value="${v('nome')}"></div>
    <div class="field"><label>Slug (identificador único)</label><input class="input" id="slug" value="${ed && item.homebrew ? v('slug') : ''}" placeholder="ex.: minha-magia"></div>
    <div class="field"><label>Fonte (obrigatória)</label><input class="input" id="fonte" value="${ed ? v('fonte') : ''}" placeholder="ex.: Homebrew da Mesa do Micael"></div>
    ${extra}
    <div class="field"><label>Descrição</label><textarea class="textarea" id="descricao">${v('descricao')}</textarea></div>
    <div class="row" style="justify-content:flex-end"><button class="btn btn--ghost" id="x">Cancelar</button><button class="btn btn--primary" id="ok">Salvar</button></div>
  </div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#x').addEventListener('click', fechar);
  conteudo.querySelector('#ok').addEventListener('click', async () => {
    const g = (id) => { const e = conteudo.querySelector('#' + id); return e ? e.value : undefined; };
    const dados = { nome: g('nome'), slug: g('slug'), fonte: g('fonte'), descricao: g('descricao') };
    if (!dados.nome || !dados.fonte) { toast('Nome e Fonte são obrigatórios.', 'err'); return; }
    if (t.tipo === 'spells') { dados.nivel = Number(g('nivel')) || 0; dados.escola = g('escola'); }
    if (t.tipo === 'classes') dados.dado_vida = Number(g('dado_vida')) || 8;
    if (t.tipo === 'races') dados.deslocamento = Number(g('deslocamento')) || 9;
    if (t.tipo === 'feats') dados.pre_requisito = g('pre_requisito');
    try {
      if (ed && item.homebrew) await api.reference.update(t.tipo, item.slug, dados);
      else if (ed) await api.reference.update(t.tipo, item.slug, dados);  // oficial -> backend cria variante
      else { if (!dados.slug) { toast('Informe um slug.', 'err'); return; } await api.reference.create(t.tipo, dados); }
      toast('Salvo!'); fechar(); aoMudar();
    } catch (erro) { toast(erro.message, 'err'); }
  });
}
