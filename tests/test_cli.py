#!/usr/bin/env python3
"""Unit tests for blog CLI helpers."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import cli


class CliHelpersTest(unittest.TestCase):
    def test_slugify_normalises_title(self):
        self.assertEqual(cli._slugify("  Hello, World!!  "), "hello-world")

    def test_draft_template_includes_idea_source_when_present(self):
        content = cli._draft_template("Test Title", "ideas/2026-06-27-test.md", "Some notes")
        self.assertIn('idea: "ideas/2026-06-27-test.md"', content)
        self.assertIn("## Notes from idea", content)
        self.assertIn("Some notes", content)

    def test_idea_template_sets_inbox_status(self):
        content = cli._idea_template("Test Idea", "2026-06-27T12:00:00")
        self.assertIn("status: inbox", content)
        self.assertIn("## Spark", content)

    def test_idea_notes_for_draft_drops_duplicate_title_heading(self):
        content = "# Test Idea\n\n## Notes\n\nA strong opening thought.\n"
        self.assertEqual(
            cli._idea_notes_for_draft("Test Idea", content), "## Notes\n\nA strong opening thought."
        )


class CliWorkflowTest(unittest.TestCase):
    def test_draft_from_idea_creates_draft_with_source_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ideas_dir = root / "ideas"
            drafts_dir = root / "drafts"
            ideas_dir.mkdir()
            drafts_dir.mkdir()

            idea_path = ideas_dir / "2026-06-27-test-idea.md"
            idea_path.write_text(
                "---\n"
                "title: Test Idea\n"
                "created: 2026-06-27T12:00:00\n"
                "status: inbox\n"
                "---\n\n"
                "# Test Idea\n\n"
                "## Notes\n\n"
                "A strong opening thought.\n"
            )

            with redirect_stdout(io.StringIO()):
                with (
                    mock.patch.object(cli, "IDEAS_DIR", ideas_dir),
                    mock.patch.object(cli, "DRAFTS_DIR", drafts_dir),
                ):
                    cli.draft_from_idea("2026-06-27-test-idea")

            draft_path = drafts_dir / "test-idea.md"
            self.assertTrue(draft_path.exists())
            content = draft_path.read_text()
            self.assertIn('idea: "ideas/2026-06-27-test-idea.md"', content)
            self.assertIn("A strong opening thought.", content)
            self.assertNotIn("# Test Idea\n\n## Notes from idea\n\n# Test Idea", content)


if __name__ == "__main__":
    unittest.main()
