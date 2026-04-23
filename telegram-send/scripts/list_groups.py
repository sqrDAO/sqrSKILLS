#!/usr/bin/env python3
"""
List Telegram group chats this twin is known to be a member of.

Primary source: OpenClaw's local sessions.json (authoritative for all chats
the twin has ever handled directly). Falls back to the YouAI backend API
(which only tracks chats processed through the backend, not OpenClaw-direct).

Group names are resolved via the Telegram Bot API (getChat) using
TELEGRAM_BOT_TOKEN, which is auto-injected in OpenClaw containers.

Usage:
    python list_groups.py

Output:
    JSON array on stdout, e.g.:
    [{"chat_id": -1001234567890, "name": "My Group", "type": "supergroup"}]

    Returns [] if no groups are known.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _groups_from_openclaw_sessions() -> list:
    """Read group chat IDs from OpenClaw's local sessions.json."""
    sessions_path = os.path.join(
        os.environ.get("OPENCLAW_STATE_DIR", "/twin-data/state"),
        "agents", "main", "sessions", "sessions.json",
    )
    if not os.path.exists(sessions_path):
        return []
    try:
        with open(sessions_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Warning: could not read sessions.json: {e}", file=sys.stderr)
        return []

    seen: set[int] = set()
    groups = []
    for session in data.values():
        to = session.get("lastTo") or session.get("deliveryContext", {}).get("to", "")
        if not isinstance(to, str) or not to.startswith("telegram:"):
            continue
        try:
            chat_id = int(to.split(":")[1])
        except (ValueError, IndexError):
            continue
        if chat_id < 0 and chat_id not in seen:
            seen.add(chat_id)
            groups.append({"chat_id": chat_id, "type": session.get("chatType", "group")})

    return groups


def _groups_from_backend() -> list:
    """Fallback: query the YouAI backend API for known group chats."""
    api_url = os.environ.get("YOUAI_API_URL", "").rstrip("/")
    twin_id = os.environ.get("YOUAI_TWIN_ID", "").strip()

    if not api_url or not twin_id:
        return []

    url = f"{api_url}/api/twins/{urllib.parse.quote(twin_id)}/telegram/chats"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {twin_id}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Warning: backend returned HTTP {e.code} for chat list", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Warning: could not reach backend: {e}", file=sys.stderr)
        return []

    chats = data.get("chats", [])
    return [c for c in chats if c.get("chat_id", 0) < 0]


def _resolve_names(groups: list) -> list:
    """Enrich each group entry with its name from the Telegram Bot API (getChat).

    Uses TELEGRAM_BOT_TOKEN, which is auto-injected in OpenClaw containers.
    Groups the bot can no longer access are returned with name=null.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        return groups

    enriched = []
    for g in groups:
        chat_id = g["chat_id"]
        try:
            url = (
                f"https://api.telegram.org/bot{bot_token}/getChat"
                f"?chat_id={urllib.parse.quote(str(chat_id))}"
            )
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
            if data.get("ok"):
                result = data["result"]
                name = (
                    result.get("title")
                    or result.get("first_name")
                    or result.get("username")
                )
                chat_type = result.get("type", g.get("type", "group"))
                enriched.append({"chat_id": chat_id, "name": name, "type": chat_type})
            else:
                enriched.append({**g, "name": None})
        except Exception as e:
            print(f"Warning: could not resolve name for chat {chat_id}: {e}", file=sys.stderr)
            enriched.append({**g, "name": None})

    return enriched


def list_groups() -> list:
    groups = _groups_from_openclaw_sessions()
    if not groups:
        groups = _groups_from_backend()
    return _resolve_names(groups)


def main():
    groups = list_groups()
    print(json.dumps(groups, ensure_ascii=False))


if __name__ == "__main__":
    main()
