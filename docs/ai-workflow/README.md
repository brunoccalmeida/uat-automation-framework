# AI Workflow

How the AI coding agent works on this repository. The notes are in Portuguese (Brazil), the working language of the project.

| File | What it is |
| --- | --- |
| [PROJECT_SESSION_SUMMARY.md](PROJECT_SESSION_SUMMARY.md) | Handoff between chats: current state, decisions and the next recommended mission. One chat works on one mission; the agent reads this first and updates it inside the mission's own PR. |
| [AGENT_TOKEN_SPEND.md](AGENT_TOKEN_SPEND.md) | Why the always-loaded rules stay short, and the measurements behind each change that promised to save context. |

The rules themselves live in the repository:

- [AGENTS.md](../../AGENTS.md): rules for every chat, in the open format for agent instructions (Claude Code imports it from [CLAUDE.md](../../CLAUDE.md));
- [.claude/rules/](../../.claude/rules/): rules scoped to part of the code;
- [REVIEW.md](../../REVIEW.md): this project's checks for the reviewer;
- the `mission` plugin ([README](https://github.com/brunoccalmeida/automation-template/blob/main/plugins/mission/README.md)), enabled in [.claude/settings.json](../../.claude/settings.json): the procedures (`/mission:close-mission`, `/mission:ship-pr`) and the read-only reviewer (`mission:reviewer`), driven by the contract table in `AGENTS.md`.

`tests/test_agent_rules.py` keeps a single copy of the rules, each path-scoped rule with its paths, the always-loaded rules under their size target, and each contract value matching what CI runs.
