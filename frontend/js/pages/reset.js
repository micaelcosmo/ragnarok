// Página pública de redefinição de senha (acessada pelo link gerado pelo admin).
import { api } from '../api.js';
import { setSession } from '../auth.js';
import { navegar } from '../router.js';
import { html, toast } from '../ui.js';

function tokenDaHash() {
  const query = (location.hash.split('?')[1] || '');
  return new URLSearchParams(query).get('token');
}

export function renderReset() {
  const app = document.getElementById('app');
  const token = tokenDaHash();

  const wrap = html(`
    <div class="auth-wrap">
      <div class="card auth-card">
        <div class="brand-big">⚔️ Ragnarok</div>
        <div class="tagline">Definir nova senha</div>
        ${token ? `
          <form id="reset-form">
            <div class="field">
              <label>Nova senha</label>
              <div class="field-inline" style="gap:6px">
                <input class="input" name="senha" type="password" placeholder="••••••" required minlength="6">
                <button type="button" class="btn btn--ghost btn--sm" id="ver">👁️</button>
              </div>
              <small class="muted">Mínimo de 6 caracteres. Não precisa da senha antiga.</small>
            </div>
            <div class="field">
              <label>Confirmar nova senha</label>
              <input class="input" name="confirma" type="password" placeholder="••••••" required minlength="6">
            </div>
            <button class="btn btn--primary btn--block" type="submit">Salvar e entrar</button>
          </form>`
        : `<p class="muted" style="text-align:center">Link inválido — falta o token.
             Peça um novo link ao administrador.</p>
           <a class="btn btn--ghost btn--block" href="#/login">Ir para o login</a>`}
      </div>
    </div>`);
  app.innerHTML = '';
  app.appendChild(wrap);
  if (!token) return;

  const campoSenha = wrap.querySelector('[name=senha]');
  wrap.querySelector('#ver').addEventListener('click', () => {
    campoSenha.type = campoSenha.type === 'password' ? 'text' : 'password';
  });

  wrap.querySelector('#reset-form').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const dados = Object.fromEntries(new FormData(evento.target).entries());
    if (dados.senha.length < 6) { toast('A senha precisa ter ao menos 6 caracteres.', 'err'); return; }
    if (dados.senha !== dados.confirma) { toast('As senhas não coincidem.', 'err'); return; }
    try {
      const sessao = await api.auth.resetPassword(token, dados.senha);
      setSession(sessao);
      toast('Senha redefinida! Bem-vindo de volta.');
      navegar('#/dashboard');
    } catch (erro) {
      toast(erro.message || 'Não foi possível redefinir.', 'err');
    }
  });
}
