#!/usr/bin/env python3
"""Score a vietnam-visa-check run against the validation split.

Usage:
    python3 evals/scripts/grade_visa.py runs/<name>.jsonl [--verbose]

The run file is JSONL, one object per case:

    {"case_id": "vvc-06",
     "tool_calls": [{"nationality": "Filipino", "duration_days": 30,
                     "phu_quoc_only": false}],
     "answer": "<the agent's final user-facing reply>"}

A case passes only when every rubric check passes AND the tool call is right.
Two axes are reported separately, because they fail for different reasons and
call for different skill edits:

  call_score    did the agent invoke the script correctly?
  answer_score  did the final reply carry what the result made available?

``translated`` is a warning, not a failure: the skill tells the agent to pass the
user's wording through, but an answer that resolves to the right country is still
correct.  It is tracked because it predicts failures on inputs the alias tables
do not cover.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "evals" / "vietnam-visa-check" / "cases.jsonl"
DEFAULT_SKILL = ROOT / "vietnam-visa-check"
DEFAULT_QUERY = DEFAULT_SKILL / "scripts" / "query_visa.py"
DEFAULT_DATA = DEFAULT_SKILL / "data" / "vietnam_immigration_policy.json"

# query_visa.py's own `--duration_days` default. Where the prompt states no
# duration, passing this explicitly is identical to omitting the flag; any other
# value is a wrong call, because it changes which pathway the script returns.
SCRIPT_DEFAULT_DURATION = 30


def load_resolver(query: Path, data: Path):
    """Reuse the skill's own resolver so grading agrees with the script."""
    spec = importlib.util.spec_from_file_location("query_visa", query)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = json.loads(data.read_text(encoding="utf-8"))
    index = module.build_country_index(policy)
    return lambda raw: module.resolve_nationality(raw or "", index)


def load_cases(cases: Path) -> dict[str, dict]:
    return {
        json.loads(line)["id"]: json.loads(line)
        for line in cases.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


# A forbidden phrase inside a negation is usually the correct answer: "does not
# have visa-free access" and "do NOT get visa-free entry" are what a right answer
# says. Only matches that are *not* negated count as hits.
_NEGATION = re.compile(
    r"(?:\bnot\b|n't\b|\bno\b|\bnever\b|\bwithout\b|\blacks?\b|"
    r"\bisn|\baren|\bdoesn|\bdon|\bcan't|\bcannot\b|\bunable\b)",
    re.I,
)
_NEGATION_WINDOW = 40


def _negated(answer: str, start: int) -> bool:
    """True if a negation appears shortly before `start`, within one sentence."""
    window = answer[max(0, start - _NEGATION_WINDOW):start]
    window = window.rsplit(".", 1)[-1]  # do not read across a sentence boundary
    return bool(_NEGATION.search(window))


def grade_checks(answer: str, checks: list[dict]) -> list[dict]:
    results = []
    for check in checks:
        if check["type"] == "forbid_all":
            hits = []
            for pattern in check["patterns"]:
                for match in re.finditer(pattern, answer, re.I | re.M):
                    if not _negated(answer, match.start()):
                        hits.append(pattern)
                        break
        else:
            hits = [p for p in check["patterns"] if re.search(p, answer, re.I | re.M)]
        if check["type"] == "require_any":
            passed = bool(hits)
        elif check["type"] == "forbid_all":
            passed = not hits
        else:
            raise ValueError(f"unknown check type {check['type']!r}")
        results.append({
            "id": check["id"], "passed": passed, "why": check["why"],
            "matched": hits,
        })
    return results


def grade_call(case: dict, calls: list[dict], resolve) -> dict:
    """Every required invocation must be present; extra calls are allowed.

    A case that needs two lookups is not satisfied by one of them, and a
    duration the prompt never stated is a wrong call, not a harmless extra --
    it changes which pathway the script returns.
    """
    if not calls:
        return {"passed": False, "reason": "no script invocation recorded", "translated": False}

    translated, reasons = False, []
    for expected in case["expected_calls"]:
        want_iso = resolve(expected["nationality"])
        matched = False
        for call in calls:
            got_raw = call.get("nationality", "")
            if resolve(got_raw) != want_iso:
                continue
            # Reported even on a call that fails below: rewriting the user's
            # wording predicts failures the alias tables do not cover.
            if got_raw.strip().lower() != expected["nationality"].strip().lower():
                translated = True
            want_duration = expected.get("duration_days")
            got_duration = call.get("duration_days")
            if want_duration is None:
                acceptable = got_duration in (None, SCRIPT_DEFAULT_DURATION)
            else:
                acceptable = got_duration == want_duration
            if not acceptable:
                reasons.append(
                    f"{expected['nationality']!r}: duration {got_duration!r} passed, "
                    f"{want_duration!r} required by the prompt"
                )
                continue
            if bool(call.get("phu_quoc_only")) != bool(expected.get("phu_quoc_only")):
                reasons.append(
                    f"{want_iso}: phu_quoc_only={call.get('phu_quoc_only')!r}, "
                    f"expected {expected.get('phu_quoc_only')}"
                )
                continue
            matched = True
            break
        if not matched:
            reasons.append(
                f"no call satisfied {expected['nationality']!r}; got "
                f"{[c.get('nationality') for c in calls]!r}"
            )

    if reasons:
        return {"passed": False, "translated": translated, "reason": "; ".join(reasons)}
    return {"passed": True, "translated": translated,
            "reason": "rewrote the user's wording" if translated else ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", help="JSONL run file")
    parser.add_argument("--verbose", action="store_true", help="list every failed check")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="cases.jsonl to grade against")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_QUERY,
                        help="path to the skill's query_visa.py")
    parser.add_argument("--policy", type=Path, default=DEFAULT_DATA, help="path to the policy JSON")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    resolve = load_resolver(args.query_script, args.policy)
    runs = [json.loads(line) for line in
            Path(args.run).read_text(encoding="utf-8").splitlines() if line.strip()]

    # A partial run must never produce a score. Omitting failing cases or
    # repeating passing ones would otherwise inflate every number below.
    seen = Counter(r["case_id"] for r in runs)
    missing = sorted(set(cases) - set(seen))
    duplicated = sorted(cid for cid, n in seen.items() if n > 1)
    unknown = sorted(set(seen) - set(cases))
    if missing or duplicated or unknown:
        print(json.dumps({
            "ok": False,
            "error": "run file must contain every case exactly once",
            "missing": missing, "duplicated": duplicated, "unknown": unknown,
        }, indent=2))
        return 1

    rows = []
    for run in runs:
        case = cases[run["case_id"]]
        checks = grade_checks(run.get("answer", ""), case["checks"])
        call = grade_call(case, run.get("tool_calls", []), resolve)
        rows.append({
            "case_id": case["id"],
            "probe": case["probe"],
            "passed": call["passed"] and all(c["passed"] for c in checks),
            "call": call,
            "checks": checks,
            "failed_checks": [c["id"] for c in checks if not c["passed"]],
        })

    total = len(rows)
    passed = sum(r["passed"] for r in rows)
    by_probe: dict[str, list[bool]] = {}
    for row in rows:
        by_probe.setdefault(row["probe"], []).append(row["passed"])

    summary = {
        "ok": True,
        "cases_scored": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "call_score": round(sum(r["call"]["passed"] for r in rows) / total, 4) if total else 0.0,
        "answer_score": round(
            sum(all(c["passed"] for c in r["checks"]) for r in rows) / total, 4
        ) if total else 0.0,
        "translated_inputs": [r["case_id"] for r in rows if r["call"].get("translated")],
        "failures": [
            {"case_id": r["case_id"], "probe": r["probe"],
             "call": None if r["call"]["passed"] else r["call"]["reason"],
             "checks": r["failed_checks"]}
            for r in rows if not r["passed"]
        ],
        "by_probe": {k: f"{sum(v)}/{len(v)}" for k, v in sorted(by_probe.items())},
    }
    print(json.dumps(summary, indent=2))

    if args.verbose:
        for row in rows:
            for check in row["checks"]:
                if not check["passed"]:
                    print(f"  {row['case_id']}/{check['id']}: {check['why']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
