"""Exercise the actual workflow shell blocks without GitHub or model calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/weekly-skill-refresh.yml').read_text()


def step_blocks(name):
    # This is a deliberately narrow extractor for the workflow's literal run
    # blocks, not a YAML parser. It runs the shipped shell, not a reimplementation.
    return [part for part in WORKFLOW.split('      - name: ')[1:]
            if part.splitlines()[0] == name]


def shell(block):
    lines = block.split('        run: |\n', 1)[1].splitlines()
    result = []
    for line in lines:
        if line and not line.startswith('          '):
            break
        result.append(line[10:] if line else '')
    return '\n'.join(result)


class RefreshWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text(f'#!{sys.executable}\n' + '''import json, os, sys
if sys.argv[1:3] == ['pr', 'list']:
    print(os.environ.get('TEST_OPEN_PR', ''))
else:
    with open(os.environ['TEST_GH_CALLS'], 'a') as output:
        output.write(json.dumps(sys.argv[1:]) + '\\n')
''')
        gh.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
                    'TEST_GH_CALLS': str(self.root / 'calls.jsonl')}

    def test_pr_opened_after_preflight_blocks_publication(self):
        guards = step_blocks('Refuse to clobber an open refresh PR')
        self.assertEqual(len(guards), 2)
        subprocess.run(['bash', '-e', '-c', shell(guards[0])], env=self.env, check=True, capture_output=True)
        all_steps = WORKFLOW.split('      - name: ')[1:]
        publish_index = next(i for i, block in enumerate(all_steps) if block.startswith('Open pull request\n'))
        self.assertTrue(all_steps[publish_index - 1].startswith('Refuse to clobber an open refresh PR\n'))
        blocked = subprocess.run(['bash', '-e', '-c', shell(guards[1])],
                                 env={**self.env, 'TEST_OPEN_PR': '60'}, text=True, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn('still open', blocked.stderr)

    def test_research_failure_publishes_red_even_with_green_data_checks(self):
        env = {**self.env, 'RESEARCH_STATUS': 'fail', 'HARNESS_STATUS': 'pass',
               'ANCHOR_STATUS': 'pass', 'AUDIT_STATUS': 'pass', 'ANCHOR_DEAD': '0',
               'ANCHOR_CHECKED': '10', 'AUDIT_REVERTED': '0', 'SHA': 'test',
               'GITHUB_REPOSITORY': 'example/repo', 'RUN_URL': 'https://example.com/run'}
        block = step_blocks('Publish check results onto the PR')[0]
        self.assertIn('RESEARCH_STATUS: ${{ steps.collect.outputs.status }}', block)
        subprocess.run(['bash', '-e', '-c', shell(block)], env=env, check=True, capture_output=True)
        calls = [json.loads(line) for line in (self.root / 'calls.jsonl').read_text().splitlines()]
        research = next(call for call in calls if 'context=Refresh / research legs' in call)
        self.assertIn('state=failure', research)
        for call in calls:
            if call != research:
                self.assertIn('state=success', call)
        failure = step_blocks('Fail the run if the refresh did not pass its checks')[0]
        self.assertIn("steps.collect.outputs.status != 'pass'", failure)

    def test_changed_roster_regenerates_only_allowlisted_case_files(self):
        for directory in ('evals', 'web3-opportunities', 'vietnam-visa-check'):
            shutil.copytree(ROOT / directory, self.root / directory, ignore=shutil.ignore_patterns('__pycache__'))
        roster_path = self.root / 'web3-opportunities/data/web3_opportunities.json'
        roster = json.loads(roster_path.read_text())
        roster['_meta']['last_updated'] = '2099-01-01'
        roster_path.write_text(json.dumps(roster))
        builder = [sys.executable, 'evals/scripts/build_web3_cases.py', '--check']
        stale = subprocess.run(builder, cwd=self.root, capture_output=True)
        self.assertNotEqual(stale.returncode, 0)
        before = {p.relative_to(self.root): p.read_bytes() for p in (self.root / 'evals').rglob('*.jsonl')}
        block = step_blocks('Regenerate evaluation cases from audited data')[0]
        subprocess.run(['bash', '-e', '-c', shell(block)], cwd=self.root, check=True, capture_output=True)
        subprocess.run(builder, cwd=self.root, check=True, capture_output=True)
        subprocess.run([sys.executable, 'evals/scripts/build_visa_cases.py', '--check'],
                       cwd=self.root, check=True, capture_output=True)
        allowed = {'evals/vietnam-visa-check/cases.jsonl', 'evals/web3-opportunities/cases.jsonl',
                   'evals/web3-opportunities/cases-v2.jsonl'}
        changed = {str(p.relative_to(self.root)) for p in (self.root / 'evals').rglob('*.jsonl')
                   if before.get(p.relative_to(self.root)) != p.read_bytes()}
        self.assertTrue(changed)
        self.assertTrue(changed <= allowed)
        publication = step_blocks('Open pull request')[0]
        paths = publication.split('          add-paths: |\n', 1)[1].split('          commit-message:', 1)[0]
        self.assertEqual({line.strip() for line in paths.splitlines() if line.strip().startswith('evals/')}, allowed)
        self.assertLess(WORKFLOW.index('name: Hold the refresh to what it verified'),
                        WORKFLOW.index('name: Regenerate evaluation cases from audited data'))


if __name__ == '__main__':
    unittest.main()
