#!/usr/bin/env python3
"""
List Telegram chats (groups and private) that have interacted with this twin.

Primary source: OpenClaw's local sessions.json (authoritative for all chats
the twin has handled directly). Falls back to the YouAI backend API for any
chats tracked there.

Usage:
    python3 list_chats.py

Output:
    JSON object with "groups" (chat_id < 0) and "private_chats" (chat_id > 0):
    {"groups": [{"chat_id": -1001234567890, "type": "group"}], "private_chats": [...]}
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


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

    seen: set[int] = set()
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


def list_chats() -> dict:
    result = _chats_from_openclaw_sessions()
    if result["groups"] or result["private_chats"]:
        return result
    return _chats_from_backend()


if __name__ == "__main__":
    print(json.dumps(list_chats(), indent=2))
