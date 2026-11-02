---
name: close-mission
description: Definition of Done da missão do chat. Use ao terminar a missão, sem esperar o usuário pedir, antes de avisar que o próximo chat pode começar.
---
<!-- LTeX: language=pt-BR -->
Feche a missão; cada item é verificado, não presumido.

1. **Fila de PRs vazia:** o PR do código integrado (o usuário roda `/ship-pr`) ou explicitamente descartado.
2. **Issues em dia:** as resolvidas fechadas pelo PR (`Closes #N`; confira `gh issue view <n> --json state`); pendências descobertas viram issues novas com label `priority: P0/P1/P2`.
3. **`docs/PROJECT_SESSION_SUMMARY.md`:** estado atual (tabela), um parágrafo "Do #N" com decisões, fontes consultadas, como o RED foi visto (ou a mutação) e achados; próxima missão recomendada pela prioridade das regras.
4. **README.md e traduções** (`README.pt-BR.md`, `README.es.md`): o hook `validate-readme-metrics` corrige as métricas e reprova tradução defasada; texto novo é traduzido.
5. Commit `docs:` em branch própria, PR, e peça ao usuário `/ship-pr <n>`.
6. Com o PR integrado e o `master` local atualizado, avise o usuário que a missão terminou e que o próximo chat pode começar.
