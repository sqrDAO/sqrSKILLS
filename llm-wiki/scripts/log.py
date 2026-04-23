#!/usr/bin/env python3
"""Append a structured entry to wiki/log.md.

Usage:
    python3 log.py <ingest|query|lint> "<title>" ["<notes>"]

Output:
    JSON: {"status": "ok", "entry": "## [YYYY-MM-DD] ingest | Title"}
"""
import argparse
import json
import os
import sys
from datetime import date


VALID_OPERATIONS = {"ingest", "query", "lint"}


def get_wiki_dir() -> str:
    return os.environ.get("WIKI_DIR", os.path.join(os.getcwd(), "wiki"))


def main():
    parser = argparse.ArgumentParser(description="Append a log entry to wiki/log.md")
    parser.add_argument("operation", choices=sorted(VALID_OPERATIONS), help="Operation type")
    parser.add_argument("title", help="Short title for the log entry")
    parser.add_argument("notes", nargs="?", default="", help="Optional notes or summary")
    args = parser.parse_args()

    wiki_dir = get_wiki_dir()
    log_path = os.path.join(wiki_dir, "log.md")

    today = date.today().isoformat()
    header = f"## [{today}] {args.operation} | {args.title}"
    body = args.notes.strip() if args.notes else ""
    entry = f"{header}\n{body}\n\n" if body else f"{header}\n\n"

    # Create wiki/ and log.md if they don't exist
    os.makedirs(wiki_dir, exist_ok=True)
    if not os.path.isfile(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("# Wiki Log\n\nChronological record of ingests, queries, and maintenance.\n\n")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)

    print(json.dumps({"status": "ok", "entry": header}))


if __name__ == "__main__":
    main()
