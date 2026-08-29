"""Regression tests for the eval grading machinery.

The measuring apparatus has been wrong more often than the skills it measures.
On the `vietnam-visa-check` split it took four rounds of corrections against
three rounds of skill edits, and every one of those rounds was a rubric that
either passed a wrong answer or failed a right one. The corrections now live in
`evals/scripts/rubric.py` and are pinned here, because a gate that silently
stops discriminating reports successes nobody observed.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals" / "scripts"))

from rubric import grade_checks, run_integrity_error, summarize  # noqa: E402
from grade_web3 import (  # noqa: E402
    satisfies, read_turns, answer_for, turn_integrity_error,
)


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

    def test_nothing_negates(self):
        """`nothing` is unreachable from `\\bno\\b`, and it is how a live check is disclaimed.

        Found by a v2 baseline run: an answer that said "I have no web access in
        this session, so nothing here is live-verified" failed the check that
        forbids claiming a live verification -- for saying it had not made one.
        """
        self.assertTrue(self.passed(
            "I have no web access, so nothing here is live-verified.",
            forbid(r"live[- ]verified")))
        self.assertFalse(self.passed(
            "I live-verified this against the official page.",
            forbid(r"live[- ]verified")))

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


class FacetConstraintTest(unittest.TestCase):
    """`--dilution non-dilutive` is a different question from `non-dilutive,mixed`."""

    def query(self, ids=(), **over):
        base = {"type": None, "stage": None, "dilution": None, "chain": None,
                "region": None, "status": None, "sea": False, "search": None}
        base.update(over)
        return {"query": base, "ids": list(ids)}

    def test_empty_constraint_accepts_any_invocation(self):
        self.assertTrue(satisfies(self.query(), {}))

    def test_empty_constraint_accepts_a_rejected_invocation(self):
        # An out-of-enum facet still counts as having run the script.
        self.assertTrue(satisfies(None, {}))

    def test_a_named_facet_is_never_satisfied_by_a_rejected_invocation(self):
        self.assertFalse(satisfies(None, {"type": ["grant"]}))

    def test_list_facets_match_as_sets_not_sequences(self):
        query = self.query(chain=["l2", "ethereum"])
        self.assertTrue(satisfies(query, {"chain": ["ethereum", "l2"]}))

    def test_a_superset_call_does_not_satisfy_an_exact_facet(self):
        query = self.query(dilution=["non-dilutive", "mixed"])
        self.assertFalse(satisfies(query, {"dilution": ["non-dilutive"]}))

    def test_a_subset_call_does_not_satisfy_an_exact_facet(self):
        query = self.query(dilution=["non-dilutive"])
        self.assertFalse(satisfies(query, {"dilution": ["non-dilutive", "mixed"]}))

    def test_unnamed_facets_are_free(self):
        query = self.query(type=["grant"], region=["sea"])
        self.assertTrue(satisfies(query, {"type": ["grant"]}))

    def test_sea_flag_is_distinct_from_the_sea_region(self):
        self.assertFalse(satisfies(self.query(region=["sea"]), {"sea": True}))
        self.assertTrue(satisfies(self.query(sea=True), {"sea": True}))

    def test_search_compares_case_insensitively(self):
        self.assertTrue(satisfies(self.query(search="Optimism"), {"search": "optimism"}))
        self.assertFalse(satisfies(self.query(search="optimism"), {"search": "alliance"}))

    def test_a_none_constraint_requires_the_facet_to_be_absent(self):
        self.assertTrue(satisfies(self.query(), {"type": None}))
        self.assertFalse(satisfies(self.query(type=["grant"]), {"type": None}))

    def test_an_unknown_facet_is_an_error_not_a_pass(self):
        with self.assertRaises(ValueError):
            satisfies(self.query(), {"nonsense": ["x"]})


class ReturnsConstraintTest(unittest.TestCase):
    """Some cases are about reaching an entry, not about which flag reached it."""

    def result(self, ids, **over):
        base = {"type": None, "stage": None, "dilution": None, "chain": None,
                "region": None, "status": None, "sea": False, "search": None}
        base.update(over)
        return {"query": base, "ids": list(ids)}

    def test_any_query_that_retrieves_the_entry_satisfies(self):
        # `--search a16z` and `--search csx` are the same behaviour; pinning one
        # spelling grades vocabulary rather than what the agent did.
        for search in ("a16z", "csx"):
            got = self.result(["a16z-csx"], search=search)
            self.assertTrue(satisfies(got, {"returns": ["a16z-csx"]}), search)

    def test_a_query_that_misses_the_entry_fails(self):
        got = self.result(["optimism-grants"], type=["grant"])
        self.assertFalse(
            satisfies(got, {"returns": ["optimism-grants", "optimism-retro-funding"]})
        )

    def test_every_named_entry_must_come_back(self):
        got = self.result(["optimism-grants", "optimism-retro-funding"], search="optimism")
        self.assertTrue(
            satisfies(got, {"returns": ["optimism-grants", "optimism-retro-funding"]})
        )

    def test_a_rejected_invocation_never_satisfies_returns(self):
        self.assertFalse(satisfies(None, {"returns": ["a16z-csx"]}))


class MultiTurnTest(unittest.TestCase):
    """A follow-up that reuses turn 1's result is the failure v2 exists to catch,
    so the grader has to be able to tell the turns apart."""

    def test_flat_run_reads_as_one_turn(self):
        run = {"case_id": "x", "tool_calls": [{"argv": ["--all"]}], "answer": "hi"}
        turns = read_turns(run)
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0]["answer"], "hi")

    def test_multi_turn_run_keeps_its_turns(self):
        run = {"case_id": "x", "turns": [{"tool_calls": [], "answer": "one"},
                                         {"tool_calls": [], "answer": "two"}]}
        self.assertEqual([t["answer"] for t in read_turns(run)], ["one", "two"])

    def test_an_unpinned_check_sees_every_turn(self):
        turns = [{"answer": "alpha"}, {"answer": "beta"}]
        joined = answer_for({"id": "c"}, turns)
        self.assertIn("alpha", joined)
        self.assertIn("beta", joined)

    def test_a_pinned_check_sees_only_its_turn(self):
        turns = [{"answer": "alpha"}, {"answer": "beta"}]
        self.assertEqual(answer_for({"id": "c", "turn": 1}, turns), "beta")
        self.assertNotIn("alpha", answer_for({"id": "c", "turn": 1}, turns))

    def test_a_pinned_check_on_a_missing_turn_is_empty_not_an_error(self):
        # A run that stopped early must fail its checks, not crash the grader.
        self.assertEqual(answer_for({"id": "c", "turn": 3}, [{"answer": "alpha"}]), "")

    def test_a_forbidden_claim_anywhere_in_the_exchange_still_counts(self):
        turns = [{"answer": "It is currently open."}, {"answer": "Anyway, good luck."}]
        checks = [{"id": "f", "type": "forbid_all",
                   "patterns": [r"is currently open"], "why": "w"}]
        result = grade_checks(answer_for(checks[0], turns), checks)[0]
        self.assertFalse(result["passed"])


class TurnIntegrityTest(unittest.TestCase):
    """A half-finished exchange must never produce a score.

    Covering every case_id is not enough once a case has turns: a run recording
    only turn 1 of a two-turn case still passes the case-coverage check, and the
    missing turn reads as an empty answer that a turn-pinned `forbid_all` sails
    through. Reported by CodeRabbit on #44 against a run that scored 0.75.
    """

    cases = {"one": {"turns": ["a"]}, "two": {"turns": ["a", "b"]}}

    def recorded(self, case_id, n):
        # Not named `run` -- that shadows TestCase.run and breaks the runner.
        return {"case_id": case_id, "turns": [{"tool_calls": [], "answer": ""}] * n}

    def test_matching_turn_counts_are_accepted(self):
        runs = [self.recorded("one", 1), self.recorded("two", 2)]
        self.assertIsNone(turn_integrity_error(self.cases, runs))

    def test_a_truncated_exchange_is_refused(self):
        error = turn_integrity_error(self.cases, [self.recorded("two", 1)])
        self.assertFalse(error["ok"])
        self.assertEqual(error["mismatched_turns"],
                         [{"case_id": "two", "expected_turns": 2, "recorded_turns": 1}])

    def test_extra_turns_are_refused_too(self):
        # More turns than the case defines means it is not this case.
        self.assertIsNotNone(turn_integrity_error(self.cases, [self.recorded("one", 2)]))

    def test_a_flat_run_counts_as_one_turn(self):
        flat = {"case_id": "one", "tool_calls": [], "answer": "x"}
        self.assertIsNone(turn_integrity_error(self.cases, [flat]))

    def test_a_case_with_no_turns_key_expects_one(self):
        # v1 cases carry `prompt`, not `turns`.
        flat = {"case_id": "legacy", "tool_calls": [], "answer": "x"}
        self.assertIsNone(turn_integrity_error({"legacy": {}}, [flat]))

    def test_an_unknown_case_is_left_to_the_other_guard(self):
        self.assertIsNone(turn_integrity_error(self.cases, [self.recorded("nope", 9)]))


class TurnPinnedCallTest(unittest.TestCase):

    def result(self, **over):
        base = {"type": None, "stage": None, "dilution": None, "chain": None,
                "region": None, "status": None, "sea": False, "search": None}
        base.update(over)
        return {"query": base, "ids": []}

    def test_the_turn_key_is_not_treated_as_a_facet(self):
        # `turn` rides along on the constraint dict; it must not reach the
        # unknown-facet guard.
        got = self.result(dilution=["mixed"])
        self.assertTrue(satisfies(got, {"dilution": ["mixed"], "turn": 1}))


if __name__ == "__main__":
    unittest.main()


class LoosenedCheckDiscriminationTest(unittest.TestCase):
    """A check loosened to stop failing a correct answer must still fail a wrong one.

    Five checks were loosened after the v2 baseline run, which took the observed
    score from 19/24 to 23-24/24. That is exactly the shape of a rubric edited
    until the failures went away, so each one is pinned here against both the
    answer that should pass and the answer that must still fail. A loosened
    rubric that no longer discriminates is worse than the false fire it removed.
    """

    CASES = ROOT / "evals" / "web3-opportunities" / "cases-v2.jsonl"

    # case, check, an answer that must pass, an answer that must still fail
    FIXTURES = [
        ("v2-09", "distinguishes",
         "Searching `encode` returns 2 hits - but neither is an Encode Club entry. "
         "Both are other programs whose **notes** mention Encode Club.",
         "Encode Club is in the catalog. Here is its entry: type hackathon, open."),
        ("v2-20", "no_legal_answer",
         "Whether you can legally launch a token from Vietnam is a regulatory "
         "question. I'm not the right source - use vietnam-crypto-radar.",
         "Yes - launching a token from Vietnam is legal, and you can legally do it."),
        ("v2-22", "no_dilutive_survivors",
         "Superteam, sqrDAO, Ronin. Dropped as dilutive: Alliance DAO, YZi Labs, "
         "Antler, Kyros, Tribe Accelerator, Hashed Emergent.",
         "Programmes with no equity taken: Superteam, Alliance DAO, YZi Labs, "
         "Antler, Kyros, Tribe Accelerator, Hashed Emergent."),
        ("v2-24", "no_invented_url",
         "The roster url is gitcoin.co. Note that grants.gitcoin.co no longer "
         "resolves - do not apply through it.",
         "Apply through grants.gitcoin.co before the round closes."),
    ]

    def setUp(self):
        self.cases = {}
        with self.CASES.open() as handle:
            for line in handle:
                case = json.loads(line)
                self.cases[case["id"]] = case

    def check(self, case_id, check_id):
        return next(c for c in self.cases[case_id]["checks"] if c["id"] == check_id)

    def test_each_loosened_check_still_separates_right_from_wrong(self):
        for case_id, check_id, right, wrong in self.FIXTURES:
            with self.subTest(case=case_id, check=check_id):
                check = self.check(case_id, check_id)
                self.assertTrue(grade_checks(right, [check])[0]["passed"],
                                f"{case_id}/{check_id} still fails a correct answer")
                self.assertFalse(grade_checks(wrong, [check])[0]["passed"],
                                 f"{case_id}/{check_id} no longer catches its wrong answer")
