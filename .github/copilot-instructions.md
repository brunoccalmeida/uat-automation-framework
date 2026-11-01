<!-- LTeX: language=pt-BR -->
# UAT Automation Framework - Regras do projeto

Regras que valem em todo chat. Regras de uma parte do código ficam em arquivos com escopo de caminho (`.claude/rules/` e `.github/instructions/`, idênticos; `tests/test_agent_rules.py` cobra).

## Regra de ouro: TDD
Nunca implemente código de produção sem antes ter um teste falhando.

## Melhores práticas sempre
Toda decisão (código, testes, CI, ambiente, processo) segue as melhores práticas reconhecidas da indústria.

- Havendo mais de um caminho, recomende o indicado pelas melhores práticas e cite o princípio que o sustenta (ex.: dev/prod parity, YAGNI, fail fast).
- Toda pergunta de decisão ao usuário traz antes o que indicam as melhores práticas (princípio ou fonte) e a recomendação; o usuário decide já informado.
- O padrão é aplicar a prática estabelecida (documentação oficial, consenso da indústria). Investigação ou medição sob medida só quando a economia esperada supera claramente o custo de investigar; estimativa e suposição são rotuladas como tais.
- Não escolha atalhos por conveniência (ex.: contornar um problema de ambiente com código novo).
- Desvios só com justificativa explícita, registrada no commit ou na documentação.
- Regra deste arquivo que não siga as melhores práticas deve ser substituída, não contornada.

## Ciclo de missão (uma missão por chat)
Contexto longo degrada a qualidade; por isso cada chat cuida de **uma missão** (objetivo coeso, normalmente uma GitHub Issue) e **o estado do projeto mora no repositório, não na conversa**. O handoff é parte do trabalho: nunca depende de o usuário pedir.

**Início de cada chat** (automático):
1. Ler `docs/PROJECT_SESSION_SUMMARY.md` (estado atual e próxima missão recomendada).
2. Listar issues e PRs abertos (`gh issue list`, `gh pr list`).
3. Propor a missão de maior prioridade e confirmar com o usuário. Prioridade: bloqueio → segurança → visibilidade → dívida técnica (labels `priority: P0/P1/P2`).

**Fechamento da missão** (Definition of Done, automático):
1. Fila de PRs vazia: tudo integrado ou explicitamente descartado.
2. Issues em dia: resolvidas fechadas pelo PR (`Closes #N`); pendências descobertas registradas como novas issues.
3. `docs/PROJECT_SESSION_SUMMARY.md` atualizado: estado atual, decisões e próxima missão recomendada.
4. README.md (incluindo métricas) atualizado.
5. Avisar o usuário que a missão terminou e que o próximo chat pode começar.

## Gasto de tokens (contexto)
Cada turno reenvia todo o contexto; contexto longo custa mais e piora a aderência às regras. Fontes, porquês e medição: `docs/AGENT_TOKEN_SPEND.md`.

- **Regras sempre carregadas < 200 linhas**, só o que vale em todo chat. `@import` não economiza; regra de uma parte do código vai para arquivo com escopo de caminho.
- **Não repita o que linter/teste já impõe**; regra sem exceção vira teste ou hook, não ênfase.
- **Filtre saídas na origem** (`grep`, `head`, `--jq`, `gh run view --log-failed`, leitura por trecho); nunca despeje log de CI ou notas de versão inteiras.
- **Documentação web por seção, não página inteira:** sumário (`curl -s <url>.md | grep -n '^##'`) e depois só a seção (`sed -n '/^### X/,/^### /p'`). O WebFetch devolve docs em Markdown crus e inteiros.
- **Subagente só com motivo**: trabalho paralelo independente, isolar saída volumosa ou revisor independente. Ele recomeça do zero e soma requisições. Tarefa simples: modelo menor (`model: haiku`); revisor mantém o modelo da sessão.
- **Medir antes e depois de cada mudança que promete economia** (`/context`, tamanho da saída), não por rotina: o `/usage` por missão não distinguia o sinal do arredondamento.
- **Modelo e esforço fixos durante o chat** (trocar invalida o cache). Duas correções sem sucesso: `/clear` e um prompt melhor.

## TDD/BDD: duplo ciclo
Double-loop TDD (Freeman & Pryce, *Growing Object-Oriented Software, Guided by Tests*): um ciclo externo de aceitação guia ciclos internos de unidade.

1. **Externo (Behave):** escreva o cenário Gherkin e os steps; rode `behave` e veja FALHAR pelo motivo esperado (documente o erro).
2. **Interno (pytest), para cada unidade que o cenário exige:** teste unitário FALHANDO → implementação MÍNIMA para passar → refatoração com tudo verde.
3. **Fechamento:** o cenário externo passa; testes de integração (driver real) cobrem o contrato do Page Object com o DOM; rode todas as camadas (unit, integração, E2E).

Convenções do Behave: cenários em `features/`, steps em `features/steps/`. Nunca comece pelo Page Object: feature → steps → `behave` (RED) → implementação (GREEN). Se você está escrevendo código que não falha em um teste existente, pare.

Todo teste deve ter sido visto falhando (RED) ao menos uma vez. Teste que nunca falhou não prova nada; se o RED não foi observado, confirme com um teste de mutação (desfaça a correção e veja o teste falhar).

**Hierarquia:** E2E (Behave, fluxos de usuário) · integração (Page Objects com driver real) · unit (lógica isolada, mocks). Testes de integração de condições de corrida são probabilísticos; a garantia determinística vem dos unitários (ex.: ordem clique → espera).

## Espere o estado ficar pronto antes de agir
Toda ação seguida de uma leitura ou decisão deve esperar o resultado da ação, nunca um estado intermediário. Vale para testes, scripts e automação de CI. Pergunte: *"isto vê o resultado da ação, ou um estado que ainda está mudando?"*

| Contexto | Estado intermediário (armadilha) | Como esperar corretamente |
|---|---|---|
| Selenium em SPA | A URL muda antes de a nova página renderizar | Navegação retorna só após o `PAGE_LOADED` do destino (`wait_until_loaded`) |
| Formulário com erro | Mensagem de erro antiga ainda na tela parece o resultado do novo envio | Remover o estado antigo antes de agir (`submit_and_wait_for_outcome`) |
| API do GitHub | `mergeStateStatus` = `UNKNOWN` logo após um merge no `master` | Aguardar até o estado deixar de ser `UNKNOWN` antes de decidir |
| Checks de CI | Logo após atualizar a branch, os checks verdes ainda são do commit anterior | Consultar os checks pelo SHA da head atual |
| `gh pr checks --watch --required` | Retorna antes de o `ci-passed` existir (o gate só aparece quando seus `needs` terminam) e mostra só o `pip-audit` | `gh run watch <run-id> --exit-status` no run do `Tests`; depois ler os checks obrigatórios do SHA da head e fazer o merge com `--match-head-commit` |

- **"Ainda não sei" não é "sim".** `UNKNOWN`, pendente ou resposta vazia significam *esperar*, nunca *seguir*.
- **Quando o estado final pode ser igual ao inicial**, não há como saber se a ação ocorreu: altere o estado inicial antes de agir (ex.: fechar o erro antigo antes de reenviar).
- **Espere por condição, nunca por tempo fixo** (`sleep`). Em polling, o intervalo é só o ritmo da checagem; a saída do laço é sempre a condição.

## Diagnóstico de erros
Nunca "chute" soluções. Antes de propor uma correção:

1. **Observe:** mensagem completa (não só a última linha), stack trace, linha e tipo da exceção.
2. **Contextualize:** código ao redor (±10 linhas), dependências, padrões do projeto.
3. **Investigue:** busque o mesmo padrão no código; compare com código que funciona.
4. **Diagnostique a causa raiz**, não o sintoma: bug ou problema de design? Há outros locais com o mesmo problema?
5. **Planeje e implemente** uma solução consistente com a arquitetura (fix único ou refactor sistêmico? impacto em testes?), corrigindo todos os locais afetados.
6. **Valide:** erro resolvido, sem regressão, casos de borda cobertos.

Exemplo: `AttributeError: 'Context' object has no attribute 'cart_page'` não se resolve criando `context.cart_page` no step; veja como os outros steps criam pages e padronize todos. Erro por erro sem ver o padrão (ex.: corrigir uma `ImportError` por vez) também é chute.

Ao reportar um erro: **erro observado**, **causa raiz** (o porquê), **análise** (o que foi investigado, padrão, impacto), **solução proposta** com justificativa e **prevenção**.

## Comunicação
- Sempre em **português (Brasil)**; código em inglês.
- Explicar o **porquê**, não só o quê; opiniões fundamentadas, não só concordância.

## Dependências e segurança
- Poetry para dependências; nunca commitar credenciais ou dados sensíveis; config separada do código.
- Consulte a documentação oficial antes de resolver problemas.
- **Duas fontes de vulnerabilidades**: Dependabot (GitHub Advisory) e `pip-audit` (PyPI/OSV). Os bancos divergem em conteúdo e momento; "zero alertas" só vale após confirmar que a varredura ocorreu.
- **Versão maior é decisão humana**: leia as notas de cada versão maior intermediária e verifique se cada mudança incompatível afeta este projeto. Meça o impacto (ex.: rodar o formatador novo) antes de concluir.

## Git e Pull Requests
- **Conventional Commits** (`feat`, `fix`, `refactor`, `test`, `docs`, `style`, `perf`, `build`, `ci`, `chore`; escopo opcional, ex.: `build(deps):`), commits atômicos.
- O `master` é protegido (ruleset): só aceita PR com os checks obrigatórios (`ci-passed` e `pip-audit`) verdes e **branch atualizada**. Cada merge desatualiza os outros PRs abertos, custando novo ciclo de CI e revisão. Por isso:
  - **Um PR aberto por vez.** Trabalho pronto espera em commit local até a fila esvaziar. Merge antes do próximo PR, sem empilhar (empilhar só se justifica com revisão demorada, em equipes).
  - **Dependabot agrupado:** GitHub Actions e Python minor/patch em um PR cada; só versões maiores do Python ficam isoladas, uma por PR.
  - **Merge só com checks verdes no SHA da head do PR.** Branch atrás do `master`: atualizar e esperar o CI de novo.
  - **Squash merge**, histórico do `master` linear. **Nunca `--admin`** para furar o ruleset: se a regra atrapalha, discuta a regra.
  - Automação de merge segue lista de permissão: só faz o merge se **cada** check obrigatório estiver explicitamente aprovado; qualquer outro estado (falha, pendente, resposta vazia) interrompe.

## Princípios
Explícito é melhor que implícito; simples é melhor que complexo; legibilidade conta; erros nunca passam em silêncio; diante da ambiguidade, recuse a tentação de adivinhar.
