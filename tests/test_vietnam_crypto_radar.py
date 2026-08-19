"""Regression tests for vietnam-crypto-radar baseline facts.

The weekly refresh workflow rewrites `references/baseline.md` wholesale. These
tests pin the facts and caveats that a previous refresh got wrong, so a later
one cannot quietly restore them.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "vietnam-crypto-radar" / "references" / "baseline.md"


class BaselineFactTest(unittest.TestCase):
    def setUp(self):
        self.text = BASELINE.read_text(encoding="utf-8")

    def test_decision_21_uses_its_real_signing_and_effective_dates(self):
        # Signed 30 Apr 2026, effective 1 Jul 2026. A 2026-08-17 refresh dated it
        # 14 Aug 2026 -- the date of press coverage, not of the instrument.
        self.assertIn("Quyết định 21/2026/QĐ-TTg", self.text)
        self.assertIn("Signed 30 Apr 2026", self.text)
        self.assertNotIn("| ENACTED / CONFIRMED | 14 Aug 2026 |", self.text)

    def test_blockchain_is_one_item_in_group_1_not_a_standalone_priority(self):
        self.assertIn("Group 1 (digital technology)", self.text)
        self.assertNotIn(
            "Designates blockchain technology as a strategic priority", self.text
        )

    def test_economy_wide_aml_instruments_are_not_described_as_crypto_specific(self):
        # Both Resolution 66.23 and Decree 296 are economy-wide. Earlier refreshes
        # presented them as crypto measures.
        self.assertEqual(self.text.count("Economy-wide, not crypto-specific"), 2)

    def test_material_legal_qualifiers_survive(self):
        # Each of these was dropped by a refresh, changing what the rule means.
        self.assertIn("unless classified as high tax risk", self.text)
        self.assertIn("one-half", self.text)
        self.assertIn("transition rules and counsel", self.text)

    def test_single_source_subclaim_keeps_its_anchor_and_promotion_rule(self):
        self.assertIn("REPORTED / SINGLE-SOURCE", self.text)
        self.assertIn("luatvietnam.vn", self.text)
        self.assertIn("Promote only when", self.text)

    def test_anchor_resolution_hygiene_rule_survives(self):
        self.assertIn("Re-check every anchor resolves before citing it", self.text)

    def test_dead_anchors_from_the_17_august_sweep_are_absent(self):
        for dead in (
            "ssc.gov.vn/ubck/faces/vi/vim/vitin/vichitiet/vichitiet_trangchu/vicsptin/1253345",
            "tai-san-so-tai-san-ma-hoa-kenh-dan-von-moi-tiem-nang-102260814085108831",
            "vanban.chinhphu.vn/?docid=218861",
            "vietnam-issues-new-beneficial-ownership-disclosure-rules-under-decree-296",
        ):
            self.assertNotIn(dead, self.text, dead)

    def test_unconfirmed_securities_law_claim_stays_unconfirmed(self):
        self.assertIn("Checked and NOT confirmed", self.text)
        self.assertNotIn("DRAFT / CONFIRMED (Tier 1)", self.text)


if __name__ == "__main__":
    unittest.main()
