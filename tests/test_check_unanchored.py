"""Tests for the unanchored-instrument check.

The check exists because the 31 August 2026 refresh added three circular numbers
and a claim about Article 9 enforcement competence to `baseline.md` citing
nothing, and every gate in the repository passed them. `validate_skills.py` does
not read prose, and `check_anchors.py` can only test URLs that exist, so a claim
citing nothing is invisible to it by construction.

The check is only worth having if it stays narrow. These tests pin the two ways
it could stop being useful: firing on a claim that honestly labels itself
unconfirmed, which would push an author into deleting the label rather than
adding a source; and firing on the standing file, which would demand a data
project before the harness could go green.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_unanchored", ROOT / "scripts" / "check_unanchored.py")
check_unanchored = importlib.util.module_from_spec(_spec)
sys.modules["check_unanchored"] = check_unanchored
_spec.loader.exec_module(check_unanchored)

scan = check_unanchored.scan
anchored_numbers = check_unanchored.anchored_numbers

REL = Path("vietnam-crypto-radar/references/baseline.md")

ANCHORS = """
## Verified source anchors

- **Government News — Decree 284/2026/NĐ-CP (Tier 1):** `https://example.gov.vn/a`
- **Da Nang city portal — Decisions 3809–3812/QĐ-UBND (Tier 1):** `https://example.gov.vn/b`
"""


def doc(body: str) -> str:
    return "## ENACTED / EFFECTIVE (the standing framework)\n" + body + "\n" + ANCHORS


class AnchorMatchingTest(unittest.TestCase):
    def test_an_anchored_instrument_does_not_fire(self):
        self.assertEqual([], scan(REL, doc(
            "| **Decree 284/2026/NĐ-CP** | Penalties. | ENACTED | 1 Sep 2026 |")))

    def test_an_unanchored_instrument_fires(self):
        found = scan(REL, doc(
            "| **Circular 89/2026/TT-BTC** | Tax administration. | EFFECTIVE | |"))
        self.assertEqual(["89/2026/TT-BTC"], [f["instrument"] for f in found])

    def test_an_anchor_range_covers_every_instrument_in_it(self):
        # The anchor names "Decisions 3809-3812"; the rows cite each separately.
        self.assertIn("3811/QĐ-UBND", anchored_numbers(ANCHORS))
        self.assertEqual([], scan(REL, doc(
            "| **3811/QĐ-UBND** | Umi Pay. | EFFECTIVE | 22 Aug 2026 |")))

    def test_a_range_is_not_expanded_without_bound(self):
        # A malformed or enormous range must not silently anchor half the corpus.
        wide = "- **Portal — Decisions 1000–9999/QĐ-UBND:** `https://example.gov.vn/c`"
        self.assertNotIn("5000/QĐ-UBND", anchored_numbers(
            "## Verified source anchors\n" + wide))


class DoesNotPunishHonestyTest(unittest.TestCase):
    """A claim that says it is unconfirmed needs no anchor.

    Labelling is the skill's documented alternative to sourcing. A check that
    fired here would make deleting the label the cheapest way to green.
    """

    def test_an_unverified_label_exempts_the_line(self):
        for label in ("UNVERIFIED", "DRAFT", "PROPOSED", "RUMORED", "REPORTED",
                      "SINGLE-SOURCE", "NEEDS_PRIMARY_SOURCE", "NOT CONFIRMED"):
            with self.subTest(label=label):
                self.assertEqual([], scan(REL, doc(
                    f"- **Circular 90/2026/TT-BTC** — {label}, no source found.")))

    def test_the_open_questions_section_is_exempt(self):
        body = ("## Known open questions to probe each run\n"
                "- Has Circular 39/2026/TT-NHNN been issued?\n" + ANCHORS)
        self.assertEqual([], scan(REL, body))

    def test_the_not_confirmed_section_is_exempt(self):
        body = ("## Checked and NOT confirmed — do not restate without new sources\n"
                "- Circular 90/2026/TT-BTC was not found on any primary site.\n" + ANCHORS)
        self.assertEqual([], scan(REL, body))


class RealRegressionTest(unittest.TestCase):
    def test_it_catches_what_the_2026_08_31_refresh_added(self):
        """The three circulars #47 introduced with no anchor, and nothing else.

        Skipped where the objects are absent (a shallow clone); the check's own
        behaviour is covered by the unit tests above regardless.
        """
        before = check_unanchored.baseline_at("57c9b02", REL)
        after = check_unanchored.baseline_at("7087236", REL)
        if before is None or after is None:
            self.skipTest("baseline revisions unavailable in this clone")
        known = {f["instrument"] for f in scan(REL, before)}
        new = sorted(f["instrument"] for f in scan(REL, after)
                     if f["instrument"] not in known)
        self.assertEqual(["39/2026/TT-NHNN", "89/2026/TT-BTC", "90/2026/TT-BTC"], new)


if __name__ == "__main__":
    unittest.main()
