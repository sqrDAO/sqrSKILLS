---
name: list-telegram-chats
version: 0.1.0
description: |
  List Telegram groups and private chats that have interacted with this agent. Use this skill whenever you need to see who has messaged the agent, list active Telegram chats, show connected groups, or view chat history participants. Trigger phrases: "list my Telegram chats", "who has messaged me on Telegram", "show connected groups", "what Telegram groups am I in", "list telegram chats".

  IMPORTANT: This is NOT a tool — invoke via the Bash tool: python3 "$SKILL_DIR/scripts/list_chats.py"
allowed-tools:
  - Bash(python3 *)
metadata:
  nanobot:
    always: true
---

# List Telegram Chats

Retrieves unique Telegram chat IDs from local session state, categorised into groups (negative IDs) and private chats (positive IDs).

## Usage

```bash
python3 "$SKILL_DIR/scripts/list_chats.py"
# Skip name resolution (no bot token required, faster):
python3 "$SKILL_DIR/scripts/list_chats.py" --no-names
```

## Output

```json
{
  "groups": [{"chat_id": -1001234567890, "name": "My Group", "type": "supergroup", "last_updated": "2024-01-15T10:30:00Z"}],
  "private_chats": [{"chat_id": 502391728, "name": "Alice Smith", "type": "private"}]
}
```

- `name` is `null` when the bot can no longer access the chat.
- `last_updated` is present only for chats sourced from nanobot sessions.

## Prerequisites

Session sources (checked in order):
1. **Nanobot** — `~/.nanobot/workspace/sessions/telegram_*.jsonl` (configurable via `NANOBOT_SESSIONS_DIR` or `NANOBOT_WORKSPACE`)
2. **OpenClaw** — `OPENCLAW_STATE_DIR/agents/main/sessions/sessions.json` (default `/twin-data/state`)
3. **YouAI backend** — `YOUAI_API_URL` + `YOUAI_TWIN_ID` (fallback when no local sessions exist)

Bot token for name resolution (tried in order):
- `TELEGRAM_BOT_TOKEN` env var
- `channels.telegram.token` in `~/.nanobot/config.json` (override path with `NANOBOT_CONFIG`)

Without a token, `name` is omitted from all entries.

## Related Skills

- [telegram-send](../telegram-send/SKILL.md) — send a message to one of the discovered chats
