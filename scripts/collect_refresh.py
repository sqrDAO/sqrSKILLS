#!/usr/bin/env python3
"""Import completed refresh artifacts into a separate, trusted checkout."""
import argparse
import json
import os
from pathlib import Path
import re
import sys

LEGS = {
    'crypto': ('vietnam-crypto-radar', 'references/baseline.md'),
    'web3': ('web3-opportunities', 'data/web3_opportunities.json'),
    'visa': ('vietnam-visa-check', 'data/vietnam_immigration_policy.json'),
}
VERSION = re.compile(rb'^version: (\d+)\.(\d+)\.(\d+)\r?$', re.MULTILINE)
# Gemini CLI's file reader cuts any line over 2000 characters and appends
# "... [truncated]". An agent that writes back what it read loses the tail of
# the line: the 2026-09-21 refresh dropped half the crypto state of play this way.
# Research files keep every line under MAX_LINE (validate_skills.py enforces it
# on main), so an over-long or marker-bearing line in an output is new.
MAX_LINE = 1500
TRUNCATION = re.compile(rb'\[[^\]\n]{0,40}truncated[^\]\n]{0,40}\]', re.IGNORECASE)


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


def version_field(document):
    """Locate exactly one version field inside YAML frontmatter, never the body."""
    lines = document.splitlines(keepends=True)
    if not lines or lines[0].rstrip(b'\r\n') != b'---':
        raise ValueError('missing SKILL.md frontmatter')
    offset, fields = len(lines[0]), []
    for line in lines[1:]:
        if line.rstrip(b'\r\n') == b'---':
            break
        if line.startswith(b'version:'):
            match = VERSION.fullmatch(line.rstrip(b'\r\n'))
            if not match:
                raise ValueError('invalid SKILL.md version field')
            fields.append((offset, offset + len(line), tuple(map(int, match.groups()))))
        offset += len(line)
    else:
        raise ValueError('unterminated SKILL.md frontmatter')
    if len(fields) != 1:
        raise ValueError('SKILL.md needs exactly one frontmatter version')
    return fields[0]


def validate_skill(before, after):
    old_start, old_end, old_version = version_field(before)
    new_start, new_end, new_version = version_field(after)
    if (before[:old_start], before[old_end:]) != (after[:new_start], after[new_end:]):
        raise ValueError('research may change only the SKILL.md version')
    if new_version not in (old_version, (*old_version[:2], old_version[2] + 1)):
        raise ValueError('research version must be unchanged or one PATCH increment')


def validate_text(relative, before, after):
    """Reject output that a truncating reader wrote back, marker or not."""
    if len(TRUNCATION.findall(after)) > len(TRUNCATION.findall(before)):
        raise ValueError(f'truncation marker added to {relative}: a line was cut on read and written back')
    for number, line in enumerate(after.decode('utf-8', 'replace').splitlines(), start=1):
        if len(line) > MAX_LINE:
            raise ValueError(f'{relative}: line {number} exceeds {MAX_LINE} characters')


def collect(checkout, artifacts, outcomes):
    """Validate each leg atomically; rejected legs cannot discard healthy work."""
    pending, summaries, imported, rejected = {}, [], [], {}
    effective = dict(outcomes)
    for leg, (skill, data) in LEGS.items():
        outcome = outcomes[leg]
        if outcome != 'success':
            summaries.append(f'## {skill}\n\n**Refresh leg did not complete ({outcome}).** '
                             'No outputs were imported; this skill is unchanged from the checkout baseline.\n')
            continue
        try:
            root = artifacts / leg
            skill_path, data_path = f'{skill}/SKILL.md', f'{skill}/{data}'
            skill_bytes = read_regular(root, skill_path)
            data_bytes = read_regular(root, data_path)
            validate_skill((checkout / skill_path).read_bytes(), skill_bytes)
            validate_text(data_path, (checkout / data_path).read_bytes(), data_bytes)
            if data.endswith('.json'):
                json.loads(data_bytes)
            summary = read_regular(root, f'REFRESH_SUMMARY.{skill}.md').decode('utf-8')
            if not summary.strip():
                raise ValueError(f'empty summary for {skill}')
            leg_files = {skill_path: skill_bytes, data_path: data_bytes}
            if leg == 'web3':
                attestation = read_regular(root, 'REFRESH_VERIFIED.json')
                document = json.loads(attestation)
                if not isinstance(document, dict) or not isinstance(document.get('web3_opportunities'), list) or any(
                    not isinstance(item, str) for item in document['web3_opportunities']
                ):
                    raise ValueError('invalid Web3 attestation')
                leg_files['REFRESH_VERIFIED.json'] = attestation
        except (OSError, ValueError) as exc:
            effective[leg] = 'rejected'
            rejected[leg] = str(exc)
            summaries.append(f'## {skill}\n\n**Refresh output rejected.** '
                             'No outputs were imported; this skill is unchanged from the checkout baseline. '
                             'See collection diagnostics in the workflow log.\n')
            continue
        pending.update(leg_files)
        summaries.append(summary)
        imported.append(skill)
    pending['REFRESH_SUMMARY.md'] = ('\n\n'.join(summaries) + '\n').encode('utf-8')
    for relative, content in pending.items():
        (checkout / relative).write_bytes(content)
    return {'ok': all(value == 'success' for value in effective.values()),
            'imported': imported, 'outcomes': effective, 'rejected': rejected}


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
    for leg, error in result['rejected'].items():
        print(f'{leg}: {error}', file=sys.stderr)
    if output := os.environ.get('GITHUB_OUTPUT'):
        with open(output, 'a', encoding='utf-8') as handle:
            handle.write('status=' + ('pass' if result['ok'] else 'fail') + '\n')
            for leg, outcome in result['outcomes'].items():
                handle.write(f'{leg}={outcome}\n')
    print(json.dumps(result))
    # Collection completed, even if a leg was rejected. Packaging must continue
    # for healthy legs; the workflow publishes status=fail and fails at the end.
    return 0


if __name__ == '__main__':
    sys.exit(main())
