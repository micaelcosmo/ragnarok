# Unit — Exportar ficha em PDF (E25)

> Ver decisão em `spec/backend/decisions/adr-0003-export-pdf.md`.

## Objetivo
Permitir baixar a ficha de um personagem em **PDF paginado, estilo oficial 5E**, reusando os
derivados já calculados pela plataforma.

## Contrato
```yaml
endpoint:
  metodo: GET
  rota: /api/v1/characters/<int:personagem_id>/pdf
  auth: obrigatório (JWT)
  permissao: dono | ADMIN | mestre da mesa do personagem  (_personagem_acessivel)
  resposta_ok:
    status: 200
    content_type: application/pdf
    headers:
      Content-Disposition: 'attachment; filename="ficha-<slug-nome>.pdf"'
    corpo: bytes começando com "%PDF"
  erros:
    404: personagem inexistente
    403: sem permissão de acesso
```

## Componentes
```yaml
servico:
  arquivo: app/services/ficha_pdf.py
  classe: FichaPDF
  responsabilidade:
    - montar o contexto a partir do Personagem + ConstrutorDeFicha (atributos_final, modificadores,
      ca, ataques_equipados, pericias, salvaguardas, percepcao_passiva, tracos_ativos, magias)
    - resolver imagens locais (UPLOAD_DIR) para file:// — ignorar URLs externas
    - renderizar Jinja (templates/pdf/ficha.html + ficha.css) e converter via WeasyPrint
  saida: bytes do PDF
template:
  - app/templates/pdf/ficha.html   # estrutura (2 páginas)
  - app/templates/pdf/ficha.css    # @page A4, colunas, blocos estilo oficial
endpoint:
  arquivo: app/api/characters.py   # GET .../pdf reusando _personagem_acessivel
frontend:
  - botão "Exportar PDF" na ficha (js/pages/character.js)
  - api.characters.pdf(id): fetch com Authorization -> blob -> download
infra:
  - requirements.txt: weasyprint
  - backend/Dockerfile: libs nativas (pango/cairo/gdk-pixbuf/shared-mime-info/fonts-dejavu)
```

## Critérios de aceite
```yaml
- baixa um PDF válido (magic bytes %PDF) para um personagem do próprio usuário
- Content-Type application/pdf + Content-Disposition attachment
- 403 quando outro usuário sem vínculo tenta baixar
- 404 para id inexistente
- o documento contém nome, os 6 atributos com modificador, CA, PV, perícias e traços
- degrada sem quebrar quando não há retrato/símbolo (ou são URLs externas)
- não introduz migração (feature somente-leitura)
```

## Fora de escopo (futuro)
- temas alternativos de PDF, watermark de homebrew, export de bestiário/PDM, fontes custom.
