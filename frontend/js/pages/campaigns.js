// Mesas/Campanhas: lista, criação (mestre), ingresso por código e detalhe.
import { api } from '../api.js';
import { getUser } from '../auth.js';
import { navegar } from '../router.js';
import { montarShell } from '../app.js';
import { iniciarPolling } from '../live.js';
import { emptyState, esc, html, modal, toast } from '../ui.js';

export async function renderCampaigns() {
  const view = montarShell('Mesas', '#/campaigns');
  const usuario = getUser();
  const ehMestre = usuario.role === 'MESTRE' || usuario.role === 'ADMIN';

  view.innerHTML = '<div class="spinner"></div>';
  let mesas = [];
  try { mesas = await api.campaigns.list(); } catch (erro) { toast(erro.message, 'err'); }

  view.innerHTML = `
    <div class="section-title">
      <h2>Suas Mesas</h2>
      <div class="row">
        <button class="btn btn--ghost" id="entrar">🔑 Entrar por código</button>
        ${ehMestre ? '<button class="btn btn--primary" id="criar">➕ Criar Mesa</button>' : ''}
      </div>
    </div>
    <div class="grid grid--cards">
      ${mesas.length ? mesas.map((mesa) => `
        <div class="card char-card" data-mesa="${mesa.id}">
          <div class="ccard-name">${esc(mesa.nome)}</div>
          <div class="ccard-sub">Mestre: ${esc(mesa.mestre_nome || '—')}</div>
          <p class="muted" style="font-size:.85rem">${esc(mesa.descricao || '')}</p>
          <div class="spread">
            <span class="badge">${mesa.total_membros} jogador(es)</span>
            <span class="chip">${esc(mesa.codigo_convite)}</span>
          </div>
        </div>`).join('') : emptyState('🛡️', 'Nenhuma mesa', 'Entre por um código de convite ou crie a sua.')}
    </div>`;

  view.querySelectorAll('[data-mesa]').forEach((no) =>
    no.addEventListener('click', () => navegar(`#/campaigns/${no.dataset.mesa}`)));
  view.querySelector('#entrar').addEventListener('click', dialogoEntrar);
  const botaoCriar = view.querySelector('#criar');
  if (botaoCriar) botaoCriar.addEventListener('click', dialogoCriar);
}

function dialogoEntrar() {
  const conteudo = html(`<div>
    <h3>Entrar numa mesa</h3>
    <div class="field"><label>Código de convite</label>
      <input class="input" id="codigo" placeholder="Ex.: A1B2C3" maxlength="6" style="text-transform:uppercase"></div>
    <div class="row" style="justify-content:flex-end">
      <button class="btn btn--ghost" id="cancelar">Cancelar</button>
      <button class="btn btn--primary" id="ok">Entrar</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#ok').addEventListener('click', async () => {
    const codigo = conteudo.querySelector('#codigo').value.trim().toUpperCase();
    if (!codigo) return;
    try {
      const mesa = await api.campaigns.join(codigo);
      toast(`Você entrou em "${mesa.nome}"!`);
      fechar();
      navegar(`#/campaigns/${mesa.id}`);
    } catch (erro) { toast(erro.message, 'err'); }
  });
}

function dialogoCriar() {
  const conteudo = html(`<div>
    <h3>Criar nova mesa</h3>
    <div class="field"><label>Nome da campanha</label><input class="input" id="nome" placeholder="A Maldição de Strahd"></div>
    <div class="field"><label>Descrição</label><textarea class="textarea" id="descricao" placeholder="Premissa da campanha..."></textarea></div>
    <div class="row" style="justify-content:flex-end">
      <button class="btn btn--ghost" id="cancelar">Cancelar</button>
      <button class="btn btn--primary" id="ok">Criar</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#ok').addEventListener('click', async () => {
    const nome = conteudo.querySelector('#nome').value.trim();
    if (!nome) { toast('Dê um nome à mesa.', 'err'); return; }
    try {
      const mesa = await api.campaigns.create({ nome, descricao: conteudo.querySelector('#descricao').value });
      toast('Mesa criada!');
      fechar();
      navegar(`#/campaigns/${mesa.id}`);
    } catch (erro) { toast(erro.message, 'err'); }
  });
}

export async function renderCampaignDetail(id) {
  const view = montarShell('Mesa', '#/campaigns');
  const usuario = getUser();
  view.innerHTML = '<div class="spinner"></div>';
  let mesa;
  try { mesa = await api.campaigns.get(id); } catch (erro) {
    toast(erro.message, 'err'); navegar('#/campaigns'); return;
  }
  const ehMestre = mesa.mestre_id === usuario.id || usuario.role === 'ADMIN';

  view.innerHTML = `
    <div class="spread" style="margin-bottom:14px">
      <button class="btn btn--ghost btn--sm" id="voltar">← Mesas</button>
      ${ehMestre ? '<button class="btn btn--danger btn--sm" id="apagar">🗑️ Excluir mesa</button>' : ''}
    </div>
    <div class="card" style="margin-bottom:18px">
      <div class="spread">
        <div><h2 style="margin:0">${esc(mesa.nome)}</h2>
          <div class="muted">${esc(mesa.sistema)} · Mestre: ${esc(mesa.mestre_nome)}</div></div>
        <div style="text-align:right"><div class="muted" style="font-size:.78rem">CÓDIGO DE CONVITE</div>
          <span class="code-pill">${esc(mesa.codigo_convite)}</span></div>
      </div>
      <p style="margin-top:10px; white-space:pre-wrap">${esc(mesa.descricao || '')}</p>
    </div>

    <div class="sheet-grid">
      <div class="card">
        <h4>Jogadores (${mesa.membros.length})</h4>
        <div class="skill-list">
          ${mesa.membros.length ? mesa.membros.map((membro) => `
            <div class="skill-line">
              <span>${esc(membro.nome)}</span>
              ${ehMestre ? `<button class="btn btn--danger btn--sm" data-kick="${membro.user_id}" style="margin-left:auto">Remover</button>` : ''}
            </div>`).join('') : '<p class="muted">Nenhum jogador entrou ainda. Compartilhe o código!</p>'}
        </div>
        ${!ehMestre ? '<button class="btn btn--gold btn--sm btn--block" id="vincular" style="margin-top:12px">Vincular meu personagem</button>' : ''}
      </div>
      <div class="card">
        <h4>Personagens na Mesa (${mesa.personagens.length})</h4>
        <div class="grid grid--cards">
          ${mesa.personagens.length ? mesa.personagens.map((personagem) => `
            <div class="card char-card" data-char="${personagem.id}">
              <div class="ccard-name">${esc(personagem.nome)}</div>
              <div class="ccard-sub">${esc([personagem.raca_slug, personagem.classe_slug].filter(Boolean).join(' · ') || '')}</div>
              <span class="badge">Nível ${personagem.nivel}</span>
            </div>`).join('') : '<p class="muted">Nenhum personagem vinculado.</p>'}
        </div>
        <div class="row" style="margin-top:12px">
          <button class="btn btn--ghost btn--sm" id="bestiario-mesa">🐉 Bestiário da mesa</button>
        </div>
      </div>
    </div>`;

  view.querySelector('#voltar').addEventListener('click', () => navegar('#/campaigns'));
  view.querySelectorAll('[data-char]').forEach((no) =>
    no.addEventListener('click', () => navegar(`#/characters/${no.dataset.char}`)));
  view.querySelector('#bestiario-mesa').addEventListener('click', () => navegar(`#/bestiary?mesa=${mesa.id}`));

  const botaoApagar = view.querySelector('#apagar');
  if (botaoApagar) botaoApagar.addEventListener('click', async () => {
    try { await api.campaigns.remove(mesa.id); toast('Mesa excluída.'); navegar('#/campaigns'); }
    catch (erro) { toast(erro.message, 'err'); }
  });

  view.querySelectorAll('[data-kick]').forEach((botao) =>
    botao.addEventListener('click', async () => {
      try { await api.campaigns.kick(mesa.id, Number(botao.dataset.kick)); toast('Jogador removido.'); renderCampaignDetail(id); }
      catch (erro) { toast(erro.message, 'err'); }
    }));

  const botaoVincular = view.querySelector('#vincular');
  if (botaoVincular) botaoVincular.addEventListener('click', () => dialogoVincular(mesa, id));

  // Ao vivo: jogadores entrando, personagens vinculados etc. aparecem sem F5.
  iniciarPolling(
    () => api.campaigns.get(id),
    () => renderCampaignDetail(id),
    { inicial: mesa, ms: 8000 },
  );
}

async function dialogoVincular(mesa, id) {
  let meus = [];
  try { meus = await api.characters.list(); } catch (erro) { toast(erro.message, 'err'); return; }
  const livres = meus.filter((personagem) => personagem.mesa_id !== mesa.id);
  const conteudo = html(`<div>
    <h3>Vincular personagem a "${esc(mesa.nome)}"</h3>
    ${livres.length ? `<div class="option-grid">${livres.map((personagem) => `
      <div class="option" data-pid="${personagem.id}"><div class="opt-name">${esc(personagem.nome)}</div>
        <div class="opt-meta">Nível ${personagem.nivel}</div></div>`).join('')}</div>`
      : '<p class="muted">Você não tem personagens livres. Crie um primeiro.</p>'}
    <div class="row" style="justify-content:flex-end; margin-top:12px">
      <button class="btn btn--ghost" id="fechar">Fechar</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#fechar').addEventListener('click', fechar);
  conteudo.querySelectorAll('[data-pid]').forEach((no) =>
    no.addEventListener('click', async () => {
      try {
        await api.campaigns.linkCharacter(mesa.id, Number(no.dataset.pid));
        toast('Personagem vinculado!');
        fechar();
        renderCampaignDetail(id);
      } catch (erro) { toast(erro.message, 'err'); }
    }));
}
