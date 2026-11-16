"""Tests for optional article summaries."""

import tempfile
import unittest
from pathlib import Path

from build import BlogBuilder


class TldrTest(unittest.TestCase):
    def test_optional_tldr_renders_markdown_before_article(self):
        builder = BlogBuilder()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            builder.posts_dir = root / "posts"
            builder.posts_dir.mkdir()
            builder.output_dir = root
            (builder.posts_dir / "with.md").write_text(
                '---\ntitle: With\ndate: 2026-01-01\ntldr: "A **short** summary."\n'
                "---\n\nArticle body.\n"
            )
            (builder.posts_dir / "without.md").write_text(
                "---\ntitle: Without\ndate: 2026-01-01\n---\n\nArticle body.\n"
            )
            builder.build_posts()
            with_tldr = (root / "with.html").read_text()
            without_tldr = (root / "without.html").read_text()
            self.assertIn("TL;DR", with_tldr)
            self.assertIn("A <strong>short</strong> summary.", with_tldr)
            self.assertLess(with_tldr.index("TL;DR"), with_tldr.index("Article body."))
            self.assertNotIn("TL;DR", without_tldr)


if __name__ == "__main__":
    unittest.main()
