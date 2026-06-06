# Frontend — Design System

Inspiração: **D&D Beyond** (UI escura, cards, acento vermelho/dourado) + identidade "pergaminho"
do Ragnarok legado.

## Paleta (CSS variables)
```css
--bg-900:#0f0d0b;  --bg-800:#1a1510;  --bg-700:#241d15;  --panel:#2c241b;
--gold:#d4af37;    --gold-dim:#8a6d3b; --red:#a4232b;     --red-bright:#c5303a;
--parch:#f4e4bc;   --parch-2:#e6d2a0; --ink:#2c241b;
--text:#e8e2d4;    --text-dim:#a99e88; --ok:#4c9a5e; --warn:#c9982f; --danger:#8b2c2c;
--font-title:'Cinzel',serif; --font-body:'Lato',system-ui,sans-serif;
```

## Tipografia
- Títulos / números de ficha: **Cinzel**.
- Corpo / formulários: **Lato**.

## Componentes base (CSS utilitário, sem framework)
- `.btn`, `.btn--primary` (vermelho), `.btn--gold`, `.btn--ghost`, `.btn--danger`.
- `.card` (painel escuro com borda dourada sutil), `.card--parch` (pergaminho p/ ficha).
- `.input`, `.select`, `.textarea`, `.field` (label + control).
- `.badge` (nível/ND/papel), `.pill`, `.chip`.
- `.stat-block` — bloco hexagonal de atributo (valor grande + modificador) estilo D&D Beyond.
- `.modal`, `.toast`, `.tabs`, `.skeleton`, `.empty-state`.
- Layout: `.app-shell` (topbar + sidebar + main), responsivo (sidebar colapsa < 900px).

## Padrão de ficha (estilo D&D Beyond)
- Cabeçalho: nome grande + raça/classe/nível + avatar/iniciais.
- Coluna esquerda: 6 **stat-blocks** (atributos) + salvaguardas + perícias.
- Centro: CA, Iniciativa, Deslocamento, PV (com barra), Inspiração.
- Direita/abas: Ataques & Magias, Equipamento, Traços, História.
- Modo leitura x edição (toggle "Editar").

## Acessibilidade
Contraste mínimo AA no texto; foco visível; `aria-label` em ícones.
