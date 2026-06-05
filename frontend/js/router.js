// Hash router minimalista com suporte a parâmetros e guardas.
const rotas = [];

export function rota(padrao, handler, opcoes = {}) {
  // padrao ex.: '#/characters/:id' -> regex com grupos nomeados.
  const partes = padrao.split('/').map((segmento) => {
    if (segmento.startsWith(':')) return `(?<${segmento.slice(1)}>[^/]+)`;
    return segmento.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  });
  const regex = new RegExp(`^${partes.join('/')}$`);
  rotas.push({ regex, handler, opcoes });
}

let aoNavegar = null;
export function definirGuard(fn) { aoNavegar = fn; }

async function resolver() {
  const hash = location.hash || '#/';
  for (const definicao of rotas) {
    const encontrado = definicao.regex.exec(hash.split('?')[0]);
    if (encontrado) {
      const params = encontrado.groups || {};
      if (aoNavegar) {
        const permitido = aoNavegar(definicao.opcoes, params);
        if (permitido === false) return;
      }
      await definicao.handler(params);
      return;
    }
  }
  // Fallback.
  location.hash = '#/dashboard';
}

export function iniciarRouter() {
  window.addEventListener('hashchange', resolver);
  resolver();
}

export function navegar(hash) {
  if (location.hash === hash) resolver();
  else location.hash = hash;
}
