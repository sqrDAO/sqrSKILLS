#!/usr/bin/env python3
"""
List Telegram group chats this twin is known to be a member of.

Queries the YouAI backend using twin-token auth to retrieve chats derived
from Redis session history, filtered to groups only (chat_id < 0).

Usage:
    python list_groups.py

Output:
    JSON array on stdout, e.g.:
    [{"chat_id": -1001234567890, "name": "Team Chat", "type": "supergroup"}]

    Returns [] if no groups are known or the backend is unreachable.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def list_groups() -> list:
    api_url = os.environ.get("YOUAI_API_URL", "").rstrip("/")
    twin_id = os.environ.get("YOUAI_TWIN_ID", "").strip()

    if not api_url or not twin_id:
        print(
            "Warning: YOUAI_API_URL or YOUAI_TWIN_ID not set; cannot fetch group list",
            file=sys.stderr,
        )
        return []

    url = f"{api_url}/api/twins/{urllib.parse.quote(twin_id)}/telegram/chats?resolve_names=true"
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
    # Filter to group chats only (negative chat_id)
    groups = [c for c in chats if c.get("chat_id", 0) < 0]
    return groups


def main():
    groups = list_groups()
    print(json.dumps(groups, ensure_ascii=False))


if __name__ == "__main__":
    main()
