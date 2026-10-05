#!/usr/bin/env python3
"""Hold each refresh leg to the harness on its own, and drop a leg that fails.

The research legs are independent: each rewrites one skill's data. Before this
gate, one leg breaking a test or citing a dead URL turned the whole refresh
red, which held back the healthy legs and left a human to separate the good
edits from the bad by hand -- the 5 Oct 2026 crypto leg dropped four pinned
Da Nang passages and cited a 404, while the visa leg beside it was fine.

So each changed leg is tried alone on top of the pre-refresh tree (HEAD): the
validator, the unit tests, the unanchored-instrument check, the regenerated
evaluation splits, and the anchors that leg newly cites. A leg that fails any
of them is reverted to HEAD and its diff is kept as a patch for review; the
legs that pass ship. The summary says which leg was dropped and why, so a
rejection is never silent.

This changes what reaches the pull request, never what a check accepts: the
harness and anchor steps still run on the gated tree afterwards.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_refresh import LEGS  # noqa: E402

# check_anchors.py names its datasets differently from the legs.
ANCHOR_TARGET = {'crypto': 'baseline', 'web3': 'web3', 'visa': 'visa'}
BUILDERS = ('evals/scripts/build_visa_cases.py', 'evals/scripts/build_web3_cases.py')
FAILED_TEST = re.compile(r'^(?:FAIL|ERROR): (\S+) \(([^)]+)\)', re.MULTILINE)


def leg_files(leg: str) -> list[str]:
    skill, data = LEGS[leg]
    return [f'{skill}/SKILL.md', f'{skill}/{data}']


def at_head(root: Path, relative: str) -> bytes:
    return subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=root,
                          capture_output=True, check=True).stdout


def changed_legs(root: Path) -> list[str]:
    return [leg for leg in LEGS
            if any((root / f).read_bytes() != at_head(root, f) for f in leg_files(leg))]


def run(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *argv], cwd=root, capture_output=True, text=True)


def regenerate(root: Path) -> list[str]:
    return [f'{Path(b).name} could not regenerate the split'
            for b in BUILDERS if run(root, b).returncode != 0]


def apply(root: Path, snapshot: dict[str, bytes], keep: set[str], rebuild=regenerate) -> list[str]:
    """Write the refreshed files for `keep` and HEAD for every other leg."""
    for leg in LEGS:
        for relative in leg_files(leg):
            content = snapshot.get(relative) if leg in keep else None
            (root / relative).write_bytes(content if content is not None else at_head(root, relative))
    return rebuild(root)


def harness(root: Path, leg: str) -> list[str]:
    """Reasons this tree fails, as short single-line strings. Empty means pass."""
    reasons = []
    if run(root, 'scripts/validate_skills.py').returncode != 0:
        reasons.append('validate_skills.py failed')
    unanchored = run(root, 'scripts/check_unanchored.py', '--since', 'HEAD')
    if unanchored.returncode != 0:
        reasons.append('an instrument was added with no anchor beside it')
    tests = run(root, '-m', 'unittest', 'discover', '-s', 'tests')
    if tests.returncode != 0:
        names = [name for name, _ in FAILED_TEST.findall(tests.stderr)]
        reasons.append('tests failed: ' + (', '.join(names) or 'see the log'))
    for builder in BUILDERS:
        if run(root, builder, '--check').returncode != 0:
            reasons.append(f'{Path(builder).name} --check failed')
    anchors = run(root, 'scripts/check_anchors.py', '--since', 'HEAD', '--targets', ANCHOR_TARGET[leg])
    try:
        dead = [r for r in json.loads(anchors.stdout)['dead'] if r.get('new')]
    except (ValueError, KeyError):
        dead = []
        if anchors.returncode != 0:
            reasons.append('check_anchors.py did not complete')
    if dead:
        reasons.append('cites dead anchors: ' + ', '.join(f"{r['url']} ({r['status']})" for r in dead))
    return reasons


def patch(root: Path, snapshot: dict[str, bytes], leg: str) -> str:
    out = []
    for relative in leg_files(leg):
        before = at_head(root, relative).decode('utf-8', 'replace').splitlines(keepends=True)
        after = snapshot[relative].decode('utf-8', 'replace').splitlines(keepends=True)
        out += difflib.unified_diff(before, after, f'a/{relative}', f'b/{relative}')
    return ''.join(out)


def replace_section(summary: str, skill: str, replacement: str) -> str:
    """Swap the `## <skill>` section of the combined summary for `replacement`."""
    headings = '|'.join(re.escape(s) for s, _ in LEGS.values())
    pattern = re.compile(rf'^## {re.escape(skill)}\b.*?(?=^## (?:{headings})\b|\Z)', re.MULTILINE | re.DOTALL)
    if pattern.search(summary):
        return pattern.sub(lambda _: replacement.rstrip('\n') + '\n\n', summary, count=1)
    return summary.rstrip('\n') + '\n\n' + replacement


def one_line(text: str) -> str:
    # Reasons quote URLs an agent copied from web pages; they reach
    # GITHUB_OUTPUT and must not smuggle in a newline.
    return ' '.join(text.split())


def gate(root: Path, patches: Path, check=harness, rebuild=regenerate) -> dict:
    legs = changed_legs(root)
    snapshot = {f: (root / f).read_bytes() for leg in legs for f in leg_files(leg)}
    verdicts = {}
    try:
        for leg in legs:
            verdicts[leg] = apply(root, snapshot, {leg}, rebuild) + check(root, leg)
    except Exception as exc:  # noqa: BLE001 - any crash must not ship a half-tried tree
        # Mid-loop the tree holds one leg with the others reverted, which the
        # PR step would otherwise package. Ship nothing instead, and fail.
        problems = [f'gate did not complete ({type(exc).__name__}: {one_line(str(exc))}); no leg shipped']
        try:
            problems += apply(root, snapshot, set(), rebuild)
        except Exception as restore:  # noqa: BLE001
            problems.append(f'restoring main failed too ({type(restore).__name__})')
        return {'ok': False, 'changed': legs, 'accepted': [], 'rejected': {}, 'problems': problems}
    accepted = {leg for leg, reasons in verdicts.items() if not reasons}
    rejected = {leg: [one_line(r) for r in reasons] for leg, reasons in verdicts.items() if reasons}
    problems = apply(root, snapshot, accepted, rebuild)

    summary_path = root / 'REFRESH_SUMMARY.md'
    summary = summary_path.read_text(encoding='utf-8') if summary_path.exists() else ''
    for leg, reasons in rejected.items():
        skill = LEGS[leg][0]
        patches.mkdir(parents=True, exist_ok=True)
        (patches / f'{skill}.patch').write_text(patch(root, snapshot, leg), encoding='utf-8')
        summary = replace_section(summary, skill, (
            f'## {skill}\n\n**Refresh rejected by the gate; this skill is unchanged from `main`.** '
            'The research output failed the checks below when applied on its own. '
            f'Its diff is in the `refresh-rejected` artifact as `{skill}.patch`.\n\n'
            + ''.join(f'- {r}\n' for r in reasons)))
    summary_path.write_text(summary, encoding='utf-8')
    return {'ok': not problems, 'changed': legs, 'accepted': sorted(accepted),
            'rejected': rejected, 'problems': problems}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--patches', type=Path, required=True, help='where rejected diffs are written')
    args = parser.parse_args()
    result = gate(Path.cwd(), args.patches)
    if output := os.environ.get('GITHUB_OUTPUT'):
        with open(output, 'a', encoding='utf-8') as handle:
            handle.write('status=' + ('pass' if result['ok'] else 'fail') + '\n')
            handle.write('rejected=' + ','.join(result['rejected']) + '\n')
            reasons = '; '.join(f"{leg}: {' | '.join(r)}" for leg, r in result['rejected'].items())
            handle.write('reasons=' + (one_line(reasons) or 'none') + '\n')
    for leg, reasons in result['rejected'].items():
        print(f'{LEGS[leg][0]} refresh rejected: ' + one_line(' | '.join(reasons)), file=sys.stderr)
    print(json.dumps(result))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
