---
name: telegram-send
description: |
  Send a message to a Telegram group or channel the twin is a member of. Use this skill whenever the owner asks to send, post, or broadcast a message to a Telegram group or channel. Trigger phrases: "send a message to [group]", "post to Telegram", "broadcast to [channel]", "message the [group name] Telegram group". Requires TELEGRAM_BOT_TOKEN, YOUAI_API_URL, and YOUAI_TWIN_ID.
allowed-tools:
  - Bash(python3 *)
---

# telegram-send

Send messages to Telegram groups and channels that this twin is a member of.

## Overview

This skill lets the twin's owner instruct the twin to proactively broadcast a message
to any Telegram group or channel the bot has previously interacted with.

## Required Environment Variables

- `TELEGRAM_BOT_TOKEN` — Telegram bot token (auto-injected for Telegram twins)
- `YOUAI_API_URL` — YouAI backend URL (auto-injected, e.g. https://api.tryyouai.me)
- `YOUAI_TWIN_ID` — This twin's ID (auto-injected)

## Commands

### List known groups

```bash
python3 "$SKILL_DIR/scripts/list_groups.py"
```

Returns a JSON array of group chats the twin has interacted with:

```json
[
  {"chat_id": -1001234567890, "name": "Team Chat", "type": "supergroup"},
  {"chat_id": -987654321, "name": "Marketing", "type": "group"}
]
```

Returns `[]` if no groups are known yet or the backend is unreachable.

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

1. When the owner asks to send a message to a group, first run `list_groups.py` to
   discover available groups and resolve the target group name to a `chat_id`.
2. If the requested group is not in the list, inform the owner that the bot has not
   received any messages from that group yet (the bot must be added and have received
   at least one message for it to appear).
3. Run `send.py` with the resolved `chat_id` and the message text.
4. Never guess or fabricate a `chat_id`.

## Notes

- Only groups that have sent at least one message to this twin are discoverable.
- `name` is resolved via the Telegram Bot API (`getChat`) using `TELEGRAM_BOT_TOKEN`. If the bot has been removed from a group, `name` will be `null` — the `chat_id` is still valid for sending if the bot is re-added.
- The bot must still be a member of the group for the send to succeed.
- Messages support Markdown formatting (bold, italic, code blocks).
