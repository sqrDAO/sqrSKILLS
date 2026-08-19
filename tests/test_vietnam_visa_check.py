"""Regression tests for vietnam-visa-check nationality resolution."""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "vietnam-visa-check"
SCRIPT = SKILL / "scripts" / "query_visa.py"
DATA = SKILL / "data" / "vietnam_immigration_policy.json"


def load_module():
    spec = importlib.util.spec_from_file_location("query_visa", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args):
    """Run the script and return (exit_code, parsed_json)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


class NormalizeTest(unittest.TestCase):
    def setUp(self):
        self.q = load_module()

    def test_strips_case_whitespace_and_punctuation(self):
        self.assertEqual(self.q.normalize("  GerMany  "), "germany")
        self.assertEqual(self.q.normalize("Czech Republic!"), "czech republic")

    def test_strips_trailing_qualifiers(self):
        for raw in ("Russian citizens", "Russian nationals", "Russian passport holders"):
            self.assertEqual(self.q.normalize(raw), "russian")

    def test_strips_leading_article(self):
        self.assertEqual(self.q.normalize("The Netherlands"), "netherlands")

    def test_rejoins_dotted_abbreviations(self):
        self.assertEqual(self.q.normalize("U.K."), "uk")
        self.assertEqual(self.q.normalize("the U.S.A."), "usa")

    def test_qualifier_alone_is_not_stripped_to_nothing(self):
        self.assertEqual(self.q.normalize("citizens"), "citizens")


class ResolutionTest(unittest.TestCase):
    def setUp(self):
        self.q = load_module()
        self.policy = json.loads(DATA.read_text(encoding="utf-8"))
        self.index = self.q.build_country_index(self.policy)

    def resolve(self, raw):
        return self.q.resolve_nationality(raw, self.index)

    def test_demonym_forms(self):
        for raw in ("Russian", "Russians", "russians", "Russian citizens", "RUSSIANS"):
            self.assertEqual(self.resolve(raw), "RU", raw)

    def test_aliases_beat_the_iso_code_shortcut(self):
        # Regression: "UK" was previously read as the literal code "UK", which
        # matched no entry and produced an EVISA answer instead of VISA_FREE.
        self.assertEqual(self.resolve("UK"), "GB")
        self.assertEqual(self.resolve("USA"), "US")

    def test_country_names_and_iso_codes(self):
        self.assertEqual(self.resolve("Germany"), "DE")
        self.assertEqual(self.resolve("de"), "DE")
        self.assertEqual(self.resolve("DE"), "DE")

    def test_plural_country_names_are_not_singularized(self):
        self.assertEqual(self.resolve("Laos"), "LA")
        self.assertEqual(self.resolve("Philippines"), "PH")
        self.assertEqual(self.resolve("Netherlands"), "NL")
        self.assertEqual(self.resolve("Seychelles"), "SC")

    def test_multiple_demonyms_per_country(self):
        for raw in ("British", "Brit", "Brits", "Briton", "English", "Scottish", "Welsh"):
            self.assertEqual(self.resolve(raw), "GB", raw)

    def test_unresolved_inputs_return_none(self):
        for raw in ("XYZ", "Atlantis", "", "   ", "12345"):
            self.assertIsNone(self.resolve(raw), raw)

    def test_unknown_two_letter_code_is_accepted(self):
        self.assertEqual(self.resolve("ZZ"), "ZZ")

    def test_every_dataset_country_has_a_demonym(self):
        covered = set(self.q._DEMONYMS.values())
        for section in ("visa_exemption_by_country", "no_visa_exemption_notable_countries"):
            for entry in self.policy[section]["entries"]:
                self.assertIn(entry["iso_alpha2"].upper(), covered, entry["country"])

    def test_every_mapped_code_has_a_display_name(self):
        names = self.q.build_display_names(self.policy)
        for iso2 in set(self.q._DEMONYMS.values()) | set(self.q._ALIASES.values()):
            self.assertIn(iso2, names)

    def test_suggestions_offered_for_near_misses(self):
        names = self.q.build_display_names(self.policy)
        self.assertIn(
            "Russia", self.q.suggest_nationalities("Rusia", self.index, names)
        )
        self.assertEqual(self.q.suggest_nationalities("Atlantis", self.index, names), [])


class CommandLineTest(unittest.TestCase):
    def test_demonym_query_reports_visa_free(self):
        code, out = run("--nationality", "Russians")
        self.assertEqual(code, 0)
        self.assertEqual(out["iso_alpha2"], "RU")
        self.assertEqual(out["nationality"], "Russia")
        self.assertEqual(out["recommended_pathway"], "VISA_FREE")
        self.assertEqual(out["visa_free"]["max_stay_days"], 45)

    def test_uk_is_visa_free(self):
        code, out = run("--nationality", "UK")
        self.assertEqual(code, 0)
        self.assertEqual(out["iso_alpha2"], "GB")
        self.assertEqual(out["recommended_pathway"], "VISA_FREE")

    def test_usa_display_name(self):
        _, out = run("--nationality", "USA")
        self.assertEqual(out["iso_alpha2"], "US")
        self.assertEqual(out["nationality"], "United States")
        self.assertEqual(out["recommended_pathway"], "EVISA")

    def test_unrecognised_input_exits_zero_with_structured_error(self):
        # A non-zero exit surfaces to end users as a raw tool failure.
        code, out = run("--nationality", "XYZ")
        self.assertEqual(code, 0)
        self.assertIn("error", out)
        self.assertIn("suggestions", out)

    def test_unrecognised_input_offers_suggestions(self):
        _, out = run("--nationality", "Rusia")
        self.assertIn("Russia", out["suggestions"])

    def test_unknown_code_carries_an_explicit_note(self):
        _, out = run("--nationality", "ZZ")
        self.assertTrue(
            any("not listed in this dataset" in note for note in out["notes"])
        )

    def test_vietnamese_nationals_need_no_visa(self):
        # A "no visa needed" note next to recommended_pathway EVISA and a populated
        # evisa_option would contradict itself for any caller reading the fields.
        for raw in ("Vietnamese", "VN", "Vietnam"):
            _, out = run("--nationality", raw)
            self.assertEqual(out["iso_alpha2"], "VN", raw)
            self.assertEqual(out["recommended_pathway"], "NOT_REQUIRED", raw)
            self.assertIsNone(out["evisa_option"], raw)
            self.assertIsNone(out["visa_free"], raw)
            self.assertTrue(
                any("do not need a visa to enter Vietnam" in note for note in out["notes"]),
                raw,
            )

    def test_vietnamese_nationals_short_circuit_every_flag(self):
        for extra in (["--duration_days", "120"], ["--phu_quoc_only"]):
            _, out = run("--nationality", "VN", *extra)
            self.assertEqual(out["recommended_pathway"], "NOT_REQUIRED", extra)
            self.assertIsNone(out["evisa_option"], extra)

    def test_duration_beyond_exemption_falls_back_to_evisa(self):
        _, out = run("--nationality", "Germans", "--duration_days", "60")
        self.assertEqual(out["iso_alpha2"], "DE")
        self.assertEqual(out["recommended_pathway"], "EVISA")
        self.assertIsNotNone(out["visa_free"])

    def test_phu_quoc_flag_resolves_demonyms(self):
        code, out = run("--nationality", "Americans", "--phu_quoc_only")
        self.assertEqual(code, 0)
        self.assertEqual(out["iso_alpha2"], "US")
        self.assertEqual(out["nationality"], "United States")
        self.assertEqual(out["recommended_pathway"], "PHU_QUOC_EXEMPTION")

    def test_signed_but_not_in_force_exemption_routes_to_evisa(self):
        """Timor-Leste's agreement is signed but not yet effective — never visa-free."""
        for raw in ("Timorese", "East Timorese", "Timor-Leste", "TL"):
            code, out = run("--nationality", raw)
            self.assertEqual(code, 0, raw)
            self.assertEqual(out["iso_alpha2"], "TL", raw)
            self.assertEqual(out["recommended_pathway"], "EVISA", raw)
            self.assertIsNone(out["visa_free"], raw)


class PolicyFactTest(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(DATA.read_text(encoding="utf-8"))

    def test_health_declarations_are_conditional_not_blanket(self):
        framework = self.policy["policy_framework"]
        self.assertIn(
            "not a routine blanket requirement",
            framework["entry_requirement_summary"],
        )
        self.assertIn(
            "Conditional, not routinely mandatory", framework["health_declaration"]
        )
        self.assertNotIn(
            "must submit a digital health declaration", framework["health_declaration"]
        )
        self.assertNotIn("Mandatory health declaration for all", json.dumps(self.policy))

    def test_pre_arrival_information_is_an_optional_tan_son_nhat_pilot(self):
        card = self.policy["entry_categories"]["DIGITAL_ARRIVAL_CARD"]
        self.assertIn("Tan Son Nhat", card["description"])
        self.assertIn("optional, not mandatory", card["description"])
        self.assertIn("no nationwide rollout confirmed", card["status"])
        self.assertNotIn("five international airports", json.dumps(self.policy))

    def test_decree_286_is_scoped_to_inter_agency_coordination(self):
        source = self.policy["_meta"]["source_registry"]["decree_286_2026_nd_cp"]
        self.assertEqual(source["tier"], 1)
        # The URL first cited for this decree 404'd, and the decree was used to
        # support a PAI airport-expansion claim it says nothing about.
        self.assertNotIn("new-rules-on-coordination", source["url"])
        self.assertTrue(
            any("does not alter visa requirements" in fact for fact in source["verified_facts"])
        )

    def test_timor_leste_uses_the_primary_source_signing_date(self):
        entries = self.policy["no_visa_exemption_notable_countries"]["entries"]
        timor = next(entry for entry in entries if entry["iso_alpha2"] == "TL")
        self.assertEqual(timor["required_pathway"], "EVISA")
        self.assertIn("9 June 2026", timor["note"])
        self.assertNotIn("23 July", timor["note"])

        timeline = " ".join(
            item["event"] for item in self.policy["key_policy_timeline"]
        )
        self.assertNotIn("23 July", timeline)

    def test_corrected_claims_use_primary_government_sources(self):
        registry = self.policy["_meta"]["source_registry"]
        expected_hosts = {
            "decree_165_2026_health_declaration": "en.baochinhphu.vn",
            "mps_pre_arrival_information_pilot": "en.mps.gov.vn",
            "government_vietnam_timor_leste_ordinary_passport_agreement": "en.baochinhphu.vn",
        }
        for key, host in expected_hosts.items():
            self.assertEqual(registry[key]["tier"], 1, key)
            self.assertIn(host, registry[key]["url"], key)


class ExemptionValidityTest(unittest.TestCase):
    def setUp(self):
        self.q = load_module()

    def test_future_valid_from_is_not_in_force(self):
        entry = {"valid_from": "2099-01-01", "valid_until": None}
        self.assertFalse(self.q.is_exemption_valid(entry))

    def test_past_valid_from_is_in_force(self):
        entry = {"valid_from": "2020-01-01", "valid_until": None}
        self.assertTrue(self.q.is_exemption_valid(entry))

    def test_expired_valid_until_is_not_in_force(self):
        entry = {"valid_from": None, "valid_until": "2020-01-01"}
        self.assertFalse(self.q.is_exemption_valid(entry))

    def test_absent_dates_mean_no_bound_and_stay_in_force(self):
        for entry in (
            {"valid_from": None, "valid_until": None},
            {},
        ):
            self.assertTrue(self.q.is_exemption_valid(entry), entry)

    def test_malformed_dates_fail_closed(self):
        """An unparseable date must never be reported as visa-free."""
        for entry in (
            {"valid_from": "not-a-date", "valid_until": None},
            {"valid_from": None, "valid_until": "not-a-date"},
            {"valid_from": "2020-13-45", "valid_until": None},
            {"valid_from": 20200101, "valid_until": None},
            {"valid_from": None, "valid_until": ["2030-01-01"]},
        ):
            self.assertFalse(self.q.is_exemption_valid(entry), entry)

    def test_no_dataset_exemption_is_future_dated(self):
        """A future-dated entry would silently vanish from results — catch it here."""
        policy = json.loads(DATA.read_text(encoding="utf-8"))
        for entry in policy["visa_exemption_by_country"]["entries"]:
            self.assertTrue(self.q.is_exemption_valid(entry), entry["country"])


if __name__ == "__main__":
    unittest.main()
