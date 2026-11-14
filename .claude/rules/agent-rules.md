---
paths:
  - "CLAUDE.md"
  - "AGENTS.md"
  - ".claude/rules/**"
  - ".claude/skills/**"
  - ".claude/agents/**"
  - ".claude/settings.json"
  - "docs/ai-workflow/**"
---
<!-- LTeX: language=pt-BR -->
# Regras do agente

- Sempre carregado (`CLAUDE.md`, que importa `AGENTS.md`): só o que vale em todo chat, abaixo de 200 linhas; nada que envelheça rápido (datas, contagens, versões, estado): isso mora em `docs/ai-workflow/PROJECT_SESSION_SUMMARY.md`.
- Regra de uma parte do código vai para arquivo com escopo de caminho em `.claude/rules/` (uma cópia só, #173); procedimento de vários passos vai para skill.
- Não repita o que linter ou teste já impõe; regra sem exceção vira teste ou hook, não ênfase.
- As seções do `AGENTS.md` são comuns com o `playwright-qa-starter-kit` (#150), exceto "TDD/BDD", "Dependências e segurança" e as linhas com comandos, ferramentas ou nomes de branch de cada stack: mudança numa seção comum vale para os dois repositórios; abra a issue irmã no kit.
- Mudança que promete economia de tokens: meça antes e depois (`docs/ai-workflow/AGENT_TOKEN_SPEND.md`), não por rotina.
