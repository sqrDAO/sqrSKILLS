from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_skills import parse_frontmatter, validate_repository, validate_skill


VALID_SKILL = """---
name: sample-skill
version: 1.2.3
description: |
  Use this sample when testing the validator.
allowed-tools:
  - Bash(python3 *)
---

# Sample

```bash
python3 "$SKILL_DIR/scripts/run.py"
```
"""


class ValidateSkillsTests(unittest.TestCase):
    def test_current_repository_is_valid(self) -> None:
        _counts, errors = validate_repository(ROOT)
        self.assertEqual([], errors)

    def test_valid_skill_frontmatter_and_script_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "sample-skill"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")
            (skill / "scripts" / "run.py").write_text("print('{}')\n", encoding="utf-8")
            fields, parse_errors = parse_frontmatter(skill / "SKILL.md")
            self.assertEqual("sample-skill", fields["name"])
            self.assertEqual([], parse_errors)
            self.assertEqual([], validate_skill(skill, root))

    def test_rejects_bad_version_and_missing_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "sample-skill"
            skill.mkdir()
            bad = VALID_SKILL.replace("version: 1.2.3", "version: next")
            (skill / "SKILL.md").write_text(bad, encoding="utf-8")
            errors = validate_skill(skill, root)
            self.assertTrue(any("not SemVer" in error for error in errors))
            self.assertTrue(any("does not exist" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
