# Planning — E20: Identidade & Imagens do Personagem

> Traz a "página 2" da ficha oficial: retrato, símbolo da facção e dados de identidade/história.
> Decisões aprovadas: **upload + volume**, **identidade completa**, **corrigir #1 (stat block)** no mesmo ciclo.

## Modelo de dados (Personagem — campos novos)
```yaml
identidade:
  idade: str        # "32" (texto livre p/ aceitar "32 anos")
  altura: str       # "94 cm"
  peso: str         # "26 kg"
  olhos: str        # "Verdes"
  pele: str         # "Branca"
  cabelo: str       # "Ruivo"
  faccao: str       # "Tribo da Garra de Yelt"
  aparencia: text   # descrição livre
  aliados: text     # aliados & organizações
  tesouro: text
imagens:
  avatar_url: str       # JÁ EXISTE -> retrato do personagem
  simbolo_faccao_url: str  # NOVO -> emblema da facção
```
Migração Alembic não-destrutiva (campos nullable / sem default problemático).

## Upload de imagem (seguro)
```yaml
endpoint:
  POST /uploads (multipart form, campo 'arquivo'):  # auth obrigatório
    valida:
      - extensão ∈ {png, jpg, jpeg, webp}
      - content-type coerente
      - MAGIC BYTES (sniff real do conteúdo; não confia na extensão)
      - tamanho <= 2 MB (Flask MAX_CONTENT_LENGTH + nginx client_max_body_size 4m)
    grava:
      - nome ALEATÓRIO (uuid4 + ext segura) — sem nome do usuário, anti path-traversal
      - pasta /app/uploads (volume Docker 'ragnarok_uploads')
    responde: { url: "/uploads/<uuid>.<ext>" }
servir:
  - nginx serve /uploads/ do volume, com Content-Disposition/again sem execução (estáticos puros)
  - ou backend serve via send_from_directory (fallback)
seguranca:
  - allowlist de tipo + sniff (Pillow.verify OU checagem de assinatura) -> rejeita SVG/HTML/scripts
  - nome gerado no servidor (uuid) -> nunca usa caminho do cliente
  - limite de tamanho no app e no nginx
  - hook anti-segredo permanece verde
limpeza:
  - ao trocar retrato/símbolo OU excluir personagem, remove o arquivo órfão (best-effort)
```

## API
```yaml
POST /uploads                      # (auth) envia imagem -> {url}
PUT  /characters/<id>              # passa a aceitar os campos novos de identidade + simbolo_faccao_url
GET  /characters/<id>              # to_dict inclui os campos novos
# servir: GET /uploads/<arquivo>   # via nginx (estático) — somente leitura
```
Permissão de upload: qualquer autenticado pode enviar; vincular ao personagem segue ownership normal.

## Frontend
- **Retrato** no cabeçalho da ficha (usa `avatar_url`); fallback nas iniciais (atual).
- Nova aba **"Identidade"**: campos físicos + facção (com **símbolo**), aparência, aliados, tesouro — editáveis.
- Botões de **upload** (retrato e símbolo) no formulário de edição; também aceita colar URL.

## Fix #1 (stat block base × modificador final)
- `renderStats()` passa a usar `derivados.atributos_final[chave]` como número do bloco
  (mantém o valor base editável no formulário). Número e modificador batem.

## Infra
- `docker-compose.yml` e `docker-compose.dev.yml`: volume `uploads` montado no backend; nginx
  com `client_max_body_size 4m` e location `/uploads/`.
- Migração roda no boot (entrypoint `flask db upgrade`).

## Testes
```yaml
backend:
  - upload aceita PNG válido -> 200 + url
  - upload recusa tipo inválido (ex.: .txt/.svg) -> 400
  - upload recusa arquivo > limite -> 413/400
  - upload exige autenticação -> 401
  - PUT personagem grava campos de identidade + simbolo_faccao_url; GET retorna
frontend:
  - smoke: aba Identidade aparece/edita; retrato renderiza; stat block (#1) bate número×mod
```

## Processo (deploy)
1. specs + status (E20) + observador HTML com steps.
2. backend + migração + testes (pytest verde).
3. fix #1 + frontend (aba + upload).
4. infra (compose dev/main + nginx).
5. docs (README, CLAUDE, changelogs).
6. **stack DEV isolada**: subir, migrar, testar upload/identidade.
7. **backup** prod -> deploy `up --build -d` (sem -v) -> verificar dados.
8. smoke público + finalizar observador. Link mantido.

## Critérios de aceite
- Enviar uma imagem retorna URL servível; vira o retrato na ficha; símbolo da facção idem.
- Upload rejeita não-imagem e arquivos grandes; nome no servidor é aleatório.
- Campos de identidade persistem e aparecem; migração preserva dados existentes.
- Stat block mostra valor final (ex.: DES 18/+4).
