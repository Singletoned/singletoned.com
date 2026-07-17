#!/usr/bin/env python3
"""Unit tests for blog CLI helpers."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import cli


class CliHelpersTest(unittest.TestCase):
    def test_slugify_normalises_title(self):
        self.assertEqual(cli._slugify("  Hello, World!!  "), "hello-world")

    def test_find_instruction_placeholders_returns_all_placeholders(self):
        content = "Intro {{link: Slashdot}} middle {{insert: a summary}} end"
        self.assertEqual(
            cli._find_instruction_placeholders(content),
            ["{{link: Slashdot}}", "{{insert: a summary}}"],
        )

    def test_draft_template_includes_idea_source_when_present(self):
        content = cli._draft_template("Test Title", "ideas/2026-06-27-test.md", "Some notes")
        self.assertIn('idea: "ideas/2026-06-27-test.md"', content)
        self.assertIn("## Notes from idea", content)
        self.assertIn("Some notes", content)

    def test_idea_template_sets_inbox_status(self):
        content = cli._idea_template("Test Idea", "2026-06-27T12:00:00")
        self.assertIn("status: inbox", content)
        self.assertIn("## Spark", content)

    def test_find_matching_idea_paths_matches_slug_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            ideas_dir = Path(temp_dir)
            idea_path = ideas_dir / "2026-06-27-second-post.md"
            idea_path.write_text("placeholder")

            with mock.patch.object(cli, "IDEAS_DIR", ideas_dir):
                matches = cli._find_matching_idea_paths("Second Post")

            self.assertEqual(matches, [idea_path])

    def test_idea_notes_for_draft_drops_duplicate_title_heading(self):
        content = "# Test Idea\n\n## Notes\n\nA strong opening thought.\n"
        self.assertEqual(
            cli._idea_notes_for_draft("Test Idea", content), "## Notes\n\nA strong opening thought."
        )

    def test_derive_excerpt_uses_first_sentence_from_first_body_paragraph(self):
        content = (
            "# Test Post\n\n"
            "This is the first sentence. Here is another sentence.\n\n"
            "A later paragraph.\n"
        )
        self.assertEqual(cli._derive_excerpt(content), "This is the first sentence.")

    def test_derive_excerpt_strips_markdown_links(self):
        content = "Read [Simon Willison](https://simonwillison.net/) for more.\n"
        self.assertEqual(cli._derive_excerpt(content), "Read Simon Willison for more.")


class CliWorkflowTest(unittest.TestCase):
    def test_process_draft_with_pi_returns_zero_when_no_placeholders_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            draft_path = Path(temp_dir) / "draft.md"
            draft_path.write_text("# Title\n\nNo instructions here.\n")

            with mock.patch.object(cli, "_run_pi_processing_prompt") as run_pi:
                resolved_count = cli._process_draft_with_pi(draft_path)

            self.assertEqual(resolved_count, 0)
            run_pi.assert_not_called()

    def test_process_draft_with_pi_runs_pi_and_rechecks_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            draft_path = Path(temp_dir) / "draft.md"
            draft_path.write_text("Before {{link: Slashdot}} after\n")

            def fake_run(path):
                self.assertEqual(path, draft_path)
                draft_path.write_text("Before [Slashdot](https://slashdot.org/) after\n")

            with mock.patch.object(cli, "_run_pi_processing_prompt", side_effect=fake_run):
                with mock.patch("cli.shutil.which", return_value="/usr/bin/pi"):
                    resolved_count = cli._process_draft_with_pi(draft_path)

            self.assertEqual(resolved_count, 1)
            self.assertIn("[Slashdot](https://slashdot.org/)", draft_path.read_text())

    def test_process_draft_with_pi_fails_if_placeholders_remain(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            draft_path = Path(temp_dir) / "draft.md"
            draft_path.write_text("Before {{link: Slashdot}} after\n")

            with mock.patch.object(cli, "_run_pi_processing_prompt"):
                with mock.patch("cli.shutil.which", return_value="/usr/bin/pi"):
                    with self.assertRaisesRegex(
                        RuntimeError, "Unresolved draft instructions remain"
                    ):
                        cli._process_draft_with_pi(draft_path)

    def test_ensure_tags_with_pi_returns_zero_when_tags_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            draft_path = Path(temp_dir) / "draft.md"
            draft_path.write_text("---\ntitle: Tagged\ntags: [ai, nostalgia]\n---\n\nBody\n")

            with mock.patch.object(cli, "_run_pi_tag_prompt") as run_pi:
                tag_count = cli._ensure_tags_with_pi(draft_path)

            self.assertEqual(tag_count, 0)
            run_pi.assert_not_called()

    def test_ensure_tags_with_pi_adds_tags_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            draft_path = Path(temp_dir) / "draft.md"
            draft_path.write_text("---\ntitle: Tagged\n---\n\nBody\n")

            def fake_run(path):
                self.assertEqual(path, draft_path)
                draft_path.write_text("---\ntitle: Tagged\ntags: [ai, writing]\n---\n\nBody\n")

            with mock.patch.object(cli, "_run_pi_tag_prompt", side_effect=fake_run):
                with mock.patch("cli.shutil.which", return_value="/usr/bin/pi"):
                    tag_count = cli._ensure_tags_with_pi(draft_path)

            self.assertEqual(tag_count, 2)
            self.assertIn("tags: [ai, writing]", draft_path.read_text())

    def test_publish_processes_draft_before_writing_post(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            drafts_dir = root / "drafts"
            posts_dir = root / "posts"
            drafts_dir.mkdir()
            posts_dir.mkdir()
            draft_path = drafts_dir / "test-post.md"
            draft_path.write_text("---\ntitle: Test Post\n---\n\nBody with {{link: Slashdot}}\n")

            def fake_process(path):
                self.assertEqual(path, draft_path)
                draft_path.write_text(
                    "---\n"
                    "title: Test Post\n"
                    "date: 2026-07-17\n"
                    "tags: [ai, blogging]\n"
                    "---\n\n"
                    "Body with [Slashdot](https://slashdot.org/)\n"
                )
                return 1

            original_cwd = Path.cwd()
            os.chdir(root)
            try:
                with redirect_stdout(io.StringIO()):
                    with mock.patch.object(cli, "DRAFTS_DIR", drafts_dir):
                        with mock.patch.object(
                            cli, "_process_draft_with_pi", side_effect=fake_process
                        ):
                            with mock.patch.object(cli, "_ensure_tags_with_pi", return_value=2):
                                cli.publish("test-post")
            finally:
                os.chdir(original_cwd)

            post_path = posts_dir / "test-post.md"
            self.assertTrue(post_path.exists())
            self.assertFalse(draft_path.exists())
            post_content = post_path.read_text()
            self.assertIn("[Slashdot](https://slashdot.org/)", post_content)
            self.assertIn("excerpt: Body with Slashdot", post_content)
            self.assertIn("tags:", post_content)

    def test_ensure_clean_working_tree_fails_with_uncommitted_changes(self):
        with mock.patch.object(cli, "_command_output", return_value=" M cli.py\n"):
            with self.assertRaisesRegex(RuntimeError, "Refusing to deploy"):
                cli._ensure_clean_working_tree()

    def test_deploy_runs_check_then_pushes_and_waits(self):
        with mock.patch.object(cli, "_ensure_clean_working_tree") as ensure_clean:
            with mock.patch.object(cli, "check") as check_command:
                with mock.patch.object(cli, "_command_output", return_value="abc123\n"):
                    with mock.patch("cli.subprocess.run") as run_command:
                        with mock.patch.object(
                            cli, "_linked_netlify_site_id", return_value="site-123"
                        ):
                            with mock.patch.object(
                                cli, "_wait_for_netlify_deploy"
                            ) as wait_for_deploy:
                                with redirect_stdout(io.StringIO()):
                                    cli.deploy()

        ensure_clean.assert_called_once_with()
        check_command.assert_called_once_with()
        run_command.assert_called_once_with(["git", "push", "origin", "HEAD:main"], check=True)
        wait_for_deploy.assert_called_once_with("site-123", "abc123")

    def test_idea_command_prints_exact_follow_up_command(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ideas_dir = root / "ideas"
            output = io.StringIO()

            with redirect_stdout(output):
                with mock.patch.object(cli, "IDEAS_DIR", ideas_dir):
                    cli.idea("Second Post")

            self.assertIn("blog draft-from-idea 2026-", output.getvalue())
            self.assertIn('blog draft-from-idea "Second Post"', output.getvalue())

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
