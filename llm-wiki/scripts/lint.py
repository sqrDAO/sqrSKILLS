#!/usr/bin/env python3
"""Health-check the wiki for structural issues.

Detects:
  - orphan: page in pages/ with no inbound links from other pages or index.md
  - missing: page listed in index.md but the file doesn't exist
  - unlisted: page file exists in pages/ but not referenced in index.md

Usage:
    python3 lint.py

Output:
    JSON array of issues.
    [{"type": "orphan"|"missing"|"unlisted", "file": "pages/foo.md", "detail": "..."}]
"""
import json
import os
import re
import sys


def get_wiki_dir() -> str:
    return os.environ.get("WIKI_DIR", os.path.join(os.getcwd(), "wiki"))


def find_all_page_files(pages_dir: str) -> set[str]:
    """Return set of page filenames (relative to pages_dir)."""
    if not os.path.isdir(pages_dir):
        return set()
    return {f for f in os.listdir(pages_dir) if f.endswith(".md")}


def find_links_in_content(content: str) -> set[str]:
    """Extract linked filenames from markdown content.
    Matches: [text](filename.md), [[filename]], [[filename|alias]]
    """
    links = set()
    # Standard markdown links to .md files
    for m in re.finditer(r"\[.*?\]\(([^)]+\.md)\)", content):
        target = os.path.basename(m.group(1))
        links.add(target)
    # Wiki-style [[links]]
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content):
        slug = m.group(1).strip()
        if not slug.endswith(".md"):
            slug += ".md"
        links.add(os.path.basename(slug))
    return links


def read_all_content(wiki_dir: str, pages_dir: str, page_files: set[str]) -> dict[str, str]:
    """Read all page files and index.md. Returns filename → content map."""
    contents = {}
    for fname in page_files:
        fpath = os.path.join(pages_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                contents[fname] = f.read()
        except OSError as e:
            print(f"Warning: could not read {fname}: {e}", file=sys.stderr)
    index_path = os.path.join(wiki_dir, "index.md")
    if os.path.isfile(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                contents["index.md"] = f.read()
        except OSError:
            pass
    return contents


def find_referenced_in_index(index_content: str) -> set[str]:
    """Extract filenames referenced in index.md."""
    return find_links_in_content(index_content)


def main():
    wiki_dir = get_wiki_dir()
    pages_dir = os.path.join(wiki_dir, "pages")

    page_files = find_all_page_files(pages_dir)
    if not page_files:
        print(json.dumps([]))
        return

    all_content = read_all_content(wiki_dir, pages_dir, page_files)
    index_content = all_content.get("index.md", "")

    # Build inbound link map: filename → set of files that link to it
    inbound: dict[str, set[str]] = {f: set() for f in page_files}
    for source_name, content in all_content.items():
        links = find_links_in_content(content)
        for target in links:
            if target in inbound:
                inbound[target].add(source_name)

    referenced_in_index = find_referenced_in_index(index_content)

    issues = []

    for fname in sorted(page_files):
        rel = os.path.join("pages", fname)
        # Orphan: no inbound links from any file (including index)
        if not inbound[fname] and fname not in referenced_in_index:
            issues.append({
                "type": "orphan",
                "file": rel,
                "detail": "No inbound links from other pages or index.md",
            })
        # Unlisted: file exists but not in index.md
        if index_content and fname not in referenced_in_index:
            # Only report as unlisted if not already reported as orphan
            if inbound[fname]:
                issues.append({
                    "type": "unlisted",
                    "file": rel,
                    "detail": "File exists but is not listed in index.md",
                })

    # Missing: linked from index.md but file doesn't exist
    for fname in sorted(referenced_in_index):
        if fname not in page_files:
            issues.append({
                "type": "missing",
                "file": os.path.join("pages", fname),
                "detail": "Listed in index.md but file does not exist",
            })

    print(json.dumps(issues, indent=2))


if __name__ == "__main__":
    main()
