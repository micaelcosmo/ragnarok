// Página de login/registro (alternância num único cartão).
import { api } from '../api.js';
import { setSession } from '../auth.js';
import { navegar } from '../router.js';
import { html, toast } from '../ui.js';

export function renderLogin() {
  const app = document.getElementById('app');
  let modoRegistro = false;

  function pintar() {
    app.innerHTML = '';
    const wrap = html(`
      <div class="auth-wrap">
        <div class="card auth-card">
          <div class="brand-big">⚔️ Ragnarok</div>
          <div class="tagline">"Toda lenda começa com uma escolha..."</div>

          <form id="auth-form">
            <div class="field" ${modoRegistro ? '' : 'style="display:none"'} id="wrap-name">
              <label>Nome de aventureiro</label>
              <input class="input" name="name" placeholder="Ex.: Elara Trevo-Negro">
            </div>
            <div class="field">
              <label>Email</label>
              <input class="input" name="email" type="email" placeholder="voce@reino.com" required>
            </div>
            <div class="field">
              <label>Senha</label>
              <div class="field-inline" style="gap:6px">
                <input class="input" name="password" type="password" placeholder="••••••" required minlength="6">
                <button type="button" class="btn btn--ghost btn--sm" id="ver-senha" title="Mostrar/ocultar senha">👁️</button>
              </div>
              ${modoRegistro ? '<small class="muted" id="dica-senha">Mínimo de 6 caracteres.</small>' : ''}
            </div>
            <div class="field" ${modoRegistro ? '' : 'style="display:none"'} id="wrap-role">
              <label>Como você joga?</label>
              <select class="select" name="role">
                <option value="JOGADOR">Jogador (cria personagens)</option>
                <option value="MESTRE">Mestre (monta mesas)</option>
              </select>
            </div>
            <button class="btn btn--primary btn--block" type="submit">
              ${modoRegistro ? 'Criar conta' : 'Entrar'}
            </button>
          </form>
          <div class="auth-toggle">
            ${modoRegistro ? 'Já tem conta?' : 'Novo por aqui?'}
            <a id="toggle-modo" href="#">${modoRegistro ? 'Entrar' : 'Criar conta'}</a>
          </div>
        </div>
      </div>`);
    app.appendChild(wrap);

    wrap.querySelector('#toggle-modo').addEventListener('click', (evento) => {
      evento.preventDefault();
      modoRegistro = !modoRegistro;
      pintar();
    });

    // Mostrar/ocultar senha (ajuda a evitar erro de digitação).
    const campoSenha = wrap.querySelector('[name=password]');
    wrap.querySelector('#ver-senha').addEventListener('click', () => {
      campoSenha.type = campoSenha.type === 'password' ? 'text' : 'password';
    });

    wrap.querySelector('#auth-form').addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const dados = Object.fromEntries(new FormData(evento.target).entries());
      if (modoRegistro && (dados.password || '').length < 6) {
        toast('A senha precisa ter ao menos 6 caracteres.', 'err');
        return;
      }
      try {
        // Tanto registro quanto login devolvem {access_token, user} -> entra direto.
        const sessao = modoRegistro
          ? await api.auth.register({ name: dados.name, email: dados.email, password: dados.password, role: dados.role })
          : await api.auth.login({ email: dados.email, password: dados.password });
        setSession(sessao);
        toast(modoRegistro ? `Conta criada! Bem-vindo, ${sessao.user.name}!` : `Bem-vindo, ${sessao.user.name}!`);
        navegar('#/dashboard');
      } catch (erro) {
        toast(erro.message || 'Falha na autenticação.', 'err');
      }
    });
  }

  pintar();
}
