---
name: ship-pr
description: Liga o auto-merge nativo (squash) de um PR no master, preso ao SHA da head, e espera o resultado; quem decide é o ruleset. Só o usuário dispara, porque o merge no master publica o relatório.
disable-model-invocation: true
argument-hint: "[pr-number]"
---
<!-- LTeX: language=pt-BR -->
Integre ao `master` o PR $ARGUMENTS (sem número: o PR aberto da branch atual, `gh pr view --json number`).

Quem decide se pode integrar é o **ruleset**; a skill liga o [auto-merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request) e espera o resultado. Toda a espera mora no `scripts/wait_for_merge.py` (prazos no docstring): nunca escreva laço de espera no chat. Nunca `--admin`.

1. Se houver outro PR aberto (`gh pr list`), pare e pergunte: um PR aberto por vez.
2. Leia `gh pr view <n> --json state,headRefOid,mergeStateStatus`.
   - `MERGED`: vá ao passo 6.
   - `UNKNOWN` (logo após um merge no `master` ele ainda não foi calculado): leia de novo, no máximo 3 vezes, uma leitura por comando; persistindo, pare e reporte.
   - `BEHIND`: `gh pr update-branch <n>` e leia de novo (o SHA da head mudou).
   - `DIRTY`: pare; o conflito se resolve localmente.
3. `gh pr merge <n> --auto --squash --match-head-commit <sha>`, sozinho no comando. Saída diferente de 0: leia o stderr e pare. Com o PR já pronto, o `gh` integra direto em vez de ligar o auto-merge; o passo 4 cobre os dois casos.
4. Rode `poetry run python scripts/wait_for_merge.py <n> <sha>` em segundo plano, aguardando a notificação, **sem nada depois dele na linha**: o código de saída notificado é o do último comando, e um `; echo` o trocaria por 0.
5. Saída 1: leia o motivo impresso, não repita o comando sem mudar nada.
   - Check obrigatório com falha: diagnostique pelo log (`gh run view <run-id> --log-failed`) e, depois do push da correção, volte ao passo 2.
   - `BEHIND`, auto-merge desligado ou head nova: volte ao passo 2.
   - Prazo esgotado: reporte o último estado impresso.
   - Com check falho ou prazo esgotado o auto-merge **continua ligado**: um re-run verde integra sozinho. Para impedir, `gh pr merge <n> --disable-auto`.
6. Saída 0: confirme `MERGED` (`gh pr view <n> --json state`) e só então `git switch master`, `git pull --ff-only` e apague a branch local integrada. Repasse ao usuário cada `WARNING`: é um check fora do ruleset que não passou, com nome, tempo pendente e remédio.
7. Prazo esgotado ou `WARNING`: se o usuário pode ter saído, avise também com `PushNotification`.
8. Espera interrompida (notificada como parada, ou a sessão reaberta): leia primeiro o estado real (`gh pr view <n> --json state,autoMergeRequest,mergeStateStatus`), conte ao usuário e só então retome do passo adequado; nunca presuma que a espera continua.

**Limite:** tarefas em segundo plano morrem com a sessão, e nada acorda uma sessão fechada. O auto-merge segue no GitHub, mas ninguém reporta: a próxima mensagem ou chat começa pelo passo 8.
