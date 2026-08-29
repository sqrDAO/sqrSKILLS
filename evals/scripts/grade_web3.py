#!/usr/bin/env python3
"""Score web3-opportunities runs against a validation split.

Usage:
    python3 evals/scripts/grade_web3.py runs/iter2-a.jsonl [runs/iter2-b.jsonl ...] \
        [--cases evals/web3-opportunities/cases-v2.jsonl] [--verbose]

Pass more than one run file to score repeats of the same iteration. Each must be
complete on its own; the summary then reports the mean, the spread, and -- the
reason repeats exist -- which cases *disagree between repeats*. A case that
passes once and fails once is measuring variance, and an edit credited to it is
an edit paid for by noise.

Run file, one object per case. A case may have several turns:

    {"case_id": "v2-04",
     "turns": [{"tool_calls": [{"argv": ["--dilution", "non-dilutive"]}],
                "answer": "<reply to turn 1>"},
               {"tool_calls": [{"argv": ["--dilution", "non-dilutive,mixed"]}],
                "answer": "<reply to turn 2>"}]}

Single-turn runs may use the flat `{"tool_calls": ..., "answer": ...}` shape;
it is read as one turn.

Each argv is normalised by running `query_opportunities.py` and reading back the
`query` block it echoes and the ids it retrieved, so the grader and the executor
cannot disagree about what a flag meant.

Expected calls and rubric checks may pin a `turn` (0-based). Without one, a call
may be satisfied by any turn and a check is graded against every turn's answer
joined together -- so a forbidden claim anywhere in the exchange still counts.
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
    """argv -> what the skill's own script makes of it."""

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
            self.cache[key] = None if "error" in out else {
                "query": out.get("query", {}),
                "ids": [r["id"] for r in out.get("results", [])],
            }
        return self.cache[key]

    @staticmethod
    def is_usage(argv: list[str]) -> bool:
        """Reading the manual is not an error."""
        return any(a in ("--help", "-h") for a in argv)


def is_full_roster(query: dict) -> bool:
    """`--all`, or a bare invocation: every facet null and the sea flag off."""
    return not query.get("sea") and all(
        query.get(f) is None for f in (*LIST_FACETS, "search")
    )


def satisfies(result: dict | None, constraint: dict) -> bool:
    """An empty constraint means 'any invocation, including a rejected one'.

    A full-roster query satisfies any facet constraint: it returns a superset,
    so the agent has more to work with, not less. `returns` asks whether the
    call retrieved the entries the question is about without dictating how --
    "a16z CSX" is findable by `--search a16z`, `--search csx`, or
    `--type accelerator`, and pinning one spelling grades vocabulary.
    """
    constraint = {k: v for k, v in constraint.items() if k != "turn"}
    unknown = set(constraint) - {*LIST_FACETS, "sea", "search", "returns"}
    if unknown:
        raise ValueError(f"unknown facet {sorted(unknown)!r} in an expected call")
    if not constraint:
        return True
    if result is None:
        return False
    query, ids = result["query"], result["ids"]

    if "returns" in constraint:
        if not set(constraint["returns"]) <= set(ids):
            return False
        if len(constraint) == 1:
            return True

    if is_full_roster(query):
        return True
    for facet, want in constraint.items():
        if facet == "returns":
            continue
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


def read_turns(run: dict) -> list[dict]:
    """Accept both the multi-turn shape and the flat single-turn one."""
    if "turns" in run:
        return run["turns"]
    return [{"tool_calls": run.get("tool_calls", []), "answer": run.get("answer", "")}]


def turn_integrity_error(cases: dict[str, dict], runs: list[dict]) -> dict | None:
    """A half-finished exchange must never produce a score either.

    `run_integrity_error` checks that every case is present exactly once. That is
    not enough once a case has turns: a run recording only turn 1 of a two-turn
    case still covers every case_id, and the missing turn reads as an empty
    answer -- on which a turn-pinned `forbid_all` passes. The result is a
    plausible-looking number computed from an exchange that never happened.

    The case defines the user's side, so the count is exact in both directions:
    too few turns means the run stopped early, too many means it is not this case.
    """
    mismatched = []
    for run in runs:
        case = cases.get(run["case_id"])
        if case is None:
            continue  # run_integrity_error reports unknown ids
        want = len(case.get("turns", [])) or 1
        got = len(read_turns(run))
        if got != want:
            mismatched.append({"case_id": run["case_id"], "expected_turns": want,
                               "recorded_turns": got})
    if not mismatched:
        return None
    return {
        "ok": False,
        "error": "every case must record exactly the turns it defines",
        "mismatched_turns": mismatched,
    }


def grade_call(case: dict, turns: list[dict], normalize) -> dict:
    required = case.get("expected_calls", [])
    per_turn: list[list[tuple]] = []
    errored = False
    for turn in turns:
        entries = []
        for call in turn.get("tool_calls", []):
            argv = call.get("argv")
            if argv is None:
                return {"passed": False, "errored": False,
                        "reason": f"tool call has no 'argv': {call!r}"}
            result = normalize(list(argv))
            errored = errored or (result is None and not Normalizer.is_usage(list(argv)))
            entries.append((argv, result))
        per_turn.append(entries)

    if not required:
        return {"passed": True, "errored": errored, "reason": ""}
    if not any(per_turn):
        return {"passed": False, "errored": False, "reason": "no script invocation recorded"}

    reasons = []
    for requirement in required:
        alternatives = requirement["any_of"]
        pinned = requirement.get("turn")
        scope = per_turn[pinned:pinned + 1] if pinned is not None else per_turn
        found = any(satisfies(res, alt)
                    for entries in scope for _, res in entries for alt in alternatives)
        if not found:
            where = f" on turn {pinned}" if pinned is not None else ""
            got = [a for entries in scope for a, _ in entries]
            reasons.append(f"no invocation{where} matched {alternatives!r}; got {got!r}")
    if reasons:
        return {"passed": False, "errored": errored, "reason": "; ".join(reasons)}
    return {"passed": True, "errored": errored,
            "reason": "an invocation was rejected by the script" if errored else ""}


def answer_for(check: dict, turns: list[dict]) -> str:
    turn = check.get("turn")
    if turn is None:
        return "\n\n".join(t.get("answer", "") for t in turns)
    return turns[turn].get("answer", "") if turn < len(turns) else ""


def score_run(cases: dict, runs: list[dict], normalize) -> list[dict]:
    rows = []
    for run in runs:
        case = cases[run["case_id"]]
        turns = read_turns(run)
        checks = [
            grade_checks(answer_for(c, turns), [c])[0] for c in case["checks"]
        ]
        call = grade_call(case, turns, normalize)
        rows.append({
            "case_id": case["id"], "probe": case["probe"],
            "passed": call["passed"] and all(c["passed"] for c in checks),
            "call": call, "checks": checks,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="+", help="one JSONL run file per repeat")
    parser.add_argument("--verbose", action="store_true", help="list every failed check")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES,
                        help="cases.jsonl to grade against")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_QUERY,
                        help="path to the skill's query_opportunities.py")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    normalize = Normalizer(args.query_script)

    per_repeat = []
    for path in args.run:
        runs = load_runs(Path(path))
        broken = run_integrity_error(cases, runs) or turn_integrity_error(cases, runs)
        if broken:
            print(json.dumps({**broken, "run": path}, indent=2))
            return 1
        per_repeat.append((path, score_run(cases, runs, normalize)))

    summary = summarize(per_repeat[0][1], {
        "errored_calls": [r["case_id"] for r in per_repeat[0][1] if r["call"].get("errored")],
    })

    if len(per_repeat) > 1:
        rates = [round(sum(r["passed"] for r in rows) / len(rows), 4)
                 for _, rows in per_repeat]
        outcomes: dict[str, list[bool]] = {}
        for _, rows in per_repeat:
            for row in rows:
                outcomes.setdefault(row["case_id"], []).append(row["passed"])
        unstable = sorted(c for c, v in outcomes.items() if len(set(v)) > 1)
        summary = {
            "ok": True,
            "repeats": len(per_repeat),
            "cases_scored": len(per_repeat[0][1]),
            "pass_rate_mean": round(sum(rates) / len(rates), 4),
            "pass_rate_per_repeat": dict(zip([p for p, _ in per_repeat], rates)),
            # Cases that disagree between repeats are noise, not signal. An edit
            # credited to one of these is an edit paid for by a coin flip.
            "unstable_cases": unstable,
            "stable_failures": sorted(c for c, v in outcomes.items() if not any(v)),
            "per_repeat": {p: summarize(rows) for p, rows in per_repeat},
        }
    print(json.dumps(summary, indent=2))

    if args.verbose:
        for _, rows in per_repeat:
            for row in rows:
                for check in row["checks"]:
                    if not check["passed"]:
                        print(f"  {row['case_id']}/{check['id']}: {check['why']}",
                              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
