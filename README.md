# sqrSKILLS

[![Install via skills.sh](https://img.shields.io/badge/skills.sh-install-green)](https://skills.sh/sqrdao/sqrSKILLS)

Open-source [Agent Skills](https://agentskills.io/home) published by [sqrDAO](https://sqrdao.com). Covers Telegram integration, location search, and personal knowledge management.

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
```

`npx skills add` installs to all 45+ supported agents automatically (Claude Code, Codex, Gemini CLI, OpenClaw, Nanobot, and others).

## Available Skills

- [**telegram-send**](./telegram-send/) — Send messages to Telegram groups and channels the twin is a member of. Requires `TELEGRAM_BOT_TOKEN`.
- [**list-telegram-chats**](./list-telegram-chats/) — List Telegram groups and private chats that have interacted with this twin. Reads local session state — no API call required.
- [**nearby-places-search**](./nearby-places-search/) — Real-time place search via Google Places API. Returns results with addresses, ratings, and Maps links. Requires `GOOGLE_PLACES_API_KEY`.
- [**llm-wiki**](./llm-wiki/) — Personal compounding knowledge base. Ingest sources, query compiled knowledge, and keep pages consistent. Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
- [**vietnam-visa-check**](./vietnam-visa-check/) — Vietnam visa and entry requirements for any nationality. Fully offline — policy data is bundled (as of April 2026).

## Requirements

- Python 3.10+
- Per-skill environment variables — see each skill's `SKILL.md` for details

## Manual Installation

For agents that look in a specific skills directory:

```bash
# Claude Code
cp -r <skill-name> ~/.claude/skills/

# OpenClaw, Nanobot, Codex, Gemini CLI, and others
cp -r <skill-name> ~/.agents/skills/
```

## Support

Open an issue in the [GitHub Issue Tracker](https://github.com/sqrdao/sqrSKILLS/issues) if you encounter a bug or have a question.

## Contributing

Contributions are welcome. To add a skill or fix an existing one:

1. Fork this repository
2. Create a new directory: `<skill-name>/SKILL.md` + `<skill-name>/scripts/*.py`
3. Follow the structure in [CLAUDE.md](./CLAUDE.md) — stdlib-only Python, JSON to stdout
4. Open a pull request

## License

MIT
