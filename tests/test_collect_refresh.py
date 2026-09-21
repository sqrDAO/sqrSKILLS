"""Research output import must survive a failed writer and reject scope creep."""
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import collect_refresh as collector


class CollectRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / 'checkout'
        self.artifacts = self.root / 'artifacts'
        self.checkout.mkdir()
        for leg, (skill, data) in collector.LEGS.items():
            for base in (self.checkout, self.artifacts / leg):
                (base / skill / data).parent.mkdir(parents=True, exist_ok=True)
                (base / skill / data).write_text('{}' if data.endswith('.json') else 'Reviewed baseline\n')
                (base / skill / 'SKILL.md').write_text('---\nname: example\nversion: 1.2.3\n---\nDo the lookup.\n')
            (self.artifacts / leg / f'REFRESH_SUMMARY.{skill}.md').write_text(f'## {skill}\nNo changes.\n')
        (self.artifacts / 'web3' / 'REFRESH_VERIFIED.json').write_text('{"web3_opportunities": []}')
        self.outcomes = {leg: 'success' for leg in collector.LEGS}

    def test_failed_writer_cannot_leak_data_or_attestation(self):
        self.outcomes['web3'] = 'failure'
        path = 'web3-opportunities/data/web3_opportunities.json'
        # Even malformed outputs from a still-running failed leg are ignored.
        (self.artifacts / 'web3' / path).write_text('partial JSON')
        (self.artifacts / 'web3' / 'REFRESH_VERIFIED.json').write_text('partial JSON')
        collector.collect(self.checkout, self.artifacts, self.outcomes)
        (self.artifacts / 'web3' / path).write_text('{"late": true}')
        self.assertEqual((self.checkout / path).read_text(), '{}')
        self.assertFalse((self.checkout / 'REFRESH_VERIFIED.json').exists())
        self.assertIn('No outputs were imported', (self.checkout / 'REFRESH_SUMMARY.md').read_text())

    def test_success_import_is_a_snapshot_and_ignores_extra_files(self):
        path = 'vietnam-crypto-radar/references/baseline.md'
        (self.artifacts / 'crypto' / path).write_text('Updated baseline\n')
        (self.artifacts / 'crypto' / 'unrequested.py').write_text('raise RuntimeError()')
        collector.collect(self.checkout, self.artifacts, self.outcomes)
        (self.artifacts / 'crypto' / path).write_text('Late mutation\n')
        self.assertEqual((self.checkout / path).read_text(), 'Updated baseline\n')
        self.assertFalse((self.checkout / 'unrequested.py').exists())
        self.assertFalse((self.checkout / 'REFRESH_SUMMARY.web3-opportunities.md').exists())
        self.assertEqual(json.loads((self.checkout / 'REFRESH_VERIFIED.json').read_text()), {'web3_opportunities': []})

    def test_prompt_edit_rejects_only_its_leg(self):
        path = self.artifacts / 'visa' / 'vietnam-visa-check/SKILL.md'
        path.write_text(path.read_text().replace('Do the lookup.', 'Skip the lookup.'))
        (self.artifacts / 'crypto' / 'vietnam-crypto-radar/references/baseline.md').write_text('New data')
        result = collector.collect(self.checkout, self.artifacts, self.outcomes)
        self.assertFalse(result['ok'])
        self.assertEqual(result['outcomes']['visa'], 'rejected')
        self.assertIn('only the SKILL', result['rejected']['visa'])
        self.assertEqual((self.checkout / 'vietnam-crypto-radar/references/baseline.md').read_text(), 'New data')
        self.assertIn('Do the lookup.', (self.checkout / 'vietnam-visa-check/SKILL.md').read_text())

    def test_missing_success_summary_is_rejected(self):
        (self.artifacts / 'web3' / 'REFRESH_SUMMARY.web3-opportunities.md').unlink()
        result = collector.collect(self.checkout, self.artifacts, self.outcomes)
        self.assertFalse(result['ok'])
        self.assertEqual(result['outcomes']['web3'], 'rejected')
        self.assertIn('missing artifact', result['rejected']['web3'])
        self.assertEqual(len(result['imported']), 2)
        self.assertFalse((self.checkout / 'REFRESH_VERIFIED.json').exists())

    def test_symlink_output_is_rejected(self):
        path = self.artifacts / 'crypto' / 'vietnam-crypto-radar/references/baseline.md'
        path.unlink()
        path.symlink_to(self.checkout / 'vietnam-crypto-radar/references/baseline.md')
        result = collector.collect(self.checkout, self.artifacts, self.outcomes)
        self.assertEqual(result['outcomes']['crypto'], 'rejected')
        self.assertIn('symlink', result['rejected']['crypto'])

    def test_version_only_patch_allowed_but_downgrade_rejected(self):
        before = b'---\nversion: 1.2.3\n---\nInstructions\n'
        collector.validate_skill(before, before.replace(b'1.2.3', b'1.2.4'))
        with self.assertRaisesRegex(ValueError, 'PATCH'):
            collector.validate_skill(before, before.replace(b'1.2.3', b'1.2.2'))


    def test_malformed_web3_outputs_never_partially_import(self):
        data = self.artifacts / 'web3' / 'web3-opportunities/data/web3_opportunities.json'
        attestation = self.artifacts / 'web3' / 'REFRESH_VERIFIED.json'
        for malformed_data, malformed_attestation in [
            ('partial JSON', '{"web3_opportunities": []}'),
            ('{"changed": true}', '{"web3_opportunities": "wrong"}'),
            ('{"changed": true}', '{}'),
        ]:
            with self.subTest(data=malformed_data, attestation=malformed_attestation):
                data.write_text(malformed_data)
                attestation.write_text(malformed_attestation)
                result = collector.collect(self.checkout, self.artifacts, self.outcomes)
                self.assertEqual(result['outcomes']['web3'], 'rejected')
                self.assertEqual(len(result['imported']), 2)
                self.assertEqual((self.checkout / 'web3-opportunities/data/web3_opportunities.json').read_text(), '{}')
                self.assertFalse((self.checkout / 'REFRESH_VERIFIED.json').exists())

    def test_cli_reports_rejection_but_allows_packaging_to_continue(self):
        (self.artifacts / 'web3' / 'REFRESH_SUMMARY.web3-opportunities.md').unlink()
        output = self.root / 'github-output'
        result = subprocess.run(
            [sys.executable, collector.__file__, '--artifacts', str(self.artifacts),
             '--crypto', 'success', '--web3', 'success', '--visa', 'success'],
            cwd=self.checkout, env={**os.environ, 'GITHUB_OUTPUT': str(output)},
            text=True, capture_output=True, check=True,
        )
        self.assertFalse(json.loads(result.stdout)['ok'])
        self.assertIn('web3:', result.stderr)
        self.assertIn('status=fail\n', output.read_text())
        self.assertIn('web3=rejected\n', output.read_text())
        self.assertIn('crypto=success\n', output.read_text())

    def test_cancelled_and_skipped_legs_report_failure_without_import(self):
        for outcome in ('cancelled', 'skipped'):
            with self.subTest(outcome=outcome):
                self.outcomes['web3'] = outcome
                result = collector.collect(self.checkout, self.artifacts, self.outcomes)
                self.assertFalse(result['ok'])
                self.assertNotIn('web3-opportunities', result['imported'])
                self.assertEqual(result['outcomes']['web3'], outcome)

    def test_body_version_edit_and_duplicate_frontmatter_are_rejected(self):
        before = b'---\nversion: 1.2.3\n---\nExample:\nversion: 4.5.6\n'
        collector.validate_skill(before, before.replace(b'1.2.3', b'1.2.4'))
        with self.assertRaisesRegex(ValueError, 'only the SKILL'):
            collector.validate_skill(before, before.replace(b'4.5.6', b'9.9.9'))
        duplicate = before.replace(b'version: 1.2.3', b'version: 1.2.3\nversion: 1.2.3')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            collector.validate_skill(duplicate, duplicate)
        for version in (b'1.3.0', b'2.0.0'):
            with self.assertRaisesRegex(ValueError, 'PATCH'):
                collector.validate_skill(before, before.replace(b'1.2.3', version))

    def test_a_line_cut_on_read_and_written_back_is_rejected(self):
        # The 2026-09-21 shape: the reader stopped at 2000 characters, appended
        # its marker, and the agent wrote the cut line back as the new paragraph.
        path = self.artifacts / 'crypto' / 'vietnam-crypto-radar/references/baseline.md'
        path.write_text('These local trial approvals are not nati... [truncated]\n')
        result = collector.collect(self.checkout, self.artifacts, self.outcomes)
        self.assertEqual(result['outcomes']['crypto'], 'rejected')
        self.assertIn('truncation marker', result['rejected']['crypto'])
        self.assertEqual((self.checkout / 'vietnam-crypto-radar/references/baseline.md').read_text(),
                         'Reviewed baseline\n')
        self.assertIn('vietnam-visa-check', result['imported'])

    def test_other_truncation_marker_shapes_are_rejected(self):
        for marker in ('[File content truncated: showing lines 1-200]', '[... content truncated ...]'):
            with self.subTest(marker=marker):
                with self.assertRaisesRegex(ValueError, 'truncation marker'):
                    collector.validate_text('data.json', b'{}', f'{{"note": "{marker}"}}'.encode())

    def test_a_marker_already_in_the_baseline_is_not_new(self):
        before = b'The tool prints "[truncated]" when output is long.\n'
        collector.validate_text('baseline.md', before, before + b'Added line.\n')

    def test_an_over_long_line_is_rejected_even_without_a_marker(self):
        # An agent may strip the marker; a line longer than the file-wide limit
        # is still new, because main keeps every refresh file under it.
        long_line = ('word ' * collector.MAX_LINE).encode()
        with self.assertRaisesRegex(ValueError, 'line 2 exceeds'):
            collector.validate_text('baseline.md', b'short\n', b'short\n' + long_line)

    def test_production_refresh_files_pass_their_own_gate(self):
        root = Path(__file__).resolve().parents[1]
        for skill, data in collector.LEGS.values():
            content = (root / skill / data).read_bytes()
            collector.validate_text(data, content, content)

    def test_production_frontmatter_is_accepted(self):
        root = Path(__file__).resolve().parents[1]
        for skill, _ in collector.LEGS.values():
            data = (root / skill / 'SKILL.md').read_bytes()
            collector.validate_skill(data, data)


if __name__ == '__main__':
    unittest.main()
