// Bestiário: lista de monstros/PDMs (SRD global + por mesa), detalhe e CRUD (mestre).
import { api } from '../api.js';
import { getUser } from '../auth.js';
import { montarShell } from '../app.js';
import { emptyState, esc, html, modal, sinal, toast } from '../ui.js';
import { modificador } from '../rules.js';

function lerMesaDaHash() {
  const partes = (location.hash.split('?')[1] || '');
  const params = new URLSearchParams(partes);
  return params.get('mesa');
}

export async function renderBestiary() {
  const view = montarShell('Bestiário', '#/bestiary');
  const usuario = getUser();
  const ehMestre = usuario.role === 'MESTRE' || usuario.role === 'ADMIN';
  const mesaId = lerMesaDaHash();

  async function carregar(busca) {
    const lista = view.querySelector('#lista-monstros');
    lista.innerHTML = '<div class="spinner"></div>';
    try {
      const monstros = await api.bestiary.list({ mesaId, q: busca });
      lista.innerHTML = monstros.length
        ? monstros.map(card).join('')
        : emptyState('🐉', 'Bestiário vazio', 'Nenhuma criatura encontrada.');
      lista.querySelectorAll('[data-mon]').forEach((no) =>
        no.addEventListener('click', () => abrirDetalhe(Number(no.dataset.mon), ehMestre, () => carregar(busca))));
    } catch (erro) { toast(erro.message, 'err'); lista.innerHTML = emptyState('⚠️', 'Erro', erro.message); }
  }

  view.innerHTML = `
    <div class="section-title">
      <h2>Bestiário ${mesaId ? '<span class="badge">da mesa</span>' : '<span class="badge">SRD</span>'}</h2>
      ${ehMestre ? '<button class="btn btn--primary" id="novo">➕ Nova criatura</button>' : ''}
    </div>
    <div class="field"><input class="input" id="busca" placeholder="🔎 Buscar criatura..."></div>
    <div class="grid grid--cards" id="lista-monstros"></div>`;

  let timer = null;
  view.querySelector('#busca').addEventListener('input', (evento) => {
    clearTimeout(timer);
    timer = setTimeout(() => carregar(evento.target.value.trim()), 250);
  });
  const botaoNovo = view.querySelector('#novo');
  if (botaoNovo) botaoNovo.addEventListener('click', () => abrirFormulario(mesaId, () => carregar('')));

  carregar('');
}

function card(monstro) {
  return `<div class="card char-card" data-mon="${monstro.id}">
    <div class="spread">
      <div class="ccard-name">${esc(monstro.nome)}</div>
      ${monstro.is_pdm ? '<span class="chip">PDM</span>' : ''}
    </div>
    <div class="ccard-sub">${esc([monstro.tamanho, monstro.tipo].filter(Boolean).join(' '))}</div>
    <div class="row">
      <span class="badge">ND ${esc(monstro.nd || '—')}</span>
      <span class="chip">CA ${monstro.ca}</span>
      <span class="chip">PV ${monstro.pv}</span>
      ${monstro.global ? '' : '<span class="chip">mesa</span>'}
    </div>
  </div>`;
}

async function abrirDetalhe(id, ehMestre, aoMudar) {
  let monstro;
  try { monstro = await api.bestiary.get(id); } catch (erro) { toast(erro.message, 'err'); return; }
  const atributos = monstro.atributos || {};
  const blocoAttr = Object.entries({ for: 'FOR', des: 'DES', con: 'CON', int: 'INT', sab: 'SAB', car: 'CAR' })
    .map(([chave, rotulo]) => {
      const valor = atributos[chave];
      return valor === undefined ? '' : `<div class="stat-block"><div class="stat-label">${rotulo}</div>
        <div class="stat-mod" style="font-size:1.2rem">${valor}</div>
        <div class="stat-score">${sinal(modificador(valor))}</div></div>`;
    }).join('');
  const habilidades = (monstro.habilidades || []).map((h) => `<p><strong>${esc(h.nome)}.</strong> ${esc(h.descricao)}</p>`).join('');
  const acoes = (monstro.acoes || []).map((a) => `<p><strong>${esc(a.nome)}.</strong> ${esc(a.descricao)}</p>`).join('');

  const conteudo = html(`<div>
    <div class="spread"><h2 style="margin:0">${esc(monstro.nome)}</h2>
      <span class="badge">ND ${esc(monstro.nd || '—')} · ${monstro.xp} XP</span></div>
    <div class="muted">${esc([monstro.tamanho, monstro.tipo, monstro.alinhamento].filter(Boolean).join(', '))}</div>
    <div class="row" style="margin:12px 0">
      <span class="chip">CA ${monstro.ca}</span>
      <span class="chip">PV ${monstro.pv} ${monstro.pv_formula ? `(${esc(monstro.pv_formula)})` : ''}</span>
      <span class="chip">Desloc. ${esc(monstro.deslocamento || '—')}</span>
    </div>
    <div class="stats-row" style="margin:14px 0">${blocoAttr}</div>
    ${monstro.pericias ? `<p><strong>Perícias:</strong> ${esc(monstro.pericias)}</p>` : ''}
    ${monstro.sentidos ? `<p><strong>Sentidos:</strong> ${esc(monstro.sentidos)}</p>` : ''}
    ${monstro.idiomas ? `<p><strong>Idiomas:</strong> ${esc(monstro.idiomas)}</p>` : ''}
    ${habilidades ? `<h4>Habilidades</h4>${habilidades}` : ''}
    ${acoes ? `<h4>Ações</h4>${acoes}` : ''}
    <div class="row" style="justify-content:flex-end; margin-top:14px">
      ${ehMestre ? '<button class="btn btn--gold btn--sm" id="editar">✏️ Editar</button>' : ''}
      ${ehMestre && !monstro.global ? '<button class="btn btn--danger btn--sm" id="excluir">Excluir</button>' : ''}
      <button class="btn btn--ghost" id="fechar">Fechar</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#fechar').addEventListener('click', fechar);
  const botaoEditar = conteudo.querySelector('#editar');
  if (botaoEditar) botaoEditar.addEventListener('click', () => {
    fechar();
    abrirFormulario(monstro.mesa_id, aoMudar, monstro);
  });
  const botaoExcluir = conteudo.querySelector('#excluir');
  if (botaoExcluir) botaoExcluir.addEventListener('click', async () => {
    try { await api.bestiary.remove(id); toast('Criatura removida.'); fechar(); aoMudar(); }
    catch (erro) { toast(erro.message, 'err'); }
  });
}

// Formulário de criação OU edição (quando `existente` é passado).
function abrirFormulario(mesaId, aoMudar, existente = null) {
  const m = existente || {};
  const attr = m.atributos || {};
  const acoesTexto = (m.acoes || []).map((a) => `${a.nome} | ${a.descricao}`).join('\n');
  const habilidadesTexto = (m.habilidades || []).map((h) => `${h.nome} | ${h.descricao}`).join('\n');
  const v = (valor, padrao = '') => esc(valor !== undefined && valor !== null ? valor : padrao);
  const titulo = existente ? `Editar ${esc(m.nome)}` : `Nova criatura ${mesaId ? '(mesa)' : '(SRD global)'}`;

  const conteudo = html(`<div>
    <h3>${titulo}</h3>
    <form id="form-mon">
      <div class="row" style="gap:10px">
        <div class="field" style="flex:2"><label>Nome</label><input class="input" name="nome" value="${v(m.nome)}" required></div>
        <div class="field" style="flex:1"><label>ND</label><input class="input" name="nd" value="${v(m.nd)}" placeholder="1/2"></div>
        <div class="field" style="flex:1"><label>XP</label><input class="input" name="xp" type="number" value="${v(m.xp, 0)}"></div>
      </div>
      <div class="row" style="gap:10px">
        <div class="field" style="flex:1"><label>Tipo</label><input class="input" name="tipo" value="${v(m.tipo)}" placeholder="Humanoide"></div>
        <div class="field" style="flex:1"><label>Tamanho</label><input class="input" name="tamanho" value="${v(m.tamanho)}" placeholder="Médio"></div>
        <div class="field" style="flex:1"><label>Alinhamento</label><input class="input" name="alinhamento" value="${v(m.alinhamento)}"></div>
      </div>
      <div class="row" style="gap:10px">
        <div class="field" style="flex:1"><label>CA</label><input class="input" name="ca" type="number" value="${v(m.ca, 12)}"></div>
        <div class="field" style="flex:1"><label>PV</label><input class="input" name="pv" type="number" value="${v(m.pv, 10)}"></div>
        <div class="field" style="flex:1"><label>Fórmula PV</label><input class="input" name="pv_formula" value="${v(m.pv_formula)}" placeholder="2d8"></div>
        <div class="field" style="flex:1"><label>Deslocamento</label><input class="input" name="deslocamento" value="${v(m.deslocamento)}" placeholder="9 m"></div>
      </div>
      <div class="option-grid">
        ${['for', 'des', 'con', 'int', 'sab', 'car'].map((chave) => `
          <div class="field" style="margin:0"><label>${chave.toUpperCase()}</label>
            <input class="input" name="attr_${chave}" type="number" value="${v(attr[chave], 10)}"></div>`).join('')}
      </div>
      <div class="row" style="gap:10px">
        <div class="field" style="flex:1"><label>Perícias</label><input class="input" name="pericias" value="${v(m.pericias)}"></div>
        <div class="field" style="flex:1"><label>Sentidos</label><input class="input" name="sentidos" value="${v(m.sentidos)}"></div>
        <div class="field" style="flex:1"><label>Idiomas</label><input class="input" name="idiomas" value="${v(m.idiomas)}"></div>
      </div>
      <div class="field"><label>Habilidades (uma por linha: Nome | descrição)</label>
        <textarea class="textarea" name="habilidades" placeholder="Visão no Escuro | enxerga no escuro até 18 m">${esc(habilidadesTexto)}</textarea></div>
      <div class="field"><label>Ações (uma por linha: Nome | descrição)</label>
        <textarea class="textarea" name="acoes" placeholder="Mordida | +4 para acertar, 1d6+2 perfurante">${esc(acoesTexto)}</textarea></div>
      <label class="field-inline"><input type="checkbox" name="is_pdm" ${m.is_pdm ? 'checked' : ''}> É um PDM (NPC)</label>
      <div class="row" style="justify-content:flex-end; margin-top:12px">
        <button class="btn btn--ghost" type="button" id="cancelar">Cancelar</button>
        <button class="btn btn--primary" type="submit">${existente ? 'Salvar' : 'Criar'}</button>
      </div>
    </form></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#form-mon').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const bruto = Object.fromEntries(new FormData(evento.target).entries());
    const parseLinhas = (texto) => (texto || '').split('\n').map((linha) => linha.trim()).filter(Boolean).map((linha) => {
      const [nome, ...resto] = linha.split('|');
      return { nome: nome.trim(), descricao: resto.join('|').trim() };
    });
    const payload = {
      nome: bruto.nome, nd: bruto.nd, xp: Number(bruto.xp) || 0,
      tipo: bruto.tipo, tamanho: bruto.tamanho, alinhamento: bruto.alinhamento,
      ca: Number(bruto.ca), pv: Number(bruto.pv), pv_formula: bruto.pv_formula, deslocamento: bruto.deslocamento,
      pericias: bruto.pericias, sentidos: bruto.sentidos, idiomas: bruto.idiomas,
      atributos: Object.fromEntries(['for', 'des', 'con', 'int', 'sab', 'car'].map((c) => [c, Number(bruto[`attr_${c}`])])),
      habilidades: parseLinhas(bruto.habilidades), acoes: parseLinhas(bruto.acoes),
      is_pdm: bruto.is_pdm === 'on',
    };
    try {
      if (existente) {
        await api.bestiary.update(existente.id, payload);
        toast('Criatura atualizada!');
      } else {
        if (mesaId) payload.mesa_id = Number(mesaId);
        await api.bestiary.create(payload);
        toast('Criatura criada!');
      }
      fechar();
      aoMudar();
    } catch (erro) { toast(erro.message, 'err'); }
  });
}
