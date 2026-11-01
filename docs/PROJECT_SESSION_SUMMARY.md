<!-- LTeX: language=pt-BR -->
# PROJECT_SESSION_SUMMARY.md

> **Handoff entre chats.** Estado atual e próxima missão. Leia no início de cada chat (ver "Ciclo de Missão" em `.github/copilot-instructions.md`).
> Histórico detalhado vive no Git: PRs, commits e issues são a fonte de verdade; este arquivo não duplica histórico.

**Última atualização:** 01/11/2026 — fim da missão "verificar a economia de tokens" (#54, com #52)

---

## Estado atual

| Área | Estado |
| --- | --- |
| CI (`master`) | ✅ Verde em todas as camadas (unit, integration, E2E Chrome, smoke Chrome + Firefox, lint, report) |
| Testes | 256 unit · 71 integration · 55 cenários E2E (386 steps) · cobertura 99% (346 statements) |
| Relatório público | ✅ <https://brunoccalmeida.github.io/uat-automation-framework/> (Allure, publicado só em push no `master`) |
| Cobertura (Codecov) | ✅ Upload via **OIDC** (sem secret), `fail_ci_if_error: true`; pulado só onde o GitHub nega o token OIDC (Dependabot, PR de fork). `tests/test_codecov_upload.py` |
| Proteção do `master` | Ruleset "Protect master": PR obrigatório, **2 checks obrigatórios com nome estável: `ci-passed`** (gate que depende de todos os jobs do `Tests`, `tests/test_ci_gate.py`) **e `pip-audit`**, branch atualizada, histórico linear, sem force push, sem bypass |
| Segurança | **Toda action fixada por SHA de commit** (inclusive `actions/*`), barrada por `tests/test_workflow_pinning.py` · Duas fontes: Dependabot (alerts + security updates) e `pip-audit --strict` no workflow `Security` (PRs, push no `master` e diário); versão travada no `poetry.lock` (grupo dev) |
| Ferramentas | Python 3.14 · **Poetry ≥ 2.5.1** (`requires-poetry`; acompanha o Dependabot) · black 26 · **Selenium 4.52** · actions atualizadas (checkout 7, codecov v7) · browsers/drivers pré-instalados no runner |
| Regras do agente | Sempre carregadas: 104 linhas, **4,1 mil tokens medidos** no `/context` (estimativa ÷ 4 dava 2,45 mil; aqui são ~2,4 bytes/token). Escopo de caminho: `.claude/rules/` = `.github/instructions/` (Selenium, Python, workflows, Poetry), carga sob demanda confirmada no Claude Code; Copilot conferido pelo formato oficial + `chat.includeApplyingInstructions`. `tests/test_agent_rules.py` barra > 200 linhas, divergência entre as cópias e regressão da config de diagnósticos |
| Diagnósticos do editor | Ortografia só no Code Spell Checker (`en,pt_BR,es` + `cSpell.words`); LTeX+ só gramática. Uma edição de doc: 45 → 6 diagnósticos (~11 → ~1,6 KB). `.vscode/settings.json` e `extensions.json` versionados |
| Fila de PRs | Vazia |

## Próxima missão recomendada

**#27 — linters como portão real** (único P1). Detalhes no item 1 da fila.

Do #54 (medições em `docs/AGENT_TOKEN_SPEND.md`, seção "Verificação"): o diálogo *Account & usage* da extensão mostra % do limite do plano em 24 h somando sessões, não tokens por missão; o maior sinal é **subagentes = 72% do uso** (#56), não o tamanho das regras ("Trim CLAUDE.md" não apareceu). Diagnósticos só existem para arquivos abertos no editor: `getDiagnostics` vazio pode ser "não checado".

Fila priorizada (revisada em 01/11/2026 por melhores práticas: bloqueio → segurança → visibilidade → efeito composto → portões de qualidade antes de refatorar → dívida por risco):

1. #27 linters como portão real (P1; inclui #33 via pylint C0415 e mover config do flake8 para arquivo). Evidência do #35: o lint fatal do CI já falha hoje (`F821 undefined name 'when'` em `features/steps/sorting_steps.py`, import abaixo do 1º step) escondido por `continue-on-error`; black usa 88 colunas e flake8 79 → #28 ordem de imports (talvez junto, se `ruff`)
2. #56 o que cria subagentes (72% do uso; efeito composto em toda missão)
3. #26 `.gitignore` UTF-16 + portão de encoding (o Git o trata como binário; editar preservando CRLF, como no #54; `docs/PROJECT_SESSION*.*` ignorado mas versionado)
4. #29 `find_element` com `visibility_of` (risco de flaky)
5. #34 → #39 validador de métricas + READMEs traduzidos
6. #30 config/senha hardcoded · #32 fixtures · #31 page objects retornados

**Antes de trocar a versão do Python na matriz** (3.15 já saiu): resolva o #48 (`build-report` baixa `allure-results-py3.14` por nome fixo; a troca quebra o report, de forma visível). O ruleset já não depende da matriz (#36).

**Se o check `pip-audit` ficar vermelho** sem mudança de código: é CVE nova. Corrija atualizando o pacote; se não houver correção, `--ignore-vuln <ID>` em `security.yml` com justificativa e issue de remoção. Nunca `continue-on-error`.

**Ao abrir PR que atualize Selenium (ou outra dependência de execução):** triagem por `grep` no `py/CHANGES` oficial (remov/deprecat) + busca no código pelas APIs citadas, e todas as camadas localmente antes do merge. Assim foi feito no #38 (4.39 → 4.52: nenhuma API removida era usada).

## Backlog

Tudo em GitHub Issues com labels `priority: P0/P1/P2`: `gh issue list`.

**Ideias de funcionalidades futuras** (ainda sem issue): página de detalhes de produto · cenários do `error_user` · regressão visual (baseline de screenshots) · containerização com Docker.

## Decisões e aprendizados que guiam o trabalho

Viraram regras em `.github/copilot-instructions.md` (ou nos arquivos com escopo de caminho); aqui só o porquê, em uma linha cada:

- **SPA + Selenium:** a URL muda antes da página renderizar → navegação retorna só após o `PAGE_LOADED` do destino (`wait_until_loaded`, `submit_and_wait_for_outcome`).
- **Espere o estado ficar pronto antes de agir** — vale também para GitHub (`UNKNOWN`) e checks de CI (SHA da head).
- **Um PR aberto por vez** (ruleset exige branch atualizada; PRs paralelos se desatualizam). Dependabot agrupado.
- **TDD de duplo ciclo:** unitário falhando antes de cada unidade; teste que nunca falhou não prova nada (teste de mutação).
- **Versão maior é decisão humana:** ler notas de cada versão intermediária e checar "isto me afeta?" (ex.: codecov v7 removeu `file`).
- **Lock é gerado:** em conflito, regenere; nunca edite à mão.
- **RED pelo motivo certo:** no #43, injetar `urllib3` 1.x com `pip` quebrou o próprio `pip-audit` (exit 1 por crash, não por detecção). Leia a saída, não só o código de saída; o RED do CI foi provado com um commit temporário revertido.
- **Pin por SHA do commit, não da tag:** tag anotada é um objeto próprio; descasque (`^{}` no `git ls-remote`) e confirme em `git/commits/<sha>`. Toda asserção precisa de RED próprio: a do comentário de versão só falhou via mutação.
- **Credencial de curta duração (OIDC) > segredo fixo:** no #25 o Codecov dispensou token. Dependabot e PRs de fork não recebem `id-token: write` (nem secrets): falha ruidosa exige pular o passo exatamente ali, senão todo PR do Dependabot fica vermelho.
- **Pergunta ao dono vem com as melhores práticas antes** (princípio/fonte + recomendação), para decidir informado.
- **Check obrigatório pulado conta como aprovado:** gate com `always()` (não `!cancelled()`: workflow cancelado pularia o gate) e lista de permissão. A mutação `!cancelled()` foi a mais sutil do #36.
- **Gasto de tokens** (#41): todo turno reenvia todo o contexto; regras sempre carregadas < 200 linhas, `@import` não economiza, saídas filtradas na origem, subagente só com motivo. Medição: `/usage` antes do `/clear`. Detalhes e fontes: `docs/AGENT_TOKEN_SPEND.md`.
- **Diagnóstico do editor entra no contexto:** a extensão do VS Code anexa os avisos do LTeX+ a cada edição; sem `<!-- LTeX: language=pt-BR -->` na 1ª linha, um `.md` em português gera centenas de falsos positivos (462 em uma edição no #41). Todo `.md` novo fora do inglês leva o comentário.
- **Regra em dois agentes = duas cópias** (#35): Claude e Copilot leem escopo de caminho de pastas e frontmatter diferentes; a divergência é barrada por teste, não por disciplina.
- **Alterar o ruleset é bloqueado para o agente** (classificador de permissões, "CI Bypass"); só com autorização explícita do dono para aquela alteração. Ordem segura: CI do PR verde com o novo check → ruleset → merge (o merge valida a regra nova).

## Ambiente local (Windows)

- Chrome e Firefox instalados; interpretador do VS Code = `.venv` do projeto.
- Poetry instalado pelo instalador oficial (`%APPDATA%\pypoetry`). Se `poetry self update` quebrar no meio, recupere com `%APPDATA%\pypoetry\venv\Scripts\python -m pip install poetry==<versão>`.
- Windows PowerShell 5.1 grava `>>`/`Out-File` em UTF-16: não use para arquivos de texto do repo (causa da issue #26).
