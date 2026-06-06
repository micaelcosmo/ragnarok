// Wizard de criação de personagem (5 passos) com preview de modificadores.
import { api } from '../api.js';
import { navegar } from '../router.js';
import { montarShell } from '../app.js';
import { esc, toast } from '../ui.js';
import { NOMES_ATRIBUTOS, modificador } from '../rules.js';

const PASSOS = ['Raça', 'Classe', 'Antecedente', 'Atributos', 'Perícias', 'Talentos'];

export async function renderCharacterNew() {
  const view = montarShell('Novo Herói', '#/characters/new');
  view.innerHTML = '<div class="spinner"></div>';

  let racas = [], classes = [], antecedentes = [], talentos = [];
  try {
    [racas, classes, antecedentes, talentos] = await Promise.all([
      api.reference.races(), api.reference.classes(), api.reference.backgrounds(), api.reference.feats(),
    ]);
  } catch (erro) {
    toast('Não foi possível carregar o catálogo: ' + erro.message, 'err');
  }

  const estado = {
    passo: 0,
    nome: '', tendencia: '',
    raca: null, classe: null, antecedente: null,
    atributos: { for: 10, des: 10, con: 10, int: 10, sab: 10, car: 10 },
    pericias: new Set(),
    talentos: new Set(),
  };

  function classeAtual() { return classes.find((classe) => classe.slug === estado.classe); }
  function racaAtual() { return racas.find((raca) => raca.slug === estado.raca); }
  function antecedenteAtual() { return antecedentes.find((a) => a.slug === estado.antecedente); }

  // Preview ao vivo dos bônus que as escolhas concedem (lido dos `efeitos` do catálogo).
  function previewBonus() {
    const linhas = [];
    const raca = racaAtual();
    if (raca) {
      const attr = (raca.efeitos && raca.efeitos.atributos) || raca.bonus_atributos || {};
      const txt = Object.entries(attr).map(([k, v]) => `${k.toUpperCase()} +${v}`).join(', ');
      if (txt) linhas.push(`🧬 <b>${esc(raca.nome)}</b>: ${esc(txt)}`);
    }
    const ant = antecedenteAtual();
    if (ant && (ant.pericias || []).length) linhas.push(`📜 <b>${esc(ant.nome)}</b>: perícias ${esc(ant.pericias.join(', '))}`);
    const classe = classeAtual();
    if (classe && (classe.salvaguardas || []).length) linhas.push(`⚔️ <b>${esc(classe.nome)}</b>: salvaguardas ${esc(classe.salvaguardas.map((s) => s.toUpperCase()).join(', '))}`);
    estado.talentos.forEach((slug) => {
      const t = talentos.find((x) => x.slug === slug);
      const ef = (t && t.efeitos) || {};
      const partes = [];
      if (ef.iniciativa) partes.push(`iniciativa +${ef.iniciativa}`);
      if (ef.atributos) partes.push(Object.entries(ef.atributos).map(([k, v]) => `${k.toUpperCase()} +${v}`).join(', '));
      if (t) linhas.push(`⭐ <b>${esc(t.nome)}</b>${partes.length ? ': ' + esc(partes.join(', ')) : ''}`);
    });
    if (!linhas.length) return '';
    return `<div class="card" style="margin-top:14px"><div class="muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.5px;color:var(--gold)">Bônus que serão aplicados</div>${linhas.map((l) => `<div style="margin-top:4px">${l}</div>`).join('')}</div>`;
  }

  function pintar() {
    view.innerHTML = `
      <div class="spread" style="margin-bottom:14px">
        <h2>Forjar Personagem</h2>
        <button class="btn btn--ghost btn--sm" id="cancelar">Cancelar</button>
      </div>
      <div class="wizard-steps">
        ${PASSOS.map((passo, indice) => `<div class="wstep ${indice === estado.passo ? 'active' : ''} ${indice < estado.passo ? 'done' : ''}">${indice + 1}. ${passo}</div>`).join('')}
      </div>
      <div class="card" id="passo-conteudo">${conteudoPasso()}</div>
      <div class="row" style="justify-content:space-between; margin-top:16px">
        <button class="btn btn--ghost" id="anterior" ${estado.passo === 0 ? 'disabled' : ''}>← Anterior</button>
        <button class="btn btn--primary" id="proximo">${estado.passo === PASSOS.length - 1 ? '⚔️ Criar Personagem' : 'Próximo →'}</button>
      </div>`;

    ligarEventosPasso();
    view.querySelector('#cancelar').addEventListener('click', () => navegar('#/dashboard'));
    view.querySelector('#anterior').addEventListener('click', () => { if (estado.passo > 0) { estado.passo--; pintar(); } });
    view.querySelector('#proximo').addEventListener('click', avancar);
  }

  function conteudoPasso() {
    switch (estado.passo) {
      case 0: return passoSelecao('raca', racas, 'deslocamento', 'm de deslocamento');
      case 1: return passoSelecao('classe', classes, 'dado_vida', 'd de vida', (item) => `d${item.dado_vida} · ${item.conjurador ? 'conjurador' : 'marcial'}`);
      case 2: return passoSelecao('antecedente', antecedentes, null, '');
      case 3: return passoAtributos() + previewBonus();
      case 4: return passoPericias() + previewBonus();
      case 5: return passoTalentos() + previewBonus();
      default: return '';
    }
  }

  function passoTalentos() {
    const opcoes = talentos.map((t) => `
      <div class="option ${estado.talentos.has(t.slug) ? 'selected' : ''}" data-talento="${esc(t.slug)}">
        <div class="opt-name" style="font-size:.95rem">${esc(t.nome)}</div>
        <div class="opt-meta">${esc(t.fonte || '')}${t.pre_requisito ? ' · ' + esc(t.pre_requisito) : ''}</div>
      </div>`).join('');
    return `<h3>Talentos (opcional)</h3>
      <p class="muted">Escolha talentos — os efeitos (atributos, iniciativa, etc.) entram na ficha
      automaticamente e podem ser removidos depois.</p>
      <div class="option-grid" style="margin-top:12px">${opcoes || '<p class="muted">Nenhum talento no catálogo.</p>'}</div>`;
  }

  function passoSelecao(tipo, lista, _campo, _sufixo, metaFn) {
    const idCampo = tipo === 'raca' ? 'campo-nome' : null;
    const opcoes = lista.map((item) => `
      <div class="option ${estado[tipo] === item.slug ? 'selected' : ''}" data-slug="${item.slug}">
        <div class="opt-name">${esc(item.nome)}</div>
        <div class="opt-meta">${esc(metaFn ? metaFn(item) : (item.tamanho || ''))}</div>
      </div>`).join('');
    const cabecalho = tipo === 'raca' ? `
      <div class="row" style="gap:10px; margin-bottom:14px">
        <div class="field" style="flex:2; margin:0"><label>Nome do personagem</label>
          <input class="input" id="campo-nome" value="${esc(estado.nome)}" placeholder="Ex.: Thorin"></div>
        <div class="field" style="flex:1; margin:0"><label>Tendência</label>
          <input class="input" id="campo-tendencia" value="${esc(estado.tendencia)}" placeholder="Ex.: Leal e Bom"></div>
      </div>` : '';
    const descricao = estado[tipo] ? `<p class="muted" style="margin-top:14px">${esc((lista.find((i) => i.slug === estado[tipo]) || {}).descricao || '')}</p>` : '';
    return `<h3>Escolha: ${PASSOS[estado.passo]}</h3>${cabecalho}
      <div class="option-grid">${opcoes || '<p class="muted">Catálogo indisponível.</p>'}</div>${descricao}`;
  }

  function passoAtributos() {
    const linhas = Object.entries(NOMES_ATRIBUTOS).map(([chave, nome]) => `
      <div class="stat-block" style="padding-bottom:22px">
        <div class="stat-label">${nome}</div>
        <input class="input stat-score-input" data-attr="${chave}" type="number" min="1" max="30" value="${estado.atributos[chave]}">
        <div class="stat-score" id="mod-${chave}">${fmtMod(estado.atributos[chave])}</div>
      </div>`).join('');
    return `<h3>Distribua os Atributos (base)</h3>
      <p class="muted">Digite os valores <b>base</b> (point-buy, rolagem ou array 15,14,13,12,10,8).
      Os bônus de raça/talento são somados <b>automaticamente</b> na ficha (veja abaixo).</p>
      <div class="stats-row" style="margin-top:18px">${linhas}</div>`;
  }

  function passoPericias() {
    const classe = classeAtual();
    const disponiveis = (classe && classe.pericias_disponiveis) || Object.keys({
      Acrobacia: 1, Atletismo: 1, Furtividade: 1, Percepção: 1, Persuasão: 1, Intuição: 1, Arcanismo: 1, História: 1,
    });
    const limite = (classe && classe.num_pericias) || 2;
    const opcoes = disponiveis.map((nome) => `
      <div class="option ${estado.pericias.has(nome) ? 'selected' : ''}" data-pericia="${esc(nome)}">
        <div class="opt-name" style="font-size:.95rem">${esc(nome)}</div>
      </div>`).join('');
    const salvaguardas = (classe && classe.salvaguardas || []).map((s) => NOMES_ATRIBUTOS[s] || s).join(', ');
    return `<h3>Perícias & Proficiências</h3>
      <p class="muted">Escolha até <strong>${limite}</strong> perícias da sua classe.
      Salvaguardas proficientes: <strong>${esc(salvaguardas || '—')}</strong>.</p>
      <div class="row"><span class="badge" id="contador-pericias">${estado.pericias.size}/${limite}</span></div>
      <div class="option-grid" style="margin-top:12px">${opcoes}</div>`;
  }

  function ligarEventosPasso() {
    const conteudo = view.querySelector('#passo-conteudo');
    conteudo.querySelectorAll('.option[data-slug]').forEach((no) =>
      no.addEventListener('click', () => {
        const tipo = ['raca', 'classe', 'antecedente'][estado.passo];
        estado[tipo] = no.dataset.slug;
        pintar();
      }));
    const campoNome = conteudo.querySelector('#campo-nome');
    if (campoNome) campoNome.addEventListener('input', (e) => { estado.nome = e.target.value; });
    const campoTend = conteudo.querySelector('#campo-tendencia');
    if (campoTend) campoTend.addEventListener('input', (e) => { estado.tendencia = e.target.value; });
    conteudo.querySelectorAll('input[data-attr]').forEach((input) =>
      input.addEventListener('input', (e) => {
        const chave = e.target.dataset.attr;
        estado.atributos[chave] = Number(e.target.value) || 0;
        const alvo = conteudo.querySelector(`#mod-${chave}`);
        if (alvo) alvo.textContent = fmtMod(estado.atributos[chave]);
      }));
    const classe = classeAtual();
    const limite = (classe && classe.num_pericias) || 2;
    conteudo.querySelectorAll('.option[data-pericia]').forEach((no) =>
      no.addEventListener('click', () => {
        const nome = no.dataset.pericia;
        if (estado.pericias.has(nome)) estado.pericias.delete(nome);
        else if (estado.pericias.size < limite) estado.pericias.add(nome);
        else { toast(`Máximo de ${limite} perícias.`, 'err'); return; }
        no.classList.toggle('selected', estado.pericias.has(nome));
        const contador = conteudo.querySelector('#contador-pericias');
        if (contador) contador.textContent = `${estado.pericias.size}/${limite}`;
      }));
    conteudo.querySelectorAll('.option[data-talento]').forEach((no) =>
      no.addEventListener('click', () => {
        const slug = no.dataset.talento;
        if (estado.talentos.has(slug)) estado.talentos.delete(slug);
        else estado.talentos.add(slug);
        pintar();   // re-renderiza para atualizar o preview de bônus
      }));
  }

  async function avancar() {
    if (estado.passo === 0 && !estado.nome.trim()) { toast('Dê um nome ao seu herói.', 'err'); return; }
    if (estado.passo < PASSOS.length - 1) { estado.passo++; pintar(); return; }
    await criar();
  }

  async function criar() {
    const classe = classeAtual();
    const raca = racas.find((r) => r.slug === estado.raca);
    const dadoVida = classe ? `1d${classe.dado_vida}` : '1d8';
    const conMod = modificador(estado.atributos.con);
    const pv = classe ? classe.dado_vida + conMod : 8 + conMod;
    const payload = {
      nome: estado.nome.trim(),
      tendencia: estado.tendencia,
      raca_slug: estado.raca, classe_slug: estado.classe, antecedente_slug: estado.antecedente,
      nivel: 1, xp: 0,
      atributos: estado.atributos,
      deslocamento: raca ? `${raca.deslocamento} m` : '9 m',
      dado_vida: dadoVida,
      pv_max: Math.max(1, pv), pv_atual: Math.max(1, pv),
      ca: 10 + modificador(estado.atributos.des),
      pericias_proficientes: Array.from(estado.pericias),
      talentos: Array.from(estado.talentos),
      classe_conjuradora: classe && classe.conjurador ? classe.nome : null,
      atributo_conjuracao: classe ? classe.atributo_conjuracao : null,
    };
    try {
      const criado = await api.characters.create(payload);
      toast(`${criado.nome} forjado com sucesso!`);
      navegar(`#/characters/${criado.id}`);
    } catch (erro) { toast(erro.message, 'err'); }
  }

  function fmtMod(valor) {
    const mod = modificador(valor);
    return mod >= 0 ? `+${mod}` : `${mod}`;
  }

  pintar();
}
