// Cliente HTTP da API do Ragnarok.
import { getToken, getIdioma, logout } from './auth.js';

export const API_BASE = '/api/v1';

// Sufixo de querystring com o idioma quando PT (para endpoints simples sem outros params).
function comIdioma() {
  return getIdioma() === 'pt' ? '?idioma=pt' : '';
}

export class ApiError extends Error {
  constructor(status, payload) {
    super((payload && payload.message) || 'Erro de API');
    this.status = status;
    this.code = (payload && payload.code) || 'ERRO';
    this.details = (payload && payload.details) || {};
  }
}

// Upload de arquivo (multipart) — separado do apiFetch (que é JSON).
export async function apiUpload(file) {
  const fd = new FormData();
  fd.append('arquivo', file);
  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/uploads`, { method: 'POST', headers, body: fd });
  let payload = null;
  try { payload = await res.json(); } catch (_) { payload = null; }
  if (!res.ok) {
    if (res.status === 401) { logout(); location.hash = '#/login'; }
    throw new ApiError(res.status, (payload && payload.error) || {});
  }
  return payload ? payload.data : null;
}

// Download autenticado de arquivo binário (ex.: PDF da ficha): busca o blob e dispara o save.
export async function baixarArquivo(path) {
  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (!res.ok) {
    if (res.status === 401) { logout(); location.hash = '#/login'; }
    let payload = null;
    try { payload = await res.json(); } catch (_) { payload = null; }
    throw new ApiError(res.status, (payload && payload.error) || {});
  }
  const blob = await res.blob();
  const disp = res.headers.get('Content-Disposition') || '';
  const m = disp.match(/filename="?([^"]+)"?/);
  const nome = m ? m[1] : 'ficha.pdf';
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = nome;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

export async function apiFetch(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const resposta = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let payload = null;
  try { payload = await resposta.json(); } catch (_) { payload = null; }

  if (!resposta.ok) {
    const erro = (payload && payload.error) || {};
    if (resposta.status === 401 && auth) {
      logout();
      location.hash = '#/login';
    }
    throw new ApiError(resposta.status, erro);
  }
  return payload ? payload.data : null;
}

// Atalhos por recurso (POO leve via objetos namespaced).
export const api = {
  upload: (file) => apiUpload(file),
  auth: {
    register: (dados) => apiFetch('/auth/register', { method: 'POST', body: dados, auth: false }),
    login: (dados) => apiFetch('/auth/login', { method: 'POST', body: dados, auth: false }),
    me: () => apiFetch('/auth/me'),
    resetPassword: (token, nova_senha) =>
      apiFetch('/auth/reset-password', { method: 'POST', body: { token, nova_senha }, auth: false }),
  },
  characters: {
    list: (mesaId) => apiFetch(`/characters${mesaId ? `?mesa_id=${mesaId}` : ''}`),
    get: (id) => apiFetch(`/characters/${id}`),
    create: (dados) => apiFetch('/characters', { method: 'POST', body: dados }),
    update: (id, dados) => apiFetch(`/characters/${id}`, { method: 'PUT', body: dados }),
    remove: (id) => apiFetch(`/characters/${id}`, { method: 'DELETE' }),
    equipar: (id, tipo, itemId) => apiFetch(`/characters/${id}/equipar`, { method: 'POST', body: { tipo, item_id: itemId } }),
    desequipar: (id, tipo, itemId) => apiFetch(`/characters/${id}/desequipar`, { method: 'POST', body: { tipo, item_id: itemId } }),
    baixarPdf: (id) => baixarArquivo(`/characters/${id}/pdf`),
    ajustarRecurso: (id, indice, delta) => apiFetch(`/characters/${id}/recursos/ajustar`, { method: 'POST', body: { indice, delta } }),
    descanso: (id, tipo) => apiFetch(`/characters/${id}/descanso`, { method: 'POST', body: { tipo } }),
  },
  catalog: {
    list: (tipo, { personagemId, q } = {}) => {
      const params = new URLSearchParams();
      if (personagemId) params.set('personagem_id', personagemId);
      if (q) params.set('q', q);
      if (getIdioma() === 'pt') params.set('idioma', 'pt');
      const qs = params.toString();
      return apiFetch(`/catalog/${tipo}${qs ? `?${qs}` : ''}`);
    },
    create: (tipo, dados) => apiFetch(`/catalog/${tipo}`, { method: 'POST', body: dados }),
    update: (tipo, id, dados) => apiFetch(`/catalog/${tipo}/${id}`, { method: 'PUT', body: dados }),
    remove: (tipo, id) => apiFetch(`/catalog/${tipo}/${id}`, { method: 'DELETE' }),
  },
  campaigns: {
    list: () => apiFetch('/campaigns'),
    get: (id) => apiFetch(`/campaigns/${id}`),
    create: (dados) => apiFetch('/campaigns', { method: 'POST', body: dados }),
    update: (id, dados) => apiFetch(`/campaigns/${id}`, { method: 'PUT', body: dados }),
    remove: (id) => apiFetch(`/campaigns/${id}`, { method: 'DELETE' }),
    join: (codigo) => apiFetch('/campaigns/join', { method: 'POST', body: { codigo } }),
    kick: (id, userId) => apiFetch(`/campaigns/${id}/kick`, { method: 'POST', body: { user_id: userId } }),
    linkCharacter: (id, personagemId) =>
      apiFetch(`/campaigns/${id}/personagens`, { method: 'POST', body: { personagem_id: personagemId } }),
  },
  bestiary: {
    list: ({ mesaId, q } = {}) => {
      const params = new URLSearchParams();
      if (mesaId) params.set('mesa_id', mesaId);
      if (q) params.set('q', q);
      const qs = params.toString();
      return apiFetch(`/bestiary${qs ? `?${qs}` : ''}`);
    },
    get: (id) => apiFetch(`/bestiary/${id}`),
    create: (dados) => apiFetch('/bestiary', { method: 'POST', body: dados }),
    update: (id, dados) => apiFetch(`/bestiary/${id}`, { method: 'PUT', body: dados }),
    remove: (id) => apiFetch(`/bestiary/${id}`, { method: 'DELETE' }),
  },
  reference: {
    races: () => apiFetch(`/reference/races${comIdioma()}`),
    classes: () => apiFetch(`/reference/classes${comIdioma()}`),
    backgrounds: () => apiFetch(`/reference/backgrounds${comIdioma()}`),
    spells: ({ nivel, classe, q, fonte } = {}) => {
      const params = new URLSearchParams();
      if (nivel !== undefined && nivel !== '') params.set('nivel', nivel);
      if (classe) params.set('classe', classe);
      if (q) params.set('q', q);
      if (fonte) params.set('fonte', fonte);
      if (getIdioma() === 'pt') params.set('idioma', 'pt');
      const qs = params.toString();
      return apiFetch(`/reference/spells${qs ? `?${qs}` : ''}`);
    },
    feats: ({ q, fonte } = {}) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (fonte) params.set('fonte', fonte);
      if (getIdioma() === 'pt') params.set('idioma', 'pt');
      const qs = params.toString();
      return apiFetch(`/reference/feats${qs ? `?${qs}` : ''}`);
    },
    sources: () => apiFetch('/reference/sources'),
    // Catálogo global de equipamento (leitura). tipo ∈ weapons|armor|items
    catalogGlobal: (tipo, { q } = {}) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (getIdioma() === 'pt') params.set('idioma', 'pt');
      const qs = params.toString();
      return apiFetch(`/reference/${tipo}${qs ? `?${qs}` : ''}`);
    },
    // CRUD do compêndio (MESTRE/ADMIN). tipo ∈ races|classes|backgrounds|feats|spells
    create: (tipo, dados) => apiFetch(`/reference/${tipo}`, { method: 'POST', body: dados }),
    update: (tipo, slug, dados) => apiFetch(`/reference/${tipo}/${slug}`, { method: 'PUT', body: dados }),
    remove: (tipo, slug) => apiFetch(`/reference/${tipo}/${slug}`, { method: 'DELETE' }),
  },
  admin: {
    users: ({ q, role } = {}) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (role) params.set('role', role);
      const qs = params.toString();
      return apiFetch(`/admin/users${qs ? `?${qs}` : ''}`);
    },
    setRole: (id, role) => apiFetch(`/admin/users/${id}/role`, { method: 'PUT', body: { role } }),
    removeUser: (id) => apiFetch(`/admin/users/${id}`, { method: 'DELETE' }),
    resetLink: (id) => apiFetch(`/admin/users/${id}/reset-link`, { method: 'POST' }),
    stats: () => apiFetch('/admin/stats'),
    campaigns: (q) => apiFetch(`/admin/campaigns${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    removeCampaign: (id) => apiFetch(`/admin/campaigns/${id}`, { method: 'DELETE' }),
  },
};
