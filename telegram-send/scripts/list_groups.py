#!/usr/bin/env python3
"""
List Telegram group chats this agent is known to be a member of.

Sources (in priority order):
  1. Nanobot sessions: ~/.nanobot/workspace/sessions/telegram_*.jsonl
  2. OpenClaw sessions.json
  3. YouAI backend API

Group names are resolved via the Telegram Bot API (getChat).

Usage:
    python list_groups.py [--no-names]

Output:
    JSON array on stdout, e.g.:
    [{"chat_id": -1001234567890, "name": "My Group", "type": "supergroup"}]

    Returns [] if no groups are known.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _telegram_bot_token() -> str:
    """Read the bot token from env or nanobot config.json."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    config_path = os.environ.get(
        "NANOBOT_CONFIG",
        os.path.expanduser("~/.nanobot/config.json"),
    )
    try:
        with open(config_path) as f:
            config = json.load(f)
        return config.get("channels", {}).get("telegram", {}).get("token", "")
    except Exception:
        return ""


def _groups_from_nanobot_sessions() -> list:
    """Read group chat IDs from nanobot session files (telegram_<chat_id>.jsonl, negative IDs only)."""
    sessions_dir = os.environ.get("NANOBOT_SESSIONS_DIR") or os.path.join(
        os.environ.get("NANOBOT_WORKSPACE", os.path.expanduser("~/.nanobot/workspace")),
        "sessions",
    )
    if not os.path.isdir(sessions_dir):
        return []

    seen: set = set()
    groups = []

    try:
        entries = os.listdir(sessions_dir)
    except Exception as e:
        print(f"Warning: could not list nanobot sessions: {e}", file=sys.stderr)
        return []

    for filename in entries:
        if not (filename.startswith("telegram_") and filename.endswith(".jsonl")):
            continue
        stem = filename[len("telegram_"):-len(".jsonl")]
        try:
            chat_id = int(stem)
        except ValueError:
            continue
        if chat_id >= 0 or chat_id in seen:
            continue
        seen.add(chat_id)
        groups.append({"chat_id": chat_id})

    return groups


def _groups_from_openclaw_sessions() -> list:
    """Read group chat IDs from OpenClaw's local sessions.json."""
    state_dir = os.environ.get("OPENCLAW_STATE_DIR", "")
    if not state_dir:
        return []
    sessions_path = os.path.join(state_dir, "agents", "main", "sessions", "sessions.json")
    if not os.path.exists(sessions_path):
        return []
    try:
        with open(sessions_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Warning: could not read sessions.json: {e}", file=sys.stderr)
        return []

    seen: set = set()
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
    """Enrich each group entry with its name from the Telegram Bot API (getChat)."""
    bot_token = _telegram_bot_token()
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


def list_groups(resolve_names: bool = True) -> list:
    nanobot = _groups_from_nanobot_sessions()
    openclaw = _groups_from_openclaw_sessions()
    seen: set = set()
    groups = []
    for g in nanobot + openclaw:
        if g["chat_id"] not in seen:
            seen.add(g["chat_id"])
            groups.append(g)
    if not groups:
        groups = _groups_from_backend()
    if resolve_names:
        return _resolve_names(groups)
    return groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-names", action="store_true", help="Skip name resolution via Telegram API")
    args = parser.parse_args()
    print(json.dumps(list_groups(resolve_names=not args.no_names), ensure_ascii=False))


if __name__ == "__main__":
    main()
