#!/usr/bin/env python3
"""Download an image and add it to a draft post."""

import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def get_image_extension(url: str) -> str:
    """Extract image extension from URL, defaulting to .jpg."""
    parsed = urlparse(url)
    ext = Path(parsed.path).suffix.lower()
    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    return ext if ext in valid_exts else ".jpg"


def sanitize_filename(filename: str) -> str:
    """Convert filename to lowercase with only alphanumeric and hyphens."""
    result = re.sub(r"[^a-z0-9-]", "-", filename.lower())
    result = re.sub(r"-+", "-", result)
    return result.strip("-")


def add_image_to_post(post_name: str, image_name: str, image_url: str):
    if not post_name or not image_name or not image_url:
        print('Usage: python scripts/add_image.py "<post-name>" "<image-name>" "<image-url>"')
        print(
            'Example: python scripts/add_image.py "my-post" "hero-image" "https://example.com/image.jpg"'
        )
        sys.exit(1)

    # Validate URL
    try:
        urlparse(image_url)
    except Exception:
        print("Invalid URL provided")
        sys.exit(1)

    # Find the draft file
    draft_path = Path("drafts") / f"{post_name}.md"
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        print("Available drafts:")
        drafts_dir = Path("drafts")
        if drafts_dir.exists():
            for draft in drafts_dir.glob("*.md"):
                print(f"  - {draft.stem}")
        sys.exit(1)

    # Create image directory for this post
    image_dir = Path("static") / post_name
    image_dir.mkdir(parents=True, exist_ok=True)

    # Get file extension from URL
    ext = get_image_extension(image_url)
    sanitized_name = sanitize_filename(image_name)
    image_path = image_dir / f"{sanitized_name}{ext}"

    # Download the image
    print(f"Downloading image from: {image_url}")
    try:
        urllib.request.urlretrieve(image_url, image_path)
    except Exception as e:
        print(f"Failed to download image: {e}")
        sys.exit(1)

    # Read the draft content
    content = draft_path.read_text()

    # Create markdown link
    relative_image_path = f"{post_name}/{sanitized_name}{ext}"
    markdown_link = f"![{image_name}]({relative_image_path})"

    # Add the image link to the end of the content
    updated_content = content.strip() + "\n\n" + markdown_link + "\n"
    draft_path.write_text(updated_content)

    print("Image downloaded and added to draft:")
    print(f"   Saved to: {image_path}")
    print(f"   Added to: {draft_path}")
    print(f"   Markdown: {markdown_link}")


if __name__ == "__main__":
    args = sys.argv[1:]
    post_name = args[0] if len(args) > 0 else ""
    image_name = args[1] if len(args) > 1 else ""
    image_url = args[2] if len(args) > 2 else ""
    add_image_to_post(post_name, image_name, image_url)
