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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "vietnam-visa-check" / "cases.jsonl"
SKILL = ROOT / "vietnam-visa-check"
QUERY = SKILL / "scripts" / "query_visa.py"
DATA = SKILL / "data" / "vietnam_immigration_policy.json"


def load_resolver():
    """Reuse the skill's own resolver so grading agrees with the script."""
    spec = importlib.util.spec_from_file_location("query_visa", QUERY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = json.loads(DATA.read_text(encoding="utf-8"))
    index = module.build_country_index(policy)
    return lambda raw: module.resolve_nationality(raw or "", index)


def load_cases() -> dict[str, dict]:
    return {
        json.loads(line)["id"]: json.loads(line)
        for line in CASES.read_text(encoding="utf-8").splitlines()
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
    expected = case["expected_call"]
    if not calls:
        return {"passed": False, "reason": "no script invocation recorded", "translated": False}

    want_iso = resolve(expected["nationality"])
    for call in calls:
        got_raw = call.get("nationality", "")
        if resolve(got_raw) != want_iso:
            continue
        # Computed before the argument checks below: rewriting the user's wording
        # is worth reporting even on a call that fails for another reason.
        translated = got_raw.strip().lower() != expected["nationality"].strip().lower()
        if expected.get("duration_days") is not None:
            if call.get("duration_days") != expected["duration_days"]:
                return {
                    "passed": False, "translated": translated,
                    "reason": (f"duration {call.get('duration_days')!r} passed, "
                               f"{expected['duration_days']} required by the prompt"),
                }
        if bool(call.get("phu_quoc_only")) != bool(expected.get("phu_quoc_only")):
            return {
                "passed": False, "translated": translated,
                "reason": f"phu_quoc_only={call.get('phu_quoc_only')!r}, expected {expected.get('phu_quoc_only')}",
            }
        return {"passed": True, "translated": translated,
                "reason": f"rewrote {expected['nationality']!r} as {got_raw!r}" if translated else ""}

    return {
        "passed": False, "translated": False,
        "reason": (f"no call resolved to {want_iso}; got "
                   f"{[c.get('nationality') for c in calls]!r}"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", help="JSONL run file")
    parser.add_argument("--verbose", action="store_true", help="list every failed check")
    args = parser.parse_args()

    cases = load_cases()
    resolve = load_resolver()
    runs = [json.loads(l) for l in Path(args.run).read_text(encoding="utf-8").splitlines() if l.strip()]

    rows, missing = [], sorted(set(cases) - {r["case_id"] for r in runs})
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
        "cases_scored": total,
        "cases_missing": missing,
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
