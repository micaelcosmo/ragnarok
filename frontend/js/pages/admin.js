// Painel ADMIN: métricas da plataforma + gestão de usuários (papel/remoção).
import { api } from '../api.js';
import { getUser } from '../auth.js';
import { montarShell } from '../app.js';
import { esc, html, modal, toast } from '../ui.js';

const PAPEIS = ['ADMIN', 'MESTRE', 'JOGADOR'];

export async function renderAdmin() {
  const view = montarShell('Administração', '#/admin');
  const eu = getUser();
  view.innerHTML = '<div class="spinner"></div>';

  let stats;
  try { stats = await api.admin.stats(); } catch (erro) { toast(erro.message, 'err'); return; }

  view.innerHTML = `
    <h2>Painel de Administração</h2>
    <div class="grid grid--cards" style="margin-bottom:24px">
      ${cardStat('👑', 'Admins', stats.usuarios.ADMIN)}
      ${cardStat('🎲', 'Mestres', stats.usuarios.MESTRE)}
      ${cardStat('🛡️', 'Jogadores', stats.usuarios.JOGADOR)}
      ${cardStat('🗺️', 'Personagens', stats.personagens)}
      ${cardStat('📜', 'Mesas', stats.mesas)}
      ${cardStat('🐉', 'Criaturas', stats.monstros)}
    </div>

    <div class="section-title"><h3>Usuários</h3>
      <input class="input" id="busca" placeholder="🔎 Buscar por nome/email" style="max-width:280px"></div>
    <div class="card"><table class="table">
      <thead><tr><th>Nome</th><th>Email</th><th>Papel</th><th>Ações</th></tr></thead>
      <tbody id="corpo-usuarios"><tr><td colspan="4"><div class="spinner"></div></td></tr></tbody>
    </table></div>`;

  async function carregar(busca) {
    const corpo = view.querySelector('#corpo-usuarios');
    try {
      const usuarios = await api.admin.users({ q: busca });
      corpo.innerHTML = usuarios.map((usuario) => `
        <tr data-uid="${usuario.id}">
          <td>${esc(usuario.name)}</td>
          <td class="muted">${esc(usuario.email)}</td>
          <td>
            <select class="select sel-papel" data-uid="${usuario.id}" style="max-width:140px">
              ${PAPEIS.map((papel) => `<option value="${papel}" ${papel === usuario.role ? 'selected' : ''}>${papel}</option>`).join('')}
            </select>
          </td>
          <td>${usuario.id === eu.id ? '<span class="chip">você</span>'
            : `<button class="btn btn--danger btn--sm" data-del="${usuario.id}" data-nome="${esc(usuario.name)}">Excluir</button>`}</td>
        </tr>`).join('');

      corpo.querySelectorAll('.sel-papel').forEach((select) =>
        select.addEventListener('change', async () => {
          try { await api.admin.setRole(Number(select.dataset.uid), select.value); toast('Papel atualizado.'); }
          catch (erro) { toast(erro.message, 'err'); }
        }));
      corpo.querySelectorAll('[data-del]').forEach((botao) =>
        botao.addEventListener('click', () => confirmarRemocao(Number(botao.dataset.del), botao.dataset.nome, () => carregar(busca))));
    } catch (erro) { toast(erro.message, 'err'); }
  }

  let timer = null;
  view.querySelector('#busca').addEventListener('input', (evento) => {
    clearTimeout(timer);
    timer = setTimeout(() => carregar(evento.target.value.trim()), 250);
  });
  carregar('');
}

function cardStat(icone, rotulo, valor) {
  return `<div class="card" style="text-align:center">
    <div style="font-size:2rem">${icone}</div>
    <div class="combat-box"><div class="cb-val">${valor ?? 0}</div><div class="cb-label">${esc(rotulo)}</div></div>
  </div>`;
}

function confirmarRemocao(id, nome, aoRemover) {
  const conteudo = html(`<div>
    <h3>Excluir usuário "${esc(nome)}"?</h3>
    <p class="muted">Todos os personagens e mesas dele serão removidos.</p>
    <div class="row" style="justify-content:flex-end">
      <button class="btn btn--ghost" id="cancelar">Cancelar</button>
      <button class="btn btn--primary" id="confirmar">Excluir</button>
    </div></div>`);
  const fechar = modal(conteudo);
  conteudo.querySelector('#cancelar').addEventListener('click', fechar);
  conteudo.querySelector('#confirmar').addEventListener('click', async () => {
    try { await api.admin.removeUser(id); toast('Usuário removido.'); fechar(); aoRemover(); }
    catch (erro) { toast(erro.message, 'err'); }
  });
}
