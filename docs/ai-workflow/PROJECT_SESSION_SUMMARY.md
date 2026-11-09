<!-- LTeX: language=pt-BR -->
# PROJECT_SESSION_SUMMARY.md

> **Handoff entre chats.** O que vale agora e qual é a próxima missão; leia no início de cada chat (ver "Ciclo de Missão" em `.github/copilot-instructions.md`).
> Só estado (`tests/test_agent_rules.py` cobra). O histórico mora em issues, corpos de PR (`gh pr view <n>`) e Git. Os registros por missão até o #155 estão em `git show 266b09a:docs/ai-workflow/PROJECT_SESSION_SUMMARY.md`.

**Última atualização:** 09/11/2026, missão #149 (resumo reduzido a estado).

---

## Estado atual

| Área | Estado |
| --- | --- |
| CI (`master`) | Verde: unit, integração Chrome + Firefox, E2E Chrome, smoke, lint, report, `secret-scan`, `workflow-audit`; navegadores no Grid do `compose.yaml` |
| Testes | Contagens no README (mantidas pelo hook `validate-readme-metrics`); cobertura mínima de 99% (`--cov-fail-under`) |
| Relatório público | Allure em <https://brunoccalmeida.github.io/uat-automation-framework/>, publicado só em push no `master` |
| Proteção do `master` | Ruleset "Protect master": PR, checks `ci-passed` e `pip-audit`, branch atualizada, histórico linear, sem bypass |
| Segurança | gitleaks e zizmor no `ci-passed`; actions e hooks fixados por SHA; Dependabot com `cooldown` de 7 dias; versões do gitleaks e do zizmor sobem à mão |
| Portões locais | `pre-commit` igual ao CI: black, ruff, pylint, pyright, métricas do README, encoding; links de docs por `tests/test_doc_links.py` |
| Ferramentas | Python pela fonte única `.python-version` (3.15 bloqueado, #95); Poetry, Selenium e demais versões em `pyproject.toml` e `poetry.lock` |
| Regras do agente | `copilot-instructions.md` com 4,3 mil tokens (`/context`, 09/11/2026); escopo de caminho em `.claude/rules/` = `.github/instructions/` |
| Skills e revisor | `/close-mission` (Definition of Done, o agente invoca), `/ship-pr` (auto-merge nativo, só o usuário dispara), `reviewer` uma vez por missão |
| Proteções do agente | `permissions.deny` nos dois shells (`--admin`, force push, push no `master`, `.env`); casam o texto, a fronteira real é o ruleset |
| Ambiente do agente | Filtro de saída de testes (`scripts/filter_test_output.py`) e `pyright-lsp`; passo a passo em `docs/ai-workflow/AGENT_TOKEN_SPEND.md` |
| Navegador | `compose.yaml` é a fonte única do Grid, local e CI; imagens por tag + digest; `SELENIUM_REMOTE_URL` liga o `webdriver.Remote` |
| Config | `config.yaml` com URL e senha da demo; migração para ambiente validado na #144 |
| Bloqueios | #95 (PyYAML sem wheel `cp315`); #153 (Betterleaks v2 ainda em rc.7); #134 (pausada até o primeiro trabalho pago). Conferidos em 09/11/2026 |
| Fila de PRs | Vazia |

## Próxima missão recomendada

**Antes de escolher, reconfira os bloqueios:** #95 (`curl -s https://pypi.org/pypi/PyYAML/json`, procurar arquivos `cp315`; com wheel, ela é a missão) e #153 (`gh api repos/betterleaks/betterleaks/releases`, procurar v2 estável).

**Sem bloqueio resolvido: #144** (P2, configuração por ambiente validado), a mais próxima de segurança. Depois, as demais P2 por `gh issue list`. A #145 cita a lição do #129: fontes no corpo do PR #139 e no registro apontado no topo.

**Ordem combinada (06/11/2026), item que falta:** bugs conhecidos no estilo do `playwright-qa-starter-kit` (afirmar o comportamento correto, marcar como falha esperada, apontar para um `KNOWN_ISSUES.md`).

**#134 (automation-template) pausada** até o primeiro trabalho pago de automação (regra de três: duas fontes não bastam para extrair o núcleo). Até lá, as melhorias entram à mão neste repositório.

**Vigiar:** o `ignore` de semver-major do Dependabot `docker-compose` esconde o Grid 5.x. Quando os PRs da 4.x pararem, confira <https://github.com/SeleniumHQ/docker-selenium/releases> e trate o major como decisão humana.

## Procedimentos recorrentes

- **Trocar a versão do Python:** edite só o `.python-version` e confira a compatibilidade antes; o ruleset não depende do nome dos jobs.
- **`pip-audit` vermelho sem mudança de código:** é CVE nova. Atualize o pacote; sem correção, `--ignore-vuln <ID>` em `security.yml` com justificativa e issue de remoção. Nunca `continue-on-error`.
- **PR que atualiza Selenium ou outra dependência de execução:** `grep` por `remov`/`deprecat` no `py/CHANGES` oficial, busca no código pelas APIs citadas e todas as camadas localmente antes do merge.

## Backlog

Tudo em GitHub Issues com labels `priority: P0/P1/P2`: `gh issue list`.

**Ideia sem issue:** regressão visual do `visual_user` (baseline de screenshots no container do `compose.yaml`; consultar as práticas antes de abrir a issue).

## Decisões e aprendizados que guiam o trabalho

O que já virou regra está em `.github/copilot-instructions.md` e nos arquivos com escopo de caminho; aqui, em uma linha, o porquê delas e as decisões ainda sem regra própria.

- **Histórico fora do resumo** (#149): o `/close-mission` pedia um parágrafo por missão e o arquivo chegou a 78 KB; o resumo guarda estado, o corpo do PR guarda a história.
- **Registro de sessão no PR da missão** (#126): PR separado dobrava os ciclos de CI e enchia o histórico.
- **Credencial de curta duração (OIDC) > segredo fixo** (#25): Dependabot e PRs de fork não recebem `id-token: write`, por isso o passo é pulado exatamente ali.
- **Cache de venv pela versão exata do Python** (#84): com a chave `3.14`, um venv de outro patch foi restaurado e o job rodou sem `behave`.
- **Pin por SHA do commit, não da tag:** tag anotada é um objeto próprio; descasque (`^{}` no `git ls-remote`) e confirme em `git/commits/<sha>`.
- **Check obrigatório pulado conta como aprovado** (#36): gate com `always()`, não `!cancelled()`, e lista de permissão.
- **Portão que nunca falha é pior que nenhum** (#27): `--exit-zero` e `continue-on-error` esconderam um F821 real.
- **Procedimento vai para skill, fato fica na regra** (#101); lógica determinística vira script testado, não prosa.
- **Regra em dois agentes = duas cópias** (#35): a divergência é barrada por teste, não por disciplina.
- **Flake se instrumenta, não se retenta** (#129): repetir o clique esconderia a causa.
- **Fatia de recomendação do `/usage` não é gasto** (#56, #58); detalhes em `docs/ai-workflow/AGENT_TOKEN_SPEND.md`.

## Armadilhas

### Mutação e RED

- Rode mutações com `PYTHONDONTWRITEBYTECODE=1`: o Python reaproveita o `.pyc` se mtime (em segundos) e tamanho batem (#98).
- Mutação que sobrevive se investiga antes de concluir: pode nem ter sido aplicada (`\r\n` no workflow, `replace(..., 1)` no comentário) (#130, #147).
- RED pelo motivo certo: leia a saída, não só o código de saída (#43). `echo $?` após pipe mede o último comando; use `${PIPESTATUS[0]}` (#125).
- Réplica de comportamento alheio se valida contra o real, não só contra a doc (#146).

### Ferramentas e GitHub

- Valide com o zizmor no mesmo escopo do CI (`.`, que inclui o `dependabot.yml`), não só `.github/workflows` (#147).
- Em PR, triagem do gitleaks com `gitleaks:allow`: o fingerprint do `.gitleaksignore` contém o SHA, que o squash troca (#147).
- `test_doc_links` parametriza por arquivo versionado: a contagem do README muda ao dar `git add` em arquivo novo (#147).
- `gh` com 5xx: antes de repetir uma escrita, confira se ela ocorreu (#125).
- Subagente criado no meio da sessão só carrega no próximo chat; skill em pasta nova pede `/reload-skills` (#101).

### Selenium e Grid

- Spike usa o `DriverManager`, nunca driver à mão: o diálogo de senha vazada do Chrome rouba o foco (#98).
- O cookie `session-username` do Sauce Demo vale 10 min; script mais longo refaz o login (#129).
- pytest interrompido deixa sessões presas no Grid: reinicie o contêiner. `docker update --cpus 0` não remove o limite: `docker compose down` + `up` (#129).

## Ambiente local (Windows)

- Chrome e Firefox instalados; interpretador do VS Code = `.venv` do projeto.
- Todo `.md` novo fora do inglês começa com `<!-- LTeX: language=pt-BR -->`, senão a extensão anexa centenas de falsos positivos ao contexto.
- Poetry pelo instalador oficial (`%APPDATA%\pypoetry`). Se `poetry self update` quebrar: `%APPDATA%\pypoetry\venv\Scripts\python -m pip install poetry==<versão>`.
- Windows PowerShell 5.1 grava `>>`/`Out-File` em UTF-16: não use para texto do repo (barrado pelo hook `check-text-encoding`).
- Saída redirecionada usa cp1252 e o `behave` quebra ao escrever `√`: diagnóstico local com `PYTHONIOENCODING=utf-8`.
- `poetry run python -c "<várias linhas>"` executa só a 1ª linha e sai com 0: Python multilinha vai em arquivo no scratchpad.
- Barra invertida dupla em heredoc no Bash tool chegou simples: para texto com barra invertida, use o Edit e confira os bytes.
- `sed -i` do Git Bash regrava com LF e remove `\r`: para editar texto, use o Edit.
