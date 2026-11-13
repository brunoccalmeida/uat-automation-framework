---
paths:
  - ".github/workflows/**"
---
<!-- LTeX: language=pt-BR -->
# Workflows do GitHub Actions

- Toda action por SHA completo do **commit** (descasque a tag anotada), com comentário `# vX.Y.Z`, inclusive `actions/*` (OpenSSF Scorecard): tag é ponteiro móvel. O `workflow-audit` (zizmor) barra o pin por tag; `tests/test_workflow_version_comments.py`, o comentário ausente.
- `secret-scan` (gitleaks, todo o histórico) e `workflow-audit` (zizmor) rodam em PR e reprovam o `ci-passed`. Falso positivo do gitleaks: `gitleaks:allow` na linha; fingerprint em `.gitleaksignore` só para commit já no `master` (ele contém o SHA, que o squash troca); segredo real é revogado antes de removido. Zizmor: ignorar só inline e com motivo (`# zizmor: ignore[regra]`). A versão do gitleaks (e o SHA-256) e o `version:` do zizmor são atualizados à mão: o Dependabot não os enxerga.
- `pip-audit --strict` (`security.yml`, em PRs e diário): exceção só via `--ignore-vuln <ID>` com justificativa e issue de remoção; nunca `continue-on-error`.
- O ruleset exige só `ci-passed` (gate do workflow `Tests`) e `pip-audit`, nunca job de matriz (o nome muda com a matriz). Job novo que roda em PR entra no `needs` do gate (`tests/test_ci_gate.py`). Check obrigatório pulado conta como aprovado: por isso o gate usa `always()` e lista de permissão.
- Check obrigatório novo, ordem segura: CI do PR verde com o novo check → ruleset (só com autorização do dono) → merge.
