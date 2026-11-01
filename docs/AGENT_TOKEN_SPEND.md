<!-- LTeX: language=pt-BR -->
# Gasto de tokens dos agentes (Claude Code, GitHub Copilot)

> Referência lida sob demanda: fontes, porquês e como medir. As regras em si (curtas) ficam em `.github/copilot-instructions.md`, seção "Gasto de tokens". Issue de origem: #41.

## Modelo mental

Cada turno reenvia **todo** o contexto ao modelo: prompt do sistema, regras do projeto, histórico e cada resultado de ferramenta. O *prompt caching* barateia a releitura do que não mudou, mas não a elimina. Por isso o custo cresce com três coisas:

1. **Contexto sempre carregado** (`CLAUDE.md`, `.github/copilot-instructions.md` e seus `@imports`): pago em toda requisição de todo chat.
2. **Tamanho da conversa**: tudo o que entra (logs, arquivos lidos, saídas de comando) é relido em todos os turnos seguintes.
3. **Requisições extras**: subagentes, compactação, tarefas agendadas.

Contexto longo também **piora a resposta**: regra perdida num arquivo grande é seguida com menos consistência. Economia e qualidade apontam na mesma direção.

## Práticas adotadas e o porquê

| Prática | Porquê | Fonte |
| --- | --- | --- |
| Arquivo de regras sempre carregado com menos de 200 linhas; só o que vale em todo chat | Arquivo maior consome contexto e reduz a aderência às regras | [memory][mem] ("target under 200 lines") · [costs][costs] |
| `@import` não economiza | O arquivo importado carrega junto com quem o importa | [memory][mem] |
| Regra de uma parte do código vai para arquivo com escopo de caminho (`.claude/rules/*.md` com `paths:`; `.github/instructions/*.instructions.md` com `applyTo`) | Carrega só quando o agente mexe nos arquivos correspondentes | [memory][mem] · [VS Code][vsc] · [GitHub][gh] |
| Não repetir o que linter, formatador ou teste já impõe; regra que não admite exceção vira teste/hook, não ênfase (IMPORTANT, CAIXA ALTA) | Ênfase faz o modelo atual aplicar a regra além da conta; o que é verificável por máquina não precisa ocupar contexto | [best practices][bp] · [VS Code][vsc] |
| Uma missão por chat; `/clear` entre tarefas não relacionadas | `/clear` custa zero; contexto velho é pago em toda mensagem seguinte. `/compact` é ele próprio uma requisição grande | [costs][costs] · [best practices][bp] |
| Depois de duas correções sem sucesso: `/clear` e um prompt melhor | A terceira correção soma-se a um histórico com duas tentativas erradas que continuam sendo relidas | [best practices][bp] |
| Escolher modelo e esforço no início do chat, sem trocar no meio | Trocar de modelo invalida o cache inteiro (o próximo turno relê tudo sem desconto) | [prompt caching][pc] |
| Editar `CLAUDE.md` no meio do chat não tem efeito até `/clear`/`/compact`/reinício | As regras são lidas uma vez no início da sessão | [prompt caching][pc] |
| Filtrar saída na origem: `grep`, `head`, `--jq`, `gh run view --log-failed`, leitura de arquivo por trecho | Saída despejada no contexto é relida em todo turno pelo resto do chat. Ex.: no #38, `grep` por remov/deprecat no `py/CHANGES` do Selenium, não as notas inteiras | [costs][costs] (hooks/pré-processamento) |
| Documentação web por seção: sumário de títulos e depois só a seção (`curl -s <url>.md \| sed -n '/^### X/,/^### /p'`) | O WebFetch devolve docs em Markdown crus e inteiros (47 mil caracteres na página de custos, ~20 mil tokens relidos em todo turno); sumário + seção = ~2,2 mil (#58) | Medição local (#58, abaixo) |
| Hook `PreToolUse` reescreve `pytest`/`behave` para a saída compacta do próprio runner (`-q`, `-f progress2`); `.claude/settings.json` + `scripts/filter_test_output.py` | Saída de teste verde é volume sem informação: `behave` pretty 51 KB → 1,1 KB; `pytest -v` 28 KB → ~1,6 KB. Flags nativas, não `\| grep \| head` como no exemplo oficial: o pipe troca o exit code pelo do `head` (suíte vermelha sai 0, visto em teste de mutação) e o `progress` simples esconde a mensagem da falha. Formato exec com `python` e matcher `Bash\|PowerShell` (só `Bash` não dispara no PowerShell) | [costs][costs] (exemplo oficial) · [hooks][hooks] · `tests/test_filter_test_output.py` (#63) |
| Plugin de *code intelligence* `pyright-lsp` (oficial): após cada edição de `.py`, o agente recebe os erros de tipo/import que introduziu | Sem ele, o erro só aparece rodando testes ou lendo o arquivo inteiro; com ele, só o diagnóstico das linhas editadas. O servidor (`pyright-langserver`) é ferramenta por máquina (`pipx`), não dependência do Poetry: o Claude Code o inicia pelo nome a partir do PATH, e o `.venv` não está no PATH da extensão. Um pyright fora do projeto só resolve os imports com `[tool.pyright] venv = ".venv"` (sem isso: 13 `reportMissingImports` falsos, visto em teste de mutação), e o `.venv` só existe no projeto para todos com o `poetry.toml` versionado. Portão de pyright no CI, com versão travada, fica para a #27 | [code intelligence][ci] · README do plugin · `tests/test_agent_rules.py` (#63) |
| CLI (`gh`) antes de servidor MCP | CLI não acrescenta listagem de ferramentas ao contexto | [costs][costs] |
| Subagente só para: trabalho paralelo independente, isolar saída volumosa, revisor que não viu o código. Pedir resumo curto; modelo menor para tarefa simples | Cada subagente começa do zero (recoleta contexto que a conversa já tinha) e soma requisições. Delegar não torna a resposta melhor | [best practices][bp] · [costs][costs] |
| Pedidos específicos (arquivo, função, critério de pronto) | Pedido vago dispara varredura ampla do código | [costs][costs] |

### Instalar o `pyright-lsp` em uma máquina nova

O `enabledPlugins` em `.claude/settings.json` liga o plugin para o projeto, mas não instala nada; cada máquina faz uma vez:

1. Servidor (o extra `nodejs` traz o Node.js em wheel; dispensa Node instalado): `py -m pip install --user pipx`, `py -m pipx ensurepath`, `pipx install "pyright[nodejs]"`.
2. Fechar e reabrir o VS Code (ou o terminal do `claude`): processos já abertos não veem o PATH novo. Conferir com `Get-Command pyright-langserver`.
3. Plugin: `/plugin` → `pyright-lsp` (marketplace `claude-plugins-official`) → escopo do projeto. No terminal: `claude plugin install pyright-lsp@claude-plugins-official --scope project`.
4. Confirmar: pedir ao agente um erro de tipo proposital em um `.py`; a edição deve mostrar `Found N new diagnostic issues`. Sem essa linha: `/plugin` → aba **Errors** (`Executable not found in $PATH` = passo 2).

## Como medir o gasto por missão

Decidir com dados, não por palpite. Antes de `/clear` no fim da missão, o dono roda no Claude Code:

- **`/usage`**: o bloco *Session* mostra tokens por modelo (entrada, saída, leitura e escrita de cache) e custo estimado. A linha *Prompt cache (main)* mostra a fração servida do cache e os *misses*. Em planos de assinatura, o detalhamento por skill/subagente/MCP e as **recomendações** (cada uma com ≥ 10% do uso) apontam o que corrigir. Na extensão do VS Code: diálogo *Account & usage*.
- **`/context`**: o que ocupa o contexto agora (regras carregadas, ferramentas, histórico). Use para conferir o tamanho real das regras.
- **Copilot**: uso de *premium requests* nas configurações de cobrança da conta no GitHub.

Sinais de desperdício e o que fazer:

| Sinal | Causa provável | Ação |
| --- | --- | --- |
| Recomendação "Trim CLAUDE.md" no `/usage` | Regras sempre carregadas grandes | Cortar ou mover para arquivo com escopo de caminho (#35) |
| Muitos *misses* de cache | Troca de modelo/esforço no meio, pausa maior que o TTL | Fixar modelo no início; retomar sabendo que o 1º turno é caro |
| Recomendação de subagentes com fatia alta | A fatia é do uso **ao qual a recomendação se aplica**, não do gasto dos subagentes: uma sessão longa que lançou um subagente conta inteira (#56) | Medir o gasto real dos subagentes nos transcripts antes de agir; só então, se alto, fazer na conversa principal |
| Chat longo com custo crescente | Missão acumulou tarefas não relacionadas | Encerrar a missão; handoff; chat novo |
| Cada edição de `.md` traz centenas de diagnósticos de ortografia | O verificador (LTeX+) checa pt-BR/es como `en-US`; a extensão do Claude Code anexa os diagnósticos do editor ao contexto | Comentário mágico na 1ª linha do arquivo: `<!-- LTeX: language=pt-BR -->` (no #41: 462 diagnósticos, ~115 KB, em uma edição); ortografia só no Code Spell Checker, com termos do projeto em `cSpell.words` (#52: 45 → 6) |

### Linha de base (01/11/2026, antes do #35)

Contexto do projeto carregado em todo chat (estimativa por bytes ÷ 4):

| Arquivo | Linhas | ~Tokens |
| --- | ---: | ---: |
| `.github/copilot-instructions.md` (via `@import` no `CLAUDE.md`) | 347 | ~4.300 |
| `CLAUDE.md` | 7 | ~60 |

`docs/PROJECT_SESSION_SUMMARY.md` (69 linhas, ~1.600) não é `@import`: só entra no contexto quando lido no início do chat (Ciclo de Missão), e por isso também se beneficia de ser curto.

### Depois do #35 (01/11/2026)

| Arquivo | Linhas | ~Tokens |
| --- | ---: | ---: |
| `.github/copilot-instructions.md` (sempre carregado) | 104 (era 357) | ~2.450 (era ~4.500) |
| 4 arquivos com escopo de caminho (`.claude/rules/` e `.github/instructions/`, idênticos) | 46 | ~600, só quando o caminho é tocado |

Como: fluxogramas ASCII e checklists que repetiam o fluxo viraram listas curtas; Selenium, Python, workflows e Poetry foram para arquivos com escopo de caminho; a ênfase (CAIXA ALTA, emojis) saiu. Linhas caíram 71%, tokens 46%: o que sobrou é denso (tabelas, comandos). `tests/test_agent_rules.py` barra o retorno acima de 200 linhas e a divergência entre as cópias Claude/Copilot.

A economia real se confirma pelo `/usage` das próximas missões, não por esta estimativa.

### Verificação (#54, 01/11/2026)

Medido, não estimado.

**Regras sempre carregadas (`/context`, bloco *Memory files*):**

| Arquivo | Bytes | Estimado (÷ 4) | Real |
| --- | ---: | ---: | ---: |
| `.github/copilot-instructions.md` | 9.902 | ~2.450 | **4.100** |
| `CLAUDE.md` | 272 | ~70 | 126 |

Neste repositório, **~2,4 bytes/token**, não 4: o "÷ 4" vale para inglês, e pt-BR (acento = 2 bytes em UTF-8), tabelas e comandos rendem menos por token. Logo o "antes" do #35 custava ~7 mil tokens reais; o corte percentual se mantém, os absolutos acima estavam subestimados em ~40%. Para estimar daqui em diante: bytes ÷ 2,4, ou meça com `/context`.

**Regras com escopo de caminho:** ausentes de *Memory files*; entram como anexo quando o caminho é tocado. Neste chat, ler `docs/` e `.vscode/` não trouxe nenhuma; ler `tests/*.py` trouxe `python.md` e `selenium.md` (e não `workflows.md`/`dependencies.md`). Copilot: formato conferido nas fontes oficiais (pasta `.github/instructions/`, `applyTo` com globs separados por vírgula, [GitHub][gh]); no VS Code a aplicação depende de `chat.includeApplyingInstructions`, de padrão não documentado, por isso fixado em `true` no `.vscode/settings.json`. No GitHub.com, regras por caminho valem só para Copilot code review e cloud agent.

**Diagnósticos do editor (#52)**, uma edição de `docs/AGENT_TOKEN_SPEND.md`:

| | Diagnósticos | Ortografia falso-positivo | ~Bytes |
| --- | ---: | ---: | ---: |
| Antes | 45 (LTeX+) | 39 | ~11 KB |
| Depois | 6 (gramática LTeX+) + 0 (cSpell, após a lista de palavras) | 0 | ~1,6 KB |

Ortografia ficou só com o Code Spell Checker (`cSpell.language: "en,pt_BR,es"`, que conhece termos técnicos em inglês, e `cSpell.words` para termos do projeto); o LTeX+ mantém a gramática (`ltex.disabledRules`). Desligar um corretor só é seguro se o outro cobre todos os idiomas: sem `cSpell.language`, o pt-BR ficaria sem checagem nenhuma. `.vscode/settings.json` e `extensions.json` passam a ser versionados (modelo oficial [github/gitignore][gitignore]). Diagnósticos só existem para arquivos abertos no editor, e o anexo automático ao contexto não é determinístico (no #35 veio, neste chat não).

**Gasto (`/usage`, diálogo *Account & usage* da extensão do VS Code, plano Pro):** não mostra tokens por missão, e sim a **% do limite** (sessão de 5 h: 71%; semana: 16%) e recomendações das **últimas 24 h somando todas as sessões da máquina** (fatias se sobrepõem). Por isso não isola uma missão; para tokens por sessão, use `/usage` na CLI. Linha de base de 01/11/2026 (dia com #35, #41 e #54):

| Recomendação | % do uso (24 h) | Leitura |
| --- | ---: | --- |
| *Give simple subagents a cheaper model* | 72 | Leitura corrigida no #58: não é o gasto dos subagentes (1,6%), e sim o uso da sessão que os lançou (ver "Diagnóstico da #56") |
| *Start fresh when you switch tasks* (`/clear`) | 65 | Confirma "uma missão por chat" |
| *See what fills your context* (`/context`) | 22 | Medido neste chat (acima) |

A recomendação "Trim CLAUDE.md" não apareceu. Este chat inclui ~14 KB das próprias consultas de diagnóstico.

### Registro por missão (`/usage` antes do `/clear`)

Mesma fonte e mesma ressalva: % do limite e fatias de 24 h somando as sessões da máquina; a missão não fica isolada.

| Missão | Sessão 5 h | Semana | `/clear` | Subagentes | `/context` | Leitura |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| #28 (01/11/2026) | 25% | 22% | 55 | 54 | 25 | Chat sem subagentes, e a fatia de subagentes segue em 54%: vem de outras sessões das 24 h, como diagnosticado no #56. Semana +6 p.p. desde o #54 somando #58 e #28 |

## Levantamento de mercado e lacunas (#58, 01/11/2026)

### Diagnóstico da #56: de onde vinham os "72% de subagentes"

Medido nos transcripts locais (`~/.claude/projects/<projeto>/*.jsonl`, campo `usage` de cada resposta; subagentes em `<sessão>/subagents/`). **Estimativa:** custo ponderado com pesos supostos, não conferidos na tabela de preços do modelo (leitura de cache 0,1×, escrita 1,25×, saída 5× a entrada); os percentuais dependem deles:

| Medida | Valor |
| --- | --- |
| Gasto real dos subagentes (2, ambos de um `/code-review`) | **1,6%** do total |
| Sessão d3e6a932 (31/10, várias missões sem `/clear`) | 339 requisições, contexto médio **277 mil**, máximo 469 mil; **61%** do custo |
| Sessões seguintes (uma missão cada) | 29–62 requisições, contexto médio 52–112 mil (≈ 75 mil) |
| Fatia da sessão d3e6a932 na janela de 24 h do #54 | 74% (o diálogo mostrou 72%; coincidência compatível, não prova) |
| Piso do 1º turno de toda sessão (prompt do sistema, ferramentas, regras) | ~46–48 mil tokens; regras do projeto = 4,1 mil |

**Causa raiz:** a recomendação atribui a si o uso inteiro das sessões em que se aplica ("*it tells you how much of your usage the row applies to, not how much the change saves*", [costs][costs]). A sessão que lançou os subagentes teve **contexto longo** (várias missões sem `/clear`); as sessões de uma missão tiveram contexto ~3,7× menor, mas fizeram trabalhos diferentes: é correlação, não prova de causa (a causa é documentada em [costs][costs], "Why usage climbs in a long session"). **Remédio:** a leitura correta da fatia entrou na tabela "Sinais de desperdício"; para subagentes, a prática oficial (modelo menor em tarefa simples) virou regra. **Lição:** métrica agregada diz onde olhar; leia como a fonte a define antes de agir.

### Onde o contexto cresce (resultados de ferramenta, todas as sessões)

| Origem | % do texto devolvido por ferramentas |
| --- | ---: |
| WebFetch | **21%** (a página de custos, 47 mil caracteres, entrou inteira 3 vezes) |
| Read | 10% (média de ~2,5 mil caracteres por leitura) |
| `cat` via shell | 6% |
| `gh run view`, `getDiagnostics`, `grep`, demais | ≤ 3% cada |

Amostra pequena (10 sessões): serve para achar desperdício óbvio, não para rejeitar prática oficial.

### Tabela de lacunas

Fontes primárias: [Anthropic, *Effective context engineering for AI agents*, 29/09/2025][ce] · [Chroma, *Context Rot*, 07/2025][rot] (18 modelos; o desempenho cai com o tamanho da entrada, mais ainda com distratores) · [Manus, *Context Engineering for AI Agents*, 18/07/2025][manus] (taxa de acerto do cache como métrica principal; entrada:saída ≈ 100:1) · [Liu et al., *Lost in the Middle*, 2023][lim] · [Claude Code, *Manage costs*][costs] (consultado em 01/11/2026). Blogs e ferramentas de terceiros com economia autodeclarada (80–99%) foram descartados como evidência.

**Critério:** prática estabelecida é aplicada por padrão; não aplicar exige motivo explícito. Medição sob medida só quando a economia esperada supera claramente o custo de investigar.

| Prática | Fonte | Hoje no projeto | Decisão |
| --- | --- | --- | --- |
| Menor conjunto de tokens de alto sinal; contexto longo degrada | ce · rot · lim | Regras < 200 linhas, cobradas por teste (#35) | Já feito |
| Limpar entre tarefas | costs | Uma missão por chat | Já feito |
| Recuperação sob demanda / revelação progressiva | ce · costs | Regras por caminho; este doc lido sob demanda | Já feito |
| Prefixo estável, cache alto | manus · [pc][pc] | Modelo/esforço fixos no chat | Já feito |
| Notas fora do contexto (`NOTES.md`) | ce | `PROJECT_SESSION_SUMMARY.md` como handoff | Já feito |
| Filtrar/pré-processar saída de ferramenta | costs (hooks) | Regra manual; docs web não cobertas | **Adotado**: regra de docs por seção (WebFetch = 21%; ~97% menos por consulta) |
| Hook que filtra saída de testes (só falhas) | costs (exemplo oficial) | Hook com flags nativas | **Adotado** (#63; ver Práticas adotadas) |
| Modelo menor para subagentes de tarefa simples | costs | Herdam o modelo da sessão | **Adotado** (regra); revisor mantém o modelo da sessão: a qualidade da revisão é o propósito dele |
| Plugin de *code intelligence* (`pyright-lsp`, oficial) | costs · [code intelligence][ci] | `pipx` + plugin no escopo do projeto | **Adotado** (#63; ver Práticas adotadas) |
| Desligar servidores MCP sem uso (`/mcp`) | costs | Conectores da conta claude.ai ativos | **Adotar**: ação do dono no `/mcp`, sem medição sob medida (#61 fechada) |
| Instruções de compactação | costs | Não há | Não se aplica: `/clear` no lugar de `/compact` |
| Medir antes de otimizar; ler a fatia corretamente | costs | `/usage` no fim da missão | Adotado: leitura da fatia corrigida em "Sinais de desperdício" |

**Antes/depois:** o `/usage` no fim de cada missão segue como medida; não há medição sob medida planejada.

[ce]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[rot]: https://www.trychroma.com/research/context-rot
[manus]: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
[lim]: https://arxiv.org/abs/2307.03172
[ci]: https://code.claude.com/docs/en/plugins/code-intelligence

[mem]: https://code.claude.com/docs/en/memory
[costs]: https://code.claude.com/docs/en/costs
[hooks]: https://code.claude.com/docs/en/hooks
[bp]: https://code.claude.com/docs/en/best-practices
[pc]: https://code.claude.com/docs/en/prompt-caching
[vsc]: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
[gitignore]: https://github.com/github/gitignore/blob/main/Global/VisualStudioCode.gitignore
[gh]: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
