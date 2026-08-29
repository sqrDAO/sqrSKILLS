#!/usr/bin/env python3
"""Grading machinery shared by every skill's grader.

The per-skill graders differ only in how they judge a *tool call* — a visa
lookup is a nationality, a roster query is a set of facets. Everything else is
the same, and the corrections that took four rounds to get right (negation-aware
`forbid_all`, refusing to score a partial run) belong in one place rather than
in each copy.

Rubric check types:
  require_any  - at least one pattern must appear in the answer
  forbid_all   - none of the patterns may appear in the answer, unless negated
Patterns are case-insensitive regular expressions.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

# A forbidden phrase inside a negation is usually the correct answer: "does not
# have visa-free access" and "not currently open" are what a right answer says.
# Only matches that are *not* negated count as hits.
_NEGATION = re.compile(
    r"(?:\bnot\b|n't\b|\bno\b|\bnone\b|\bneither\b|\bnor\b|\bnever\b|\bwithout\b|"
    r"\blacks?\b|\bisn|\baren|\bdoesn|\bdon|\bcan't|\bcannot\b|\bunable\b)",
    re.I,
)
_NEGATION_WINDOW = 40


def negated(answer: str, start: int) -> bool:
    """True if a negation appears shortly before `start`, within one sentence."""
    window = answer[max(0, start - _NEGATION_WINDOW):start]
    # Do not read across a sentence or a line break: a negation two bullets up,
    # or in the question before this one, says nothing about the claim here.
    # `?` and `!` end a sentence as surely as `.` does -- without them,
    # "Is it not open? It is currently open." excuses the second clause.
    window = re.split(r"[.!?\n]", window)[-1]
    return bool(_NEGATION.search(window))


def load_cases(cases: Path) -> dict[str, dict]:
    return {
        json.loads(line)["id"]: json.loads(line)
        for line in cases.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def load_runs(run: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in run.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def grade_checks(answer: str, checks: list[dict]) -> list[dict]:
    results = []
    for check in checks:
        if check["type"] == "forbid_all":
            hits = []
            for pattern in check["patterns"]:
                for match in re.finditer(pattern, answer, re.I | re.M):
                    if not negated(answer, match.start()):
                        hits.append(pattern)
                        break
            passed = not hits
        elif check["type"] == "require_any":
            hits = [p for p in check["patterns"] if re.search(p, answer, re.I | re.M)]
            passed = bool(hits)
        else:
            raise ValueError(f"unknown check type {check['type']!r}")
        results.append({
            "id": check["id"], "passed": passed, "why": check["why"], "matched": hits,
        })
    return results


def run_integrity_error(cases: dict[str, dict], runs: list[dict]) -> dict | None:
    """A partial run must never produce a score.

    Omitting failing cases or repeating passing ones would otherwise inflate
    every number in the summary.
    """
    seen = Counter(r["case_id"] for r in runs)
    missing = sorted(set(cases) - set(seen))
    duplicated = sorted(cid for cid, n in seen.items() if n > 1)
    unknown = sorted(set(seen) - set(cases))
    if not (missing or duplicated or unknown):
        return None
    return {
        "ok": False,
        "error": "run file must contain every case exactly once",
        "missing": missing, "duplicated": duplicated, "unknown": unknown,
    }


def summarize(rows: list[dict], extra: dict | None = None) -> dict:
    """`rows` carry case_id, probe, passed, call{passed,reason}, checks[]."""
    total = len(rows)
    by_probe: dict[str, list[bool]] = {}
    for row in rows:
        by_probe.setdefault(row["probe"], []).append(row["passed"])

    def rate(values) -> float:
        return round(sum(values) / total, 4) if total else 0.0

    summary = {
        "ok": True,
        "cases_scored": total,
        "pass_rate": rate(r["passed"] for r in rows),
        "call_score": rate(r["call"]["passed"] for r in rows),
        "answer_score": rate(all(c["passed"] for c in r["checks"]) for r in rows),
    }
    summary.update(extra or {})
    summary["failures"] = [
        {"case_id": r["case_id"], "probe": r["probe"],
         "call": None if r["call"]["passed"] else r["call"]["reason"],
         "checks": [c["id"] for c in r["checks"] if not c["passed"]]}
        for r in rows if not r["passed"]
    ]
    summary["by_probe"] = {k: f"{sum(v)}/{len(v)}" for k, v in sorted(by_probe.items())}
    return summary
