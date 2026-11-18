<!-- LTeX: language=pt-BR -->

# Instruções de revisão

Verificações específicas deste projeto para o revisor (`mission:reviewer` e o [Code Review](https://code.claude.com/docs/en/code-review-customize.md) da Anthropic, que lê este arquivo na raiz), somadas à lista genérica dele. As regras gerais estão no [AGENTS.md](AGENTS.md); as de escopo de caminho, que o revisor não recebe sozinho, em [.claude/rules/](.claude/rules/): leia [selenium.md](.claude/rules/selenium.md) para mudanças em `pages/`, `features/` e `tests/integration/`, e [workflows.md](.claude/rules/workflows.md) para `.github/workflows/`.

## Sempre verificar

- **Isolamento:** cada teste novo parte de um estado limpo e conhecido: navegador próprio (`before_scenario` no Behave, fixture `driver` de escopo `function` na integração) e pré-condições (login, carrinho) montadas no próprio `Given` ou fixture. Não depende de ordem nem do que outro teste deixou, nem compartilha estado mutável entre os workers do `-n auto` (o CI roda unitários e integração em paralelo).
- **Espera do estado final no navegador:** `WebDriverWait` com condição (`element_to_be_clickable` para agir, `visibility_of_element_located` para ler), nunca `time.sleep`; navegação em SPA espera o `PAGE_LOADED` do destino; formulário com erro remove o erro antigo antes de reenviar.
- **Bug conhecido da aplicação:** o teste afirma o comportamento correto e é falha esperada estrita, com o bug no catálogo; confirme que ele falha pelo motivo do bug, não por erro do próprio teste.
- **Job novo no CI:** entra no `needs` do `ci-passed`; job que roda Behave ou integração guarda screenshot e URL como artefato.

## Não reportar

- O que black, ruff, pylint, pyright e os hooks do `pre-commit` já impõem (estilo, formatação, imports, tipos, métricas e traduções do README, encoding, pins por SHA via zizmor).
