#!/usr/bin/env python3
"""Search wiki pages by keyword relevance.

Usage:
    python3 search.py "<query>" [--top N]

Output:
    JSON array of matching pages, sorted by score descending.
    [{"file": "pages/foo.md", "title": "Foo", "score": 7, "excerpt": "..."}]
"""
import argparse
import json
import os
import re
import sys


def get_wiki_dir() -> str:
    wiki_dir = os.environ.get("WIKI_DIR", os.path.join(os.getcwd(), "wiki"))
    return wiki_dir


def extract_title(content: str, filename: str) -> str:
    """Extract title from YAML frontmatter or first H1 heading."""
    fm_match = re.search(r"^---\s*\ntitle:\s*(.+?)\s*\n", content, re.MULTILINE)
    if fm_match:
        return fm_match.group(1).strip().strip('"\'')
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    return os.path.splitext(filename)[0].replace("-", " ").title()


def score_page(content: str, title: str, terms: list[str]) -> tuple[int, str]:
    """Score a page for relevance. Returns (score, excerpt)."""
    score = 0
    excerpt_line = ""
    lines = content.splitlines()

    title_lower = title.lower()
    content_lower = content.lower()

    for term in terms:
        term_lower = term.lower()
        # Title match: 3 points each
        if term_lower in title_lower:
            score += 3
        # Heading match: 2 points each occurrence
        for line in lines:
            if line.startswith("#") and term_lower in line.lower():
                score += 2
                if not excerpt_line:
                    excerpt_line = line.lstrip("#").strip()

    # Body match: 1 point per term found anywhere
    for term in terms:
        if term.lower() in content_lower:
            score += 1
            if not excerpt_line:
                # Find first matching line for excerpt
                for line in lines:
                    if term.lower() in line.lower() and not line.startswith("#") and not line.startswith("---"):
                        excerpt_line = line.strip()[:120]
                        break

    return score, excerpt_line


def main():
    parser = argparse.ArgumentParser(description="Search wiki pages by keyword relevance")
    parser.add_argument("query", help="Search query (space-separated terms)")
    parser.add_argument("--top", type=int, default=10, help="Number of results to return (default: 10)")
    args = parser.parse_args()

    wiki_dir = get_wiki_dir()
    pages_dir = os.path.join(wiki_dir, "pages")

    if not os.path.isdir(pages_dir):
        print(json.dumps([]))
        return

    terms = args.query.split()
    if not terms:
        print(json.dumps([]))
        return

    results = []
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

        title = extract_title(content, fname)
        score, excerpt = score_page(content, title, terms)
        if score > 0:
            results.append({
                "file": os.path.join("pages", fname),
                "title": title,
                "score": score,
                "excerpt": excerpt,
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    print(json.dumps(results[: args.top], indent=2))


if __name__ == "__main__":
    main()
