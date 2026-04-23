# sqrSkills

Open-source Claude Code skills published by [sqrDAO](https://sqrdao.com).

Each skill is a self-contained directory with a `SKILL.md` (the skill prompt) and `scripts/` (Python helpers). Install via [skills.sh](https://skills.sh) or copy the directory into your Claude Code skills path.

## Skills

| Skill | Description |
|-------|-------------|
| [list-telegram-chats](./list-telegram-chats/) | List Telegram groups and private chats that have interacted with the twin |
| [nearby-places-search](./nearby-places-search/) | Real-time place search via Google Places API |
| [llm-wiki](./llm-wiki/) | Personal compounding knowledge base (Karpathy's LLM Wiki pattern) |
| [telegram-send](./telegram-send/) | Send messages to Telegram groups via a bot |
| [vietnam-visa-check](./vietnam-visa-check/) | Vietnam visa & entry requirements for any nationality (offline, bundled data) |

## Installation

### Via skills.sh
```bash
skills install sqrdao/list-telegram-chats
skills install sqrdao/nearby-places-search
skills install sqrdao/llm-wiki
skills install sqrdao/telegram-send
skills install sqrdao/vietnam-visa-check
```

### Manual
Copy the skill directory into your Claude Code skills path. The skill scripts use `SKILL_DIR` (automatically set to the skill's installed directory) so no path adjustment is needed.

## Requirements

- Python 3.10+
- Per-skill environment variables (see each skill's README)

## License

MIT
