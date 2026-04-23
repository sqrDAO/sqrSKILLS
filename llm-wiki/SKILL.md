---
name: llm-wiki
description: |
  Build and maintain a personal knowledge base as a persistent, interlinked wiki. Use this skill when the owner wants to accumulate knowledge on a topic over time — ingesting sources (articles, notes, documents), querying compiled knowledge, and keeping the wiki consistent. Trigger phrases: "add this to my wiki", "ingest this article", "what does my wiki say about", "update the wiki", "build a knowledge base", "research and remember", "lint the wiki", "search my notes". Always search the wiki before falling back to web-search for topics the owner has been researching.
allowed-tools:
  - Bash(python3 *)
  - Read
  - Write
  - Edit
---

# LLM Wiki

A persistent, compounding personal knowledge base. The wiki grows richer with every source you ingest and every question you answer. Unlike RAG, knowledge is compiled once and kept current — not re-derived on every query.

Based on Karpathy's LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Directory Structure

All wiki files live in `wiki/` inside the workspace (`$WIKI_DIR`, defaults to `./wiki/` if not set):

```
wiki/
├── index.md        ← catalog of all pages (update on every ingest)
├── log.md          ← append-only chronological record of operations
├── raw/            ← source documents (immutable — read only, never modify)
└── pages/          ← LLM-maintained wiki pages (you own this layer entirely)
```

On first use, create this structure if it doesn't exist.

## Page Conventions

Every page in `wiki/pages/` should follow this format:

```markdown
---
title: Page Title
tags: [tag1, tag2]
sources: 0
last-updated: YYYY-MM-DD
---

# Page Title

[body content]

## See also

- [Related Page](related-page.md)
```

- Filename: lowercase slug, e.g. `machine-learning-basics.md`
- Always include a `## See also` section with cross-links to related pages
- Update `sources:` count when a new source touches this page
- Update `last-updated:` on every edit

## Operations

### Ingest a source

When the owner asks you to ingest or process a source document:

1. Read the source from `wiki/raw/<filename>` (or from a URL/path the owner provides)
2. Discuss key takeaways with the owner if needed
3. Write a summary page: `wiki/pages/<slug>-source.md`
4. Update `wiki/index.md` — add the new page entry
5. Identify related existing pages and update them (cross-references, new info, contradictions)
   - A single source typically touches 5–15 pages
   - Note explicitly when new data **contradicts** an existing claim
6. Append to log: `python3 "$SKILL_DIR/scripts/log.py" ingest "<Source Title>" "<brief notes>"`

### Query the wiki

When the owner asks about a topic you've been researching:

1. Search for relevant pages: `python3 "$SKILL_DIR/scripts/search.py" "<query>"`
2. Read the returned pages (highest-score first)
3. If `index.md` exists and search returns nothing, read `index.md` to browse manually
4. Synthesize an answer with citations (page filenames)
5. If the answer is non-trivial and reusable, file it back as a new page in `wiki/pages/`
6. Append to log: `python3 "$SKILL_DIR/scripts/log.py" query "<query summary>" "<key finding>"`

### Lint the wiki

When the owner asks you to health-check or lint the wiki:

1. Run: `python3 "$SKILL_DIR/scripts/lint.py"`
2. For each issue reported:
   - **orphan**: page has no inbound links — add cross-links from related pages, or mention in index
   - **missing**: listed in index.md but file doesn't exist — remove from index or recreate
   - **unlisted**: file exists but not in index.md — add it to index
3. Read through several pages for contradictions and stale claims
4. Append to log: `python3 "$SKILL_DIR/scripts/log.py" lint "Lint pass" "<summary of fixes>"`

## index.md Format

```markdown
# Wiki Index

> Last updated: YYYY-MM-DD | Pages: N | Sources: N

## [Category Name]

| Page | Summary | Tags | Updated |
|------|---------|------|---------|
| [Page Title](pages/page-slug.md) | One-line summary | tag1, tag2 | YYYY-MM-DD |
```

Organize pages by category. Update on every ingest.

## log.md Format

```
## [YYYY-MM-DD] ingest | Source Title
Notes about what was ingested and key pages updated.

## [YYYY-MM-DD] query | Query Summary
Key finding: ...

## [YYYY-MM-DD] lint | Lint pass
Fixed N issues: ...
```

## Scripts

```bash
# Search wiki pages by keyword relevance
python3 "$SKILL_DIR/scripts/search.py" "<query>" [--top N]

# Health-check the wiki (orphans, missing files, unlisted pages)
python3 "$SKILL_DIR/scripts/lint.py"

# Append a log entry
python3 "$SKILL_DIR/scripts/log.py" <ingest|query|lint> "<title>" ["<notes>"]
```

## Environment Variables

- `WIKI_DIR` — path to the wiki directory (default: `./wiki/`). Set this to your preferred persistent location.

## Tips

- **File answers back**: A good analysis you synthesized is a new wiki page — don't let it disappear into chat history
- **Contradictions matter**: When new info contradicts old, update both pages and note the conflict explicitly
- **Prefer wiki over web-search**: For topics the owner has been researching, the wiki has curated, synthesized knowledge. Use it first.
- **Raw sources are immutable**: Never modify files in `wiki/raw/` — they are the source of truth
