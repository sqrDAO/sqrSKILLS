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
        changed = [
            line
            for old, new in zip(original.splitlines(), self.after.read_text(encoding="utf-8").splitlines())
            if old != new
            for line in (old,)
        ]
        self.assertTrue(all("last_verified" in line for line in changed), changed)


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


if __name__ == "__main__":
    unittest.main()
