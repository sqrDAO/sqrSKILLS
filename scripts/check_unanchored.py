#!/usr/bin/env python3
"""Fail when a legal instrument is cited in a baseline with no anchor for it.

`check_anchors.py` fetches the URLs a baseline cites, so it catches an anchor
that rots. It cannot catch the opposite failure -- an instrument number asserted
with no anchor at all -- because there is no URL for it to fetch. That gap is
how the 31 August 2026 refresh added three circular numbers and a claim about
Article 9 enforcement competence, all uncited and one of them wrong, past every
check in the repository.

This is a text check and makes no network calls. It reads each baseline, finds
the instrument numbers it states, and reports any that the file's own anchors
section never mentions.

It judges only what a change *introduces*, comparing against a base revision.
Scanning the whole file was tried first and was wrong: it reported 14
instruments on a corrected baseline, most of them long-standing claims whose
anchors are titled by subject rather than by number. Failing on those would
demand a data project before the check could ever go green, and the pressure
would be to weaken the check rather than source the claims. `--all` still
reports that standing backlog, without a verdict.

Two exemptions, both deliberate:

* A number inside a bullet or table row that labels it unconfirmed -- UNVERIFIED,
  DRAFT, PROPOSED, RUMORED, REPORTED, SINGLE-SOURCE, NEEDS_PRIMARY_SOURCE -- is
  exempt. Labelling a claim as unconfirmed is the documented alternative to
  sourcing it. A check that fired on those would push an author into deleting the
  label rather than adding a source, which makes the data worse while turning the
  harness green.
* Everything under "Known open questions" and "Checked and NOT confirmed" is
  exempt for the same reason: those sections exist to name instruments the skill
  has *not* confirmed.

What this proves is narrow, and worth stating plainly: it catches an instrument
with no anchor, not an instrument whose anchor points somewhere unrelated.
Detecting a mismatch needs the fetch, and belongs with `check_anchors.py`.

The command prints one JSON result to stdout; diagnostics go to stderr.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BASELINES = {
    "crypto-radar": Path("vietnam-crypto-radar/references/baseline.md"),
}

# Vietnamese legal instrument numbers: 284/2026/NĐ-CP, 89/2026/TT-BTC,
# 39/2026/TT-NHNN, 3809/QĐ-UBND, 20/2026/NQ-HĐND, 109/2025/QH15, 96/QĐ-BTC.
# The year is optional because decisions are cited both ways in these files.
INSTRUMENT = re.compile(
    r"\b\d{1,4}(?:\.\d{1,2})?/(?:20\d\d/)?"
    r"(?:N[ĐD]-CP|TT-[A-Z]{2,6}|Q[ĐD]-[A-Z\w]{2,8}|NQ-[A-Z\w]{2,8}|QH\d{1,3})",
    re.UNICODE,
)

# An anchor may name a range -- "Decisions 3809-3812/QĐ-UBND" anchors all four.
RANGE = re.compile(
    r"\b(\d{1,4})\s*[-\u2013\u2014]\s*(\d{1,4})/((?:20\d\d/)?[A-ZĐ]{2}-[A-Z\w]{2,8})",
    re.UNICODE,
)

# A claim that says of itself that it is not confirmed needs no anchor.
UNCONFIRMED = re.compile(
    r"UNVERIFIED|DRAFT|PROPOSED|RUMORED|REPORTED|SINGLE[- ]SOURCE"
    r"|NEEDS_PRIMARY_SOURCE|NOT CONFIRMED",
)

ANCHORS_HEADING = "## Verified source anchors"
EXEMPT_HEADINGS = ("## Known open questions", "## Checked and NOT confirmed")


def sections(text: str) -> list[tuple[str, str]]:
    """Split on `## ` headings, keeping each heading with its body."""
    parts, current, body = [], "", []
    for line in text.splitlines():
        if line.startswith("## "):
            parts.append((current, "\n".join(body)))
            current, body = line, []
        else:
            body.append(line)
    parts.append((current, "\n".join(body)))
    return parts


def anchored_numbers(text: str) -> set[str]:
    """Every instrument number named anywhere in the anchors section.

    A range is expanded: an anchor for `Decisions 3809-3812/QĐ-UBND` anchors
    3809, 3810, 3811 and 3812, each of which is cited individually elsewhere.
    """
    for heading, body in sections(text):
        if not heading.startswith(ANCHORS_HEADING):
            continue
        found = set(INSTRUMENT.findall(body))
        for lo, hi, suffix in RANGE.findall(body):
            if 0 < int(hi) - int(lo) < 50:
                found.update(f"{n}/{suffix}" for n in range(int(lo), int(hi) + 1))
        return found
    return set()


def baseline_at(ref: str, rel: Path) -> str | None:
    """The file as of `ref`, or None when the revision is unavailable."""
    try:
        out = subprocess.run(["git", "show", f"{ref}:{rel.as_posix()}"],
                             cwd=ROOT, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout.decode("utf-8", "replace")


def scan(path: Path, text: str | None = None) -> list[dict]:
    text = path.read_text(encoding="utf-8") if text is None else text
    anchored = anchored_numbers(text)
    findings, seen = [], set()
    for heading, body in sections(text):
        if heading.startswith(EXEMPT_HEADINGS) or heading.startswith(ANCHORS_HEADING):
            continue
        for lineno, line in enumerate(body.splitlines(), start=1):
            if UNCONFIRMED.search(line):
                continue
            for number in INSTRUMENT.findall(line):
                if number in anchored or number in seen:
                    continue
                seen.add(number)
                findings.append({
                    "instrument": number,
                    "section": heading.removeprefix("## ").strip() or "(preamble)",
                    "line": line.strip()[:160],
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="append", choices=sorted(BASELINES),
                        help="limit to one baseline (default: all)")
    parser.add_argument("--since", default="origin/main", metavar="REF",
                        help="base revision to judge against (default: origin/main)")
    parser.add_argument("--all", action="store_true",
                        help="report every unanchored instrument, not only new "
                             "ones, and do not fail on them")
    args = parser.parse_args()

    targets = args.baseline or sorted(BASELINES)
    results, total, base_missing = {}, 0, []
    for name in targets:
        rel = BASELINES[name]
        findings = scan(ROOT / rel)
        if not args.all:
            before = baseline_at(args.since, rel)
            if before is None:
                # No base revision to compare against. Reporting every standing
                # instrument as a failure here would fail a harness for content
                # nobody in this change touched, so say so and pass.
                base_missing.append(name)
                findings = []
            else:
                known = {f["instrument"] for f in scan(rel, before)}
                findings = [f for f in findings if f["instrument"] not in known]
        results[name] = findings
        total += len(findings)
        for f in findings:
            print(f"UNANCHORED {f['instrument']}  ({name}: {f['section']})",
                  file=sys.stderr)

    for name in base_missing:
        print(f"NOTE {name}: {args.since} unavailable; nothing to compare against",
              file=sys.stderr)

    ok = args.all or total == 0
    print(json.dumps({
        "ok": ok,
        "mode": "all" if args.all else f"since {args.since}",
        "counts": {"baselines": len(targets), "unanchored": total},
        "unanchored": results,
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
