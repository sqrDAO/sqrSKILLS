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


SKILL = ROOT / "vietnam-crypto-radar" / "SKILL.md"
GLOSSARY = ROOT / "vietnam-crypto-radar" / "references" / "glossary.md"
SOURCES = ROOT / "vietnam-crypto-radar" / "references" / "sources.md"
WORKFLOW = ROOT / ".github" / "workflows" / "weekly-skill-refresh.yml"


class SkillRoutingTest(unittest.TestCase):
    def test_da_nang_routing_covers_every_trial_the_baseline_documents(self):
        # The routing line said "the four local controlled-trial decisions" after the
        # baseline grew to six, so a sandbox answer could silently omit Basal Pay and MIMO.
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("all six", text)
        self.assertNotIn("baseline.md` for the four", text)


class WeeklyRefreshPromptTest(unittest.TestCase):
    """The refresh rewrites baseline.md wholesale, so its prompt is data too.

    #33, #47 and #48 were all the same failure: a refresh regenerated a section
    from the prompt and lost what a correction pass had put in the file. A
    correction that is not also made in the prompt has a one-week half-life.
    """

    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_prompt_names_the_resolution_the_trials_actually_sit_under(self):
        self.assertIn("Nghị quyết 55/2024/NQ-HĐND", self.text)
        self.assertIn("Do NOT restore Nghị quyết 20/2026/NQ-HĐND", self.text)

    def test_prompt_carries_the_scheme_and_its_tier_4_mechanisms(self):
        self.assertIn("2728/QĐ-UBND", self.text)
        self.assertIn("CITY SANDBOX", self.text)
        self.assertIn("Never swap those", self.text)

    def test_prompt_disambiguates_the_two_ifcs(self):
        # The prompt is a wrapped YAML block scalar, so match across line breaks.
        self.assertRegex(self.text, r"International Finance\s+Corporation")
        self.assertRegex(self.text, r"Trung tâm tài chính quốc tế")
        self.assertIn("ORIENTATION", self.text)


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
            r"carrying no date marker at all were[\s>]+last[\s>]+checked[\s>]+on"
            r"[\s>]+([0-9]+ \w+ [0-9]{4})",
            self.text,
        )
        section = re.search(
            r"Unmarked anchors were[\s>]+last[\s>]+confirmed[\s>]+on"
            r"[\s>]+([0-9]+ \w+ [0-9]{4})",
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
    def test_da_nang_controlled_trials_keep_their_decisions_and_primary_anchor(self):
        for decision in ("3809/QĐ-UBND", "3810/QĐ-UBND", "3811/QĐ-UBND", "3812/QĐ-UBND"):
            self.assertIn(decision, self.text)
        self.assertIn("danang.gov.vn/vi/web/dng/w/chi-dao-dieu-hanh-noi-bat", self.text)

    def test_da_nang_trials_are_not_presented_as_national_licenses(self):
        self.assertIn("not national CASP/exchange licenses", self.text)
        self.assertIn("do not infer that direct payment", self.text)

    def test_da_nang_records_the_trials_that_predate_the_august_2026_batch(self):
        # The 22 Aug 2026 batch was not the start of the programme. Basal Pay
        # (1181) and MIMO (2895) were licensed first and both still run -- MIMO
        # to Dec 2028. A radar that lists only the latest batch undercounts.
        for decision in ("1181/QĐ-UBND", "2895/QĐ-UBND"):
            self.assertIn(decision, self.text, decision)
        self.assertIn("Dragon Lab", self.text)
        self.assertIn("AlphaTrue Solutions", self.text)

    def test_no_unqualified_first_crypto_trial_claim(self):
        # Basal Pay (Aug 2025) predates MIMO (Dec 2025) in the same city, so neither
        # is "the first" without a qualifier. Each operator's claim is narrower than
        # it sounds and must stay attributed.
        self.assertNotIn("the first such licence in the country", self.text)
        self.assertNotIn("the first controlled-trial licence of its kind in Vietnam", self.text)
        self.assertIn("Dragon Lab\ndescribes MIMO as the first licensed-trial solution", self.text)
        self.assertIn("Travel Rule", self.text)

    def test_da_nang_trial_count_is_stated_as_a_floor_not_a_total(self):
        # The regime is not crypto-specific and the 2026 first-batch approvals were
        # never enumerated, so a bare count would repeat the undercount this pass fixed.
        self.assertIn("floor", self.text)
        self.assertNotIn("by August 2026 six such trials are live", self.text)

    def test_da_nang_records_the_resolution_the_trials_sit_under(self):
        # The city's own signed blockchain scheme cites 55/2024/NQ-HĐND as the basis
        # of its sandbox. 20/2026/NQ-HĐND stays recorded, but it cannot be what the
        # 2025 approvals were issued under -- both predate it.
        self.assertIn("55/2024/NQ-HĐND", self.text)
        self.assertIn("20/2026/NQ-HĐND", self.text)
        self.assertNotIn(
            "Da Nang is reported to license these under **Nghị quyết 20/2026/NQ-HĐND**",
            self.text,
        )

    def test_resolution_20_is_not_reasserted_as_the_enabling_instrument(self):
        # The failure this guards is a refresh restoring the old framing wholesale.
        # 20/2026 may detail or replace 55/2024; which one the Aug 2026 batch issued
        # under is an open question, not a fact.
        self.assertIn("cannot be what the 2025 approvals were issued under", self.text)

    def test_da_nang_scheme_records_its_decision_and_public_anchor(self):
        self.assertIn("2728/QĐ-UBND", self.text)
        self.assertIn("Signed 23 Jun 2026; effective on signing", self.text)
        self.assertIn(
            "2728.QD.UBND.23.06.2026.signed.signed.signed.signed.pdf", self.text
        )
        # The anchor is the same document the entry was written from.
        self.assertIn(
            "e7ab57b90861224bb280669f0e243269cbb86a531750185c42ca7b71946f3db2",
            self.text,
        )

    def test_scheme_tier_4_records_which_mechanism_each_product_runs_under(self):
        # SP8 is live under the city sandbox; SP9 and SP10 are IFC-routed and not
        # approved. Collapsing or swapping the two mechanisms is the error this
        # pins, so assert the mapping itself -- asserting only that SP8/SP9/SP10
        # appear would pass on a baseline that reversed them.
        for product in ("SP8", "SP9", "SP10"):
            self.assertIn(product, self.text, product)
        self.assertRegex(
            self.text, r"SP8 runs under the \*\*city sandbox\*\*"
        )
        self.assertRegex(
            self.text, r"\*\*SP9 and SP10 run under the IFC mechanism\*\*"
        )
        self.assertRegex(self.text, r"Neither is\s+approved, licensed or live")
        # The inverse must never appear.
        self.assertNotRegex(self.text, r"SP8 runs under the \*\*IFC")
        self.assertNotRegex(self.text, r"SP9 and SP10 run under the (\*\*)?city sandbox")

    def test_scheme_is_not_presented_as_a_licence(self):
        self.assertIn(
            "it creates no crypto-asset licence and no payment authorisation", self.text
        )

    def test_dnc_chain_constraints_are_not_attributed_to_tier_4(self):
        # Báo Công luận filed the Tier-3 principle and DNC-Chain's exchange ban under
        # Tier 4. The signed annex puts them elsewhere, and the difference is what the
        # scheme means for crypto products.
        # Match across a line wrap: reflowing the paragraph must not fail the test,
        # the way test_the_two_unmarked_anchor_dates_agree once did.
        self.assertRegex(self.text, r"the operating\s+principle for \*\*Tier 3\*\*")
        self.assertRegex(self.text, r"\*\*DNC-Chain's\*\*\s+three constraints")

    def test_annex_only_detail_is_marked_as_annex_only(self):
        # The promulgating Decision resolves publicly; the annex does not. A later
        # pass must not cite a URL for annex-sourced claims.
        self.assertIn("not publicly resolvable", self.text)
        self.assertIn("*(annex)*", self.text)

    def test_ifc_instruments_are_recorded_with_the_orientation_caveat(self):
        for instrument in (
            "222/2025/QH15",
            "323/2025/NĐ-CP",
            "324/2025/NĐ-CP",
            "329/2025/NĐ-CP",
        ):
            self.assertIn(instrument, self.text, instrument)
        self.assertIn("That is a stated orientation, not a licence", self.text)

    def test_ifc_name_collision_is_flagged(self):
        # The World Bank's International Finance Corporation appears in the same
        # Da Nang coverage as Vietnam's Trung tâm tài chính quốc tế. The baseline
        # mention is incidental; the guidance an agent reads when labelling an
        # instrument lives in glossary.md and sources.md, so guard those too.
        self.assertIn("International Finance Corporation", self.text)
        for path in (GLOSSARY, SOURCES):
            body = path.read_text(encoding="utf-8")
            self.assertIn("International Finance Corporation", body, path.name)
        # Three different regimes answer to the word "sandbox".
        self.assertIn("Trung tâm tài chính quốc tế", GLOSSARY.read_text(encoding="utf-8"))
        self.assertIn(
            "thử nghiệm có kiểm soát", GLOSSARY.read_text(encoding="utf-8")
        )

    def test_rwa_tokenisation_proposal_stays_a_proposal(self):
        self.assertIn("PROPOSED / SINGLE-SOURCE", self.text)
        self.assertIn("This is an intention, not an instrument", self.text)

    def test_investment_law_uses_the_tier_1_signing_date(self):
        # The Da Nang scheme dates Law 143/2025/QH15 to 27 Jun 2025, which is the
        # date of Resolution 222/2025/QH15. The government database says 11 Dec
        # 2025. Assert the date the row actually gives, not just the warning that
        # follows it -- a row could adopt the wrong date and keep the warning.
        self.assertIn("143/2025/QH15", self.text)
        self.assertIn("gives 11 Dec 2025 as the signing date", self.text)
        self.assertIn("do not repeat that date", self.text)
        self.assertNotRegex(
            self.text, r"143/2025/QH15[^|]*?[Ss]igned 27 Jun 2025"
        )

    def test_annex_iv_commencement_is_not_asserted_as_tier_1(self):
        # The Tier-1 page carries only the law's 1 Mar 2026 commencement. The
        # 1 Jul 2026 Annex IV date rests on Tier-2 publishers plus the Da Nang
        # scheme, and the state-of-play paragraph must say so rather than
        # asserting it flat -- an agent leads with that paragraph.
        self.assertIn("its Annex IV is REPORTED to take effect", self.text)
        self.assertNotIn(
            "whose Annex IV takes effect **1 July 2026**", self.text
        )

    def test_scheme_decision_number_provenance_is_recorded(self):
        # Neither "2728" nor the day appears in the Decision's text layer, so a
        # verifier who opens the anchor and searches for them finds nothing.
        # Without this note the entry looks unverifiable against its own source.
        self.assertIn("Number and day are not in the text layer", self.text)
        self.assertIn("comes from the portal filename", self.text)

    def test_annex_provenance_is_not_overstated(self):
        # One organisational CA seal with no named signer, and a modification
        # timestamp rather than a signature date. The annex is the sole source
        # for the heaviest claims in this section, so it must not read as equal
        # to the Decision, which carries three named signatures.
        self.assertIn("no named signer", self.text)
        self.assertIn("not a signature date", self.text)
        self.assertNotIn("Tier 1 by signature", self.text)

    def test_resolution_20_is_not_published_as_confirmed_on_one_source(self):
        # sources.md requires Tier 1, a named law firm, or two independent Tier-2
        # sources. Only VnEconomy carries this one, so it stays single-source.
        self.assertIn("REPORTED / SINGLE-SOURCE (LOCAL)", self.text)
        self.assertNotIn("ENACTED / CONFIRMED (LOCAL) | Signed 29 May 2026", self.text)

    def test_no_unconfirmed_effective_dates_on_the_da_nang_instruments(self):
        # A reported 10 Jun 2026 effective date for Resolution 20 could not be
        # confirmed against any source, so it is not asserted. Both Da Nang rows
        # say what their anchor actually carries instead of implying a date.
        self.assertNotIn("effective 10 Jun 2026", self.text)
        self.assertIn(
            "Issued 29 May 2026; no effective date stated in the anchor", self.text
        )
        self.assertIn(
            "No separate legal effective date is stated in the anchor", self.text
        )

    def test_umi_pay_scope_discrepancy_stays_flagged_not_resolved_by_guess(self):
        # Pre-approval filings describe a prediction-market element the decision
        # title does not carry. Neither reading is confirmed, so neither is stated.
        self.assertIn("prediction market", self.text)
        self.assertIn("UNVERIFIED", self.text)

    def test_undecided_da_nang_applications_are_tracked_not_dropped(self):
        for applicant in ("VON", "G-Flow", "GM Services", "Dinogo"):
            self.assertIn(applicant, self.text, applicant)

    def test_da_nang_locations_are_not_generalised_to_a_whole_ward(self):
        # The source names sites per decision; an earlier draft flattened them to
        # "designated technology and innovation sites in Hải Châu ward".
        self.assertNotIn("innovation sites in\nHải Châu ward", self.text)
        self.assertIn("Công viên phần mềm số 1", self.text)


if __name__ == "__main__":
    unittest.main()
