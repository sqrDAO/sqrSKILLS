"""Regression tests for the eval grading machinery.

The measuring apparatus has been wrong more often than the skills it measures.
On the `vietnam-visa-check` split it took four rounds of corrections against
three rounds of skill edits, and every one of those rounds was a rubric that
either passed a wrong answer or failed a right one. The corrections now live in
`evals/scripts/rubric.py` and are pinned here, because a gate that silently
stops discriminating reports successes nobody observed.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals" / "scripts"))

from rubric import grade_checks, run_integrity_error, summarize  # noqa: E402


def forbid(*patterns):
    return [{"id": "f", "type": "forbid_all", "patterns": list(patterns), "why": "why"}]


def require(*patterns):
    return [{"id": "r", "type": "require_any", "patterns": list(patterns), "why": "why"}]


class NegationAwareForbidTest(unittest.TestCase):
    """A forbidden phrase inside a negation is usually the correct answer."""

    def passed(self, answer, checks):
        return grade_checks(answer, checks)[0]["passed"]

    def test_bare_claim_is_caught(self):
        self.assertFalse(self.passed("Optimism Grants is currently open.",
                                     forbid(r"is currently open")))

    def test_negated_claim_is_allowed(self):
        self.assertTrue(self.passed("Optimism Grants is not currently open.",
                                    forbid(r"is currently open")))

    def test_neither_counts_as_a_negation(self):
        # The fix for the one check that fired on a correct answer during
        # calibration of the web3-opportunities split.
        self.assertTrue(self.passed("Neither programme is aimed at Vietnam.",
                                    forbid(r"is aimed at[^.\n]{0,20}vietnam")))

    def test_negation_does_not_carry_across_a_line_break(self):
        answer = "This one is not open.\nAlliance DAO is currently open."
        self.assertFalse(self.passed(answer, forbid(r"is currently open")))

    def test_negation_does_not_carry_across_a_sentence(self):
        answer = "It is not a grant. It is currently open."
        self.assertFalse(self.passed(answer, forbid(r"is currently open")))

    def test_negation_does_not_carry_across_a_question(self):
        # A question mark ends a sentence as surely as a period. Without this,
        # a rhetorical question excuses the claim that answers it.
        answer = "Is it not open? It is currently open."
        self.assertFalse(self.passed(answer, forbid(r"is currently open")))

    def test_negation_does_not_carry_across_an_exclamation(self):
        answer = "Do not apply! It is currently open."
        self.assertFalse(self.passed(answer, forbid(r"is currently open")))

    def test_require_any_ignores_negation(self):
        # require_any asks whether a topic was addressed, not whether it was
        # affirmed -- "not closed" still mentions closure.
        self.assertTrue(self.passed("It is not closed.", require(r"closed")))

    def test_unknown_check_type_is_an_error_not_a_pass(self):
        with self.assertRaises(ValueError):
            grade_checks("x", [{"id": "q", "type": "require_most", "patterns": ["x"], "why": "w"}])


class RunIntegrityTest(unittest.TestCase):
    """A partial run must never produce a score."""

    cases = {"a": {}, "b": {}}

    def test_complete_run_is_accepted(self):
        runs = [{"case_id": "a"}, {"case_id": "b"}]
        self.assertIsNone(run_integrity_error(self.cases, runs))

    def test_missing_case_is_refused(self):
        error = run_integrity_error(self.cases, [{"case_id": "a"}])
        self.assertEqual(error["missing"], ["b"])
        self.assertFalse(error["ok"])

    def test_duplicated_case_is_refused(self):
        runs = [{"case_id": "a"}, {"case_id": "a"}, {"case_id": "b"}]
        self.assertEqual(run_integrity_error(self.cases, runs)["duplicated"], ["a"])

    def test_unknown_case_is_refused(self):
        runs = [{"case_id": "a"}, {"case_id": "b"}, {"case_id": "zz"}]
        self.assertEqual(run_integrity_error(self.cases, runs)["unknown"], ["zz"])


class SummaryTest(unittest.TestCase):

    def rows(self):
        return [
            {"case_id": "a", "probe": "p", "passed": False,
             "call": {"passed": True, "reason": ""},
             "checks": [{"id": "c", "passed": False, "why": "w"}]},
            {"case_id": "b", "probe": "p", "passed": True,
             "call": {"passed": True, "reason": ""},
             "checks": [{"id": "c", "passed": True, "why": "w"}]},
        ]

    def test_axes_are_reported_separately(self):
        summary = summarize(self.rows())
        self.assertEqual(summary["pass_rate"], 0.5)
        self.assertEqual(summary["call_score"], 1.0)
        self.assertEqual(summary["answer_score"], 0.5)

    def test_a_case_fails_when_only_its_checks_fail(self):
        summary = summarize(self.rows())
        self.assertEqual([f["case_id"] for f in summary["failures"]], ["a"])
        self.assertEqual(summary["by_probe"], {"p": "1/2"})


if __name__ == "__main__":
    unittest.main()
