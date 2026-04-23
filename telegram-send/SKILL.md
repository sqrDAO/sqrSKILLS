---
name: telegram-send
description: |
  Send messages to Telegram groups and channels that a bot is a member of. Use this skill when the user asks to broadcast, notify, or send a message to a Telegram group or channel. Trigger phrases: "send to telegram", "message the group", "broadcast to", "notify the channel", "post to telegram". Requires TELEGRAM_BOT_TOKEN.
allowed-tools:
  - Bash(python3 *)
---

# Telegram Send

Send messages to Telegram groups and channels the bot is a member of.

## Required Environment Variables

- `TELEGRAM_BOT_TOKEN` — Telegram bot token

## Optional Environment Variables (for group discovery)

- `YOUAI_API_URL` — YouAI backend URL (for listing known groups via the YouAI platform)
- `YOUAI_TWIN_ID` — Twin ID (for YouAI platform group discovery)

> **Note**: Without `YOUAI_API_URL` / `YOUAI_TWIN_ID`, group listing returns an empty array. You can still send directly if you know the `chat_id`.

## Commands

### List known groups

```bash
python3 "$SKILL_DIR/scripts/list_groups.py"
```

Returns a JSON array of group chats the bot has interacted with:

```json
[
  {"chat_id": -1001234567890, "name": "Team Chat", "type": "supergroup"},
  {"chat_id": -987654321, "name": "Marketing", "type": "group"}
]
```

Returns `[]` if no groups are known or the backend is unreachable.

### Send a message

```bash
python3 "$SKILL_DIR/scripts/send.py" <chat_id> "<message>"
```

Example:

```bash
python3 "$SKILL_DIR/scripts/send.py" -1001234567890 "Meeting at 3pm today!"
```

Exits 0 on success, 1 on failure (error written to stderr).

## Usage Instructions

1. When the owner asks to send a message to a group, first run `list_groups.py` to discover available groups and resolve the target group name to a `chat_id`.
2. If the requested group is not in the list, inform the owner that the bot has not received any messages from that group yet.
3. Run `send.py` with the resolved `chat_id` and the message text.
4. Never guess or fabricate a `chat_id`.

## Notes

- Only groups that have sent at least one message to the bot are discoverable via `list_groups.py`.
- The bot must be a member of the group for the send to succeed.
- Messages support Markdown formatting (bold, italic, code blocks).
