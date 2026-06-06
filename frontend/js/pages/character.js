// Ficha de personagem estilo D&D Beyond (leitura + edição inline).
import { api } from '../api.js';
import { navegar } from '../router.js';
import { montarShell } from '../app.js';
import { esc, iniciais, ligarTabs, modal, html, sinal, toast } from '../ui.js';
import { NOMES_ATRIBUTOS, PERICIAS, DESC_ATRIBUTOS, DESC_PERICIAS, DESC_COMBATE } from '../rules.js';

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
          <div class="spread has-tip" style="margin-top:10px" data-tip="${esc(DESC_COMBATE.PassivaPercepcao)}">
            <span class="muted">Percepção Passiva</span>
            <span class="badge">${derivados.percepcao_passiva}</span>
          </div>
        </div>
      </div>

      <div>
        <div class="combat-row card">
          ${combatBox('CA', personagem.ca, DESC_COMBATE.CA)}
          ${combatBox('Iniciativa', sinal(derivados.iniciativa), DESC_COMBATE.Iniciativa)}
          ${combatBox('Deslocamento', esc(personagem.deslocamento || '—'), DESC_COMBATE.Deslocamento)}
          ${combatBox('Proficiência', sinal(derivados.bonus_proficiencia), DESC_COMBATE.Proficiência)}
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
          <div data-panel="ataques">
            ${(derivados.ataques_equipados || []).length ? `<table class="table" style="margin-bottom:10px"><thead><tr><th>Arma</th><th>Acerto</th><th>Dano</th></tr></thead><tbody>
              ${derivados.ataques_equipados.map((a) => `<tr><td>${esc(a.nome)}</td><td>${sinal(a.bonus_acerto)}</td><td>${esc(a.dano || '')} ${esc(a.tipo_dano || '')} ${a.bonus_dano ? '(' + sinal(a.bonus_dano) + ')' : ''}</td></tr>`).join('')}
            </tbody></table>` : ''}
            ${blocoTexto(personagem.ataques, 'Nenhum ataque manual registrado.')}
            ${personagem.atributo_conjuracao ? `<div class="row" style="margin-top:10px">
              <span class="chip">CD de Magia: ${derivados.cd_magia ?? '—'}</span>
              <span class="chip">Ataque de Magia: ${sinal(derivados.bonus_ataque_magia)}</span></div>` : ''}</div>
          <div data-panel="equip" style="display:none">
            <div class="spread"><h4 style="margin:0">Equipamento</h4>
              <button class="btn btn--gold btn--sm" id="gerenciar-equip">⚔️ Gerenciar / criar itens</button></div>
            <div id="resumo-equip" style="margin:10px 0"></div>
            ${blocoTexto(personagem.equipamento, 'Mochila vazia.')}
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
  view.querySelector('#gerenciar-equip').addEventListener('click', () => gerenciarEquipamento(view, personagem));
  renderResumoEquip(view, personagem);
}

function renderResumoEquip(view, personagem) {
  const alvo = view.querySelector('#resumo-equip');
  if (!alvo) return;
  const ataques = personagem.derivados.ataques_equipados || [];
  const temArmadura = personagem.armadura_equipada_id;
  alvo.innerHTML = `
    <div class="row">
      <span class="chip">🛡️ Armadura: ${temArmadura ? 'equipada (CA ' + personagem.derivados.ca + ')' : 'nenhuma (CA ' + personagem.derivados.ca + ')'}</span>
      <span class="chip">⚔️ Armas equipadas: ${ataques.length}</span>
    </div>`;
}

// Modal: lista itens usáveis (global + do personagem), equipa/desequipa e cria novos.
async function gerenciarEquipamento(view, personagem) {
  const conteudo = html(`<div>
    <h3>Equipamento de ${esc(personagem.nome)}</h3>
    <div class="tabs">
      <div class="tab active" data-tab="g-armas">⚔️ Armas</div>
      <div class="tab" data-tab="g-armaduras">🛡️ Armaduras</div>
      <div class="tab" data-tab="g-itens">✨ Itens</div>
    </div>
    <div data-panel="g-armas"><div id="lst-weapons"><div class="spinner"></div></div></div>
    <div data-panel="g-armaduras" style="display:none"><div id="lst-armor"><div class="spinner"></div></div></div>
    <div data-panel="g-itens" style="display:none"><div id="lst-items"><div class="spinner"></div></div></div>
    <div class="row" style="justify-content:flex-end;margin-top:12px"><button class="btn btn--ghost" id="fechar">Fechar</button></div>
  </div>`);
  const fechar = modal(conteudo);
  ligarTabs(conteudo);
  conteudo.querySelector('#fechar').addEventListener('click', () => { fechar(); renderCharacter(personagem.id); });

  const recarregar = async (tipo, containerId, equipavel) => {
    const alvo = conteudo.querySelector(`#${containerId}`);
    const lista = await api.catalog.list(tipo, { personagemId: personagem.id });
    alvo.innerHTML = `
      <button class="btn btn--gold btn--sm" data-criar="${tipo}" style="margin-bottom:8px">+ Criar ${tipo === 'weapons' ? 'arma' : tipo === 'armor' ? 'armadura' : 'item'}</button>
      ${lista.length ? lista.map((it) => `
        <div class="skill-line"><span>${esc(it.nome)} ${it.homebrew ? '<span class="chip">🧪 ' + esc(it.fonte) + '</span>' : '<span class="chip">🛡️ ' + esc(it.fonte) + '</span>'}</span>
          ${equipavel ? `<button class="btn btn--ghost btn--sm" data-equipar="${tipo}:${it.id}" style="margin-left:auto">Equipar</button>` : ''}</div>`).join('') : '<p class="muted">Nada aqui ainda.</p>'}`;
    alvo.querySelectorAll('[data-equipar]').forEach((b) => b.addEventListener('click', async () => {
      const [, id] = b.dataset.equipar.split(':');
      const tipoEquip = tipo === 'weapons' ? 'arma' : 'armadura';
      try { await api.characters.equipar(personagem.id, tipoEquip, Number(id)); toast('Equipado!'); }
      catch (e) { toast(e.message, 'err'); }
    }));
    alvo.querySelectorAll('[data-criar]').forEach((b) => b.addEventListener('click', () => formItem(tipo, personagem, () => recarregar(tipo, containerId, equipavel))));
  };
  recarregar('weapons', 'lst-weapons', true);
  recarregar('armor', 'lst-armor', true);
  recarregar('items', 'lst-items', false);
}

function formItem(tipo, personagem, aoCriar) {
  const ehArma = tipo === 'weapons', ehArmadura = tipo === 'armor';
  const conteudo = html(`<div>
    <h3>Criar ${ehArma ? 'arma' : ehArmadura ? 'armadura' : 'item'}</h3>
    <div class="field"><label>Nome</label><input class="input" id="nome"></div>
    ${ehArma ? `<div class="row" style="gap:8px">
      <div class="field" style="flex:1"><label>Dano</label><input class="input" id="dano" placeholder="1d8"></div>
      <div class="field" style="flex:1"><label>Tipo de dano</label><input class="input" id="tipo_dano" placeholder="cortante"></div></div>` : ''}
    ${ehArmadura ? `<div class="row" style="gap:8px">
      <div class="field" style="flex:1"><label>CA base</label><input class="input" id="ca_base" type="number" value="12"></div>
      <label class="field-inline" style="flex:1"><input type="checkbox" id="ca_soma_des" checked> Soma DES</label></div>` : ''}
    <div class="field"><label>Descrição</label><textarea class="textarea" id="descricao"></textarea></div>
    <p class="muted" style="font-size:.8rem">Será criado como 🧪 Homebrew vinculado a ${esc(personagem.nome)}.</p>
    <div class="row" style="justify-content:flex-end"><button class="btn btn--ghost" id="x">Cancelar</button><button class="btn btn--primary" id="ok">Criar</button></div>
  </div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#x').addEventListener('click', fechar);
  conteudo.querySelector('#ok').addEventListener('click', async () => {
    const g = (id) => { const e = conteudo.querySelector('#' + id); return e ? (e.type === 'checkbox' ? e.checked : e.value) : undefined; };
    const dados = { nome: g('nome'), descricao: g('descricao'), personagem_id: personagem.id };
    if (!dados.nome) { toast('Dê um nome ao item.', 'err'); return; }
    if (ehArma) { dados.dano = g('dano'); dados.tipo_dano = g('tipo_dano'); dados.efeitos = { ataque: { dano: g('dano'), tipo: g('tipo_dano') } }; }
    if (ehArmadura) { dados.ca_base = Number(g('ca_base')); dados.ca_soma_des = g('ca_soma_des'); dados.efeitos = { ca_base: Number(g('ca_base')), ca_soma_des: g('ca_soma_des'), ca_des_max: 2 }; }
    try { await api.catalog.create(tipo, dados); toast('Item criado!'); fechar(); aoCriar(); }
    catch (e) { toast(e.message, 'err'); }
  });
}

function renderStats(personagem, derivados) {
  return Object.keys(NOMES_ATRIBUTOS).map((chave) => {
    const valor = personagem.atributos[chave];
    return `<div class="stat-block has-tip" data-tip="${esc(NOMES_ATRIBUTOS[chave])} — ${esc(DESC_ATRIBUTOS[chave])}">
      <div class="stat-label">${chave.toUpperCase()}</div>
      <div class="stat-mod">${sinal(derivados.modificadores[chave])}</div>
      <div class="stat-score">${valor}</div>
    </div>`;
  }).join('');
}

function renderSaves(derivados) {
  return derivados.salvaguardas.map((salva) => `
    <div class="skill-line has-tip" data-tip="Salvaguarda de ${esc(NOMES_ATRIBUTOS[salva.atributo])}. ${esc(DESC_COMBATE.Salvaguarda)}">
      <span class="dot ${salva.proficiente ? 'on' : ''}"></span>
      <span>${NOMES_ATRIBUTOS[salva.atributo]}</span>
      <span class="sk-val">${sinal(salva.valor)}</span>
    </div>`).join('');
}

function renderSkills(derivados) {
  return derivados.pericias.map((pericia) => `
    <div class="skill-line has-tip" data-tip="${esc(DESC_PERICIAS[pericia.nome] || pericia.nome)}${pericia.proficiente ? ' (proficiente)' : ''}">
      <span class="dot ${pericia.proficiente ? 'on' : ''}"></span>
      <span>${esc(pericia.nome)} <span class="muted">(${pericia.atributo.toUpperCase()})</span></span>
      <span class="sk-val">${sinal(pericia.valor)}</span>
    </div>`).join('');
}

function combatBox(label, valor, dica) {
  const tip = dica ? ` has-tip" data-tip="${esc(dica)}` : '';
  return `<div class="combat-box${tip}"><div class="cb-val">${valor}</div><div class="cb-label">${label}</div></div>`;
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

// --- Edição COMPLETA: todos os campos da ficha são editáveis. ---
function abrirEdicao(view, personagem) {
  const proeficientesPericias = new Set(personagem.pericias_proficientes || []);
  const proeficientesSalva = new Set(personagem.salvaguardas_proficientes || []);

  const campoAttr = Object.entries(NOMES_ATRIBUTOS).map(([chave, nome]) => `
    <div class="field" style="margin-bottom:8px">
      <label>${nome} (${chave.toUpperCase()})</label>
      <input class="input" name="attr_${chave}" type="number" value="${personagem.atributos[chave]}">
    </div>`).join('');

  const togglesSalva = Object.entries(NOMES_ATRIBUTOS).map(([chave, nome]) => `
    <label class="option" style="display:flex;gap:8px;align-items:center;cursor:pointer">
      <input type="checkbox" data-salva="${chave}" ${proeficientesSalva.has(chave) ? 'checked' : ''}>
      <span>${nome}</span></label>`).join('');

  const togglesPericia = Object.keys(PERICIAS).map((nome) => `
    <label class="option" style="display:flex;gap:8px;align-items:center;cursor:pointer">
      <input type="checkbox" data-pericia="${esc(nome)}" ${proeficientesPericias.has(nome) ? 'checked' : ''}>
      <span>${esc(nome)}</span></label>`).join('');

  const texto = (campo, valor) => esc(valor || '');

  const conteudo = html(`<div>
    <h3>Editar ${esc(personagem.nome)}</h3>
    <form id="form-edit">
      <div class="tabs">
        <div class="tab active" data-tab="e-ident">Identidade</div>
        <div class="tab" data-tab="e-attr">Atributos & Combate</div>
        <div class="tab" data-tab="e-prof">Proficiências</div>
        <div class="tab" data-tab="e-magia">Magia & Itens</div>
        <div class="tab" data-tab="e-rp">Roleplay</div>
      </div>

      <div data-panel="e-ident">
        <div class="row" style="gap:10px">
          <div class="field" style="flex:2"><label>Nome</label><input class="input" name="nome" value="${texto('', personagem.nome)}"></div>
          <div class="field" style="flex:1"><label>Nível</label><input class="input" name="nivel" type="number" value="${personagem.nivel}"></div>
          <div class="field" style="flex:1"><label>XP</label><input class="input" name="xp" type="number" value="${personagem.xp}"></div>
        </div>
        <div class="row" style="gap:10px">
          <div class="field" style="flex:1"><label>Nome do Jogador</label><input class="input" name="nome_jogador" value="${texto('', personagem.nome_jogador)}"></div>
          <div class="field" style="flex:1"><label>Tendência</label><input class="input" name="tendencia" value="${texto('', personagem.tendencia)}"></div>
        </div>
        <div class="row" style="gap:10px">
          <div class="field" style="flex:1"><label>Raça</label><input class="input" name="raca_slug" value="${texto('', personagem.raca_slug)}"></div>
          <div class="field" style="flex:1"><label>Classe</label><input class="input" name="classe_slug" value="${texto('', personagem.classe_slug)}"></div>
          <div class="field" style="flex:1"><label>Antecedente</label><input class="input" name="antecedente_slug" value="${texto('', personagem.antecedente_slug)}"></div>
        </div>
        <div class="field"><label>URL do Avatar</label><input class="input" name="avatar_url" value="${texto('', personagem.avatar_url)}"></div>
      </div>

      <div data-panel="e-attr" style="display:none">
        <h4>Atributos</h4>
        <div class="option-grid">${campoAttr}</div>
        <div class="row" style="gap:10px">
          <div class="field" style="flex:1"><label>CA</label><input class="input" name="ca" type="number" value="${personagem.ca}"></div>
          <div class="field" style="flex:1"><label>Bônus Iniciativa</label><input class="input" name="iniciativa_bonus" type="number" value="${personagem.iniciativa_bonus || 0}"></div>
          <div class="field" style="flex:1"><label>Deslocamento</label><input class="input" name="deslocamento" value="${texto('', personagem.deslocamento)}"></div>
        </div>
        <div class="row" style="gap:10px">
          <div class="field" style="flex:1"><label>PV Máx</label><input class="input" name="pv_max" type="number" value="${personagem.pv_max}"></div>
          <div class="field" style="flex:1"><label>PV Atual</label><input class="input" name="pv_atual" type="number" value="${personagem.pv_atual}"></div>
          <div class="field" style="flex:1"><label>PV Temp</label><input class="input" name="pv_temp" type="number" value="${personagem.pv_temp || 0}"></div>
          <div class="field" style="flex:1"><label>Dado de Vida</label><input class="input" name="dado_vida" value="${texto('', personagem.dado_vida)}"></div>
        </div>
        <label class="field-inline"><input type="checkbox" name="inspiracao" ${personagem.inspiracao ? 'checked' : ''}> Inspiração</label>
      </div>

      <div data-panel="e-prof" style="display:none">
        <h4>Salvaguardas proficientes</h4>
        <div class="option-grid">${togglesSalva}</div>
        <h4 style="margin-top:14px">Perícias proficientes</h4>
        <div class="option-grid">${togglesPericia}</div>
        <div class="field" style="margin-top:12px"><label>Outras Proficiências</label><textarea class="textarea" name="outras_proficiencias">${texto('', personagem.outras_proficiencias)}</textarea></div>
      </div>

      <div data-panel="e-magia" style="display:none">
        <div class="row" style="gap:10px">
          <div class="field" style="flex:2"><label>Classe Conjuradora</label><input class="input" name="classe_conjuradora" value="${texto('', personagem.classe_conjuradora)}"></div>
          <div class="field" style="flex:1"><label>Atributo de Conjuração (for/des/...)</label><input class="input" name="atributo_conjuracao" value="${texto('', personagem.atributo_conjuracao)}"></div>
        </div>
        <div class="field"><label>Ataques & Magias</label><textarea class="textarea" name="ataques">${texto('', personagem.ataques)}</textarea></div>
        <div class="field"><label>Equipamento & Inventário</label><textarea class="textarea" name="equipamento">${texto('', personagem.equipamento)}</textarea></div>
        <div class="field"><label>Dinheiro</label><input class="input" name="dinheiro" value="${texto('', personagem.dinheiro)}"></div>
      </div>

      <div data-panel="e-rp" style="display:none">
        <div class="field"><label>Traços de Personalidade</label><textarea class="textarea" name="tracos_personalidade">${texto('', personagem.tracos_personalidade)}</textarea></div>
        <div class="row" style="gap:10px">
          <div class="field" style="flex:1"><label>Ideais</label><textarea class="textarea" name="ideais">${texto('', personagem.ideais)}</textarea></div>
          <div class="field" style="flex:1"><label>Vínculos</label><textarea class="textarea" name="vinculos">${texto('', personagem.vinculos)}</textarea></div>
          <div class="field" style="flex:1"><label>Fraquezas</label><textarea class="textarea" name="fraquezas">${texto('', personagem.fraquezas)}</textarea></div>
        </div>
        <div class="field"><label>Características e Talentos</label><textarea class="textarea" name="caracteristicas">${texto('', personagem.caracteristicas)}</textarea></div>
        <div class="field"><label>Idiomas</label><textarea class="textarea" name="idiomas">${texto('', personagem.idiomas)}</textarea></div>
        <div class="field"><label>História</label><textarea class="textarea" name="historia">${texto('', personagem.historia)}</textarea></div>
      </div>

      <div class="row" style="justify-content:flex-end; margin-top:14px">
        <button class="btn btn--ghost" type="button" id="cancelar">Cancelar</button>
        <button class="btn btn--primary" type="submit">Salvar</button>
      </div>
    </form></div>`);
  const fechar = modal(conteudo);
  ligarTabs(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#form-edit').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const form = evento.target;
    const bruto = Object.fromEntries(new FormData(form).entries());
    const atributos = {};
    Object.keys(NOMES_ATRIBUTOS).forEach((chave) => { atributos[chave] = Number(bruto[`attr_${chave}`]); });
    const pericias = Array.from(form.querySelectorAll('[data-pericia]:checked')).map((c) => c.dataset.pericia);
    const salvaguardas = Array.from(form.querySelectorAll('[data-salva]:checked')).map((c) => c.dataset.salva);

    const payload = {
      nome: bruto.nome, nivel: Number(bruto.nivel), xp: Number(bruto.xp),
      nome_jogador: bruto.nome_jogador, tendencia: bruto.tendencia,
      raca_slug: bruto.raca_slug, classe_slug: bruto.classe_slug, antecedente_slug: bruto.antecedente_slug,
      avatar_url: bruto.avatar_url,
      ca: Number(bruto.ca), iniciativa_bonus: Number(bruto.iniciativa_bonus),
      deslocamento: bruto.deslocamento,
      pv_max: Number(bruto.pv_max), pv_atual: Number(bruto.pv_atual), pv_temp: Number(bruto.pv_temp),
      dado_vida: bruto.dado_vida, inspiracao: form.querySelector('[name=inspiracao]').checked,
      pericias_proficientes: pericias, salvaguardas_proficientes: salvaguardas,
      outras_proficiencias: bruto.outras_proficiencias,
      classe_conjuradora: bruto.classe_conjuradora, atributo_conjuracao: bruto.atributo_conjuracao || null,
      ataques: bruto.ataques, equipamento: bruto.equipamento, dinheiro: bruto.dinheiro,
      tracos_personalidade: bruto.tracos_personalidade, ideais: bruto.ideais, vinculos: bruto.vinculos,
      fraquezas: bruto.fraquezas, caracteristicas: bruto.caracteristicas, idiomas: bruto.idiomas,
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
