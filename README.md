# sqrSKILLS

[![Install via skills.sh](https://img.shields.io/badge/skills.sh-install-green)](https://skills.sh/sqrdao/sqrSKILLS)

Open-source [Agent Skills](https://agentskills.io/home) published by [sqrDAO](https://sqrdao.com). Covers Telegram integration, location search, personal knowledge management, Luma events, Vietnam visa checks, Vietnam crypto regulation briefings, Web3 builder opportunities, and business-model and go-to-market planning.

## Installation

```bash
npx skills add sqrdao/sqrSKILLS
```

The installer lets you select which skills to install. To install a specific skill directly:

```bash
npx skills add sqrdao/sqrSKILLS@telegram-send
npx skills add sqrdao/sqrSKILLS@list-telegram-chats
npx skills add sqrdao/sqrSKILLS@nearby-places-search
npx skills add sqrdao/sqrSKILLS@llm-wiki
npx skills add sqrdao/sqrSKILLS@vietnam-visa-check
npx skills add sqrdao/sqrSKILLS@vietnam-crypto-radar
npx skills add sqrdao/sqrSKILLS@telegram-group-summary
npx skills add sqrdao/sqrSKILLS@luma-calendar
npx skills add sqrdao/sqrSKILLS@web3-opportunities
npx skills add sqrdao/sqrSKILLS@business-model-to-market
```

`npx skills add` installs to all supported agents automatically where the skills installer has an adapter (Claude Code, Codex, Gemini CLI, OpenClaw, Hermes, Nanobot, and others).

## Available Skills

- [**telegram-send**](./telegram-send/) — Send messages to Telegram groups and channels the agent's Telegram bot can access. Requires `TELEGRAM_BOT_TOKEN`.
- [**list-telegram-chats**](./list-telegram-chats/) — List Telegram groups and private chats that have interacted with the agent's Telegram bot. Reads local session state first.
- [**nearby-places-search**](./nearby-places-search/) — Real-time place search via Google Places API. Returns results with addresses, ratings, and Maps links. Requires `GOOGLE_PLACES_API_KEY`.
- [**llm-wiki**](./llm-wiki/) — Personal compounding knowledge base. Ingest sources, query compiled knowledge, and keep pages consistent. Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
- [**vietnam-visa-check**](./vietnam-visa-check/) — Vietnam visa and entry requirements for any nationality. Fully offline — policy data is bundled (verified through June 2026).
- [**vietnam-crypto-radar**](./vietnam-crypto-radar/) — Up-to-date intelligence briefings on Vietnam's crypto/digital-asset regulation: laws, decrees, tax, the pilot exchange market, and enforcement. Diffs against a dated baseline so you always know what's new.
- [**telegram-group-summary**](./telegram-group-summary/) — Fetch messages from a Telegram group and produce a structured summary: topics, decisions, action items, and tone. Requires `TELEGRAM_BOT_TOKEN`.
- [**luma-calendar**](./luma-calendar/) — Manage Luma events and guests via the Luma API: list events, create events, view registrants, and add guests. Requires `LUMA_API_KEY`.
- [**web3-opportunities**](./web3-opportunities/) — Curated, filterable catalog of Web3 builder/founder opportunities (accelerators, incubators, grants, hackathons, bounties, retroactive funding, fellowships) split by type, stage/dilution, chain/ecosystem, and geography, with a SEA/Vietnam highlight. Bundled offline roster + optional live enrichment of deadlines and cohort status.
- [**business-model-to-market**](./business-model-to-market/) — Take a venture from a blank page to closed deals: opportunity brainstorms and weighted decision matrices, the nine-block Business Model Canvas, mission, ICP and buyer personas, sales methodologies (BANT, MEDDIC/MEDDPICC, Value Selling, Challenger), the 8-stage sales cycle, cold outreach, objection handling, and Web3 partnership goal matrices. Emits an 11-tab spreadsheet deliverable (needs `openpyxl`). Formerly `gtm-playbook`.

## Requirements

- Python 3.10+
- Per-skill environment variables:

| Skill | Required | Optional |
|-------|----------|----------|
| telegram-send | `TELEGRAM_BOT_TOKEN`, `YOUAI_API_URL`, `YOUAI_TWIN_ID` | — |
| list-telegram-chats | `TELEGRAM_BOT_TOKEN` | `OPENCLAW_STATE_DIR` (reads local session state when set) |
| nearby-places-search | `GOOGLE_PLACES_API_KEY` | — |
| llm-wiki | — | `WIKI_DIR` (defaults to `./wiki/`) |
| vietnam-visa-check | — | — |
| vietnam-crypto-radar | — | — |
| telegram-group-summary | `TELEGRAM_BOT_TOKEN` | `OPENCLAW_STATE_DIR` |
| luma-calendar | `LUMA_API_KEY` | — |
| web3-opportunities | — | — |
| business-model-to-market | — | — (spreadsheet output needs the `openpyxl` Python package) |

Set these through your agent's environment/configuration mechanism (for example a shell profile, project `.env`, Claude Code env file, Codex environment, Hermes/OpenClaw config, or your runtime's equivalent).

## Manual Installation

For agents that don't use `npx skills add`, copy the skill directory to the appropriate location:

```bash
# Claude Code
cp -r <skill-name> ~/.claude/skills/

# OpenClaw
cp -r <skill-name> ~/.openclaw/skills/

# Hermes
cp -r <skill-name> ~/.hermes/skills/

# Nanobot, Codex, Gemini CLI, Antigravity, and other Agent Skills-compatible runtimes
cp -r <skill-name> ~/.agents/skills/
```

| Agent | Global skills directory |
|-------|------------------------|
| Claude Code | `~/.claude/skills/` |
| OpenClaw | `~/.openclaw/skills/` |
| Hermes | `~/.hermes/skills/` |
| Nanobot | `~/.agents/skills/` |
| Codex | `~/.agents/skills/` |
| Gemini CLI | `~/.agents/skills/` |
| Antigravity | `~/.agents/skills/` or the skills directory configured by the runtime |
| Other Agent Skills runtimes | Use the runtime's configured skills directory |

## Installing via chat

Many agents can install and invoke skills without leaving the conversation:

| Agent | Install | Invoke |
|-------|---------|--------|
| Claude Code | Ask: *"install the sqrdao telegram-send skill"* | `/<skill-name>` or describe what you need — auto-activates on description match |
| OpenClaw | Paste the GitHub URL in chat and ask the agent to install it — text only, no commands needed (see below) | `/skill <name>` or describe what you need — auto-activates on description match |
| Hermes | Type `/skills` or `/` to browse and install from the Skills Hub | `/skill <name>` or describe what you need — auto-activates on description match |
| Codex / Antigravity / others | Install via the runtime's skills mechanism or copy the folder manually | Describe what you need; agents with skill selection should auto-activate on description match |

### OpenClaw: install with plain text, no commands

OpenClaw installs skills entirely through conversation — you never need to open a terminal or run a command. Just send the agent a message:

> Install this skill: https://github.com/sqrdao/sqrSKILLS/tree/main/llm-wiki

The GitHub URL for any skill in this repo follows this pattern:

```
https://github.com/sqrdao/sqrSKILLS/tree/main/<skill-name>
```

You can also ask by name without a URL:

> Install the telegram-send skill from the sqrdao/sqrSKILLS repo on GitHub

Or install everything at once:

> Install all skills from https://github.com/sqrdao/sqrSKILLS

The agent fetches the skill, places it in its skills directory (`~/.openclaw/skills/`), and confirms when it's ready. If a skill needs an environment variable (see [Requirements](#requirements)), tell the agent in the same conversation — for example: *"Set TELEGRAM_BOT_TOKEN to `<your token>` for the telegram-send skill"* — and it will store it in its config.

Once installed, invoke a skill with `/skill <name>` or just describe what you need; skills auto-activate when your request matches their description.

## Skill Format

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: |
  One-paragraph trigger description. The agent's skill picker reads this
  to decide when to activate the skill.
allowed-tools:
  - Bash(python3 *)   # shell/terminal commands the skill may run
  - Read              # file reads, if needed
  - Write             # file writes, if needed
---

[skill prompt / instructions follow here]
```

`allowed-tools` maps to the agent's tool permission system. Agents with different tool names should map these capabilities to their local equivalents (shell/terminal, file read, file write/edit, web search/fetch). Agents that don't use this field can ignore it — the skill body below the frontmatter is plain natural-language instructions.

### Runtime conventions

- Commands use `$SKILL_DIR` for the installed skill directory. If your agent does not set it automatically, resolve it to the directory containing the active `SKILL.md` before running examples.
- Skill bodies should refer to "the user" and "the agent" instead of assuming a specific product identity.
- Helper scripts use Python 3.10+ and stdlib-only dependencies unless a skill explicitly says otherwise.

## Automated maintenance

Skills with time-sensitive data are refreshed weekly by a scheduled GitHub
Actions workflow ([`.github/workflows/weekly-skill-refresh.yml`](./.github/workflows/weekly-skill-refresh.yml)).
Every Monday it re-researches `vietnam-crypto-radar`, `web3-opportunities`, and
`vietnam-visa-check` against their dated baselines and opens a pull request with
any verified changes — nothing is merged automatically.

To enable it on a fork: add a `GEMINI_API_KEY` repository secret (get a key from
[Google AI Studio](https://aistudio.google.com/apikey)) and allow Actions to
create pull requests (Settings → Actions → General → Workflow permissions). The
workflow can also be triggered manually from the Actions tab.

## Support

Open an issue in the [GitHub Issue Tracker](https://github.com/sqrdao/sqrSKILLS/issues) if you encounter a bug or have a question.

## Contributing

Contributions are welcome. To add a skill or fix an existing one:

1. Fork this repository
2. Create a `docs/backlog/todo.<slug>.md` spec and list it in
   [`docs/backlog/PRIORITY.md`](./docs/backlog/PRIORITY.md)
3. Create or update `<skill-name>/SKILL.md` and any `<skill-name>/scripts/*.py`
4. Follow the structure in [AGENTS.md](./AGENTS.md) — portable wording,
   stdlib-only Python, JSON to stdout
5. Run the same harness used by CI:

   ```bash
   python3 scripts/validate_skills.py
   python3 -m unittest discover -s tests -v
   ```

6. Open a pull request; `main` requires the `Skill Harness` check to pass

The `todo.*` spec becomes `done.*` only after explicit maintainer approval. See
[AGENTS.md](./AGENTS.md) for the full Plan → Do → Check → Verify → Act workflow.

## License

MIT
