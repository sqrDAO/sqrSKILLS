"""Regression tests for vietnam-crypto-radar baseline facts.

The weekly refresh workflow rewrites `references/baseline.md` wholesale. These
tests pin the facts and caveats that a previous refresh got wrong, so a later
one cannot quietly restore them.
"""

import re
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

    def test_the_two_unmarked_anchor_dates_agree(self):
        # The header and the anchors section both state when an anchor carrying no
        # date marker was last checked. The 2026-08-24 sweep moved the header to
        # 17 August while the anchors section still said 3 August, silently ageing
        # 20+ unverified anchors forward by two weeks.
        header = re.search(
            r"carrying no date marker at all were last checked on ([0-9]+ \w+ [0-9]{4})",
            self.text,
        )
        section = re.search(
            r"Unmarked anchors were last\s+confirmed on ([0-9]+ \w+ [0-9]{4})",
            self.text,
        )
        self.assertIsNotNone(header, "header statement missing")
        self.assertIsNotNone(section, "anchors-section statement missing")
        self.assertEqual(header.group(1), section.group(1))

    def test_decision_1624_does_not_assert_an_unverified_effective_date(self):
        # The row put the signing date in the Effective column. The anchor states
        # a signing date only, so the column must say that rather than imply one.
        self.assertIn("Quyết định số 1624/QĐ-TTg", self.text)
        self.assertIn("no separate effective date stated in the anchor", self.text)
        self.assertNotIn(
            "creates no direct crypto-asset market obligations. | ENACTED / CONFIRMED | 21 Aug 2026 |",
            self.text,
        )

    def test_decision_1624_keeps_the_wording_its_anchor_actually_carries(self):
        # The claim that it names digital assets and blockchain is real, but it is
        # a quotation -- keep the source wording so the next refresh cannot drift it.
        self.assertIn("tài sản số, công nghệ chuỗi khối (blockchain)", self.text)


if __name__ == "__main__":
    unittest.main()
