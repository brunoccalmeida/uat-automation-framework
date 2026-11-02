---
name: ship-pr
description: Faz o squash merge de um PR no master só quando cada check obrigatório passou no SHA da head e o estado de merge está limpo. Só o usuário dispara, porque o merge no master publica o relatório.
disable-model-invocation: true
argument-hint: "[pr-number]"
---
<!-- LTeX: language=pt-BR -->
Integre ao `master` o PR $ARGUMENTS (sem número: o PR aberto da branch atual, `gh pr view --json number`).

1. Se houver outro PR aberto (`gh pr list`), pare e pergunte: um PR aberto por vez.
2. Leia `gh pr view <n> --json mergeStateStatus` até sair de `UNKNOWN` (logo após um merge no `master` ele ainda não foi calculado); `BEHIND`: `gh pr update-branch <n>`.
3. Rode `poetry run python scripts/merge_when_green.py <n>` como comando longo (até 30 min; em segundo plano, aguardando a notificação, sem polling). Ele lê os checks obrigatórios do ruleset, espera cada um no SHA da head e faz o squash merge só com tudo aprovado.
4. Saída 1: leia o motivo impresso, não repita o comando sem mudar nada. Check com falha: diagnostique pelo log (`gh run view <run-id> --log-failed`); `BEHIND` de novo: volte ao passo 2. Nunca `--admin`.
5. Saída 0: `git switch master`, `git pull --ff-only` e apague a branch local integrada.
