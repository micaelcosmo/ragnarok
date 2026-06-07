# ADR-0003 — Exportação da ficha em PDF (motor WeasyPrint)

- **Status**: Aceito
- **Data**: 2026-06-06

## Contexto
O jogador quer **baixar a ficha em PDF** com layout o mais próximo possível da ficha oficial 5E,
para imprimir/levar para a mesa. A plataforma já calcula todos os derivados (atributos finais,
modificadores, CA, ataques, perícias, salvaguardas, traços, magias, identidade). Faltava uma
**saída de serviço** que materialize isso num documento paginado e fiel.

Restrições do projeto:
- **Backend é só Python** (sem Node) → soluções que dependem de Chromium/Node (Playwright,
  puppeteer, wkhtmltopdf desatualizado) são indesejadas.
- O frontend é **vanilla JS** sem build → evitar empurrar libs pesadas (jsPDF/html2canvas) com
  baixa fidelidade de impressão.
- **Licença**: não podemos embutir o formulário oficial da WotC (IP). Só conteúdo SRD + nossos dados.

## Alternativas avaliadas
```yaml
opcoes:
  weasyprint:
    tipo: HTML + print-CSS (@page A4) -> PDF, Python puro
    fidelidade: alta (layout em colunas, web fonts, controle de página)
    custo: libs de sistema no Dockerfile (pango/cairo/gdk-pixbuf) -> imagem maior
    escolhida: true
  reportlab:
    tipo: desenho programático (canvas)
    fidelidade: alta mas trabalhosa (posicionar cada campo à mão)
    custo: imagem menor; muito código de layout
  client_jspdf:
    tipo: gera no navegador
    fidelidade: baixa em impressão; adiciona dependência JS ao frontend vanilla
```

## Decisão
Adotar **WeasyPrint** (renderiza um template **HTML + CSS de impressão** para PDF, 100% Python):
1. Serviço `app/services/ficha_pdf.py` (`FichaPDF`, POO) monta o **contexto** a partir de
   `ConstrutorDeFicha` (reaproveita os mesmos derivados da ficha web) e renderiza o template
   Jinja `app/templates/pdf/ficha.html` com `app/templates/pdf/ficha.css`.
2. Endpoint `GET /api/v1/characters/<id>/pdf` (autenticado; dono/mestre/ADMIN via
   `_personagem_acessivel`) devolve `application/pdf` com `Content-Disposition: attachment`.
3. **Imagens**: retrato/símbolo são resolvidos para **arquivo local** (`UPLOAD_DIR`) quando forem
   uploads nossos (`/api/v1/uploads/<nome>`); URLs externas **não** são buscadas pelo renderizador
   (evita SSRF/timeout) — degrada sem a imagem.
4. Dockerfile do backend ganha as libs de sistema do WeasyPrint; `requirements.txt` ganha
   `weasyprint`. Sem mudança de schema (feature só de leitura) → **sem migração**.
5. Frontend: botão **"Exportar PDF"** na ficha baixa via `fetch` → `blob` (envia o JWT no header).

## Layout (fidelidade ao oficial, recriado por nós)
```yaml
pagina_1:
  topo: nome, classe/nível, raça, antecedente, tendência, jogador, XP
  coluna_esq: 6 atributos (mod grande + valor), salvaguardas, perícias, percepção passiva, proficiência
  centro: CA / iniciativa / deslocamento / PV (máx/atual/temp) / dados de vida, ataques equipados
  coluna_dir: outras proficiências & idiomas, traços & recursos (cards), personalidade
pagina_2:
  identidade: idade/altura/peso/olhos/pele/cabelo/facção, aparência, aliados & organizações, tesouro
  midia: retrato + símbolo da facção (se uploads locais)
  historia: texto
```

## Consequências
- (+) Saída de serviço fiel, imprimível, reusando os cálculos já testados (uma fonte da verdade).
- (+) Mantém "backend só Python"; sem dependência de navegador.
- (−) Imagem Docker do backend maior (libs nativas). Build um pouco mais lento.
- (−) Fontes: usamos as do sistema (DejaVu) — fidelidade tipográfica "parecida", não idêntica.

## Notas
- Testes geram o PDF em memória (SQLite) e verificam magic bytes `%PDF`, `Content-Type`, permissão
  (403 sem acesso) e presença de campos-chave no HTML intermediário.
- Futuro: tema de PDF alternativo, watermark de homebrew, export de bestiário/PDM.
