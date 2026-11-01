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
| CLI (`gh`) antes de servidor MCP | CLI não acrescenta listagem de ferramentas ao contexto | [costs][costs] |
| Subagente só para: trabalho paralelo independente, isolar saída volumosa, revisor que não viu o código. Pedir resumo curto; modelo menor para tarefa simples | Cada subagente começa do zero (recoleta contexto que a conversa já tinha) e soma requisições. Delegar não torna a resposta melhor | [best practices][bp] · [costs][costs] |
| Pedidos específicos (arquivo, função, critério de pronto) | Pedido vago dispara varredura ampla do código | [costs][costs] |

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
| Subagentes com fatia alta | Delegação sem um dos três motivos acima | Fazer na conversa principal |
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
| *Give simple subagents a cheaper model* | 72 | Subagentes de missões anteriores (o #54 não usou nenhum; `/code-review` só 2%): a regra existe e não bastou → issue própria |
| *Start fresh when you switch tasks* (`/clear`) | 65 | Confirma "uma missão por chat" |
| *See what fills your context* (`/context`) | 22 | Medido neste chat (acima) |

A recomendação "Trim CLAUDE.md" não apareceu. Este chat inclui ~14 KB das próprias consultas de diagnóstico.

[mem]: https://code.claude.com/docs/en/memory
[costs]: https://code.claude.com/docs/en/costs
[bp]: https://code.claude.com/docs/en/best-practices
[pc]: https://code.claude.com/docs/en/prompt-caching
[vsc]: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
[gitignore]: https://github.com/github/gitignore/blob/main/Global/VisualStudioCode.gitignore
[gh]: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
