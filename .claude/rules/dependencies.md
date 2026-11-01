---
paths:
  - "pyproject.toml"
  - "poetry.lock"
---
<!-- LTeX: language=pt-BR -->
# Dependências (Poetry)

- `poetry.lock` é gerado: nunca edite à mão; em conflito, regenere.
- A versão do Poetry acompanha a do Dependabot (sempre a mais recente): `requires-poetry` no `pyproject.toml` e versão do CI atualizadas juntas.
- Priorize por exposição: dependências de execução (incluindo transitivas, ex.: `urllib3`) antes das de desenvolvimento.
