#!/usr/bin/env python3
"""test_constitution_is_one_document.py — the Constitution has ONE source.

21 September 2026
=================

Until today the Constitution was two hand-maintained files. The six amendments
of 21 September were applied to both by hand and the copies disagreed WITHIN
THE HOUR — the .md placed the new E0 evidence tier after E3, the .html placed
it before. One hour, one editor, one divergence, in the document that outranks
every other document, dataset, script and sentinel in the estate.

`SSI_FOUNDATION_BIBLE.md` is now authored and `SSI_FOUNDATION_BIBLE.html` is
rendered from it by `SSI_BIBLE_RENDER.py`. This sentinel is what makes that a
fact rather than an intention: a promise to re-render is exactly the kind of
marker Prohibition 9 now forbids relying on.

It is skipped, not failed, where the master-documents tree is not checked out
beside the site repository — the two live in separate repositories.
"""
from __future__ import annotations
import os
import subprocess
import sys
import unittest

# The master documents are a sibling OneDrive tree, not part of this repo.
CANDIDATES = [
    os.path.expanduser("~/Library/CloudStorage/OneDrive-IkengaSL/"
                       "Internal - IKENGA EU - Documents/0.22. IP agenda/"
                       "SSI Index/master documents"),
    os.path.expanduser("~/mnt/SSI Index/master documents"),
    os.path.expanduser("~/SSI Index/master documents"),
]
MD = next((d for d in CANDIDATES if os.path.isdir(d)), None)


@unittest.skipIf(MD is None, "master documents tree not reachable from here")
class TestConstitutionIsOneDocument(unittest.TestCase):

    def test_renderer_exists(self):
        self.assertTrue(os.path.exists(os.path.join(MD, "SSI_BIBLE_RENDER.py")),
                        "SSI_BIBLE_RENDER.py is what makes the .html a projection")

    def test_html_is_exactly_the_render_of_the_md(self):
        """The whole point. If this fails, the Constitution has forked again."""
        r = subprocess.run(
            [sys.executable, "SSI_BIBLE_RENDER.py", "--check"],
            cwd=MD, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0,
                         "the Constitution's .html is not the render of its .md:\n"
                         + r.stdout + r.stderr)

    def test_the_md_says_which_copy_is_authored(self):
        """A reader must be able to tell the source from the projection by
        reading the document itself, not by reading this test."""
        with open(os.path.join(MD, "SSI_FOUNDATION_BIBLE.md"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("SSI_FOUNDATION_BIBLE.md` is authored", src)
        self.assertIn("is a RENDERING of it", src)
        self.assertIn("SSI_BIBLE_RENDER.py", src)

    def test_nothing_else_claims_to_render_the_bible(self):
        """Prohibition 4's exception rests on there being exactly ONE renderer."""
        hits = []
        for root, _dirs, files in os.walk(MD):
            if "zzz" in root or "_to_delete" in root or "__pycache__" in root:
                continue
            for f in files:
                if not f.endswith(".py") or f == "SSI_BIBLE_RENDER.py":
                    continue
                with open(os.path.join(root, f), encoding="utf-8",
                          errors="replace") as fh:
                    if "BIBLE" in fh.read():
                        hits.append(f)
        self.assertEqual(hits, [],
                         "a second tool references the BIBLE: %s" % hits)


if __name__ == "__main__":
    unittest.main(verbosity=2)
