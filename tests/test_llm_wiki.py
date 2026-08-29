"""Ordering tests for the llm-wiki query scripts.

`search.py` and `list.py` sorted on score or date alone. Python's sort is
stable, so equal-ranking pages kept the order `os.listdir` returned them in --
filesystem hash order, which is neither alphabetical nor creation order. On a
four-way tie, `search.py --top 2` returned two arbitrary pages: the two a macOS
checkout happened to enumerate first, and a disjoint pair once enumeration was
reversed. Two users with identical wikis got different answers, and any
generated answer key would have encoded the machine that built it.

These tests pin the invariant rather than a snapshot: each script is run twice
over one fixture, with enumeration forced into opposite orders, and the two
outputs must be equal. A snapshot would pass on whichever machine produced it.
"""

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "llm-wiki" / "scripts"

# filename -> (title, last-updated, body)
FIXTURE = {
    # Six pages that tie: same date, same body term, no query term in the title.
    "apple.md": ("Apple notes", "2026-08-01", "Body mentions kubernetes once."),
    "banana.md": ("Banana notes", "2026-08-01", "Body mentions kubernetes once."),
    "mango.md": ("Mango notes", "2026-08-01", "Body mentions kubernetes once."),
    "zebra.md": ("Zebra notes", "2026-08-01", "Body mentions kubernetes once."),
    # Two more that also tie on title, to exercise the title tiebreak.
    "dup-a.md": ("Duplicate", "2026-08-01", "Body mentions kubernetes once."),
    "dup-b.md": ("Duplicate", "2026-08-01", "Body mentions kubernetes once."),
    # Ranks first on score, and last by filename -- so a filename tiebreak that
    # leaked into the primary key would visibly demote it.
    "zzz-kubernetes.md": ("Kubernetes deep dive", "2026-07-01", "About kubernetes."),
    # Newest, and late by filename, for the same reason under --sort updated.
    "zzz-newer.md": ("Later notes", "2026-08-20", "Nothing relevant here."),
}


def _load(name):
    """Import a script by path, without requiring it to be an installed module."""
    spec = importlib.util.spec_from_file_location(f"llm_wiki_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OrderingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = _load("search")
        cls.list = _load("list")
        cls.lint = _load("lint")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        pages = Path(self.tmp.name) / "pages"
        pages.mkdir()
        for fname, (title, updated, body) in FIXTURE.items():
            (pages / fname).write_text(
                f"---\ntitle: {title}\ntags: [note]\nsources: 1\n"
                f"last-updated: {updated}\n---\n\n# {title}\n\n{body}\n",
                encoding="utf-8",
            )
        patcher = mock.patch.dict(os.environ, {"WIKI_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_script(self, module, argv, *, reverse):
        """Run a script's main() with directory enumeration forced into one order."""
        real_listdir = os.listdir
        buf = io.StringIO()
        with mock.patch("os.listdir", lambda p: sorted(real_listdir(p), reverse=reverse)), \
                mock.patch.object(sys, "argv", ["script"] + argv), \
                contextlib.redirect_stdout(buf):
            module.main()
        return json.loads(buf.getvalue())

    def assert_order_independent(self, module, argv):
        forward = self.run_script(module, argv, reverse=False)
        backward = self.run_script(module, argv, reverse=True)
        self.assertEqual(forward, backward, f"{argv} depends on enumeration order")
        return forward

    def test_search_ranks_tied_pages_the_same_way_whatever_the_filesystem_returns(self):
        results = self.assert_order_independent(self.search, ["kubernetes"])
        self.assertGreater(len(results), 2, "fixture must produce a tie to be a test")

    def test_search_top_n_cutting_through_a_tie_returns_the_same_pages(self):
        # Rank 1 is the sole high scorer; the cut at 3 falls inside the tie group.
        results = self.assert_order_independent(self.search, ["kubernetes", "--top", "3"])
        self.assertEqual(len(results), 3)
        self.assertEqual(results[1]["score"], results[2]["score"])

    def test_list_sorted_by_title_is_independent_of_enumeration(self):
        self.assert_order_independent(self.list, ["--sort", "title"])

    def test_list_sorted_by_date_is_independent_of_enumeration(self):
        self.assert_order_independent(self.list, ["--sort", "updated"])

    def test_lint_is_independent_of_enumeration(self):
        self.assert_order_independent(self.lint, [])

    # The runs below force enumeration into the order least like the answer, so a
    # sort that still leaned on listdir could not coincidentally satisfy them.
    def test_score_still_decides_before_the_filename_tiebreak(self):
        results = self.run_script(self.search, ["kubernetes"], reverse=True)
        self.assertEqual(results[0]["file"], "pages/zzz-kubernetes.md")
        self.assertEqual([r["score"] for r in results], sorted((r["score"] for r in results), reverse=True))

    def test_the_most_recent_page_still_comes_first(self):
        pages = self.run_script(self.list, ["--sort", "updated"], reverse=True)
        self.assertEqual(pages[0]["file"], "pages/zzz-newer.md")

    def test_title_order_survives_the_tiebreak(self):
        pages = self.run_script(self.list, ["--sort", "title"], reverse=True)
        titles = [p["title"].lower() for p in pages]
        self.assertEqual(titles, sorted(titles))

    def test_pages_sharing_a_title_are_ordered_by_filename(self):
        pages = self.run_script(self.list, ["--sort", "title"], reverse=True)
        duplicates = [p["file"] for p in pages if p["title"] == "Duplicate"]
        self.assertEqual(duplicates, ["pages/dup-a.md", "pages/dup-b.md"])

    def test_the_ordering_is_total(self):
        """No two results compare equal, so nothing is left for listdir to decide."""
        results = self.run_script(self.search, ["kubernetes"], reverse=True)
        keys = [(-r["score"], r["file"]) for r in results]
        self.assertEqual(len(set(keys)), len(keys))
        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()
