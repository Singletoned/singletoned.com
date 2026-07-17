#!/usr/bin/env python3
"""Blog CLI with shell completion for draft and idea names."""

import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

import frontmatter
import typer

DRAFTS_DIR = Path("drafts")
IDEAS_DIR = Path("ideas")
TEST_PATTERN = "test_*.py"
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")
PI_PROCESS_PROMPT = (
    "Process the draft article at {draft_path} in place. "
    "Resolve every authoring-time placeholder of the form {{{{command: instruction}}}}. "
    "Replace {{{{link: ...}}}} placeholders with the correct Markdown links. "
    "Replace {{{{insert: ...}}}} placeholders with suitable content, and clearly mark any "
    "AI-generated prose using the site's documented HTML pattern for AI-generated content. "
    "Preserve the existing frontmatter and all unrelated writing. "
    "Do not leave any {{{{...}}}} placeholders unresolved. "
    "If you cannot complete the task confidently, do not make partial changes; explain "
    "the problem instead."
)
PI_TAG_PROMPT = (
    "Update the draft article at {draft_path} in place. "
    "If the frontmatter already has a non-empty tags field, leave the file unchanged. "
    "Otherwise add a tags field in frontmatter with 2 to 4 short lowercase category tags "
    "that fit the article, using simple slug-like names such as ai, nostalgia, writing, or "
    "football-data. Preserve all existing prose and frontmatter fields. Do not add any "
    "explanatory text outside the file."
)
PI_COMMAND = "pi"
NETLIFY_COMMAND = "netlify"
GIT_REMOTE = "origin"
PRODUCTION_BRANCH = "main"
NETLIFY_DEPLOY_TIMEOUT_SECONDS = 300
NETLIFY_POLL_INTERVAL_SECONDS = 5

app = typer.Typer(help="Blog management CLI")


def _list_markdown_stems(directory: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(file.stem for file in directory.glob("*.md"))


def _slugify(value: str) -> str:
    result = re.sub(r"[^a-z0-9\s-]", "", value.lower())
    result = re.sub(r"\s+", "-", result)
    result = re.sub(r"-+", "-", result)
    return result.strip("-")


def _draft_path(name: str) -> Path:
    filename = name if name.endswith(".md") else f"{name}.md"
    return DRAFTS_DIR / filename


def _idea_path(name: str) -> Path:
    filename = name if name.endswith(".md") else f"{name}.md"
    return IDEAS_DIR / filename


def _draft_template(title: str, idea_source: str | None = None, notes: str = "") -> str:
    source_line = f'idea: "{idea_source}"\n' if idea_source else ""
    notes_block = f"\n## Notes from idea\n\n{notes.strip()}\n" if notes.strip() else ""
    return f"""---
title: {title}
excerpt: ""
{source_line}---

# {title}
{notes_block}
Write your article here...
"""


def _idea_notes_for_draft(title: str, content: str) -> str:
    lines = content.strip().splitlines()
    heading = f"# {title}"
    if lines and lines[0].strip() == heading:
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def _idea_template(title: str, created_at: str) -> str:
    return f"""---
title: {title}
created: {created_at}
status: inbox
---

# {title}

## Spark

## Notes

## Possible directions

## Next step
"""


def _strip_markdown_links(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)


def _first_sentence(text: str) -> str:
    match = re.search(r"(.+?[.!?])(?:\s|$)", text.strip(), re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _derive_excerpt(content: str) -> str:
    for block in content.split("\n\n"):
        stripped = block.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<"):
            continue
        excerpt = _strip_markdown_links(stripped)
        excerpt = re.sub(r"`([^`]+)`", r"\1", excerpt)
        excerpt = re.sub(r"\s+", " ", excerpt)
        return _first_sentence(excerpt)
    return ""


def _find_matching_idea_paths(idea_name: str) -> list[Path]:
    direct_path = _idea_path(idea_name)
    if direct_path.exists():
        return [direct_path]

    slug = _slugify(idea_name)
    if not slug or not IDEAS_DIR.exists():
        return []

    matches = []
    for path in sorted(IDEAS_DIR.glob("*.md")):
        stem = path.stem
        if stem == slug or stem.endswith(f"-{slug}"):
            matches.append(path)
    return matches


def _load_idea(idea_name: str):
    matches = _find_matching_idea_paths(idea_name)
    if len(matches) == 1:
        idea_path = matches[0]
        return idea_path, frontmatter.load(idea_path)

    if len(matches) > 1:
        print(f"Idea name is ambiguous: {idea_name}")
        print("Matching ideas:")
        for match in matches:
            print(f"  - {match.stem}")
        print("Use the full idea name shown above.")
        raise typer.Exit(1)

    print(f'Idea not found for input: "{idea_name}"')
    print("Available ideas:")
    for idea in _list_markdown_stems(IDEAS_DIR):
        print(f"  - {idea}")
    raise typer.Exit(1)


def _find_instruction_placeholders(content: str) -> list[str]:
    return PLACEHOLDER_PATTERN.findall(content)


def _run_pi_processing_prompt(draft_path: Path):
    subprocess.run(
        [
            PI_COMMAND,
            "--approve",
            "--no-session",
            "-p",
            PI_PROCESS_PROMPT.format(draft_path=draft_path.as_posix()),
        ],
        check=True,
    )


def _process_draft_with_pi(draft_path: Path) -> int:
    content = draft_path.read_text()
    placeholders = _find_instruction_placeholders(content)
    if not placeholders:
        return 0

    if shutil.which(PI_COMMAND) is None:
        raise RuntimeError("pi command not found in PATH")

    _run_pi_processing_prompt(draft_path)

    remaining = _find_instruction_placeholders(draft_path.read_text())
    if remaining:
        placeholders_text = ", ".join(remaining)
        raise RuntimeError(
            f"Unresolved draft instructions remain in {draft_path}: {placeholders_text}"
        )

    return len(placeholders)


def _run_pi_tag_prompt(draft_path: Path):
    subprocess.run(
        [
            PI_COMMAND,
            "--approve",
            "--no-session",
            "-p",
            PI_TAG_PROMPT.format(draft_path=draft_path.as_posix()),
        ],
        check=True,
    )


def _ensure_tags_with_pi(draft_path: Path) -> int:
    post = frontmatter.load(draft_path)
    if post.metadata.get("tags"):
        return 0

    if shutil.which(PI_COMMAND) is None:
        raise RuntimeError("pi command not found in PATH")

    _run_pi_tag_prompt(draft_path)

    updated_post = frontmatter.load(draft_path)
    if not updated_post.metadata.get("tags"):
        raise RuntimeError(f"Missing tags after processing {draft_path}")

    return len(updated_post.metadata["tags"])


def complete_drafts() -> list[str]:
    """Return list of draft names for completion."""
    return _list_markdown_stems(DRAFTS_DIR)


def complete_ideas() -> list[str]:
    """Return list of idea names for completion."""
    return _list_markdown_stems(IDEAS_DIR)


def _command_output(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def _ensure_clean_working_tree():
    status = _command_output(["git", "status", "--short"]).strip()
    if status:
        raise RuntimeError(f"Refusing to deploy with uncommitted changes:\n{status}")


def _linked_netlify_site_id() -> str | None:
    if shutil.which(NETLIFY_COMMAND) is None:
        return None

    status = json.loads(_command_output([NETLIFY_COMMAND, "status", "--json"]))
    site_data = status.get("siteData", {})
    return site_data.get("site-id")


def _latest_netlify_deploy_for_commit(site_id: str, commit_sha: str):
    deploys = json.loads(
        _command_output(
            [
                NETLIFY_COMMAND,
                "api",
                "listSiteDeploys",
                "--data",
                json.dumps({"site_id": site_id, "page": 1, "per_page": 20}),
            ]
        )
    )
    for deploy in deploys:
        if deploy.get("commit_ref") == commit_sha:
            return deploy
    return None


def _wait_for_netlify_deploy(site_id: str, commit_sha: str):
    deadline = time.monotonic() + NETLIFY_DEPLOY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        deploy = _latest_netlify_deploy_for_commit(site_id, commit_sha)
        if deploy is None:
            time.sleep(NETLIFY_POLL_INTERVAL_SECONDS)
            continue

        state = deploy.get("state")
        if state == "ready":
            print(f"Netlify deploy ready: {deploy.get('ssl_url')}")
            print(f"Unique deploy URL: {deploy.get('deploy_ssl_url')}")
            return

        if state == "error":
            message = deploy.get("error_message") or "unknown Netlify deploy error"
            raise RuntimeError(f"Netlify deploy failed for {commit_sha}: {message}")

        time.sleep(NETLIFY_POLL_INTERVAL_SECONDS)

    raise RuntimeError(f"Timed out waiting for Netlify deploy for {commit_sha}")


@app.command()
def build():
    """Build the static site."""
    from build import BlogBuilder

    builder = BlogBuilder()
    builder.build()


@app.command()
def dev():
    """Start development server with live reload."""
    subprocess.run([sys.executable, "scripts/dev.py"], check=True)


@app.command()
def new(title: str = typer.Argument(..., help="Title for the new draft")):
    """Create a new draft article."""
    slug = _slugify(title)
    if not slug:
        print('Usage: blog new "<title>"')
        raise typer.Exit(1)

    draft_path = _draft_path(slug)
    if draft_path.exists():
        print(f"Draft already exists: {draft_path.name}")
        raise typer.Exit(1)

    DRAFTS_DIR.mkdir(exist_ok=True)
    draft_path.write_text(_draft_template(title))

    print(f"Created new draft: {draft_path.name}")
    print(f"Edit it in: {draft_path}")
    print(f"When ready, publish with: blog publish {draft_path.stem}")


@app.command()
def idea(title: str = typer.Argument(..., help="Short title for the idea")):
    """Capture a new idea in the inbox."""
    slug = _slugify(title)
    if not slug:
        print('Usage: blog idea "<title>"')
        raise typer.Exit(1)

    created_at = datetime.now().replace(microsecond=0).isoformat()
    filename = f"{created_at[:10]}-{slug}.md"
    idea_path = _idea_path(filename)

    if idea_path.exists():
        print(f"Idea already exists: {idea_path.name}")
        raise typer.Exit(1)

    IDEAS_DIR.mkdir(exist_ok=True)
    idea_path.write_text(_idea_template(title, created_at))

    print(f"Captured idea: {idea_path.name}")
    print(f"Edit it in: {idea_path}")
    print(f"When it deserves a draft, run: blog draft-from-idea {idea_path.stem}")
    print(f'Or use the title if it is unique: blog draft-from-idea "{title}"')


@app.command()
def ideas():
    """List captured ideas."""
    names = _list_markdown_stems(IDEAS_DIR)
    if not names:
        print("No ideas captured yet.")
        return

    print("Ideas:")
    for name in names:
        print(f"  - {name}")


@app.command("draft-from-idea")
def draft_from_idea(
    idea_name: str = typer.Argument(..., help="Idea name", autocompletion=complete_ideas),
):
    """Create a draft from an existing idea note."""
    idea_path, idea_post = _load_idea(idea_name)
    title = idea_post.metadata.get("title") or idea_path.stem.replace("-", " ").title()
    draft_slug = _slugify(title)
    draft_path = _draft_path(draft_slug)

    if draft_path.exists():
        print(f"Draft already exists: {draft_path.name}")
        raise typer.Exit(1)

    DRAFTS_DIR.mkdir(exist_ok=True)
    idea_reference = idea_path.relative_to(IDEAS_DIR.parent).as_posix()
    idea_notes = _idea_notes_for_draft(title, idea_post.content)
    draft_path.write_text(_draft_template(title, idea_reference, idea_notes))

    print(f"Created draft: {draft_path.name}")
    print(f"Source idea: {idea_path}")
    print(f"Edit it in: {draft_path}")


@app.command()
def process(
    draft: str = typer.Argument(..., help="Draft name to process", autocompletion=complete_drafts),
):
    """Resolve AI instruction placeholders in a draft in place."""
    draft_path = _draft_path(draft)
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        for name in _list_markdown_stems(DRAFTS_DIR):
            print(f"  - {name}")
        raise typer.Exit(1)

    print(f"Processing draft instructions in: {draft_path}")
    resolved_count = _process_draft_with_pi(draft_path)
    if resolved_count == 0:
        print("No draft instructions found.")
        return

    print(f"Resolved {resolved_count} draft instruction(s).")


@app.command()
def publish(
    draft: str = typer.Argument(..., help="Draft name to publish", autocompletion=complete_drafts),
):
    """Process and publish a draft article."""
    draft_path = _draft_path(draft)
    post_path = Path("posts") / draft_path.name

    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        for name in _list_markdown_stems(DRAFTS_DIR):
            print(f"  - {name}")
        raise typer.Exit(1)

    resolved_count = _process_draft_with_pi(draft_path)
    if resolved_count:
        print(f"Resolved {resolved_count} draft instruction(s) before publishing.")

    added_tag_count = _ensure_tags_with_pi(draft_path)
    if added_tag_count:
        print(f"Added {added_tag_count} tag(s) before publishing.")

    post = frontmatter.load(draft_path)

    if "date" not in post.metadata:
        post.metadata["date"] = date.today().isoformat()
    if "title" not in post.metadata:
        post.metadata["title"] = draft_path.stem.replace("-", " ").title()
    if not post.metadata.get("excerpt"):
        post.metadata["excerpt"] = _derive_excerpt(post.content)

    post_path.parent.mkdir(exist_ok=True)
    with open(post_path, "wb") as file_handle:
        frontmatter.dump(post, file_handle)

    draft_path.unlink()

    print(f"Published: {draft_path.name}")
    print("Moved from drafts/ to posts/")
    print(f"Added publication date: {post.metadata['date']}")


def _get_image_extension(source: str) -> str:
    """Extract image extension from path or URL, defaulting to .jpg."""
    ext = Path(source).suffix.lower()
    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    return ext if ext in valid_exts else ".jpg"


def _sanitize_filename(filename: str) -> str:
    """Convert filename to lowercase with only alphanumeric and hyphens."""
    result = re.sub(r"[^a-z0-9-]", "-", filename.lower())
    result = re.sub(r"-+", "-", result)
    return result.strip("-")


def _is_url(source: str) -> bool:
    """Check if source is a URL."""
    return source.startswith(("http://", "https://"))


@app.command("add-image")
def add_image(
    draft: str = typer.Argument(..., help="Draft name", autocompletion=complete_drafts),
    name: str = typer.Argument(..., help="Image name (used in filename)"),
    source: str = typer.Argument(..., help="URL or local path to image"),
):
    """Add an image to a draft post from a URL or local file."""
    draft_path = _draft_path(draft)
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        for draft_name in _list_markdown_stems(DRAFTS_DIR):
            print(f"  - {draft_name}")
        raise typer.Exit(1)

    image_dir = Path("static") / draft_path.stem
    image_dir.mkdir(parents=True, exist_ok=True)

    ext = _get_image_extension(source)
    sanitized_name = _sanitize_filename(name)
    image_path = image_dir / f"{sanitized_name}{ext}"

    if _is_url(source):
        print(f"Downloading image from: {source}")
        try:
            urllib.request.urlretrieve(source, image_path)
        except Exception as error:
            print(f"Failed to download image: {error}")
            raise typer.Exit(1)
    else:
        source_path = Path(source).expanduser()
        if not source_path.exists():
            print(f"File not found: {source_path}")
            raise typer.Exit(1)
        print(f"Copying image from: {source_path}")
        shutil.copy2(source_path, image_path)

    content = draft_path.read_text()
    relative_image_path = f"{draft_path.stem}/{sanitized_name}{ext}"
    markdown_link = f"![{name}]({relative_image_path})"
    updated_content = content.strip() + "\n\n" + markdown_link + "\n"
    draft_path.write_text(updated_content)

    print("Image added to draft:")
    print(f"   Saved to: {image_path}")
    print(f"   Added to: {draft_path}")
    print(f"   Markdown: {markdown_link}")


@app.command()
def clean():
    """Clean generated files."""
    public_dir = Path("public")
    if public_dir.exists():
        for item in public_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        print("Cleaned public/ directory")
    else:
        print("Nothing to clean")


@app.command()
def test():
    """Run unit tests and check internal links after building."""
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", TEST_PATTERN],
        check=True,
    )
    build()
    subprocess.run([sys.executable, "tests/link_checker.py"], check=True)


@app.command()
def check():
    """Build and test - useful before deployment."""
    test()


@app.command()
def format():
    """Format code using ruff."""
    subprocess.run(["ruff", "format", "."], check=True)
    subprocess.run(["ruff", "check", "--fix", "."], check=True)


@app.command()
def lint():
    """Lint code using ruff."""
    subprocess.run(["ruff", "check", "."], check=True)


@app.command()
def deploy():
    """Build, test, push to GitHub, and wait for Netlify to deploy production."""
    _ensure_clean_working_tree()
    check()

    commit_sha = _command_output(["git", "rev-parse", "HEAD"]).strip()
    subprocess.run(["git", "push", GIT_REMOTE, f"HEAD:{PRODUCTION_BRANCH}"], check=True)
    print(f"Pushed {commit_sha[:7]} to {GIT_REMOTE}/{PRODUCTION_BRANCH}.")

    site_id = _linked_netlify_site_id()
    if site_id is None:
        print("Netlify CLI not found; wait for the GitHub-triggered deploy in Netlify.")
        return

    _wait_for_netlify_deploy(site_id, commit_sha)


if __name__ == "__main__":
    app()
