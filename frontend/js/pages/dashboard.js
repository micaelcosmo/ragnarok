// Dashboard: personagens do usuário + mesas, com CTAs por papel.
import { api } from '../api.js';
import { getUser } from '../auth.js';
import { navegar } from '../router.js';
import { montarShell } from '../app.js';
import { emptyState, esc, iniciais, toast } from '../ui.js';

export async function renderDashboard() {
  const view = montarShell('Início', '#/dashboard');
  const usuario = getUser();

  try {
    const [personagens, mesas] = await Promise.all([
      api.characters.list(),
      api.campaigns.list(),
    ]);

    view.innerHTML = `
      <div class="section-title">
        <h2>Saudações, ${esc(usuario.name)}</h2>
        <button class="btn btn--primary" id="cta-novo">➕ Novo Herói</button>
      </div>

      <h3 class="muted">Seus Personagens</h3>
      <div class="grid grid--cards" id="lista-personagens" style="margin-bottom:28px">
        ${personagens.length ? personagens.map(cardPersonagem).join('') : emptyState('🗺️', 'Nenhum herói ainda', 'Crie seu primeiro personagem para começar a aventura.')}
      </div>

      <div class="section-title">
        <h3 class="muted">Suas Mesas</h3>
        <button class="btn btn--ghost btn--sm" id="cta-mesas">Ver todas →</button>
      </div>
      <div class="grid grid--cards">
        ${mesas.length ? mesas.map(cardMesa).join('') : emptyState('🛡️', 'Sem mesas', 'Entre numa mesa pelo código de convite ou crie uma (se for mestre).')}
      </div>`;

    view.querySelector('#cta-novo').addEventListener('click', () => navegar('#/characters/new'));
    view.querySelector('#cta-mesas').addEventListener('click', () => navegar('#/campaigns'));
    view.querySelectorAll('[data-char]').forEach((no) =>
      no.addEventListener('click', () => navegar(`#/characters/${no.dataset.char}`)));
    view.querySelectorAll('[data-mesa]').forEach((no) =>
      no.addEventListener('click', () => navegar(`#/campaigns/${no.dataset.mesa}`)));
  } catch (erro) {
    toast(erro.message, 'err');
    view.innerHTML = emptyState('⚠️', 'Erro ao carregar', erro.message);
  }
}

function cardPersonagem(personagem) {
  const linha = [personagem.raca_slug, personagem.classe_slug].filter(Boolean).join(' · ') || 'Aventureiro';
  return `
    <div class="card char-card" data-char="${personagem.id}">
      <div class="ccard-top">
        <span class="sheet-portrait" style="width:48px;height:48px;font-size:1.2rem">${iniciais(personagem.nome)}</span>
        <div>
          <div class="ccard-name">${esc(personagem.nome)}</div>
          <div class="ccard-sub">${esc(linha)}</div>
        </div>
      </div>
      <div class="spread">
        <span class="badge">Nível ${personagem.nivel}</span>
        <span class="muted">${personagem.mesa_id ? '🛡️ em mesa' : 'livre'}</span>
      </div>
    </div>`;
}

function cardMesa(mesa) {
  return `
    <div class="card char-card" data-mesa="${mesa.id}">
      <div class="ccard-name">${esc(mesa.nome)}</div>
      <div class="ccard-sub">${esc(mesa.sistema)} · Mestre: ${esc(mesa.mestre_nome || '—')}</div>
      <div class="spread">
        <span class="badge">${mesa.total_membros} jogador(es)</span>
        <span class="chip">${esc(mesa.codigo_convite)}</span>
      </div>
    </div>`;
}
