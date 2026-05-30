#!/usr/bin/env python3
"""
List Telegram chats (groups and private) that have interacted with this agent.

Sources (in priority order):
  1. Nanobot sessions: ~/.nanobot/workspace/sessions/telegram_*.jsonl
  2. OpenClaw sessions.json
  3. YouAI backend API

Usage:
    python3 list_chats.py [--no-names]

Output:
    JSON object with "groups" (chat_id < 0) and "private_chats" (chat_id > 0):
    {"groups": [{"chat_id": -100123, "name": "My Group", "type": "supergroup"}],
     "private_chats": [...]}
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


def _chats_from_nanobot_sessions() -> dict:
    """Read chat IDs from nanobot session files (telegram_<chat_id>.jsonl)."""
    sessions_dir = os.environ.get("NANOBOT_SESSIONS_DIR") or os.path.join(
        os.environ.get("NANOBOT_WORKSPACE", os.path.expanduser("~/.nanobot/workspace")),
        "sessions",
    )
    if not os.path.isdir(sessions_dir):
        return {"groups": [], "private_chats": []}

    seen: set = set()
    groups = []
    private_chats = []

    try:
        entries = os.listdir(sessions_dir)
    except Exception as e:
        print(f"Warning: could not list nanobot sessions: {e}", file=sys.stderr)
        return {"groups": [], "private_chats": []}

    for filename in entries:
        if not (filename.startswith("telegram_") and filename.endswith(".jsonl")):
            continue
        stem = filename[len("telegram_"):-len(".jsonl")]
        try:
            chat_id = int(stem)
        except ValueError:
            continue
        if chat_id in seen:
            continue
        seen.add(chat_id)

        last_updated = None
        try:
            with open(os.path.join(sessions_dir, filename)) as f:
                first_line = f.readline()
            if first_line:
                meta = json.loads(first_line)
                last_updated = meta.get("last_updated") or meta.get("timestamp")
        except Exception:
            pass

        entry: dict = {"chat_id": chat_id}
        if last_updated is not None:
            entry["last_updated"] = last_updated

        if chat_id < 0:
            groups.append(entry)
        else:
            private_chats.append(entry)

    return {"groups": groups, "private_chats": private_chats}


def _chats_from_openclaw_sessions() -> dict:
    """Read chat IDs from OpenClaw's local sessions.json."""
    sessions_path = os.path.join(
        os.environ.get("OPENCLAW_STATE_DIR", "/twin-data/state"),
        "agents", "main", "sessions", "sessions.json",
    )
    if not os.path.exists(sessions_path):
        return {"groups": [], "private_chats": []}

    try:
        with open(sessions_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Warning: could not read sessions.json: {e}", file=sys.stderr)
        return {"groups": [], "private_chats": []}

    seen: set = set()
    groups = []
    private_chats = []

    for session in data.values():
        to = session.get("lastTo") or session.get("deliveryContext", {}).get("to", "")
        if not isinstance(to, str) or not to.startswith("telegram:"):
            continue
        try:
            chat_id = int(to.split(":")[1])
        except (ValueError, IndexError):
            continue
        if chat_id in seen:
            continue
        seen.add(chat_id)
        entry = {"chat_id": chat_id, "type": session.get("chatType", "unknown")}
        if chat_id < 0:
            groups.append(entry)
        else:
            private_chats.append(entry)

    return {"groups": groups, "private_chats": private_chats}


def _chats_from_backend() -> dict:
    """Fallback: query the YouAI backend API."""
    api_url = os.environ.get("YOUAI_API_URL", "").rstrip("/")
    twin_id = os.environ.get("YOUAI_TWIN_ID", "").strip()
    if not api_url or not twin_id:
        return {"groups": [], "private_chats": []}

    url = f"{api_url}/api/twins/{urllib.parse.quote(twin_id)}/telegram/chats"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {twin_id}"}, method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Warning: could not reach backend: {e}", file=sys.stderr)
        return {"groups": [], "private_chats": []}

    chats = data.get("chats", [])
    groups = [c for c in chats if c.get("chat_id", 0) < 0]
    private_chats = [c for c in chats if c.get("chat_id", 0) > 0]
    return {"groups": groups, "private_chats": private_chats}


def _merge(a: dict, b: dict) -> dict:
    """Merge two {groups, private_chats} dicts, deduplicating by chat_id (a takes priority)."""
    seen: set = set()
    groups = []
    private_chats = []
    for entry in a["groups"] + b["groups"]:
        if entry["chat_id"] not in seen:
            seen.add(entry["chat_id"])
            groups.append(entry)
    for entry in a["private_chats"] + b["private_chats"]:
        if entry["chat_id"] not in seen:
            seen.add(entry["chat_id"])
            private_chats.append(entry)
    return {"groups": groups, "private_chats": private_chats}


def _resolve_names(chats: list) -> list:
    """Enrich each chat entry with its name from the Telegram Bot API (getChat)."""
    bot_token = _telegram_bot_token()
    if not bot_token:
        return chats

    enriched = []
    for c in chats:
        chat_id = c["chat_id"]
        try:
            url = (
                f"https://api.telegram.org/bot{bot_token}/getChat"
                f"?chat_id={urllib.parse.quote(str(chat_id))}"
            )
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
            if data.get("ok"):
                result = data["result"]
                first = result.get("first_name", "")
                last = result.get("last_name", "")
                full_name = (first + (" " + last if last else "")).strip()
                name = result.get("title") or full_name or result.get("username")
                chat_type = result.get("type", c.get("type", "unknown"))
                enriched.append({**c, "name": name, "type": chat_type})
            else:
                enriched.append({**c, "name": None})
        except Exception as e:
            print(f"Warning: could not resolve name for chat {chat_id}: {e}", file=sys.stderr)
            enriched.append({**c, "name": None})

    return enriched


def list_chats(resolve_names: bool = True) -> dict:
    nanobot = _chats_from_nanobot_sessions()
    openclaw = _chats_from_openclaw_sessions()
    result = _merge(nanobot, openclaw)
    if not (result["groups"] or result["private_chats"]):
        result = _chats_from_backend()
    if resolve_names:
        return {
            "groups": _resolve_names(result["groups"]),
            "private_chats": _resolve_names(result["private_chats"]),
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-names", action="store_true", help="Skip name resolution via Telegram API")
    args = parser.parse_args()
    print(json.dumps(list_chats(resolve_names=not args.no_names), indent=2))
