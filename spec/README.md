# spec/ — Spec-Driven Development

Esta pasta é a "fonte da verdade" do **design** do Ragnarok. O código segue as specs;
quando a realidade diverge, atualiza-se a spec **e** o `changelog.md` correspondente.

```
spec/
├── backend/
│   ├── planning/    # arquitetura, domínio, contrato de API, RBAC
│   ├── units/       # spec por unidade (entradas/saídas/critérios de aceite)
│   ├── tests/       # plano de testes (TDD)
│   ├── decisions/   # ADRs
│   └── changelog.md
└── frontend/
    ├── planning/    # design system, fluxos de UX, páginas
    ├── units/       # spec do cliente de API/sessão e componentes
    ├── tests/       # plano de testes (smoke/E2E)
    └── changelog.md
```

## Ciclo de trabalho (por task)
1. **Planning** — confirma a intenção na spec de planning.
2. **Unit spec** — define entradas, saídas e critérios de aceite.
3. **Teste (RED)** — escreve o teste que falha.
4. **Código (GREEN)** — implementa até passar.
5. **Refatora** — limpa mantendo verde.
6. **Changelog + status.md** — registra e marca a task.
7. **Próxima task** (se a anterior não passou, volta a ela).

Progresso global e lista de tasks: ver [`/status.md`](../status.md).
