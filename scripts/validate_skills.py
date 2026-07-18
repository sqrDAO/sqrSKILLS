#!/usr/bin/env python3
"""Validate the sqrSKILLS repository without third-party dependencies.

The command prints one JSON result to stdout. Human-readable diagnostics are
written to stderr so CI and other agents can consume the result reliably.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_NAME = re.compile(r"^(?:todo|done)\.([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
REQUIRED_SPEC_HEADINGS = ("## Goal", "## Files", "## Acceptance", "## Verify")


def visible(paths: list[Path]) -> list[Path]:
    """Ignore macOS AppleDouble sidecars that may exist in a local checkout."""
    return [path for path in paths if not path.name.startswith("._")]


def parse_frontmatter(path: Path) -> tuple[dict[str, object], list[str]]:
    """Parse the top-level fields used by SKILL.md frontmatter."""
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, [f"{path}: missing opening YAML frontmatter delimiter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [f"{path}: missing closing YAML frontmatter delimiter"]

    fields: dict[str, object] = {}
    current: str | None = None
    for line in lines[1:end]:
        match = re.match(r"^([a-z][a-z0-9-]*):(?:\s*(.*))?$", line)
        if match:
            current = match.group(1)
            value = (match.group(2) or "").strip()
            fields[current] = [] if current == "allowed-tools" else value
            continue
        if current == "allowed-tools":
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                value = item.group(1).split("#", 1)[0].rstrip()
                cast = fields[current]
                if isinstance(cast, list):
                    cast.append(value)
        elif current == "description" and line.startswith((" ", "\t")):
            previous = str(fields[current])
            fields[current] = f"{previous}\n{line.strip()}".strip()

    for key in ("name", "version", "description", "allowed-tools"):
        value = fields.get(key)
        if value is None or value == "" or value == []:
            errors.append(f"{path}: missing or empty frontmatter field '{key}'")
    return fields, errors


def validate_skill(skill_dir: Path, root: Path) -> list[str]:
    path = skill_dir / "SKILL.md"
    fields, errors = parse_frontmatter(path)
    name = str(fields.get("name", "")).strip("'\"")
    version = str(fields.get("version", "")).strip("'\"")

    if name and name != skill_dir.name:
        errors.append(f"{path}: name '{name}' does not match directory '{skill_dir.name}'")
    if name and not SKILL_NAME.fullmatch(name):
        errors.append(f"{path}: name '{name}' is not lowercase kebab-case")
    if version and not SEMVER.fullmatch(version):
        errors.append(f"{path}: version '{version}' is not SemVer MAJOR.MINOR.PATCH")

    text = path.read_text(encoding="utf-8")
    for reference in sorted(set(re.findall(r"\$SKILL_DIR/([^`\"\s)]+\.py)", text))):
        target = (skill_dir / reference).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path}: script reference escapes repository: {reference}")
            continue
        if not target.is_file():
            errors.append(f"{path}: referenced script does not exist: {reference}")
    return errors


def validate_backlog(root: Path) -> list[str]:
    errors: list[str] = []
    backlog = root / "docs" / "backlog"
    priority = backlog / "PRIORITY.md"
    if not priority.is_file():
        return ["docs/backlog/PRIORITY.md: missing backlog priority index"]
    priority_text = priority.read_text(encoding="utf-8")

    for path in visible(sorted(backlog.glob("*.md"))):
        if path.name == "PRIORITY.md":
            continue
        match = SPEC_NAME.fullmatch(path.name)
        if not match:
            errors.append(f"{path}: spec name must be todo.<slug>.md or done.<slug>.md")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.splitlines()) > 80:
            errors.append(f"{path}: spec exceeds the 80-line limit")
        for heading in REQUIRED_SPEC_HEADINGS:
            if heading not in text:
                errors.append(f"{path}: missing required heading '{heading}'")
        if path.name.startswith("todo.") and f"`{match.group(1)}`" not in priority_text:
            errors.append(f"{path}: open spec is not listed in docs/backlog/PRIORITY.md")
    return errors


def validate_repository(root: Path) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    skill_dirs = sorted(path.parent for path in root.glob("*/SKILL.md"))
    if not skill_dirs:
        errors.append("repository: no */SKILL.md files found")

    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir, root))

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if not readme:
        errors.append("README.md: missing or empty")
    for skill_dir in skill_dirs:
        name = skill_dir.name
        if f"](./{name}/)" not in readme:
            errors.append(f"README.md: missing inventory link for '{name}'")
        if f"@{name}" not in readme:
            errors.append(f"README.md: missing direct-install example for '{name}'")

    json_files = visible(
        sorted(root.glob("*/data/*.json"))
        + sorted(root.glob("*/assets/*.json"))
        + sorted((root / ".github").glob("*.json"))
    )
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")

    python_files = visible(
        sorted(root.glob("*/scripts/*.py")) + sorted((root / "scripts").glob("*.py"))
    )
    for path in python_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{path}: Python syntax error: {exc.msg}")

    errors.extend(validate_backlog(root))
    counts = {
        "skills": len(skill_dirs),
        "python_files": len(python_files),
        "json_files": len(json_files),
        "specs": len(list((root / "docs" / "backlog").glob("[td][oo][dn][oe].*.md"))),
    }
    return counts, errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    counts, errors = validate_repository(root)
    for error in errors:
        print(error, file=sys.stderr)
    print(json.dumps({"ok": not errors, "counts": counts, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
