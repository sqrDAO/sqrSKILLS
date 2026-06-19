#!/usr/bin/env python3
"""Filter the bundled Web3 opportunities roster by type, stage, dilution, chain, region.

Usage:
    python3 query_opportunities.py [--type T...] [--stage S...] [--dilution D]
                                   [--chain C...] [--region R...] [--status ST]
                                   [--sea] [--search TEXT] [--all]

Filtering semantics:
    - AND across facets (an entry must pass every supplied facet).
    - OR within a facet (entry matches if its values intersect the requested set).
    - List facets accept repeated flags AND/OR comma-separated values, e.g.
      `--type grant --type hackathon` is equivalent to `--type grant,hackathon`.
    - --dilution is exact-match: `non-dilutive` does NOT auto-include `mixed`.
    - --sea restricts to curated SEA/Vietnam-relevant entries (sea_relevant == true).
    - No filters (or --all) returns the entire roster.

Output:
    JSON to stdout: {query, count, data_as_of, time_sensitive_fields, results[]}
    Diagnostics and errors to stderr; JSON error object also to stdout; exit 1 on error.
"""
import argparse
import json
import os
import sys


def load_data(data_path: str) -> dict:
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def split_values(raw_values: list[str] | None) -> list[str]:
    """Flatten repeated flags and comma-separated values into a lowercased list."""
    if not raw_values:
        return []
    out: list[str] = []
    for chunk in raw_values:
        for part in chunk.split(","):
            part = part.strip().lower()
            if part:
                out.append(part)
    return out


def validate(values: list[str], facet: str, valid: list[str]) -> None:
    """Exit 1 if any value is not in the enum for this facet."""
    for v in values:
        if v not in valid:
            msg = f"invalid --{facet} value '{v}'; valid: {','.join(valid)}"
            print(f"[web3-opportunities] {msg}", file=sys.stderr)
            print(json.dumps({"error": msg, "valid_values": valid}))
            sys.exit(1)


def intersects(entry_values: list[str], requested: list[str]) -> bool:
    """OR within a facet: True if any requested value is present in the entry."""
    if not requested:
        return True
    entry_set = {str(x).lower() for x in entry_values}
    return any(r in entry_set for r in requested)


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter Web3 builder opportunities")
    parser.add_argument("--type", action="append", help="accelerator, incubator, grant, hackathon, bounty, retroactive_funding, fellowship, education")
    parser.add_argument("--stage", action="append", help="idea, pre-seed, mvp, growth")
    parser.add_argument("--dilution", action="append", help="dilutive, non-dilutive, mixed (exact match)")
    parser.add_argument("--chain", action="append", help="ethereum, l2, solana, polkadot, cosmos, near, sui, multi-chain")
    parser.add_argument("--region", action="append", help="global, us, europe, india, sea, latam, africa, remote")
    parser.add_argument("--status", action="append", help="open, closed, rolling, cohort-based, unknown (time-sensitive)")
    parser.add_argument("--sea", action="store_true", help="restrict to SEA/Vietnam-relevant entries")
    parser.add_argument("--search", help="case-insensitive substring over name, id, notes")
    parser.add_argument("--all", action="store_true", help="return the full roster (default when no filters given)")
    args = parser.parse_args()

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "web3_opportunities.json")
    try:
        data = load_data(data_path)
    except OSError as e:
        print(f"[web3-opportunities] could not load data: {e}", file=sys.stderr)
        print(json.dumps({"error": f"Could not load opportunity data: {e}"}))
        sys.exit(1)

    enums = data.get("enums", {})
    meta = data.get("_meta", {})
    opportunities = data.get("opportunities", [])

    f_type = split_values(args.type)
    f_stage = split_values(args.stage)
    f_dilution = split_values(args.dilution)
    f_chain = split_values(args.chain)
    f_region = split_values(args.region)
    f_status = split_values(args.status)
    search = (args.search or "").strip().lower()

    validate(f_type, "type", enums.get("type", []))
    validate(f_stage, "stage", enums.get("stage", []))
    validate(f_dilution, "dilution", enums.get("dilution", []))
    validate(f_chain, "chain", enums.get("chain", []))
    validate(f_region, "region", enums.get("region", []))
    validate(f_status, "status", enums.get("status", []))

    results = []
    for o in opportunities:
        if f_type and o.get("type", "").lower() not in f_type:
            continue
        if not intersects(o.get("stage", []), f_stage):
            continue
        if f_dilution and o.get("dilution", "").lower() not in f_dilution:
            continue
        if not intersects(o.get("chains", []), f_chain):
            continue
        if not intersects(o.get("regions", []), f_region):
            continue
        if f_status and o.get("status", "").lower() not in f_status:
            continue
        if args.sea and not o.get("sea_relevant", False):
            continue
        if search:
            haystack = " ".join([
                str(o.get("name", "")),
                str(o.get("id", "")),
                str(o.get("notes", "")),
            ]).lower()
            if search not in haystack:
                continue
        results.append(o)

    output = {
        "query": {
            "type": f_type or None,
            "stage": f_stage or None,
            "dilution": f_dilution or None,
            "chain": f_chain or None,
            "region": f_region or None,
            "status": f_status or None,
            "sea": args.sea,
            "search": args.search or None,
        },
        "count": len(results),
        "data_as_of": meta.get("last_updated"),
        "time_sensitive_fields": meta.get("time_sensitive_fields", []),
        "results": results,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
