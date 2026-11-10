# Flaky Test Policy

A test is flaky when it both passes and fails on the same code ([Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)). A flaky test is not a nuisance to route around: once a red build can mean "probably nothing", people stop reading red builds, and real failures go unnoticed along with the false ones ([Fowler](https://martinfowler.com/articles/nonDeterminism.html)).

**In short:** record it, instrument it, find the cause, fix it, and prove the fix. Never retry a test until it passes. Quarantine is the last resort, and it has a deadline.

## 1. Record it

A red test is a real failure until shown otherwise. To call it flaky, see it pass on the **same commit**: a GitHub Actions re-run [uses the same `GITHUB_SHA`](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs), so it is a valid check.

Open the issue **before** the re-run, titled `test: flaky <what failed>`, with:

- the test ID and the complete error, not only its last line;
- the run URL and the commit SHA;
- the observed rate (failures / runs of that job);
- the evidence from section 2, copied into the issue, because CI artifacts here expire after 30 days;
- each hypothesis, labelled as a hypothesis until it is observed.

A manual re-run is allowed for two reasons: to confirm the flake, and to unblock a merge once the issue exists. It is never a way to make the failure go away unrecorded.

## 2. Instrument first

Do not guess at a cause the evidence cannot show. Failures already leave evidence:

| Layer | Evidence on failure | Where |
| --- | --- | --- |
| Integration (pytest + real browser) | Screenshot and page source | `reports/integration-failures/`, uploaded as a CI artifact |
| E2E (Behave, `test` job) | Screenshot and current URL | Attached to the Allure result |
| Smoke (Behave, `smoke-matrix` job) | Screenshot and current URL; Grid and browser logs | Allure results in the `smoke-failures-<browser>` CI artifact; logs in the job log |

If that evidence cannot tell the hypotheses apart, add the evidence first, test-first, and let the next failure answer. That includes failure messages: one message for two different causes is a bug in the instrumentation.

## 3. No automatic retries

No retry plugin, runner flag, CI retry action, or Behave auto-retry. `tests/test_agent_rules.py` enforces this.

- **A retry hides the cause.** A race that fails 1 run in 9 becomes a green build, and the bug stays. Google reports that its own "fail only 3 times in a row" option "encourages developers to ignore flakiness" and delays real failures.
- **Green carries no warning.** The merge gate reads pass or fail, so nobody opens a report to learn that a pass needed two attempts.

Not retries, and therefore fine:

- **An explicit wait on a condition** (`WebDriverWait`): it polls for a state and does not repeat the action under test.
- **Repeating a setup step that gives no test verdict**, such as a package download. The enforcing test bans the switches above everywhere to stay simple, so such a step needs another mechanism.

*Judgment call:* a runner that reports a pass-on-retry as its own "flaky" outcome ([Playwright](https://playwright.dev/docs/test-retries)) makes retries less dangerous, and a project on that stack can decide differently. What must hold in every case is that the instability stays visible and tracked in an issue.

## 4. Fix the cause and prove it

The issue closes with a root cause that was **observed**, not inferred, and one of two outcomes:

- **Fix.** The product or test is corrected, with a deterministic unit test (order of actions, wait condition) that was seen failing. Integration tests of a race are probabilistic; the guarantee comes from the unit test.
- **Delete or rewrite.** If other tests cover the behaviour, remove the test, or rewrite it at a lower level ([pytest](https://docs.pytest.org/en/stable/explanation/flaky.html)). Name the test that covers it.

Repeated green runs are supporting evidence only, and the record must state their odds. With a failure rate `p`, `n` green runs happen by chance with probability `(1 - p)^n`:

| Failure rate | Green runs | Chance of all green with the bug still there |
| --- | --- | --- |
| 1 in 9 | 10 | 31% |
| 1 in 9 | 26 | under 5% |

## 5. Quarantine: the last resort

Quarantine protects the healthy tests' signal, but a quarantined test detects nothing, and it can hide a real race ([Fowler](https://martinfowler.com/articles/nonDeterminism.html), [Google](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)). A flake that fails rarely stays in the suite: its next failure is the data the investigation needs.

**Criteria, all required:**

- the issue exists and holds the evidence collected so far;
- the flake keeps blocking unrelated work, despite the investigation;
- the issue names the behaviour that loses coverage while the test is out.

**Limits** (*judgment call*; Fowler recommends a numeric or time limit, with 8 tests and one week as his examples): at most **3 tests** at once and **14 days** per test, with the issue at `priority: P1` and its deadline written in it. Reaching a limit makes clearing the quarantine the next mission.

**How:**

- **pytest:** `@pytest.mark.xfail(strict=False, reason="flaky: #<issue>")`. The test still runs and reports, without failing the build. pytest itself calls this ["rather dangerous to use permanently"](https://docs.pytest.org/en/stable/explanation/flaky.html). As wired today, an expected failure saves no evidence: pytest reports it as skipped, so `call_failed` in `tests/helpers/failure_artifacts.py` sees no failure. The first quarantine must make `call_failed` count `wasxfail` and run the Firefox artifact upload with `always()`, which only runs on `failure()` today.
- **Behave:** tag the scenario `@quarantine`. The `@e2e` and `@smoke` tags sit on whole features, so removing them from a scenario changes nothing. The first quarantine must also change the CI selections in `.github/workflows/tests.yml` to `--tags="@e2e and not @quarantine"` and `--tags="@smoke and not @quarantine"`. The scenario then stops running in CI and produces no new evidence, so the issue must say how it will be run on demand until the fix.

No test is in quarantine today.

## Worked example: the Firefox logout flake (#129)

1. **Recorded.** `test_logout_returns_to_login_page` failed on a PR that changed only documentation, about 1 run in 9. The issue held the full error and the run, and marked its analysis as a hypothesis.
2. **Instrumented.** The error, `did not stop moving`, covered both "still moving" and "never visible". The failure did not reproduce locally, and each hypothesis measured there (animation, slow CI, header remount) came up empty. So the first PR (#132) only added evidence: a distinct message and a screenshot and page source on failure.
3. **Not retried, not quarantined.** The test kept running, because its next failure was the data needed.
4. **Observed.** The artifact from the next failure showed the menu panel with `aria-hidden="false"` (React state: open) and `hidden="true"` at once. That pointed to the cause: a 500 ms timer in `react-burger-menu` can hide a menu that was just opened, in the gap between the click and React's effect. A spike at controlled delays on the Grid reproduced the state.
5. **Fixed.** `open_menu` waits until the panel carries `hidden`, the settled closed state, and only then clicks. Retrying the click was rejected because it would have hidden the cause.
6. **Proved.** Unit tests pin the order and the condition, each seen failing by mutation. CI went 10 for 10 on the branch, and the record says what that is worth: 31% by chance alone.

## Sources

Read on 09/11/2026, for pytest 9.2 and Behave 1.3.3.

- Martin Fowler, [Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html): why flaky tests ruin a suite, quarantine and its limits.
- Google Testing Blog, [Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html): definition and the cost of retries and of quarantine.
- pytest, [Flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html): `xfail(strict=False)` as manual quarantine, failure screenshots, delete or rewrite.
- GitHub Docs, [Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs): a re-run uses the same commit.
- Playwright, [Retries](https://playwright.dev/docs/test-retries): the "flaky" outcome, for comparison.
- Behave, `behave/contrib/scenario_autoretry.py` in the installed version: the auto-retry this policy forbids.
