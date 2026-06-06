// Gerência de sessão do usuário (token + dados) em localStorage.
const CHAVE_TOKEN = 'ragnarok.token'; // gitleaks:allow (chave de localStorage, não é segredo)
const CHAVE_USER = 'ragnarok.user';

export function setSession({ access_token, user }) {
  if (access_token) localStorage.setItem(CHAVE_TOKEN, access_token);
  if (user) localStorage.setItem(CHAVE_USER, JSON.stringify(user));
}

export function getToken() {
  return localStorage.getItem(CHAVE_TOKEN);
}

export function getUser() {
  const bruto = localStorage.getItem(CHAVE_USER);
  if (!bruto) return null;
  try { return JSON.parse(bruto); } catch (_) { return null; }
}

export function isLogged() {
  return Boolean(getToken());
}

export function logout() {
  localStorage.removeItem(CHAVE_TOKEN);
  localStorage.removeItem(CHAVE_USER);
}

const CHAVE_IDIOMA = 'ragnarok.idioma';
export function getIdioma() { return localStorage.getItem(CHAVE_IDIOMA) || 'pt'; }
export function setIdioma(idioma) { localStorage.setItem(CHAVE_IDIOMA, idioma); }

// ADMIN sempre passa; senão verifica se o papel está na lista permitida.
export function requireRole(...papeis) {
  const usuario = getUser();
  if (!usuario) return false;
  if (usuario.role === 'ADMIN') return true;
  return papeis.length === 0 || papeis.includes(usuario.role);
}
