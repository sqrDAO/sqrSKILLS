"""Tests for the refresh guard scripts.

Neither script touches the network here: check_anchors is exercised at its
collection and classification seams, and audit_refresh is pure file work.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_refresh  # noqa: E402
import check_anchors  # noqa: E402


ROSTER = {
    "_meta": {"last_updated": "2026-01-01"},
    "opportunities": [
        {"id": "kept", "url": "https://a.example/", "notes": "old", "last_verified": "2026-01-01"},
        {"id": "bumped", "url": "https://b.example/", "notes": "same", "last_verified": "2026-01-01"},
        {"id": "attested", "url": "https://c.example/", "notes": "same", "last_verified": "2026-01-01"},
        {"id": "static", "url": "https://d.example/", "notes": "same", "last_verified": "2026-01-01"},
    ],
}


def roster_after() -> dict:
    after = json.loads(json.dumps(ROSTER))
    entries = {e["id"]: e for e in after["opportunities"]}
    entries["kept"]["notes"] = "new"           # content changed -> date is earned
    entries["kept"]["last_verified"] = "2026-02-01"
    entries["bumped"]["last_verified"] = "2026-02-01"    # date only, unattested
    entries["attested"]["last_verified"] = "2026-02-01"  # date only, attested
    return after


class AuditRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.before = base / "before.json"
        self.after = base / "after.json"
        self.before.write_text(json.dumps(ROSTER, indent=2), encoding="utf-8")
        self.after.write_text(json.dumps(roster_after(), indent=2), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _audit(self, attested: set[str]) -> dict:
        return audit_refresh.audit(
            json.loads(self.before.read_text(encoding="utf-8")),
            json.loads(self.after.read_text(encoding="utf-8")),
            attested,
            "opportunities",
        )

    def test_content_change_earns_its_date(self) -> None:
        self.assertIn("kept", self._audit(set())["changed"])

    def test_date_only_bump_is_unsupported_without_attestation(self) -> None:
        unsupported = {i["id"] for i in self._audit(set())["unsupported"]}
        self.assertIn("bumped", unsupported)
        self.assertIn("attested", unsupported)

    def test_attestation_supports_a_date_only_bump(self) -> None:
        result = self._audit({"attested"})
        self.assertEqual(["attested"], result["attested_only"])
        self.assertEqual({"bumped"}, {i["id"] for i in result["unsupported"]})

    def test_untouched_entry_is_never_flagged(self) -> None:
        result = self._audit(set())
        self.assertNotIn("static", result["changed"])
        self.assertNotIn("static", {i["id"] for i in result["unsupported"]})

    def test_revert_restores_only_unsupported_dates(self) -> None:
        result = self._audit({"attested"})
        audit_refresh.revert(
            self.after,
            json.loads(self.before.read_text(encoding="utf-8")),
            result["unsupported"],
            "opportunities",
        )
        entries = {
            e["id"]: e for e in json.loads(self.after.read_text(encoding="utf-8"))["opportunities"]
        }
        self.assertEqual("2026-01-01", entries["bumped"]["last_verified"])
        self.assertEqual("2026-02-01", entries["attested"]["last_verified"])
        self.assertEqual("2026-02-01", entries["kept"]["last_verified"])

    def test_revert_preserves_surrounding_formatting(self) -> None:
        original = self.after.read_text(encoding="utf-8")
        result = self._audit(set())
        audit_refresh.revert(
            self.after,
            json.loads(self.before.read_text(encoding="utf-8")),
            result["unsupported"],
            "opportunities",
        )
        updated = self.after.read_text(encoding="utf-8")
        before_lines = original.splitlines()
        after_lines = updated.splitlines()
        # zip() stops at the shorter input, so a rollback that added or removed a
        # line would slip past a zip-only comparison.
        self.assertEqual(len(before_lines), len(after_lines))
        changed = [old for old, new in zip(before_lines, after_lines) if old != new]
        self.assertTrue(changed, "expected at least one reverted date")
        self.assertTrue(all("last_verified" in line for line in changed), changed)


class AuditDirectionTests(unittest.TestCase):
    """A lowered date withdraws a claim; only a raised one has to earn its keep."""

    def _audit(self, before_date: str, after_date: str, attested: set[str] = frozenset()) -> dict:
        before = {"opportunities": [{"id": "e", "notes": "same", "last_verified": before_date}]}
        after = {"opportunities": [{"id": "e", "notes": "same", "last_verified": after_date}]}
        return audit_refresh.audit(before, after, set(attested), "opportunities")

    def test_lowered_date_is_never_unsupported(self) -> None:
        # The 2026-08-24 correction pass lowered five dates the refresh had not
        # earned. Reverting those would restore the false dates this script exists
        # to stop.
        result = self._audit("2026-08-24", "2026-08-17")
        self.assertEqual([], result["unsupported"])
        self.assertEqual(["e"], [i["id"] for i in result["lowered"]])

    def test_raised_date_still_needs_support(self) -> None:
        result = self._audit("2026-08-17", "2026-08-24")
        self.assertEqual(["e"], [i["id"] for i in result["unsupported"]])
        self.assertEqual([], result["lowered"])

    def test_raised_date_is_supported_by_attestation(self) -> None:
        result = self._audit("2026-08-17", "2026-08-24", {"e"})
        self.assertEqual([], result["unsupported"])
        self.assertEqual(["e"], result["attested_only"])

    def test_unparseable_dates_fall_through_to_needing_support(self) -> None:
        # "less than" on free text would order these arbitrarily, so they are
        # treated as raised and must earn their keep.
        for before, after in (
            ("2026-08-24", "August 2026"),
            ("sometime", "2026-08-17"),
            ("2026-08-24", "2026-8-17"),
        ):
            with self.subTest(before=before, after=after):
                result = self._audit(before, after)
                self.assertEqual([], result["lowered"])
                self.assertEqual(["e"], [i["id"] for i in result["unsupported"]])

    def test_missing_date_field_is_not_read_as_lowered(self) -> None:
        before = {"opportunities": [{"id": "e", "notes": "same", "last_verified": "2026-08-24"}]}
        after = {"opportunities": [{"id": "e", "notes": "same"}]}
        result = audit_refresh.audit(before, after, set(), "opportunities")
        self.assertEqual([], result["lowered"])
        self.assertEqual(["e"], [i["id"] for i in result["unsupported"]])

    def test_lowered_date_survives_the_reverting_path(self) -> None:
        # End to end: the file must come back byte-identical.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            before_doc = {"opportunities": [{"id": "e", "notes": "same", "last_verified": "2026-08-24"}]}
            after_doc = {"opportunities": [{"id": "e", "notes": "same", "last_verified": "2026-08-17"}]}
            before = base / "before.json"
            after = base / "after.json"
            before.write_text(json.dumps(before_doc, indent=2), encoding="utf-8")
            after.write_text(json.dumps(after_doc, indent=2), encoding="utf-8")
            original = after.read_bytes()
            result = audit_refresh.audit(before_doc, after_doc, set(), "opportunities")
            audit_refresh.revert(after, before_doc, result["unsupported"], "opportunities")
            self.assertEqual(original, after.read_bytes())


class CheckAnchorsTests(unittest.TestCase):
    def test_collects_backticked_urls_from_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "baseline.md"
            path.write_text(
                "see `https://one.example/a` and `https://two.example/b`\n"
                "prose http://three.example/ is not an anchor\n",
                encoding="utf-8",
            )
            urls = [url for url, _ in check_anchors.collect_markdown(path)]
            self.assertEqual(["https://one.example/a", "https://two.example/b"], urls)

    def test_collects_visa_registry_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "policy.json"
            path.write_text(
                json.dumps(
                    {
                        "_meta": {
                            "sources": ["https://evisa.example/", "not-a-url"],
                            "source_registry": {"decree": {"url": "https://gov.example/d"}},
                        }
                    }
                ),
                encoding="utf-8",
            )
            urls = [url for url, _ in check_anchors.collect_visa(path)]
            self.assertEqual(["https://evisa.example/", "https://gov.example/d"], urls)

    def test_missing_files_collect_nothing(self) -> None:
        absent = Path("/nonexistent/nope.md")
        self.assertEqual([], check_anchors.collect_markdown(absent))
        self.assertEqual([], check_anchors.collect_visa(absent))
        self.assertEqual([], check_anchors.collect_web3(absent))

    def test_gone_codes_are_definitive_but_refusals_are_not(self) -> None:
        # 403 means the host declined us, which says nothing about the document.
        self.assertIn(404, check_anchors.DEFINITIVELY_GONE)
        self.assertIn(410, check_anchors.DEFINITIVELY_GONE)
        self.assertNotIn(403, check_anchors.DEFINITIVELY_GONE)
        self.assertNotIn(429, check_anchors.DEFINITIVELY_GONE)

    def test_unresolvable_hostname_is_detected(self) -> None:
        self.assertFalse(
            check_anchors.hostname_resolves("https://no-such-host.invalid/x")
        )

    def test_repository_anchors_are_collected_from_every_target(self) -> None:
        for target in check_anchors.TARGETS:
            self.assertTrue(check_anchors.collect(ROOT, (target,)), target)


class AnchorTargetSafetyTests(unittest.TestCase):
    """The URLs come from files an agent writes out of untrusted web pages."""

    def reason(self, url: str) -> str:
        with self.assertRaises(check_anchors.UnsafeTarget) as caught:
            check_anchors.check_target(url)
        return str(caught.exception)

    def test_non_web_schemes_are_refused(self) -> None:
        # urlopen speaks file:, so an unfiltered value would read the CI disk.
        self.assertIn("unsupported-scheme", self.reason("file:///etc/passwd"))
        self.assertIn("unsupported-scheme", self.reason("ftp://example.com/x"))
        self.assertIn("unsupported-scheme", self.reason("data:text/plain,hi"))

    def test_url_without_a_host_is_refused(self) -> None:
        self.assertIn("no-host", self.reason("http:///nowhere"))

    def test_loopback_and_private_targets_are_refused(self) -> None:
        for url in (
            "http://127.0.0.1/admin",
            "http://localhost/admin",
            "http://10.0.0.1/",
            "http://192.168.1.1/",
            "http://169.254.169.254/latest/meta-data/",  # cloud metadata
        ):
            self.assertIn("non-public-address", self.reason(url), url)

    def test_unresolvable_host_is_reported_as_nxdomain(self) -> None:
        self.assertEqual("NXDOMAIN", self.reason("https://no-such-host.invalid/x"))

    def test_public_url_is_allowed(self) -> None:
        check_anchors.check_target("https://example.com/a")  # must not raise

    def test_classify_refuses_unsafe_targets_without_fetching(self) -> None:
        verdict, status = check_anchors.classify("file:///etc/passwd", 1.0, 1)
        self.assertEqual("dead", verdict)
        self.assertIn("unsupported-scheme", str(status))

    def test_redirect_handler_validates_its_target(self) -> None:
        handler = check_anchors.ValidatingRedirectHandler()
        with self.assertRaises(check_anchors.UnsafeTarget):
            handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/")

    def test_collection_drops_non_web_urls_from_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "policy.json"
            path.write_text(
                json.dumps(
                    {
                        "_meta": {
                            "sources": ["file:///etc/passwd", "https://ok.example/"],
                            "source_registry": {"bad": {"url": "file:///etc/shadow"}},
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                ["https://ok.example/"], [u for u, _ in check_anchors.collect_visa(path)]
            )

    def test_tls_verification_is_not_disabled(self) -> None:
        source = (ROOT / "scripts" / "check_anchors.py").read_text(encoding="utf-8")
        self.assertNotIn("CERT_NONE", source)
        self.assertNotIn("check_hostname = False", source)


if __name__ == "__main__":
    unittest.main()
