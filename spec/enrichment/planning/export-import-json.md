# Unit — Exportar/Importar ficha em JSON (E37, nova)

> Agiliza a ficha: **backup/portabilidade** dos dados (transferir entre contas, versionar offline).
> Complementa o PDF (impressão) com um formato de **dados**. NÃO é importação por LLM/PDF
> (o dono vetou) — é só serialização/deserialização do nosso próprio modelo.

## API
```yaml
- GET /characters/<id>/export  (acessível por _personagem_acessivel)
    resposta: application/json (attachment "ficha-<slug>.json")
    corpo: { "_ragnarok": "ficha", "versao": 1, "dados": {<campos da ficha, sem derivados/ids/itens equipados>} }
- POST /characters/import  (autenticado)
    body: o JSON exportado (aceita {dados:{...}} ou os campos direto)
    efeito: cria um novo Personagem do usuário atual a partir dos campos suportados (_aplicar_campos)
    resposta: 201 + a nova ficha
  - body inválido / sem nome -> 400
```

## Implementação
```yaml
- export: to_dict(incluir_derivados=False) menos id/user_id/mesa_id/armadura_equipada_id/armas_equipadas
  (refs de itens não portáveis); embrulha em {_ragnarok, versao, dados}
- import: extrai `dados` (ou usa o corpo), exige `nome`, cria Personagem(user_id atual) + _aplicar_campos
```

## Frontend
```yaml
- ficha: botão "⬇️ Exportar JSON" (download via blob autenticado)
- dashboard: botão "⬆️ Importar ficha" (seleciona .json -> POST import -> navega para a nova)
```

## Critérios de aceite
```yaml
- export devolve JSON com os campos da ficha (nome, atributos, recursos, moedas, etc.)
- import cria nova ficha do usuário com esses campos
- import sem nome -> 400
- itens equipados não são portados (limitação consciente)
- sem migração; sem regressão
```
