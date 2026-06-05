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
              <input class="input" name="password" type="password" placeholder="••••••" required>
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

    wrap.querySelector('#auth-form').addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const dados = Object.fromEntries(new FormData(evento.target).entries());
      try {
        if (modoRegistro) {
          await api.auth.register({ name: dados.name, email: dados.email, password: dados.password, role: dados.role });
          toast('Conta criada! Faça login.');
          modoRegistro = false;
          pintar();
          return;
        }
        const sessao = await api.auth.login({ email: dados.email, password: dados.password });
        setSession(sessao);
        toast(`Bem-vindo, ${sessao.user.name}!`);
        navegar('#/dashboard');
      } catch (erro) {
        toast(erro.message || 'Falha na autenticação.', 'err');
      }
    });
  }

  pintar();
}
