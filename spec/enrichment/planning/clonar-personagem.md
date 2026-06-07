# Unit — Clonar personagem (E36, nova)

> Agiliza a ficha: duplicar um personagem com 1 clique (variantes, backup rápido, base para um novo).
> Não é gamificação — é produtividade de ficha. Sem custo.

## API
```yaml
- POST /characters/<id>/clonar  (autenticado; fonte acessível por _personagem_acessivel)
    efeito: cria um novo Personagem do USUÁRIO ATUAL, copiando todos os campos da fonte,
      exceto id/user_id/created_at; nome recebe sufixo " (cópia)"
    resposta: 201 + a nova ficha
  - fonte inexistente -> 404 ; sem acesso -> 403
```

## Implementação
```yaml
- copia coluna a coluna (SQLAlchemy inspect), pulando id/user_id/created_at
- a cópia é sempre do usuário atual (mestre pode clonar uma ficha que ele acessa para a própria conta)
```

## Frontend
```yaml
- botão "📑 Clonar" no topo da ficha; ao concluir, navega para a cópia
```

## Critérios de aceite
```yaml
- clonar gera novo id != original, nome termina com "(cópia)"
- atributos/itens/recursos/etc. iguais aos da fonte
- a cópia pertence a quem clonou
- 404 inexistente; 403 sem acesso
- sem migração; sem regressão
```
