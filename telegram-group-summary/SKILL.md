---
name: telegram-group-summary
version: 0.1.0
description: |
  Summarize recent activity in a Telegram group. Use this skill when the owner asks to
  summarize a Telegram group, recap what's been discussed, get a digest of a channel,
  or produce a weekly/daily summary of group activity. Trigger phrases: "summarize
  [group]", "recap [group]", "what's been happening in [group]", "digest of [group]",
  "weekly summary of [group] Telegram". Requires TELEGRAM_BOT_TOKEN.
allowed-tools:
  - Bash(python3 *)
metadata:
  nanobot:
    always: true
---

# telegram-group-summary

Fetch messages from a Telegram group and produce a structured summary.

## Required Environment Variables

- `TELEGRAM_BOT_TOKEN` — Telegram bot token (auto-injected for Telegram twins)
- `OPENCLAW_STATE_DIR` — (optional) path to OpenClaw's state directory; defaults to `/twin-data/state`

## Workflow

### Step 1 — Resolve the group

Run `list_groups.py` from the `telegram-send` skill to see available groups:

```bash
python3 "$SKILL_DIR/../telegram-send/scripts/list_groups.py"
```

Match the owner's requested group name (case-insensitive fuzzy match) to get its `chat_id`.
If the group is not listed, it may not have interacted with this twin yet.

### Step 2 — Fetch messages

```bash
python3 "$SKILL_DIR/scripts/fetch_messages.py" <chat_id>
```

Optional flags:
- `--limit N` — cap the number of messages (default: 100)
- `--since-hours N` — only include messages from the last N hours (e.g. `--since-hours 168` for 7 days)

The script tries two sources in order:
1. **OpenClaw state files** — walks `$OPENCLAW_STATE_DIR` for any stored Telegram message data (primary)
2. **Bot API `getUpdates`** — falls back to pending unprocessed updates from the Telegram Bot API

The output JSON has this shape:
```json
{
  "chat_id": -1001234567890,
  "source": "openclaw_state",
  "message_count": 83,
  "time_range": {"earliest": "2026-05-26T08:00:00Z", "latest": "2026-05-28T13:00:00Z"},
  "messages": [
    {"message_id": 1001, "sender": "Alice", "text": "Hello!", "date": "2026-05-26T08:00:00Z"}
  ]
}
```

### Step 3 — Summarize

With the messages in hand, produce a structured summary:

- **Overview** — total messages, time range, list of unique participants
- **Main topics** — 3–7 bullet points covering key themes discussed
- **Key announcements / decisions** — anything explicitly decided, announced, or agreed upon
- **Open questions / unresolved threads** — unanswered questions or ongoing debates
- **Action items** — clear next steps or tasks mentioned by participants
- **Tone** — one-line assessment (e.g. "active and collaborative", "mostly announcements", "heated debate on X")

Format the summary in clear markdown so the owner can skim it quickly.

## Handling No Data

If `source` is `"none"` in the output, inform the owner that no messages were found and suggest:
- Verify the group with `list_groups.py`
- The twin may be running in webhook mode — messages processed live aren't available via `getUpdates`
- Try a smaller `--since-hours` window in case the filter is too broad

## Notes

- **Bot privacy mode** — By default, Telegram bots in groups only receive messages directed at them (commands or replies). To summarize general group conversation, the bot must have privacy mode disabled (BotFather → `/mybots` → Bot Settings → Group Privacy → Turn off) or be a group admin. Without this, both data sources will only contain bot-directed messages, not the full chat history.
- Only `text` and `caption` fields are captured — photo/file messages without a caption are skipped.
- Summaries are produced by Claude from raw message data — no external summarization API is used.
- The `getUpdates` fallback is non-destructive (no offset is advanced), so it won't affect normal message processing.

## Related Skills

- [telegram-send](../telegram-send/SKILL.md) — send a follow-up message to the group
- [list-telegram-chats](../list-telegram-chats/SKILL.md) — list all known chats and their IDs
