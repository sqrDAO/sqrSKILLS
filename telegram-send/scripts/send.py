#!/usr/bin/env python3
"""
Send a message to one or more Telegram chats.

Usage:
    python send.py <chat_id> "<message>"
    python send.py --keyword <substr> "<message>"

Exit codes:
    0 — all messages sent successfully
    1 — one or more sends failed (errors on stderr)
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import escape as html_escape


def markdown_to_html(text: str) -> str:
    """Convert standard markdown to Telegram HTML format."""
    protected = []

    def stash_fence(match):
        protected.append(f"<pre><code>{html_escape(match.group(1), quote=False)}</code></pre>")
        return f"@@CODE{len(protected) - 1}@@"

    def stash_inline(match):
        protected.append(f"<code>{html_escape(match.group(1), quote=False)}</code>")
        return f"@@CODE{len(protected) - 1}@@"

    # Protect code before escaping and applying prose emphasis.
    text = re.sub(r"```(?:\w+\n)?(.*?)```", stash_fence, text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", stash_inline, text)
    text = html_escape(text, quote=False)

    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text, flags=re.DOTALL)

    # Italic: *text* or _text_  (after bold so ** is already consumed)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text, flags=re.DOTALL)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text, flags=re.DOTALL)

    # Strikethrough: ~~text~~
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text, flags=re.DOTALL)

    return re.sub(r"@@CODE(\d+)@@", lambda m: protected[int(m.group(1))], text)


def send_message(bot_token: str, chat_id: int, text: str) -> dict:
    base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    html_text = markdown_to_html(text)

    def _post(parse_mode=None, body_text=None):
        payload = {"chat_id": chat_id, "text": body_text if body_text is not None else text}
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

    # Try HTML (converted from markdown); fall back to plain text if parsing fails
    try:
        result = _post(parse_mode="HTML", body_text=html_text)
        if result.get("ok"):
            return result.get("result", result)
        error = result.get("description", "Unknown error")
        if "parse" in error.lower() or "entities" in error.lower():
            result = _post()
            if result.get("ok"):
                return result.get("result", result)
            raise RuntimeError(result.get("description", "Unknown error"))
        raise RuntimeError(error)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err_data = json.loads(body)
            description = err_data.get("description", str(e))
            if "parse" in description.lower() or "entities" in description.lower():
                result = _post()
                if result.get("ok"):
                    return result.get("result", result)
            raise RuntimeError(description)
        except (json.JSONDecodeError, KeyError):
            raise RuntimeError(f"HTTP {e.code}: {body}")


def main():
    parser = argparse.ArgumentParser(
        description="Send a Telegram message to one or more chats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  send.py -1001234567890 'Hello!'\n"
            "  send.py --keyword crypto 'Market update!'\n"
        ),
    )
    parser.add_argument(
        "--keyword",
        metavar="SUBSTR",
        help="send to all groups whose name contains SUBSTR (case-insensitive)",
    )
    parser.add_argument("args", nargs="+", metavar="ARG")
    parsed = parser.parse_args()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        _cfg = os.path.expanduser(os.environ.get("NANOBOT_CONFIG", "~/.nanobot/config.json"))
        try:
            with open(_cfg) as _f:
                bot_token = json.load(_f).get("channels", {}).get("telegram", {}).get("token", "")
        except Exception:
            pass
    if not bot_token:
        print(json.dumps({"ok": False, "error": "TELEGRAM_BOT_TOKEN is not set"}))
        sys.exit(1)

    if parsed.keyword:
        if len(parsed.args) != 1:
            parser.error("--keyword mode expects exactly: --keyword <substr> <message>")
        message = parsed.args[0].replace("\\n", "\n")
        if not message.strip():
            print(json.dumps({"ok": False, "error": "message cannot be empty"}))
            sys.exit(1)

        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from list_groups import list_groups

        groups = list_groups()
        keyword_lower = parsed.keyword.lower()
        matches = [g for g in groups if g.get("name") and keyword_lower in g["name"].lower()]

        if not matches:
            print(json.dumps({"ok": False, "error": f"No groups found matching keyword: {parsed.keyword!r}"}))
            sys.exit(1)

        failed = False
        results = []
        for g in matches:
            try:
                sent = send_message(bot_token, g["chat_id"], message)
                results.append({"chat_id": g["chat_id"], "name": g.get("name"), "ok": True, "message": sent})
            except Exception as e:
                results.append({"chat_id": g["chat_id"], "name": g.get("name"), "ok": False, "error": str(e)})
                print(f"Error sending to {g['name']!r} ({g['chat_id']}): {e}", file=sys.stderr)
                failed = True
        print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False))
        sys.exit(1 if failed else 0)

    else:
        if len(parsed.args) != 2:
            parser.error("expects: <chat_id> <message>")
        try:
            chat_id = int(parsed.args[0])
        except ValueError:
            print(f"Error: chat_id must be an integer, got: {parsed.args[0]!r}", file=sys.stderr)
            sys.exit(1)
        message = parsed.args[1].replace("\\n", "\n")
        if not message.strip():
            print(json.dumps({"ok": False, "chat_id": chat_id, "error": "message cannot be empty"}))
            sys.exit(1)

        try:
            sent = send_message(bot_token, chat_id, message)
            print(json.dumps({"ok": True, "chat_id": chat_id, "message": sent}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"ok": False, "chat_id": chat_id, "error": str(e)}, ensure_ascii=False))
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
