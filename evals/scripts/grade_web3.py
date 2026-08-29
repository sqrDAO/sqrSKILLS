#!/usr/bin/env python3
"""Score a web3-opportunities run against the validation split.

Usage:
    python3 evals/scripts/grade_web3.py runs/<name>.jsonl [--verbose]

The run file is JSONL, one object per case. A tool call is recorded as the argv
the agent actually passed to the script -- not as a parsed facet set, so the
grader and the executor cannot disagree about what a flag meant:

    {"case_id": "w3o-03",
     "tool_calls": [{"argv": ["--dilution", "non-dilutive", "--chain", "solana"]}],
     "answer": "<the agent's final user-facing reply>"}

Each argv is normalised by running ``query_opportunities.py`` and reading the
``query`` block it echoes back, so the skill's own argument parsing -- comma
splitting, repeated flags, lowercasing -- is the authority. An argv the script
rejects normalises to ``None``: it counts as an invocation, but cannot satisfy a
constraint that names facets.

A case passes only when every required invocation is present AND every rubric
check passes. Two axes are reported separately because they call for different
edits: ``call_score`` (did the agent query the roster correctly) and
``answer_score`` (did the reply carry what the result made available).

``errored_calls`` is a warning, not a failure. Reaching for a facet value
outside the enum is recoverable, but it predicts answers that quietly drop the
constraint the user asked for.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rubric import (  # noqa: E402  (path set above)
    grade_checks, load_cases, load_runs, run_integrity_error, summarize,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "evals" / "web3-opportunities" / "cases.jsonl"
DEFAULT_QUERY = ROOT / "web3-opportunities" / "scripts" / "query_opportunities.py"

LIST_FACETS = ("type", "stage", "dilution", "chain", "region", "status")


class Normalizer:
    """argv -> the query block the skill's own script echoes for it."""

    def __init__(self, script: Path):
        self.script = script
        self.cache: dict[tuple[str, ...], dict | None] = {}

    def __call__(self, argv: list[str]) -> dict | None:
        key = tuple(argv)
        if key not in self.cache:
            proc = subprocess.run(
                [sys.executable, str(self.script), *argv],
                capture_output=True, text=True,
            )
            try:
                out = json.loads(proc.stdout)
            except json.JSONDecodeError:
                out = {"error": proc.stderr.strip() or "no JSON on stdout"}
            self.cache[key] = None if "error" in out else out.get("query")
        return self.cache[key]

    @staticmethod
    def is_usage(argv: list[str]) -> bool:
        """`--help` prints usage rather than JSON. Reading the manual is not an
        error, and counting it as one makes the warning signal useless."""
        return any(a in ("--help", "-h") for a in argv)


def is_full_roster(query: dict) -> bool:
    """`--all`, or a bare invocation: every facet null and the sea flag off."""
    return not query.get("sea") and all(
        query.get(f) is None for f in (*LIST_FACETS, "search")
    )


def satisfies(query: dict | None, constraint: dict) -> bool:
    """An empty constraint means 'any invocation, including a rejected one'.

    A full-roster query satisfies any constraint: it returns a superset of every
    filtered result, so the agent has strictly more to work with, not less.
    Grading it as a wrong call would fail an answer that is right -- what the
    agent then did with the rows is the answer checks' job, not the call layer's.
    """
    unknown = set(constraint) - {*LIST_FACETS, "sea", "search"}
    if unknown:
        raise ValueError(f"unknown facet {sorted(unknown)!r} in an expected call")
    if not constraint:
        return True
    if query is None:
        return False
    if is_full_roster(query):
        return True
    for facet, want in constraint.items():
        got = query.get(facet)
        if facet in LIST_FACETS:
            if want is None:
                if got is not None:
                    return False
            elif got is None or set(got) != {str(v).lower() for v in want}:
                return False
        elif facet == "sea":
            if bool(got) != bool(want):
                return False
        elif facet == "search":
            if want is None:
                if got is not None:
                    return False
            elif (got or "").strip().lower() != str(want).strip().lower():
                return False
    return True


def grade_call(case: dict, calls: list[dict], normalize) -> dict:
    """Every required invocation must be satisfied; extra invocations are fine."""
    required = case.get("expected_calls", [])
    queries = []
    errored = False
    for call in calls:
        argv = call.get("argv")
        if argv is None:
            return {"passed": False, "errored": False,
                    "reason": f"tool call has no 'argv': {call!r}"}
        query = normalize(list(argv))
        errored = errored or (query is None and not Normalizer.is_usage(list(argv)))
        queries.append((argv, query))

    if not required:
        # Nothing is required of the call layer here; the answer is the probe.
        return {"passed": True, "errored": errored, "reason": ""}

    if not calls:
        return {"passed": False, "errored": False, "reason": "no script invocation recorded"}

    reasons = []
    for requirement in required:
        alternatives = requirement["any_of"]
        if not any(satisfies(q, alt) for _, q in queries for alt in alternatives):
            reasons.append(
                f"no invocation matched {alternatives!r}; got "
                f"{[a for a, _ in queries]!r}"
            )
    if reasons:
        return {"passed": False, "errored": errored, "reason": "; ".join(reasons)}
    return {"passed": True, "errored": errored,
            "reason": "an invocation was rejected by the script" if errored else ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", help="JSONL run file")
    parser.add_argument("--verbose", action="store_true", help="list every failed check")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES,
                        help="cases.jsonl to grade against")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_QUERY,
                        help="path to the skill's query_opportunities.py")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    normalize = Normalizer(args.query_script)
    runs = load_runs(Path(args.run))

    broken = run_integrity_error(cases, runs)
    if broken:
        print(json.dumps(broken, indent=2))
        return 1

    rows = []
    for run in runs:
        case = cases[run["case_id"]]
        checks = grade_checks(run.get("answer", ""), case["checks"])
        call = grade_call(case, run.get("tool_calls", []), normalize)
        rows.append({
            "case_id": case["id"],
            "probe": case["probe"],
            "passed": call["passed"] and all(c["passed"] for c in checks),
            "call": call,
            "checks": checks,
        })

    summary = summarize(rows, {
        "errored_calls": [r["case_id"] for r in rows if r["call"].get("errored")],
    })
    print(json.dumps(summary, indent=2))

    if args.verbose:
        for row in rows:
            for check in row["checks"]:
                if not check["passed"]:
                    print(f"  {row['case_id']}/{check['id']}: {check['why']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
