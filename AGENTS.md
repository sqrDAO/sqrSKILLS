# AGENTS.md

This file provides agent-neutral guidance for maintaining the skills in this repository.
It applies to Codex, Claude Code, Antigravity, Hermes, OpenClaw, Nanobot, Gemini CLI,
and other agentic coding systems that can read `SKILL.md` files and run local helper scripts.

## What This Repo Is

A collection of open-source Agent Skills published by [sqrDAO](https://sqrdao.com).
Each skill is a self-contained directory installable via [skills.sh](https://skills.sh):

```bash
npx skills add sqrdao/sqrSKILLS@<skill-name>
```

## Skill Structure

Every skill follows this layout:

```
<skill-name>/
├── SKILL.md        <- skill prompt + YAML frontmatter (the installable artifact)
└── scripts/        <- Python 3.10+ helper scripts invoked from SKILL.md
    └── *.py
```

Some skills also have a `data/` directory for bundled offline data or a `references/`
directory for reusable source material.

## SKILL.md Frontmatter

```yaml
---
name: skill-name
description: |
  One-paragraph trigger description for the agent's skill picker.
  Be explicit about user intents and trigger phrases.
allowed-tools:
  - Bash(python3 *)
  - Read          # only if the skill needs file reads
  - Write         # only if the skill needs file writes
  - Edit          # only if the skill needs file edits
---
```

`allowed-tools` is advisory metadata for agents that support tool permissions. Agents
with different tool names should map these capabilities to their local equivalents
(for example shell/terminal, file read, file write, file edit, web search, or fetch).
Agents that do not use this field can ignore it; the skill body remains plain
natural-language instructions.

## Runtime Portability

- Do not assume the runner is Claude Code, Codex, OpenClaw, Hermes, Antigravity, or
  any other specific agent unless a script source explicitly needs that runtime's
  local state format.
- Refer to the human as "the user" and the automation as "the agent" or "assistant".
  Avoid runtime-specific labels such as "twin" or "owner" in generic instructions.
- Use `python3` and Python stdlib only unless a skill has an explicit, documented
  dependency. The installer does not run `pip install`.
- Scripts must output machine-readable JSON to stdout and diagnostics to stderr.
- Keep commands copy-pasteable across POSIX shells.

## `$SKILL_DIR` Convention

Examples in `SKILL.md` use `$SKILL_DIR` to mean the absolute path of the installed
skill directory. Many skill installers set this automatically. If an agent does not
set it, it should resolve `$SKILL_DIR` to the directory containing the active
`SKILL.md`, or replace `$SKILL_DIR` with that path before running commands.

Scripts must never hardcode repository paths. Example invocation from `SKILL.md`:

```bash
python3 "$SKILL_DIR/scripts/my_script.py" "<arg>"
```

## Running Scripts Locally

Set `SKILL_DIR` manually and invoke directly:

```bash
SKILL_DIR=./nearby-places-search \
  GOOGLE_PLACES_API_KEY=<key> \
  python3 nearby-places-search/scripts/search_places.py "coffee shop" "London"

SKILL_DIR=./vietnam-visa-check \
  python3 vietnam-visa-check/scripts/query_visa.py --nationality US --duration_days 14

SKILL_DIR=./telegram-send \
  TELEGRAM_BOT_TOKEN=<token> YOUAI_API_URL=<url> YOUAI_TWIN_ID=<id> \
  python3 telegram-send/scripts/list_groups.py

WIKI_DIR=./wiki SKILL_DIR=./llm-wiki \
  python3 llm-wiki/scripts/search.py "my query"
```

## Per-Skill Environment Variables

| Skill | Required Env Vars | Optional Env Vars |
|-------|-------------------|-------------------|
| `nearby-places-search` | `GOOGLE_PLACES_API_KEY` | `OPENCLAW_WORKSPACE_DIR` |
| `telegram-send` | `TELEGRAM_BOT_TOKEN` | `YOUAI_API_URL`, `YOUAI_TWIN_ID`, `NANOBOT_CONFIG`, `NANOBOT_SESSIONS_DIR`, `NANOBOT_WORKSPACE`, `OPENCLAW_STATE_DIR` |
| `list-telegram-chats` | `TELEGRAM_BOT_TOKEN` for name resolution | `NANOBOT_CONFIG`, `NANOBOT_SESSIONS_DIR`, `NANOBOT_WORKSPACE`, `OPENCLAW_STATE_DIR`, `YOUAI_API_URL`, `YOUAI_TWIN_ID` |
| `telegram-group-summary` | `TELEGRAM_BOT_TOKEN` for Bot API fallback | `OPENCLAW_STATE_DIR` |
| `llm-wiki` | None | `WIKI_DIR` |
| `vietnam-visa-check` | None | None |
| `vietnam-crypto-radar` | Web access or equivalent research tools | None |
| `luma-calendar` | `LUMA_API_KEY` | None |
| `gtm-playbook` | None | None |

## Versioning

Every `SKILL.md` has a `version:` field following SemVer (`MAJOR.MINOR.PATCH`).
Bump the version in the same commit as the change:

| Change type | Example | Bump |
|-------------|---------|------|
| Bugfix, non-breaking prompt/script tweak | Fix formatting, clarify portable invocation | PATCH -> `0.1.1` |
| New feature, new optional arg/command | Add `--dry-run` flag, new subcommand | MINOR -> `0.2.0` |
| Breaking change | Rename/remove env var, change arg signature | MAJOR -> `1.0.0` |

Users running `npx skills update` rely on this to understand what changed.

## Adding a New Skill

1. Create `<skill-name>/SKILL.md` with the frontmatter above.
2. Add Python scripts to `<skill-name>/scripts/` using stdlib-only Python unless
   there is a compelling documented reason.
3. Add the skill to the table in `README.md`.
4. Use portable language in the skill body and document how non-shell tool names map
   to the needed capabilities.
5. If the skill needs runtime-specific state, document each supported source and
   treat it as one input source, not as the identity of the whole agent.

## Architecture Notes

- No package managers, no build step.
- Scripts output JSON to stdout, diagnostics to stderr.
- `vietnam-visa-check` is fully offline. Policy data lives in
  `data/vietnam_immigration_policy.json`.
- `nearby-places-search` can use a workspace memory file
  (`OPENCLAW_WORKSPACE_DIR/MEMORY.md`) for cached coordinates before hitting Google
  geocoding.
- `llm-wiki` wiki data is gitignored. The `wiki/` directory is a runtime artifact,
  not tracked in this repo.
- `gtm-playbook` is the documented exception to stdlib-only Python: its
  `scripts/build_gtm_workbook.py` needs `openpyxl` to emit the xlsx workbook.
  All conversational/markdown flows in the skill work without it. It also has
  `references/` (framework source material) and `assets/` (original templates
  plus `example-answers.json`).
