# AI Workflow

How the AI coding agent works on this repository. The notes are in Portuguese (Brazil), the working language of the project.

| File | What it is |
| --- | --- |
| [PROJECT_SESSION_SUMMARY.md](PROJECT_SESSION_SUMMARY.md) | Handoff between chats: current state, decisions and the next recommended mission. One chat works on one mission; the agent reads this first and updates it inside the mission's own PR. |
| [AGENT_TOKEN_SPEND.md](AGENT_TOKEN_SPEND.md) | Why the always-loaded rules stay short, and the measurements behind each change that promised to save context. |

The rules themselves live where both agents read them:

- [.github/copilot-instructions.md](../../.github/copilot-instructions.md): rules for every chat (Claude Code imports it from [CLAUDE.md](../../CLAUDE.md));
- [.claude/rules/](../../.claude/rules/) and [.github/instructions/](../../.github/instructions/): rules scoped to part of the code, identical copies;
- [.claude/skills/](../../.claude/skills/): procedures (merge, Definition of Done) and [.claude/agents/](../../.claude/agents/): the read-only reviewer.

`tests/test_agent_rules.py` keeps the copies identical and the always-loaded rules under their size target.
