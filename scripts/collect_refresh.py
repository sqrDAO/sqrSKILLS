#!/usr/bin/env python3
"""Import completed refresh artifacts into a separate, trusted checkout."""
import argparse
import json
from pathlib import Path
import re
import sys

LEGS = {
    'crypto': ('vietnam-crypto-radar', 'references/baseline.md'),
    'web3': ('web3-opportunities', 'data/web3_opportunities.json'),
    'visa': ('vietnam-visa-check', 'data/vietnam_immigration_policy.json'),
}
VERSION = re.compile(rb'^version: (\d+)\.(\d+)\.(\d+)\r?$', re.MULTILINE)


def read_regular(root, relative):
    path = root / relative
    # Reject symlinks in every component, including the artifact root.
    components = [root.joinpath(*Path(relative).parts[:i])
                  for i in range(len(Path(relative).parts) + 1)]
    if any(p.is_symlink() for p in components):
        raise ValueError(f'symlink in artifact path: {relative}')
    if not path.is_file():
        raise ValueError(f'missing artifact file: {relative}')
    return path.read_bytes()


def validate_skill(before, after):
    old, new = VERSION.search(before), VERSION.search(after)
    if not old or not new or VERSION.sub(b'version: VERSION', before) != VERSION.sub(b'version: VERSION', after):
        raise ValueError('research may change only the SKILL.md version')
    old_version = tuple(map(int, old.groups()))
    new_version = tuple(map(int, new.groups()))
    if new_version not in (old_version, (*old_version[:2], old_version[2] + 1)):
        raise ValueError('research version must be unchanged or one PATCH increment')


def collect(checkout, artifacts, outcomes):
    """Validate all inputs before writing; never read a failed leg's files."""
    pending, summaries, imported = {}, [], []
    for leg, (skill, data) in LEGS.items():
        outcome = outcomes[leg]
        if outcome != 'success':
            summaries.append(f'## {skill}\n\n**Refresh leg did not complete ({outcome}).** '
                             'No outputs were imported; this skill is unchanged from the checkout baseline.\n')
            continue
        root = artifacts / leg
        skill_path, data_path = f'{skill}/SKILL.md', f'{skill}/{data}'
        skill_bytes = read_regular(root, skill_path)
        data_bytes = read_regular(root, data_path)
        validate_skill((checkout / skill_path).read_bytes(), skill_bytes)
        if data.endswith('.json'):
            json.loads(data_bytes)
        summary = read_regular(root, f'REFRESH_SUMMARY.{skill}.md').decode('utf-8')
        if not summary.strip():
            raise ValueError(f'empty summary for {skill}')
        if leg == 'web3':
            attestation = read_regular(root, 'REFRESH_VERIFIED.json')
            document = json.loads(attestation)
            if not isinstance(document, dict) or not isinstance(document.get('web3_opportunities'), list) or any(
                not isinstance(item, str) for item in document['web3_opportunities']
            ):
                raise ValueError('invalid Web3 attestation')
            pending['REFRESH_VERIFIED.json'] = attestation
        pending[skill_path], pending[data_path] = skill_bytes, data_bytes
        summaries.append(summary)
        imported.append(skill)
    pending['REFRESH_SUMMARY.md'] = ('\n\n'.join(summaries) + '\n').encode('utf-8')
    for relative, content in pending.items():
        (checkout / relative).write_bytes(content)
    return {'ok': True, 'imported': imported, 'outcomes': outcomes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    for leg in LEGS:
        parser.add_argument(f'--{leg}', choices=('success', 'failure', 'cancelled', 'skipped'), required=True)
    args = parser.parse_args()
    try:
        result = collect(Path.cwd(), args.artifacts, {leg: getattr(args, leg) for leg in LEGS})
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
