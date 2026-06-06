// Ponto de entrada: monta o shell, registra rotas e aplica guardas por papel.
import { getUser, isLogged, logout, requireRole, getIdioma, setIdioma } from './auth.js';
import { rota, definirGuard, iniciarRouter, navegar } from './router.js';
import { esc, iniciais, toast } from './ui.js';

import { renderLogin } from './pages/login.js';
import { renderReset } from './pages/reset.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderCharacter } from './pages/character.js';
import { renderCharacterNew } from './pages/character_new.js';
import { renderCampaigns, renderCampaignDetail } from './pages/campaigns.js';
import { renderBestiary } from './pages/bestiary.js';
import { renderCompendium } from './pages/compendium.js';
import { renderAdmin } from './pages/admin.js';

const NAV = [
  { hash: '#/dashboard', ico: '🏠', label: 'Início', papeis: ['JOGADOR', 'MESTRE'] },
  { hash: '#/characters/new', ico: '➕', label: 'Novo Herói', papeis: ['JOGADOR', 'MESTRE'] },
  { hash: '#/campaigns', ico: '🛡️', label: 'Mesas', papeis: ['JOGADOR', 'MESTRE'] },
  { hash: '#/bestiary', ico: '🐉', label: 'Bestiário', papeis: ['JOGADOR', 'MESTRE'] },
  { hash: '#/compendium', ico: '📖', label: 'Compêndio', papeis: ['JOGADOR', 'MESTRE'] },
  { hash: '#/admin', ico: '⚙️', label: 'Admin', papeis: [], adminOnly: true },
];

// Renderiza o shell e devolve o container #view onde cada página injeta conteúdo.
export function montarShell(tituloPagina, hashAtivo) {
  const usuario = getUser();
  const itens = NAV.filter((item) => {
    if (item.adminOnly) return usuario && usuario.role === 'ADMIN';
    return requireRole(...item.papeis);
  }).map((item) => `
    <div class="nav-link ${hashAtivo === item.hash ? 'active' : ''}" data-hash="${item.hash}">
      <span class="ico">${item.ico}</span><span>${item.label}</span>
    </div>`).join('');

  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="app-shell">
      <div class="brand"><span class="logo">⚔️ Ragna<span class="spark">rok</span></span></div>
      <div class="topbar">
        <div class="page-title">${esc(tituloPagina)}</div>
        <div class="user-chip">
          <button class="btn btn--ghost btn--sm" id="btn-idioma" title="Idioma do conteúdo">🌐 ${getIdioma().toUpperCase()}</button>
          <span class="role-badge role-${esc(usuario?.role)}">${esc(usuario?.role || '')}</span>
          <span class="avatar" title="${esc(usuario?.name)}">${iniciais(usuario?.name)}</span>
          <span class="muted">${esc(usuario?.name || '')}</span>
          <button class="btn btn--ghost btn--sm" id="btn-logout">Sair</button>
        </div>
      </div>
      <div class="sidebar">
        ${itens}
        <div class="nav-sep"></div>
        <div class="muted" style="padding:8px 12px; font-size:.75rem;">D&D 5E · SRD</div>
      </div>
      <div class="main" id="view"><div class="spinner"></div></div>
    </div>`;

  app.querySelectorAll('.nav-link[data-hash]').forEach((no) => {
    no.addEventListener('click', () => navegar(no.dataset.hash));
  });
  app.querySelector('#btn-logout').addEventListener('click', () => {
    logout();
    toast('Sessão encerrada.');
    navegar('#/login');
  });
  app.querySelector('#btn-idioma').addEventListener('click', () => {
    const novo = getIdioma() === 'pt' ? 'en' : 'pt';
    setIdioma(novo);
    toast(novo === 'pt' ? 'Conteúdo em Português (traduz importados).' : 'Conteúdo no idioma original (EN).');
    location.reload();
  });
  return app.querySelector('#view');
}

// Guarda global: exige login (exceto login) e papel quando definido.
definirGuard((opcoes) => {
  const ehLogin = opcoes.publico === true;
  if (!ehLogin && !isLogged()) {
    navegar('#/login');
    return false;
  }
  if (isLogged() && opcoes.soDeslogado) {
    navegar('#/dashboard');
    return false;
  }
  if (opcoes.papeis && !requireRole(...opcoes.papeis)) {
    toast('Acesso restrito.', 'err');
    navegar('#/dashboard');
    return false;
  }
  return true;
});

// Registro de rotas.
rota('#/', () => navegar('#/dashboard'));
rota('#/login', renderLogin, { publico: true, soDeslogado: true });
rota('#/reset', renderReset, { publico: true });
rota('#/dashboard', renderDashboard);
rota('#/characters/new', renderCharacterNew);
rota('#/characters/:id', (params) => renderCharacter(params.id));
rota('#/campaigns', renderCampaigns);
rota('#/campaigns/:id', (params) => renderCampaignDetail(params.id));
rota('#/bestiary', renderBestiary);
rota('#/compendium', renderCompendium);
rota('#/admin', renderAdmin, { papeis: ['ADMIN'] });

iniciarRouter();
