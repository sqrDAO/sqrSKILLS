#!/usr/bin/env python3
"""Hold an automated refresh to what it actually verified.

`last_verified` is a freshness claim. A refresh that bumps it on every entry
while re-checking a handful turns the field into noise -- and worse, into a
false assurance, since a reader treats a recent date as evidence someone looked.
The 2026-08-17 refresh dated 41 entries as verified that day; three of them
pointed at domains that no longer had DNS records.

The refresh agent therefore attests, in REFRESH_VERIFIED.json, which entry ids
it actually re-checked against a live source:

    {"web3_opportunities": ["alliance-dao", "yzi-labs"]}

This command compares the working tree against the pre-refresh state and:

  - keeps a raised date where the entry's content also changed (self-evident),
  - keeps a raised date where the id is attested,
  - reverts a raised date that is neither, since nothing supports it,
  - always keeps a LOWERED date, which needs no support at all.

Direction matters, and only one direction is an abuse. Raising `last_verified`
asserts a fresh check; lowering it withdraws one. A correction pass that finds a
date was never earned lowers it deliberately, so treating that like an unearned
bump would revert the correction and restore the false date -- which is what this
script exists to prevent. Dates that are not plain ISO `YYYY-MM-DD` cannot be
ordered, so they are treated as raised and must earn their keep.

Reverting rather than merely reporting is deliberate: an unattended job that
only warns produces warnings nobody reads, and the wrong date has already
shipped by then. Missing or unparseable attestation is treated as attesting
nothing, so the conservative outcome is the default.

The command prints one JSON result to stdout. Human-readable diagnostics are
written to stderr so CI and other agents can consume the result reliably.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DATE_FIELD = "last_verified"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_by_id(data: dict, list_key: str) -> dict[str, dict]:
    return {
        entry["id"]: entry
        for entry in data.get(list_key, [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }


def content_without_date(entry: dict) -> dict:
    return {key: value for key, value in entry.items() if key != DATE_FIELD}


def is_lowered(previous: object, current: object) -> bool:
    """True when the date moved backwards, which claims less and needs no support.

    Only comparable ISO dates can be ordered. Anything else -- a missing field, a
    free-text date, a format change -- is not treated as lowered, so it falls
    through to the rules that require support.
    """
    if not (isinstance(previous, str) and isinstance(current, str)):
        return False
    if not (ISO_DATE.match(previous) and ISO_DATE.match(current)):
        return False
    return current < previous


def audit(before: dict, after: dict, attested: set[str], list_key: str) -> dict:
    old = index_by_id(before, list_key)
    new = index_by_id(after, list_key)

    changed: list[str] = []
    attested_only: list[str] = []
    lowered: list[dict[str, str]] = []
    unsupported: list[dict[str, str]] = []

    for entry_id, entry in new.items():
        previous = old.get(entry_id)
        if previous is None:
            changed.append(entry_id)  # a new entry is verified by construction
            continue
        if entry.get(DATE_FIELD) == previous.get(DATE_FIELD):
            continue
        if is_lowered(previous.get(DATE_FIELD), entry.get(DATE_FIELD)):
            # Withdrawing a freshness claim needs no evidence. Reverting this
            # would restore a date the refresh never earned.
            lowered.append(
                {
                    "id": entry_id,
                    "from": str(previous.get(DATE_FIELD)),
                    "to": str(entry.get(DATE_FIELD)),
                }
            )
            continue
        if content_without_date(entry) != content_without_date(previous):
            changed.append(entry_id)
        elif entry_id in attested:
            attested_only.append(entry_id)
        else:
            unsupported.append(
                {
                    "id": entry_id,
                    "from": str(previous.get(DATE_FIELD)),
                    "to": str(entry.get(DATE_FIELD)),
                }
            )
    return {
        "changed": changed,
        "attested_only": attested_only,
        "lowered": lowered,
        "unsupported": unsupported,
    }


def revert(path: Path, before: dict, unsupported: list[dict[str, str]], list_key: str) -> None:
    """Restore prior dates via string surgery so the file's formatting survives."""
    if not unsupported:
        return
    text = path.read_text(encoding="utf-8")
    old = index_by_id(before, list_key)
    for item in unsupported:
        anchor = f'"id": "{item["id"]}"'
        start = text.index(anchor)
        needle = f'"{DATE_FIELD}": "{item["to"]}"'
        at = text.index(needle, start)
        restored = f'"{DATE_FIELD}": "{old[item["id"]][DATE_FIELD]}"'
        text = text[:at] + restored + text[at + len(needle) :]
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit refresh verification claims")
    parser.add_argument("--before", required=True, type=Path, help="pre-refresh JSON")
    parser.add_argument("--after", required=True, type=Path, help="post-refresh JSON (edited in place)")
    parser.add_argument("--attested", type=Path, help="REFRESH_VERIFIED.json written by the agent")
    parser.add_argument("--list-key", default="opportunities", help="key holding the entry list")
    parser.add_argument(
        "--attest-key", default="web3_opportunities", help="key in the attestation file"
    )
    parser.add_argument(
        "--report-only", action="store_true", help="report without reverting unsupported dates"
    )
    args = parser.parse_args()

    attested: set[str] = set()
    if args.attested and args.attested.is_file():
        try:
            claimed = load(args.attested).get(args.attest_key, [])
            attested = {i for i in claimed if isinstance(i, str)}
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            print(f"attestation unreadable, treating as empty: {exc}", file=sys.stderr)

    before = load(args.before)
    after = load(args.after)
    result = audit(before, after, attested, args.list_key)

    for item in result["lowered"]:
        print(
            f"LOWERED {item['id']}: {DATE_FIELD} {item['from']} -> {item['to']} "
            "kept as-is; withdrawing a freshness claim needs no support",
            file=sys.stderr,
        )

    for item in result["unsupported"]:
        print(
            f"UNSUPPORTED {item['id']}: {DATE_FIELD} {item['from']} -> {item['to']} "
            "with no content change and no attestation",
            file=sys.stderr,
        )

    reverted = False
    if result["unsupported"] and not args.report_only:
        revert(args.after, before, result["unsupported"], args.list_key)
        reverted = True

    print(
        json.dumps(
            {
                "ok": True,
                "counts": {
                    "changed": len(result["changed"]),
                    "attested_only": len(result["attested_only"]),
                    "lowered": len(result["lowered"]),
                    "unsupported": len(result["unsupported"]),
                },
                "reverted": reverted,
                "lowered": result["lowered"],
                "unsupported": result["unsupported"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
