"""Research output import must survive a failed writer and reject scope creep."""
import json
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

    def test_prompt_edit_rejected_before_any_import(self):
        path = self.artifacts / 'visa' / 'vietnam-visa-check/SKILL.md'
        path.write_text(path.read_text().replace('Do the lookup.', 'Skip the lookup.'))
        (self.artifacts / 'crypto' / 'vietnam-crypto-radar/references/baseline.md').write_text('New data')
        with self.assertRaisesRegex(ValueError, 'only the SKILL'):
            collector.collect(self.checkout, self.artifacts, self.outcomes)
        self.assertEqual((self.checkout / 'vietnam-crypto-radar/references/baseline.md').read_text(), 'Reviewed baseline\n')

    def test_missing_success_summary_is_rejected(self):
        (self.artifacts / 'web3' / 'REFRESH_SUMMARY.web3-opportunities.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing artifact'):
            collector.collect(self.checkout, self.artifacts, self.outcomes)

    def test_symlink_output_is_rejected(self):
        path = self.artifacts / 'crypto' / 'vietnam-crypto-radar/references/baseline.md'
        path.unlink()
        path.symlink_to(self.checkout / 'vietnam-crypto-radar/references/baseline.md')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            collector.collect(self.checkout, self.artifacts, self.outcomes)

    def test_version_only_patch_allowed_but_downgrade_rejected(self):
        before = b'---\nversion: 1.2.3\n---\nInstructions\n'
        collector.validate_skill(before, before.replace(b'1.2.3', b'1.2.4'))
        with self.assertRaisesRegex(ValueError, 'PATCH'):
            collector.validate_skill(before, before.replace(b'1.2.3', b'1.2.2'))


if __name__ == '__main__':
    unittest.main()
