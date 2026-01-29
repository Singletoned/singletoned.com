#!/usr/bin/env python3
"""Publish a draft article by moving it to posts/ with metadata."""

import sys
from datetime import date
from pathlib import Path

import frontmatter


def publish_draft(filename: str):
    if not filename:
        print("Usage: python scripts/publish.py <filename>")
        print("Example: python scripts/publish.py my-article")
        sys.exit(1)

    if not filename.endswith(".md"):
        filename += ".md"

    draft_path = Path("drafts") / filename
    post_path = Path("posts") / filename

    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        sys.exit(1)

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


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    publish_draft(filename)
