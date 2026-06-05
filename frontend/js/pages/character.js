// Ficha de personagem estilo D&D Beyond (leitura + edição inline).
import { api } from '../api.js';
import { navegar } from '../router.js';
import { montarShell } from '../app.js';
import { esc, iniciais, ligarTabs, modal, html, sinal, toast } from '../ui.js';
import { NOMES_ATRIBUTOS } from '../rules.js';

const COLUNA_ATRIBUTO = {
  for: 'forca', des: 'destreza', con: 'constituicao',
  int: 'inteligencia', sab: 'sabedoria', car: 'carisma',
};

export async function renderCharacter(id) {
  const view = montarShell('Ficha', '#/dashboard');
  let personagem;
  try {
    personagem = await api.characters.get(id);
  } catch (erro) {
    toast(erro.message, 'err');
    navegar('#/dashboard');
    return;
  }
  pintarFicha(view, personagem);
}

function pintarFicha(view, personagem) {
  const derivados = personagem.derivados;
  const pvPercentual = personagem.pv_max ? Math.max(0, Math.min(100, Math.round(100 * personagem.pv_atual / personagem.pv_max))) : 0;

  view.innerHTML = `
    <div class="spread" style="margin-bottom:16px">
      <button class="btn btn--ghost btn--sm" id="voltar">← Voltar</button>
      <div class="row">
        <button class="btn btn--gold btn--sm" id="editar">✏️ Editar</button>
        <button class="btn btn--danger btn--sm" id="apagar">🗑️ Excluir</button>
      </div>
    </div>

    <div class="card card--parch">
      <div class="sheet-head">
        <span class="sheet-portrait">${iniciais(personagem.nome)}</span>
        <div style="flex:1">
          <div class="sh-name" style="font-family:var(--font-title)">${esc(personagem.nome)}</div>
          <div>${esc([personagem.raca_slug, personagem.classe_slug, personagem.antecedente_slug].filter(Boolean).join(' · ') || 'Aventureiro')}</div>
          <div class="muted">${esc(personagem.tendencia || '')} ${personagem.nome_jogador ? '· Jogador: ' + esc(personagem.nome_jogador) : ''}</div>
        </div>
        <div style="text-align:center">
          <div class="badge" style="font-size:1rem">Nível ${personagem.nivel}</div>
          <div class="muted" style="margin-top:6px">${personagem.xp} XP</div>
        </div>
      </div>
    </div>

    <div class="sheet-grid" style="margin-top:18px">
      <div>
        <div class="card" style="margin-bottom:16px">
          <div class="stats-row">${renderStats(personagem, derivados)}</div>
        </div>
        <div class="card" style="margin-bottom:16px">
          <h4>Salvaguardas</h4>
          <div class="save-list">${renderSaves(derivados)}</div>
        </div>
        <div class="card">
          <h4>Perícias</h4>
          <div class="skill-list">${renderSkills(derivados)}</div>
          <div class="spread" style="margin-top:10px">
            <span class="muted">Percepção Passiva</span>
            <span class="badge">${derivados.percepcao_passiva}</span>
          </div>
        </div>
      </div>

      <div>
        <div class="combat-row card">
          ${combatBox('CA', personagem.ca)}
          ${combatBox('Iniciativa', sinal(derivados.iniciativa))}
          ${combatBox('Deslocamento', esc(personagem.deslocamento || '—'))}
          ${combatBox('Proficiência', sinal(derivados.bonus_proficiencia))}
        </div>

        <div class="card" style="margin-bottom:16px">
          <div class="spread"><h4 style="margin:0">Pontos de Vida</h4>
            <span class="muted">${personagem.pv_atual} / ${personagem.pv_max} ${personagem.pv_temp ? `(+${personagem.pv_temp} temp)` : ''}</span></div>
          <div class="pv-bar" style="margin:10px 0"><span style="width:${pvPercentual}%"></span></div>
          <div class="row">
            <input class="input" id="pv-delta" type="number" placeholder="valor" style="max-width:120px">
            <button class="btn btn--danger btn--sm" id="pv-dano">− Dano</button>
            <button class="btn btn--ghost btn--sm" id="pv-cura">+ Cura</button>
            <span class="chip">${personagem.dado_vida || ''}</span>
            ${personagem.inspiracao ? '<span class="badge">✨ Inspiração</span>' : ''}
          </div>
        </div>

        <div class="card">
          <div class="tabs">
            <div class="tab active" data-tab="ataques">Ataques & Magias</div>
            <div class="tab" data-tab="equip">Equipamento</div>
            <div class="tab" data-tab="tracos">Traços</div>
            <div class="tab" data-tab="historia">História</div>
          </div>
          <div data-panel="ataques">${blocoTexto(personagem.ataques, 'Nenhum ataque ou magia registrado.')}
            ${personagem.atributo_conjuracao ? `<div class="row" style="margin-top:10px">
              <span class="chip">CD de Magia: ${derivados.cd_magia ?? '—'}</span>
              <span class="chip">Ataque de Magia: ${sinal(derivados.bonus_ataque_magia)}</span></div>` : ''}</div>
          <div data-panel="equip" style="display:none">${blocoTexto(personagem.equipamento, 'Mochila vazia.')}
            ${personagem.dinheiro ? `<div class="chip" style="margin-top:8px">💰 ${esc(personagem.dinheiro)}</div>` : ''}</div>
          <div data-panel="tracos" style="display:none">
            ${campo('Traços de Personalidade', personagem.tracos_personalidade)}
            ${campo('Ideais', personagem.ideais)}
            ${campo('Vínculos', personagem.vinculos)}
            ${campo('Fraquezas', personagem.fraquezas)}
            ${campo('Características e Talentos', personagem.caracteristicas)}
            ${campo('Idiomas e Proficiências', personagem.idiomas || personagem.outras_proficiencias)}
          </div>
          <div data-panel="historia" style="display:none">${blocoTexto(personagem.historia, 'História ainda não escrita.')}</div>
        </div>
      </div>
    </div>`;

  ligarTabs(view);
  view.querySelector('#voltar').addEventListener('click', () => navegar('#/dashboard'));
  view.querySelector('#editar').addEventListener('click', () => abrirEdicao(view, personagem));
  view.querySelector('#apagar').addEventListener('click', () => confirmarExclusao(personagem));
  view.querySelector('#pv-dano').addEventListener('click', () => ajustarPV(view, personagem, -1));
  view.querySelector('#pv-cura').addEventListener('click', () => ajustarPV(view, personagem, +1));
}

function renderStats(personagem, derivados) {
  return Object.keys(NOMES_ATRIBUTOS).map((chave) => {
    const valor = personagem.atributos[chave];
    return `<div class="stat-block">
      <div class="stat-label">${chave.toUpperCase()}</div>
      <div class="stat-mod">${sinal(derivados.modificadores[chave])}</div>
      <div class="stat-score">${valor}</div>
    </div>`;
  }).join('');
}

function renderSaves(derivados) {
  return derivados.salvaguardas.map((salva) => `
    <div class="skill-line">
      <span class="dot ${salva.proficiente ? 'on' : ''}"></span>
      <span>${NOMES_ATRIBUTOS[salva.atributo]}</span>
      <span class="sk-val">${sinal(salva.valor)}</span>
    </div>`).join('');
}

function renderSkills(derivados) {
  return derivados.pericias.map((pericia) => `
    <div class="skill-line">
      <span class="dot ${pericia.proficiente ? 'on' : ''}"></span>
      <span>${esc(pericia.nome)} <span class="muted">(${pericia.atributo.toUpperCase()})</span></span>
      <span class="sk-val">${sinal(pericia.valor)}</span>
    </div>`).join('');
}

function combatBox(label, valor) {
  return `<div class="combat-box"><div class="cb-val">${valor}</div><div class="cb-label">${label}</div></div>`;
}

function blocoTexto(texto, vazio) {
  if (!texto) return `<p class="muted">${esc(vazio)}</p>`;
  return `<p style="white-space:pre-wrap">${esc(texto)}</p>`;
}

function campo(rotulo, valor) {
  if (!valor) return '';
  return `<div style="margin-bottom:10px"><strong>${esc(rotulo)}:</strong><div style="white-space:pre-wrap">${esc(valor)}</div></div>`;
}

async function ajustarPV(view, personagem, sentido) {
  const campoDelta = view.querySelector('#pv-delta');
  const delta = parseInt(campoDelta.value, 10);
  if (!delta) return;
  const novo = Math.max(0, Math.min(personagem.pv_max, personagem.pv_atual + sentido * Math.abs(delta)));
  try {
    const atualizado = await api.characters.update(personagem.id, { pv_atual: novo });
    toast(sentido > 0 ? `+${Math.abs(delta)} PV` : `−${Math.abs(delta)} PV`);
    pintarFicha(view, atualizado);
  } catch (erro) { toast(erro.message, 'err'); }
}

function confirmarExclusao(personagem) {
  const conteudo = html(`<div>
    <h3>Excluir ${esc(personagem.nome)}?</h3>
    <p class="muted">Esta ação não pode ser desfeita.</p>
    <div class="row" style="justify-content:flex-end">
      <button class="btn btn--ghost" id="cancelar">Cancelar</button>
      <button class="btn btn--primary" id="confirmar">Excluir</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#confirmar').addEventListener('click', async () => {
    try {
      await api.characters.remove(personagem.id);
      toast('Personagem excluído.');
      fechar();
      navegar('#/dashboard');
    } catch (erro) { toast(erro.message, 'err'); }
  });
}

// --- Edição: formulário em modal com os campos principais e atributos. ---
function abrirEdicao(view, personagem) {
  const atributosCampos = Object.entries(NOMES_ATRIBUTOS).map(([chave, nome]) => `
    <div class="field" style="margin-bottom:8px">
      <label>${nome} (${chave.toUpperCase()})</label>
      <input class="input" name="attr_${chave}" type="number" value="${personagem.atributos[chave]}">
    </div>`).join('');

  const conteudo = html(`<div>
    <h3>Editar ${esc(personagem.nome)}</h3>
    <form id="form-edit">
      <div class="row" style="gap:10px">
        <div class="field" style="flex:2"><label>Nome</label><input class="input" name="nome" value="${esc(personagem.nome)}"></div>
        <div class="field" style="flex:1"><label>Nível</label><input class="input" name="nivel" type="number" value="${personagem.nivel}"></div>
        <div class="field" style="flex:1"><label>XP</label><input class="input" name="xp" type="number" value="${personagem.xp}"></div>
      </div>
      <div class="row" style="gap:10px">
        <div class="field" style="flex:1"><label>Raça</label><input class="input" name="raca_slug" value="${esc(personagem.raca_slug || '')}"></div>
        <div class="field" style="flex:1"><label>Classe</label><input class="input" name="classe_slug" value="${esc(personagem.classe_slug || '')}"></div>
        <div class="field" style="flex:1"><label>Tendência</label><input class="input" name="tendencia" value="${esc(personagem.tendencia || '')}"></div>
      </div>
      <div class="row" style="gap:10px">
        <div class="field" style="flex:1"><label>CA</label><input class="input" name="ca" type="number" value="${personagem.ca}"></div>
        <div class="field" style="flex:1"><label>PV Máx</label><input class="input" name="pv_max" type="number" value="${personagem.pv_max}"></div>
        <div class="field" style="flex:1"><label>PV Atual</label><input class="input" name="pv_atual" type="number" value="${personagem.pv_atual}"></div>
        <div class="field" style="flex:1"><label>Deslocamento</label><input class="input" name="deslocamento" value="${esc(personagem.deslocamento || '')}"></div>
      </div>
      <h4>Atributos</h4>
      <div class="option-grid">${atributosCampos}</div>
      <div class="field"><label>Ataques & Magias</label><textarea class="textarea" name="ataques">${esc(personagem.ataques || '')}</textarea></div>
      <div class="field"><label>Equipamento</label><textarea class="textarea" name="equipamento">${esc(personagem.equipamento || '')}</textarea></div>
      <div class="field"><label>História</label><textarea class="textarea" name="historia">${esc(personagem.historia || '')}</textarea></div>
      <div class="row" style="justify-content:flex-end">
        <button class="btn btn--ghost" type="button" id="cancelar">Cancelar</button>
        <button class="btn btn--primary" type="submit">Salvar</button>
      </div>
    </form></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#form-edit').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const bruto = Object.fromEntries(new FormData(evento.target).entries());
    const atributos = {};
    Object.keys(NOMES_ATRIBUTOS).forEach((chave) => { atributos[chave] = Number(bruto[`attr_${chave}`]); });
    const payload = {
      nome: bruto.nome, nivel: Number(bruto.nivel), xp: Number(bruto.xp),
      raca_slug: bruto.raca_slug, classe_slug: bruto.classe_slug, tendencia: bruto.tendencia,
      ca: Number(bruto.ca), pv_max: Number(bruto.pv_max), pv_atual: Number(bruto.pv_atual),
      deslocamento: bruto.deslocamento, ataques: bruto.ataques, equipamento: bruto.equipamento,
      historia: bruto.historia, atributos,
    };
    try {
      const atualizado = await api.characters.update(personagem.id, payload);
      toast('Ficha salva!');
      fechar();
      pintarFicha(view, atualizado);
    } catch (erro) { toast(erro.message, 'err'); }
  });
}
