#!/usr/bin/env python3
"""
Fetch messages from a Telegram group for summarization.

Primary source: OpenClaw's local state directory (stored message history).
Fallback: Telegram Bot API getUpdates (pending unprocessed messages only).

Usage:
    python3 fetch_messages.py <chat_id> [--limit N] [--since-hours N]

Output:
    JSON to stdout with "messages" array and source metadata.
    Diagnostics to stderr.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request


def _normalize_message(msg: dict) -> "dict | None":
    """Normalize a Telegram message dict into our output format."""
    try:
        text = msg.get("text") or msg.get("caption", "")
        if not text:
            return None
        date_ts = float(msg["date"])
        date_iso = datetime.datetime.utcfromtimestamp(date_ts).strftime("%Y-%m-%dT%H:%M:%SZ")

        from_field = msg.get("from") or {}
        if isinstance(from_field, dict):
            first = from_field.get("first_name", "")
            last = from_field.get("last_name", "")
            username = from_field.get("username", "")
            sender = (f"{first} {last}".strip() or username or "Unknown")
        else:
            sender = str(from_field) or "Unknown"

        return {
            "message_id": msg.get("message_id"),
            "sender": sender,
            "text": str(text),
            "date": date_iso,
            "date_ts": date_ts,
        }
    except (KeyError, TypeError, ValueError):
        return None


def _extract_from_value(value, target_chat_id: int, since_ts: "float | None") -> list:
    """Recursively extract Telegram messages matching target_chat_id from a parsed JSON value."""
    messages = []
    if isinstance(value, dict):
        # Check if this dict looks like a Telegram message
        chat = value.get("chat")
        chat_id = (chat.get("id") if isinstance(chat, dict) else None) or value.get("chat_id")
        if "text" in value and "date" in value and chat_id == target_chat_id:
            normalized = _normalize_message(value)
            if normalized and (since_ts is None or normalized["date_ts"] >= since_ts):
                messages.append(normalized)
        else:
            for v in value.values():
                if isinstance(v, (dict, list)):
                    messages.extend(_extract_from_value(v, target_chat_id, since_ts))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                messages.extend(_extract_from_value(item, target_chat_id, since_ts))
    return messages


def _messages_from_openclaw_state(target_chat_id: int, limit: int, since_ts: "float | None") -> list:
    """Walk OpenClaw's state directory looking for stored Telegram messages."""
    state_dir = os.environ.get("OPENCLAW_STATE_DIR", "")
    if not os.path.isdir(state_dir):
        return []

    messages = []
    for root, _dirs, files in os.walk(state_dir):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)
                messages.extend(_extract_from_value(data, target_chat_id, since_ts))
            except Exception:
                continue

    # Deduplicate by message_id (or text prefix if no ID)
    seen: set = set()
    deduped = []
    for m in messages:
        key = m.get("message_id") or m["text"][:60]
        if key not in seen:
            seen.add(key)
            deduped.append(m)

    deduped.sort(key=lambda m: m["date_ts"])
    return deduped[-limit:]


def _messages_from_bot_api(target_chat_id: int, limit: int, since_ts: "float | None") -> list:
    """Fetch pending updates from Bot API, filtered by chat_id (non-destructive — no offset advance)."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        print("Warning: TELEGRAM_BOT_TOKEN not set — skipping Bot API fallback", file=sys.stderr)
        return []

    url = (
        f"https://api.telegram.org/bot{bot_token}/getUpdates"
        "?limit=100&allowed_updates=%5B%22message%22%5D"
    )
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Warning: Bot API getUpdates failed: {e}", file=sys.stderr)
        return []

    if not data.get("ok"):
        print(f"Warning: Bot API error: {data.get('description', 'unknown')}", file=sys.stderr)
        return []

    messages = []
    for update in data.get("result", []):
        msg = update.get("message")
        if not msg:
            continue
        chat = msg.get("chat", {})
        if chat.get("id") != target_chat_id:
            continue
        normalized = _normalize_message(msg)
        if normalized and (since_ts is None or normalized["date_ts"] >= since_ts):
            messages.append(normalized)

    messages.sort(key=lambda m: m["date_ts"])
    return messages[-limit:]


def fetch_messages(chat_id: int, limit: int, since_ts: "float | None") -> dict:
    messages = _messages_from_openclaw_state(chat_id, limit, since_ts)
    source = "openclaw_state"

    if not messages:
        messages = _messages_from_bot_api(chat_id, limit, since_ts)
        source = "bot_api" if messages else "none"

    if not messages:
        print(
            "No messages found. Possible reasons:\n"
            "  • Bot uses webhooks (OpenClaw default) — getUpdates returns nothing.\n"
            "  • No messages from this group are stored in local state.\n"
            "  • chat_id is incorrect — run list_groups.py to verify.\n"
            "  • --since-hours filter may be too narrow.",
            file=sys.stderr,
        )

    result: dict = {
        "chat_id": chat_id,
        "source": source,
        "message_count": len(messages),
        "time_range": None,
        "messages": messages,
    }
    if messages:
        result["time_range"] = {
            "earliest": messages[0]["date"],
            "latest": messages[-1]["date"],
        }
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Telegram group messages for summarization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  fetch_messages.py -1001234567890\n"
            "  fetch_messages.py -1001234567890 --limit 200\n"
            "  fetch_messages.py -1001234567890 --since-hours 48\n"
        ),
    )
    parser.add_argument("chat_id", type=int, help="Telegram chat ID (negative for groups)")
    parser.add_argument("--limit", type=int, default=100, help="max messages to return (default: 100)")
    parser.add_argument(
        "--since-hours",
        type=float,
        dest="since_hours",
        help="only include messages newer than N hours",
    )
    args = parser.parse_args()

    since_ts = None
    if args.since_hours is not None:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=args.since_hours)
        since_ts = cutoff.timestamp()

    result = fetch_messages(args.chat_id, args.limit, since_ts)
    # Strip internal date_ts field before output
    for msg in result["messages"]:
        msg.pop("date_ts", None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
