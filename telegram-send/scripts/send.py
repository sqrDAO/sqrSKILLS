#!/usr/bin/env python3
"""
Send a message to a Telegram chat using the bot's token.

Usage:
    python send.py <chat_id> <message>

Exit codes:
    0 — message sent successfully
    1 — failed to send (error on stderr)
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def _post(parse_mode=None):
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            base_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())

    # Try Markdown first; fall back to plain text if parsing fails
    try:
        result = _post(parse_mode="Markdown")
        if result.get("ok"):
            return
        error = result.get("description", "Unknown error")
        if "parse" in error.lower() or "entities" in error.lower():
            result = _post()
            if result.get("ok"):
                return
            raise RuntimeError(result.get("description", "Unknown error"))
        raise RuntimeError(error)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err_data = json.loads(body)
            description = err_data.get("description", str(e))
            # Markdown parse error — retry as plain text
            if "parse" in description.lower() or "entities" in description.lower():
                result = _post()
                if result.get("ok"):
                    return
            raise RuntimeError(description)
        except (json.JSONDecodeError, KeyError):
            raise RuntimeError(f"HTTP {e.code}: {body}")


def main():
    if len(sys.argv) < 3:
        print("Usage: send.py <chat_id> <message>", file=sys.stderr)
        sys.exit(1)

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set", file=sys.stderr)
        sys.exit(1)

    try:
        chat_id = int(sys.argv[1])
    except ValueError:
        print(f"Error: chat_id must be an integer, got: {sys.argv[1]!r}", file=sys.stderr)
        sys.exit(1)

    message = sys.argv[2].replace('\\n', '\n')
    if not message.strip():
        print("Error: message cannot be empty", file=sys.stderr)
        sys.exit(1)

    try:
        send_message(bot_token, chat_id, message)
        print(f"Message sent to chat {chat_id}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
