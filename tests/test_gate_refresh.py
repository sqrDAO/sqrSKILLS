"""A leg that fails the harness is dropped on its own; healthy legs still ship."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import gate_refresh as gate  # noqa: E402


class GateRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.patches = Path(self.temp.name) / 'rejected'
        self.root.mkdir()
        for leg in gate.LEGS:
            for relative in gate.leg_files(leg):
                (self.root / relative).parent.mkdir(parents=True, exist_ok=True)
                (self.root / relative).write_text(f'{relative} at HEAD\n')
        git = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com']
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run([*git, 'commit', '-q', '-m', 'head'], cwd=self.root, check=True)
        self.summary = self.root / 'REFRESH_SUMMARY.md'
        self.summary.write_text(''.join(f'## {skill}\n\nAgent summary for {skill}.\n\n'
                                        for skill, _ in gate.LEGS.values()))
        self.rebuilds = []

    def refresh(self, leg, text):
        skill, data = gate.LEGS[leg]
        (self.root / skill / data).write_text(text)

    def read(self, leg):
        skill, data = gate.LEGS[leg]
        return (self.root / skill / data).read_text()

    def run_gate(self, broken):
        # The fake harness fails whenever a broken leg's edit is in the tree,
        # which is also how it proves each leg was tried alone.
        def check(root, leg):
            return [f'{name} is broken' for name in broken if 'refreshed' in self.read(name)]
        return gate.gate(self.root, self.patches, check=check,
                         rebuild=lambda root: self.rebuilds.append(root) or [])

    def test_a_failing_leg_is_dropped_and_the_healthy_one_ships(self):
        self.refresh('crypto', 'refreshed crypto\n')
        self.refresh('visa', 'refreshed visa\n')
        result = self.run_gate(broken={'crypto'})
        self.assertEqual(result['accepted'], ['visa'])
        self.assertEqual(list(result['rejected']), ['crypto'])
        self.assertTrue(result['ok'])
        self.assertIn('at HEAD', self.read('crypto'))
        self.assertEqual(self.read('visa'), 'refreshed visa\n')
        patch = (self.patches / 'vietnam-crypto-radar.patch').read_text()
        self.assertIn('+refreshed crypto', patch)

    def test_rejection_replaces_only_that_skills_summary(self):
        self.refresh('crypto', 'refreshed crypto\n')
        self.run_gate(broken={'crypto'})
        summary = self.summary.read_text()
        self.assertNotIn('Agent summary for vietnam-crypto-radar', summary)
        self.assertIn('Refresh rejected by the gate', summary)
        self.assertIn('- crypto is broken', summary)
        self.assertIn('Agent summary for web3-opportunities', summary)
        self.assertIn('Agent summary for vietnam-visa-check', summary)

    def test_unchanged_legs_are_not_tested_and_nothing_is_rejected(self):
        result = self.run_gate(broken={'crypto', 'web3', 'visa'})
        self.assertEqual(result['changed'], [])
        self.assertEqual(result['rejected'], {})
        self.assertFalse(self.patches.exists())

    def test_evaluation_splits_are_rebuilt_for_the_final_tree(self):
        self.refresh('web3', 'refreshed web3\n')
        self.run_gate(broken=set())
        # Once for the leg on its own, once for the tree that ships.
        self.assertEqual(len(self.rebuilds), 2)

    def test_reasons_cannot_carry_a_newline_into_github_output(self):
        self.assertEqual(gate.one_line('dead: https://x.example/\nstatus=pass'),
                         'dead: https://x.example/ status=pass')


if __name__ == '__main__':
    unittest.main()
