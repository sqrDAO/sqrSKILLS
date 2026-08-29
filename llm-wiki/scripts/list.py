#!/usr/bin/env python3
"""List all wiki pages with metadata.

Usage:
    python3 list.py [--tag TAG] [--sort title|updated]

Output:
    JSON array of pages, one per file in pages/.
    [{"file": "pages/foo.md", "title": "Foo", "tags": ["a", "b"],
      "sources": 0, "last_updated": "YYYY-MM-DD"}]
"""
import argparse
import json
import os
import re
import sys


def get_wiki_dir() -> str:
    return os.environ.get("WIKI_DIR", os.path.join(os.getcwd(), "wiki"))


def extract_frontmatter(content: str) -> dict:
    """Extract the YAML frontmatter block as a flat dict of raw string values."""
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return {}
    fields = {}
    for line in fm_match.group(1).splitlines():
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            fields[kv.group(1).strip()] = kv.group(2).strip()
    return fields


def parse_tags(raw: str) -> list[str]:
    """Parse a `tags:` value like `[a, b]` or `a, b` into a list."""
    if not raw:
        return []
    raw = raw.strip().strip("[]")
    return [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]


def extract_title(content: str, fm: dict, filename: str) -> str:
    """Title from frontmatter, else first H1, else humanized filename."""
    if fm.get("title"):
        return fm["title"].strip().strip("\"'")
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    return os.path.splitext(filename)[0].replace("-", " ").title()


def main():
    parser = argparse.ArgumentParser(description="List all wiki pages with metadata")
    parser.add_argument("--tag", help="Only list pages carrying this tag")
    parser.add_argument(
        "--sort",
        choices=["title", "updated"],
        default="title",
        help="Sort order (default: title)",
    )
    args = parser.parse_args()

    wiki_dir = get_wiki_dir()
    pages_dir = os.path.join(wiki_dir, "pages")

    if not os.path.isdir(pages_dir):
        print(json.dumps([]))
        return

    pages = []
    for fname in os.listdir(pages_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(pages_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"Warning: could not read {fname}: {e}", file=sys.stderr)
            continue

        fm = extract_frontmatter(content)
        tags = parse_tags(fm.get("tags", ""))
        if args.tag and args.tag not in tags:
            continue

        try:
            sources = int(fm.get("sources", "0"))
        except ValueError:
            sources = 0

        pages.append({
            "file": os.path.join("pages", fname),
            "title": extract_title(content, fm, fname),
            "tags": tags,
            "sources": sources,
            "last_updated": fm.get("last-updated", "").strip().strip("\"'"),
        })

    # Sort by filename first so the requested order below, which is stable, breaks
    # its own ties by filename. Without this, pages sharing a title or a
    # last-updated date come back in os.listdir order -- filesystem hash order,
    # which differs between machines holding the same wiki.
    pages.sort(key=lambda p: p["file"])
    if args.sort == "updated":
        pages.sort(key=lambda p: p["last_updated"], reverse=True)
    else:
        pages.sort(key=lambda p: p["title"].lower())

    print(json.dumps(pages, indent=2))


if __name__ == "__main__":
    main()
