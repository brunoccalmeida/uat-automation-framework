---
name: close-mission
description: Definition of Done da missão do chat. Use quando a implementação estiver pronta, antes do revisor e do PR, sem esperar o usuário pedir.
---
<!-- LTeX: language=pt-BR -->
Feche a missão; cada item é verificado, não presumido. O registro de sessão entra **no PR da própria missão** (#126): o squash grava código e estado num commit só; nunca abra PR separado de registro.

1. **Issues em dia:** as resolvidas citadas no PR (`Closes #N`); pendências descobertas viram issues novas com label `priority: P0/P1/P2`.
2. **`docs/ai-workflow/PROJECT_SESSION_SUMMARY.md`**, na branch da missão: só estado: tabela (uma ideia por linha, com a fila de PRs como ficará após o merge) e próxima missão recomendada pela prioridade das regras. O histórico (decisões, fontes consultadas, como o RED foi visto ou a mutação, achados) vai no **corpo do PR**. Decisão duradoura vira regra; armadilha que vai se repetir ganha uma linha no resumo. Cite issues, não o número do PR (ele ainda não existe).
3. **README.md e traduções** (`README.pt-BR.md`, `README.es.md`): o hook `validate-readme-metrics` corrige as métricas e reprova tradução defasada; texto novo é traduzido.
4. **Revisor** (`reviewer`) sobre o diff completo, resumo incluído; corrija os achados que procedem e registre os descartados com o porquê; atualize o resumo e o corpo do PR com o que as correções mudaram (o hook só corrige os READMEs).
5. Commit, PR e peça ao usuário `/ship-pr <n>`. O corpo do PR segue as seções de `.github/pull_request_template.md` (`gh pr create --body` ignora o modelo); issue nova segue os campos do formulário em `.github/ISSUE_TEMPLATE/`.
6. Com o PR integrado: confirme as issues fechadas (`gh issue view <n> --json state`) e o `master` local atualizado; avise que a missão terminou e que o próximo chat pode começar. Fato surgido no merge (ex.: check intermitente) vira issue e entra no resumo da próxima missão, não em PR novo.
