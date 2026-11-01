---
applyTo: ".github/workflows/**"
---
<!-- LTeX: language=pt-BR -->
# Workflows do GitHub Actions

- Toda action por SHA completo do **commit** (descasque a tag anotada), com comentário `# vX.Y.Z`, inclusive `actions/*` (OpenSSF Scorecard): tag é ponteiro móvel. `tests/test_workflow_pinning.py` barra regressões.
- `pip-audit --strict` (`security.yml`, em PRs e diário): exceção só via `--ignore-vuln <ID>` com justificativa e issue de remoção; nunca `continue-on-error`.
- O ruleset exige só `ci-passed` (gate do workflow `Tests`) e `pip-audit`, nunca job de matriz (o nome muda com a matriz). Job novo que roda em PR entra no `needs` do gate (`tests/test_ci_gate.py`). Check obrigatório pulado conta como aprovado: por isso o gate usa `always()` e lista de permissão.
