// Cliente HTTP da API do Ragnarok.
import { getToken, logout } from './auth.js';

export const API_BASE = '/api/v1';

export class ApiError extends Error {
  constructor(status, payload) {
    super((payload && payload.message) || 'Erro de API');
    this.status = status;
    this.code = (payload && payload.code) || 'ERRO';
    this.details = (payload && payload.details) || {};
  }
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
    races: () => apiFetch('/reference/races'),
    classes: () => apiFetch('/reference/classes'),
    backgrounds: () => apiFetch('/reference/backgrounds'),
    spells: ({ nivel, classe, q, fonte } = {}) => {
      const params = new URLSearchParams();
      if (nivel !== undefined && nivel !== '') params.set('nivel', nivel);
      if (classe) params.set('classe', classe);
      if (q) params.set('q', q);
      if (fonte) params.set('fonte', fonte);
      const qs = params.toString();
      return apiFetch(`/reference/spells${qs ? `?${qs}` : ''}`);
    },
    feats: ({ q, fonte } = {}) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (fonte) params.set('fonte', fonte);
      const qs = params.toString();
      return apiFetch(`/reference/feats${qs ? `?${qs}` : ''}`);
    },
    sources: () => apiFetch('/reference/sources'),
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
