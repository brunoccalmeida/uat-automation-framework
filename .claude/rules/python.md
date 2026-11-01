---
paths:
  - "**/*.py"
---
<!-- LTeX: language=pt-BR -->
# Código Python

- Imports no topo do arquivo, nunca dentro de função ou método: dificulta o mocking (pylint C0415).
- Nomes em inglês; docstrings; type hints quando esclarecem.
- Linters: black, ruff, pylint e pyright (tipos), portão real no pre-commit e no CI (`tests/test_lint_gate.py`). Supressão só inline ou na config, com o porquê ao lado.
