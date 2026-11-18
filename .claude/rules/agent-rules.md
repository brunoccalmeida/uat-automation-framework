---
paths:
  - "CLAUDE.md"
  - "AGENTS.md"
  - ".claude/rules/**"
  - "REVIEW.md"
  - ".claude/settings.json"
  - "docs/ai-workflow/**"
---
<!-- LTeX: language=pt-BR -->
# Regras do agente

- Sempre carregado (`CLAUDE.md`, que importa `AGENTS.md`): só o que vale em todo chat, abaixo de 200 linhas; nada que envelheça rápido (datas, contagens, versões, estado): isso mora em `docs/ai-workflow/PROJECT_SESSION_SUMMARY.md`.
- Regra de uma parte do código vai para arquivo com escopo de caminho em `.claude/rules/` (uma cópia só, #173); procedimento de vários passos vai para skill.
- Não repita o que linter ou teste já impõe; regra sem exceção vira teste ou hook, não ênfase.
- As seções do `AGENTS.md` são comuns com o `playwright-qa-starter-kit` (#150), exceto "TDD/BDD", "Dependências e segurança" e as linhas com comandos, ferramentas ou nomes de branch de cada stack: mudança numa seção comum vale para os dois repositórios; abra a issue irmã no kit.
- Plugin `mission` (marketplace `brunoccalmeida-plugins`) declarado em `.claude/settings.json` com `"autoUpdate": false`: atualizar de propósito, depois de ler o que mudou. Cada clone instala uma vez (`/plugin install mission@brunoccalmeida-plugins`; pelo shell, `/reload-plugins` na sessão aberta); comportamento errado do plugin vira issue no `automation-template`, não regra local.
- Mudança que promete economia de tokens: meça antes e depois (`docs/ai-workflow/AGENT_TOKEN_SPEND.md`), não por rotina.
