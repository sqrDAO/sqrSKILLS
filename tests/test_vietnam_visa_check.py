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


if __name__ == "__main__":
    unittest.main()
