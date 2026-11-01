---
applyTo: "**/*.py"
---
<!-- LTeX: language=pt-BR -->
# Código Python

- Imports no topo do arquivo, nunca dentro de função ou método: dificulta o mocking (pylint C0415; ainda não cobrado no CI, #27).
- Nomes em inglês; docstrings; type hints quando esclarecem.
- Linters: black, flake8, pylint.
