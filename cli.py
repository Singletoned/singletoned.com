#!/usr/bin/env python3
"""Blog CLI with shell completion for draft names."""

import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

import frontmatter
import typer

app = typer.Typer(help="Blog management CLI")


def complete_drafts() -> list[str]:
    """Return list of draft names for completion."""
    drafts_dir = Path("drafts")
    if not drafts_dir.exists():
        return []
    return [f.stem for f in drafts_dir.glob("*.md")]


@app.command()
def build():
    """Build the static site."""
    from build import BlogBuilder

    builder = BlogBuilder()
    builder.build()


@app.command()
def dev():
    """Start development server with live reload."""
    subprocess.run([sys.executable, "scripts/dev.py"])


@app.command()
def new(title: str = typer.Argument(..., help="Title for the new draft")):
    """Create a new draft article."""
    if not title:
        print('Usage: blog new "<title>"')
        raise typer.Exit(1)

    # Create filename from title
    filename = re.sub(r"[^a-z0-9\s]", "", title.lower())
    filename = re.sub(r"\s+", "-", filename) + ".md"

    drafts_dir = Path("drafts")
    draft_path = drafts_dir / filename

    if draft_path.exists():
        print(f"Draft already exists: {filename}")
        raise typer.Exit(1)

    content = f"""---
title: {title}
excerpt: ""
---

# {title}

Write your article here..."""

    drafts_dir.mkdir(exist_ok=True)
    draft_path.write_text(content)

    print(f"Created new draft: {filename}")
    print(f"Edit it in: drafts/{filename}")
    print(f"When ready, publish with: blog publish {draft_path.stem}")


@app.command()
def publish(
    draft: str = typer.Argument(..., help="Draft name to publish", autocompletion=complete_drafts),
):
    """Publish a draft article (moves from drafts/ to posts/ with metadata)."""
    filename = draft
    if not filename.endswith(".md"):
        filename += ".md"

    draft_path = Path("drafts") / filename
    post_path = Path("posts") / filename

    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        drafts_dir = Path("drafts")
        if drafts_dir.exists():
            for d in drafts_dir.glob("*.md"):
                print(f"  - {d.stem}")
        raise typer.Exit(1)

    post = frontmatter.load(draft_path)

    # Set publication date if not present
    if "date" not in post.metadata:
        post.metadata["date"] = date.today().isoformat()

    # Ensure title exists
    if "title" not in post.metadata:
        post.metadata["title"] = draft_path.stem.replace("-", " ").title()

    # Ensure excerpt exists
    if "excerpt" not in post.metadata:
        post.metadata["excerpt"] = ""

    # Write to posts directory
    post_path.parent.mkdir(exist_ok=True)
    with open(post_path, "wb") as f:
        frontmatter.dump(post, f)

    draft_path.unlink()

    print(f"Published: {filename}")
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
    # Find the draft file
    draft_path = Path("drafts") / f"{draft}.md"
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        drafts_dir = Path("drafts")
        if drafts_dir.exists():
            for d in drafts_dir.glob("*.md"):
                print(f"  - {d.stem}")
        raise typer.Exit(1)

    # Create image directory for this post
    image_dir = Path("static") / draft
    image_dir.mkdir(parents=True, exist_ok=True)

    # Get file extension and destination path
    ext = _get_image_extension(source)
    sanitized_name = _sanitize_filename(name)
    image_path = image_dir / f"{sanitized_name}{ext}"

    # Copy or download the image
    if _is_url(source):
        print(f"Downloading image from: {source}")
        try:
            urllib.request.urlretrieve(source, image_path)
        except Exception as e:
            print(f"Failed to download image: {e}")
            raise typer.Exit(1)
    else:
        source_path = Path(source).expanduser()
        if not source_path.exists():
            print(f"File not found: {source_path}")
            raise typer.Exit(1)
        print(f"Copying image from: {source_path}")
        shutil.copy2(source_path, image_path)

    # Read the draft content
    content = draft_path.read_text()

    # Create markdown link
    relative_image_path = f"{draft}/{sanitized_name}{ext}"
    markdown_link = f"![{name}]({relative_image_path})"

    # Add the image link to the end of the content
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
    """Test internal links after building."""
    build()
    subprocess.run([sys.executable, "tests/link_checker.py"], check=True)


@app.command()
def check():
    """Build and test - useful before deployment."""
    test()


@app.command()
def format():
    """Format code using ruff."""
    subprocess.run(["ruff", "format", "."])
    subprocess.run(["ruff", "check", "--fix", "."])


@app.command()
def lint():
    """Lint code using ruff."""
    subprocess.run(["ruff", "check", "."])


@app.command()
def deploy():
    """Deploy the site (placeholder - implement your deployment)."""
    print("Deploy command not yet implemented.")
    print("Add your deployment logic here (e.g., rsync, aws s3 sync, etc.)")


if __name__ == "__main__":
    app()
