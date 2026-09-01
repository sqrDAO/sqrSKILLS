"""Regression tests for the web3-opportunities roster.

The weekly refresh rewrites `data/web3_opportunities.json` wholesale, and the
2026-08-24 run showed the shape of the damage it can do while every existing
gate stayed green: `status` values that contradicted the entry's own notes,
deadlines deleted, and dates bumped onto claims nobody re-checked. JSON parsing
and `validate_skills.py` cannot see any of that, so these tests pin it.

Entries here are dated facts. When one legitimately changes -- a cohort really
does reopen -- update the test deliberately in the same commit as the data.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "web3-opportunities" / "data" / "web3_opportunities.json"

KNOWN_STATUSES = {"open", "closed", "rolling", "cohort-based"}


class RosterConsistencyTest(unittest.TestCase):
    """Cross-field checks that catch the class, not just the instance."""

    def setUp(self):
        self.data = json.loads(ROSTER.read_text(encoding="utf-8"))
        self.entries = self.data["opportunities"]
        self.by_id = {e["id"]: e for e in self.entries}

    def test_every_status_is_in_the_known_vocabulary(self):
        # There is no enum in the file and nothing enforces one, so a refresh can
        # invent a status that every query filter then silently misses.
        for entry in self.entries:
            self.assertIn(entry["status"], KNOWN_STATUSES, entry["id"])

    def test_no_entry_is_verified_later_than_the_roster_itself(self):
        last_updated = self.data["_meta"]["last_updated"]
        for entry in self.entries:
            self.assertLessEqual(entry["last_verified"], last_updated, entry["id"])

    def test_a_closed_entry_does_not_advertise_work_in_progress(self):
        # web3-foundation-grants was marked closed while `cadence` still read
        # "rolling (Wave 31 in progress)" -- the record contradicted itself.
        for entry in self.entries:
            if entry["status"] == "closed":
                self.assertNotIn("in progress", entry["cadence"].lower(), entry["id"])

    def test_an_open_entry_does_not_say_the_program_does_not_exist(self):
        # solana-foundation-fellowships was `open` while its own note said no
        # program by that name was listed, so --type fellowship --status open
        # returned an entry asserting it did not exist.
        disavowals = ("no program labelled", "no specific programs labeled")
        for entry in self.entries:
            if entry["status"] != "open":
                continue
            notes = entry["notes"].lower()
            for phrase in disavowals:
                self.assertNotIn(phrase, notes, entry["id"])

    def test_bot_protected_domains_keep_their_do_not_prune_guardrail(self):
        # This sentence is written for the automation, not the reader: it stops a
        # future refresh from pruning a live entry on a failed automated fetch.
        for entry_id in ("corelia-academy", "unihackfest"):
            self.assertIn(
                "403 to plain fetchers",
                self.by_id[entry_id]["notes"],
                entry_id,
            )


class RosterFactTest(unittest.TestCase):
    """Facts a refresh has already got wrong once."""

    def setUp(self):
        self.by_id = {
            e["id"]: e
            for e in json.loads(ROSTER.read_text(encoding="utf-8"))["opportunities"]
        }

    def test_alliance_dao_keeps_both_deadlines(self):
        # Dropping the later of two deadlines is the failure mode that costs the
        # user the opportunity: after 23 Sep the regular window still has weeks left.
        notes = self.by_id["alliance-dao"]["notes"]
        self.assertIn("September 23, 2026", notes)
        self.assertIn("November 18, 2026", notes)

    def test_epf_is_not_open_while_its_cohort_is_mid_flight(self):
        # EPF7 applications closed 13 May 2026 and the cohort runs Jun-Nov 2026.
        # Flip this deliberately when an EPF8 intake is actually announced.
        self.assertNotEqual(self.by_id["ethereum-protocol-fellowship"]["status"], "open")

    def test_drips_keeps_the_legacy_contract_exploit_warning(self):
        self.assertIn("July 14", self.by_id["drips-network"]["notes"])

    def test_colosseum_entries_agree_on_the_fall_hackathon_window(self):
        # Two entries describe the same event; a refresh left them contradicting
        # each other and dropped the announced dates from both. What matters is
        # that both still carry the window, not how either spells it: a refresh
        # that rewrites "Sep 28-Nov 2" as "September 28 to November 2" has kept
        # the fact, and failing it there teaches the next refresh to restore a
        # string rather than a date.
        starts = (r"Sep(?:t|tember)?\.?\s*28", r"Nov(?:ember)?\.?\s*2(?!\d)")
        for entry_id in ("colosseum-eternal", "colosseum-hackathon"):
            notes = self.by_id[entry_id]["notes"]
            for pattern in starts:
                self.assertRegex(notes, pattern, entry_id)

    def test_dead_or_redirecting_urls_are_not_reinstated(self):
        # Each of these was the entry's own `url` and no longer resolves there.
        self.assertNotIn(
            "polkadot.network/development", self.by_id["polkadot-hackathons"]["url"]
        )
        self.assertNotIn(
            "grants.web3.foundation", self.by_id["web3-foundation-grants"]["url"]
        )

    def test_kyros_does_not_announce_a_past_year_event_as_news(self):
        # "GM Vietnam 2025 has been announced" survived two refreshes into
        # August 2026; the 2026 edition had already been held by then.
        self.assertNotIn("2025 has been announced", self.by_id["kyros-ventures"]["notes"])


if __name__ == "__main__":
    unittest.main()
