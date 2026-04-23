---
name: list-telegram-chats
description: Lists Telegram chat IDs (groups and private chats) that have interacted with this twin. Use this skill whenever the owner asks to see who has messaged the twin, list active chats, show connected groups, or view chat history participants. Execute via Bash: `python3 "$SKILL_DIR/scripts/list_chats.py"`. Do NOT use Telegram API tools — this skill works by reading the local session state.
allowed-tools:
  - Bash(python3 *)
---

# List Telegram Chats

Retrieves unique Telegram chat IDs from local session state, categorised into groups (negative IDs) and private chats (positive IDs).

## Usage

```bash
python3 "$SKILL_DIR/scripts/list_chats.py"
```

## Output

```json
{
  "groups": [{"chat_id": -1001234567890, "type": "group"}],
  "private_chats": [{"chat_id": 502391728, "type": "direct"}]
}
```

## Prerequisites

- No additional configuration required — reads from local session files (`OPENCLAW_STATE_DIR`, default `/twin-data/state`).
- Falls back to the YouAI backend API (`YOUAI_API_URL` + `YOUAI_TWIN_ID`) if no local sessions exist.
