# Frontend — Fluxos de UX

## Sessão
1. Visitante → `/login` ou `/register`. Sucesso salva `access_token` em `localStorage`.
2. Topbar mostra nome + papel + sair. Rotas protegidas redirecionam p/ login sem token.

## JOGADOR
- Dashboard → "Meus Personagens" (cards) + "Minhas Mesas".
- "Novo Personagem" → wizard: (1) Raça → (2) Classe → (3) Antecedente →
  (4) Atributos (point-buy/manual) → (5) Perícias/Salvaguardas → cria → abre ficha.
- Ficha: leitura imersiva; botão "Editar" abre formulários inline; PV ajustável; rolagens
  mostram valor calculado.
- "Entrar em mesa" → informa código → entra → vincula um personagem.

## MESTRE
- Tudo do jogador + "Minhas Mesas (Mestre)": criar mesa (gera código), ver membros,
  remover jogador, ver personagens dos jogadores.
- Bestiário da mesa: criar/editar monstros e PDMs.

## ADMIN
- Painel: métricas (cards de contagem). Tabela de usuários com busca e troca de papel.
- Compêndio editável (catálogo SRD).

## Navegação (SPA leve via hash router)
`#/login #/register #/dashboard #/characters/:id #/characters/new
 #/campaigns #/campaigns/:id #/bestiary #/compendium #/admin`
