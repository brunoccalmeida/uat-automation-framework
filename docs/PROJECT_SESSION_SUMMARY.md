<!-- LTeX: language=pt-BR -->
# PROJECT_SESSION_SUMMARY.md

> **Handoff entre chats.** Estado atual e próxima missão. Leia no início de cada chat (ver "Ciclo de Missão" em `.github/copilot-instructions.md`).
> Histórico detalhado vive no Git: PRs, commits e issues são a fonte de verdade; este arquivo não duplica histórico.

**Última atualização:** 01/11/2026 — fim da missão "`.gitignore` UTF-16 + portão de encoding" (#26)

---

## Estado atual

| Área | Estado |
| --- | --- |
| CI (`master`) | ✅ Verde em todas as camadas (unit, integration, E2E Chrome, smoke Chrome + Firefox, lint, report) |
| Testes | 325 unit · 71 integration · 55 cenários E2E (386 steps) · cobertura 99% (346 statements) |
| Relatório público | ✅ <https://brunoccalmeida.github.io/uat-automation-framework/> (Allure, publicado só em push no `master`) |
| Cobertura (Codecov) | ✅ Upload via **OIDC** (sem secret), `fail_ci_if_error: true`; pulado só onde o GitHub nega o token OIDC (Dependabot, PR de fork). `tests/test_codecov_upload.py` |
| Proteção do `master` | Ruleset "Protect master": PR obrigatório, **2 checks obrigatórios com nome estável: `ci-passed`** (gate que depende de todos os jobs do `Tests`, `tests/test_ci_gate.py`) **e `pip-audit`**, branch atualizada, histórico linear, sem force push, sem bypass |
| Segurança | **Toda action fixada por SHA de commit** (inclusive `actions/*`), barrada por `tests/test_workflow_pinning.py` · Duas fontes: Dependabot (alerts + security updates) e `pip-audit --strict` no workflow `Security` (PRs, push no `master` e diário); versão travada no `poetry.lock` (grupo dev) |
| Portão de lint | CI roda `pre-commit run --all-files`: os mesmos hooks do commit local (black, **ruff** (regras `E`, `W`, `F` do flake8, que ele substituiu no #73, e `I`, ordem de imports, #28), pylint, pyright, validador de métricas…). O editor ordena com a mesma ferramenta: `charliermarsh.ruff` recomendada e `source.organizeImports.ruff` ao salvar (o `source.organizeImports` genérico chamava também o Pylance, de ordem diferente); `tests/test_lint_gate.py` cobra. Linters via Poetry (versão do `poetry.lock`), sem exclusões, sem `--exit-zero`/`continue-on-error` (`tests/test_lint_gate.py`). 0 avisos no repo. Config toda no `pyproject.toml`: `[tool.ruff.lint]` (sem `ignore`: E203 é só preview no ruff e o E701 dele aceita o `class A: ...` do black; ambos com 88 colunas por padrão), `[tool.pylint.*]` e `[tool.pyright]`. Supressões só com o porquê ao lado. Auxiliares de teste em `tests/helpers/` (fora do `name-tests-test`) |
| Encoding e fim de linha | Hook `check-text-encoding` (`scripts/check_text_encoding.py`, #26) barra texto fora de UTF-8 **ou com NUL** (NUL é UTF-8 válido: só decodificar aceitaria o `.gitignore` quebrado). `types: [text]`: o `identify` classifica nomes conhecidos pelo nome, então UTF-16 chega ao hook; extensão desconhecida em UTF-16 escapa (limitação documentada). `.gitattributes` `* text=auto`: índice sempre LF, disco no padrão da plataforma (CRLF no Windows); `eol=lf` rejeitado por forçar LF no disco. `tests/test_check_text_encoding.py` |
| Ferramentas | Python 3.14 · **Poetry ≥ 2.5.1** (`requires-poetry`; acompanha o Dependabot) · black 26 · ruff 0.17 · pyright 1.1.414 (grupo dev) · **Selenium 4.52** · actions atualizadas (checkout 7, codecov v7) · browsers/drivers pré-instalados no runner |
| Regras do agente | Sempre carregadas: 106 linhas (#58: docs por seção, prática estabelecida por padrão, subagente simples com modelo menor), **4,1 mil tokens medidos no #54** no `/context` (estimativa ÷ 4 dava 2,45 mil; aqui são ~2,4 bytes/token). Escopo de caminho: `.claude/rules/` = `.github/instructions/` (Selenium, Python, workflows, Poetry), carga sob demanda confirmada no Claude Code; Copilot conferido pelo formato oficial + `chat.includeApplyingInstructions`. `tests/test_agent_rules.py` barra > 200 linhas, divergência entre as cópias e regressão da config de diagnósticos |
| Diagnósticos do editor | Ortografia só no Code Spell Checker (`en,pt_BR,es` + `cSpell.words`); LTeX+ só gramática. Uma edição de doc: 45 → 6 diagnósticos (~11 → ~1,6 KB). `.vscode/settings.json` e `extensions.json` versionados |
| Hook de saída de testes | `PreToolUse` (`Bash\|PowerShell`) em `.claude/settings.json` reescreve `pytest` → `-q` e `behave` → `-f progress2` (`scripts/filter_test_output.py`, #65): `behave` 51 → 1,1 KB, `pytest -v` 28 → ~1,6 KB. Flags nativas, sem pipe (o pipe troca o exit code pelo do `head`); `behave` com `-f` explícito fica intacto. `tests/test_filter_test_output.py` |
| Code intelligence | Plugin oficial `pyright-lsp` ligado no escopo do projeto (`enabledPlugins` em `.claude/settings.json`); servidor por máquina via `pipx install "pyright[nodejs]"` (precisa estar no PATH; o `.venv` não está no PATH da extensão). `[tool.pyright] venv = ".venv"` + `poetry.toml` (`in-project`) para resolver os imports do projeto. Verificado: erro proposital → diagnóstico `reportAssignmentType`, assíncrono (chega logo após a edição). Passo a passo por máquina em `docs/AGENT_TOKEN_SPEND.md`. `tests/test_agent_rules.py` |
| Fila de PRs | Vazia |

## Próxima missão recomendada

**#82 — `is_element_present` com `visibility_of`** (mesmo risco do #29, agora nas verificações; decidir se o nome muda para `is_element_visible`, 12 chamadores incluindo `smoke_steps.py`).

Do #29: o teste `test_find_element_uses_visibility_condition` já existia e **passava com `presence_of`**: só cobrava `wait.until` chamado, não a condição. Nome promete, asserção não cobra: teste que nunca podia falhar. Corrigido no padrão do arquivo (`patch("pages.base_page.EC")` + `assert_called_once_with(locator)`), RED visto ("called 0 times"). Chamadores que poderiam depender de elemento escondido (o `<select>` de ordenação) verificados no navegador real: todas as camadas verdes. `is_element_present` ficou fora por atomicidade (#82).

Do #73 (flake8 → ruff): RED por comportamento, não por lista. Tirar `flake8` de `LINTERS` só reduz testes parametrizados e não falha nada; o RED veio de `TestRuffReplacesFlake8` (ruff seleciona E/W/F; flake8 fora do hook, das dependências e sem `.flake8`). A tradução 1:1 do `.flake8` (`ignore E203,E701`) foi **medida antes de copiada**: o próprio ruff avisa que o E203 "has no effect" (preview), e o E701 dele aceita os corpos `...` do black. As duas exceções seriam config morta, então não entraram. 0 achados com E/W/F/I. O validador de métricas pegou o total (395 → 393) mas não a linha "Lint gate" da tabela (24 → 22), corrigida à mão: é o #34 na prática. Avaliar as regras do ruff que se sobrepõem ao pylint ficou para issue própria (#78).

Do #26: o arquivo era UTF-8 com só a cauda em UTF-16 sem BOM. O TDD estrito foi questionado pelo dono; consenso da indústria (meta-análises mistas sobre TDD como ritual; regressão-primeiro e "ver falhar" incontestes): aqui o rótulo certo é **teste de regressão + portão visto barrando pelo pre-commit**, não ciclos red-green. Hipótese minha (o `identify` trataria UTF-16 como binário e o hook nunca o veria) foi **refutada em parte por medição** antes de virar código. Mutação: sem a checagem de NUL, só o teste de NUL falha; com "sempre reclama", os 5 de "passa".

Do #28 (ruff só com a regra `I`): decisão ruff × isort tomada com medição (os dois achavam os mesmos ~12 arquivos; as regras do ruff equivalentes ao flake8 dão 0 achados). ruff porque uma ferramenta substitui flake8 + isort; o isort seria removido na migração (retrabalho). Troca do flake8 em PR próprio (#73), por atomicidade. Commit `style` antes do `ci`: o hook novo barraria o próprio commit se entrasse antes da correção (nunca `--no-verify`).

Do #58 (detalhes em `docs/AGENT_TOKEN_SPEND.md`, seção "Levantamento de mercado e lacunas"): os "72% de subagentes" (#56) eram leitura errada da métrica: a fatia de uma recomendação é o uso **ao qual ela se aplica**, não o que custou. Estimativa (pesos de custo supostos): subagentes ≈ 1,6%; a fatia veio de uma sessão com várias missões sem `/clear` (contexto médio 277 mil; as de uma missão, ~75 mil, com trabalhos diferentes: correlação). O maior consumo por ferramenta é o **WebFetch (21%)**, que traz docs em Markdown inteiros: nova regra, documentação por seção. Correção feita no mesmo chat, a pedido do dono: o levantamento tinha presunções (pesos de custo não conferidos, correlação lida como causa, práticas oficiais rejeitadas com amostra pequena). Critério agora em regra: prática estabelecida por padrão; medição sob medida só se a economia supera claramente o custo de investigar. Ação do dono: desligar no `/mcp` conectores sem uso (#61 fechada, sem medição).

Fila priorizada (revisada em 01/11/2026 por melhores práticas: bloqueio → segurança → visibilidade → efeito composto → portões de qualidade antes de refatorar → dívida por risco):

1. #82 `is_element_present` com `visibility_of` (risco de flaky)
2. #34 → #39 validador de métricas (já tem testes de caracterização, `tests/test_validate_readme_metrics.py`) + READMEs traduzidos
3. #30 config/senha hardcoded · #31 page objects retornados
4. #78 avaliar regras do ruff que se sobrepõem ao pylint (medido, separado)

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
- **Cache de venv pela versão exata do Python** (#84): o venv aponta para o interpretador exato e as imagens de runner trocam de patch aos poucos; com a chave `3.14`, um venv do 3.14.9 foi restaurado no 3.14.8, o `poetry install` foi pulado (cache hit) e o job rodou sem `behave`. Chave por `steps.setup-python.outputs.python-version` (doc do snok/install-poetry), `tests/test_venv_cache_key.py`.
- **RED pelo motivo certo:** no #43, injetar `urllib3` 1.x com `pip` quebrou o próprio `pip-audit` (exit 1 por crash, não por detecção). Leia a saída, não só o código de saída; o RED do CI foi provado com um commit temporário revertido.
- **Pin por SHA do commit, não da tag:** tag anotada é um objeto próprio; descasque (`^{}` no `git ls-remote`) e confirme em `git/commits/<sha>`. Toda asserção precisa de RED próprio: a do comentário de versão só falhou via mutação.
- **Credencial de curta duração (OIDC) > segredo fixo:** no #25 o Codecov dispensou token. Dependabot e PRs de fork não recebem `id-token: write` (nem secrets): falha ruidosa exige pular o passo exatamente ali, senão todo PR do Dependabot fica vermelho.
- **Pergunta ao dono vem com as melhores práticas antes** (princípio/fonte + recomendação), para decidir informado.
- **Check obrigatório pulado conta como aprovado:** gate com `always()` (não `!cancelled()`: workflow cancelado pularia o gate) e lista de permissão. A mutação `!cancelled()` foi a mais sutil do #36.
- **Gasto de tokens** (#41): todo turno reenvia todo o contexto; regras sempre carregadas < 200 linhas, `@import` não economiza, saídas filtradas na origem (docs web por seção, #58), subagente só com motivo; fatia de recomendação do `/usage` ≠ gasto (#56). Medição: antes/depois de cada mudança que promete economia; o registro de `/usage` por missão foi encerrado após 3 registros sem sinal. Detalhes e fontes: `docs/AGENT_TOKEN_SPEND.md`.
- **Diagnóstico do editor entra no contexto:** a extensão do VS Code anexa os avisos do LTeX+ a cada edição; sem `<!-- LTeX: language=pt-BR -->` na 1ª linha, um `.md` em português gera centenas de falsos positivos (462 em uma edição no #41). Todo `.md` novo fora do inglês leva o comentário.
- **Regra em dois agentes = duas cópias** (#35): Claude e Copilot leem escopo de caminho de pastas e frontmatter diferentes; a divergência é barrada por teste, não por disciplina.
- **Portão que nunca falha é pior que nenhum** (#27): exclusões, `--exit-zero` e `continue-on-error` esconderam um F821 real. CI e commit rodam os mesmos hooks; regra sem exceção virou teste (`tests/test_lint_gate.py`). Falso positivo se suprime no ponto exato, com o porquê (behave troca os decorators em tempo de import; pylint não lê stubs `.pyi`, e o Selenium carrega `webdriver.Chrome` sob demanda: importar do módulo concreto resolveu sem supressão).
- **Portão novo barra commits parciais:** cada commit é checado com a config *dele*; dividir "ligar o portão" e "corrigir o que ele acusa" exigiria `--no-verify`. Mudança indivisível = commit único com mensagem detalhada.
- **Alterar o ruleset é bloqueado para o agente** (classificador de permissões, "CI Bypass"); só com autorização explícita do dono para aquela alteração. Ordem segura: CI do PR verde com o novo check → ruleset → merge (o merge valida a regra nova).

## Ambiente local (Windows)

- Chrome e Firefox instalados; interpretador do VS Code = `.venv` do projeto.
- Poetry instalado pelo instalador oficial (`%APPDATA%\pypoetry`). Se `poetry self update` quebrar no meio, recupere com `%APPDATA%\pypoetry\venv\Scripts\python -m pip install poetry==<versão>`.
- Windows PowerShell 5.1 grava `>>`/`Out-File` em UTF-16: não use para arquivos de texto do repo (causa da issue #26; agora barrado pelo hook `check-text-encoding`).
- `poetry run python -c "<várias linhas>"` executa só a 1ª linha e sai com 0 (o shim do Windows trunca o argumento): falso sucesso. Python multilinha vai em arquivo (scratchpad).
- O `sed -i` do Git Bash lê em modo texto: remove o `\r` (padrão com `\r` não casa) e regrava o arquivo com LF. Para editar texto, use o Edit; se o disco ficar com LF, `git add` + regerar o arquivo pelo `git checkout`.
