# Unit — Toggle EN/PT na UI (E28)

> Fecha o i18n visual: o backend já entrega `?idioma=pt` (cache `Traducao`, E24); faltava um
> **botão** para o usuário alternar e ver o conteúdo original (EN) ou traduzido (PT).

## Estado atual
- `auth.js`: `getIdioma()` (default "pt") / `setIdioma()` em localStorage.
- `api.js`: `catalog.list` e `reference.catalogGlobal` já anexam `?idioma=pt` quando o idioma é "pt".
- Afeta o conteúdo importado em inglês (open5e): **armas/armaduras/itens**. Spells/raças/classes do
  SRD já são pt-nativo (o `Tradutor` não toca em `idioma=pt`).

## Entrega
```yaml
frontend:
  - compendium.js: botão "🌐 PT | EN" no cabeçalho. Alterna setIdioma e re-renderiza as listas.
  - preferência persiste (localStorage) e vale para qualquer chamada que use idioma (ex.: lista de
    itens no gerenciador de equipamento da ficha).
backend:
  - nenhuma mudança (contrato ?idioma=pt já existe); apenas teste cobrindo /reference/armor.
```

## Critérios de aceite
```yaml
- botão mostra o idioma atual e alterna PT<->EN, re-renderizando as abas
- em EN: armas/armaduras aparecem com o nome original (ex.: "Greataxe"); em PT: "Machado Grande"
- a escolha persiste ao navegar/voltar (localStorage)
- /reference/armor?idioma=pt traduz pelo cache (teste); sem tradução -> original (fallback)
- sem regressão na suíte
```

## Fora de escopo (futuro)
- traduzir spells/feats/raças quando houver conteúdo importado em inglês desses tipos; seletor de
  idioma no header global (hoje fica no compêndio).
