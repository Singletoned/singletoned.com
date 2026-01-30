#!/usr/bin/env python3
"""Add an image to a draft post from a URL or local file."""

import re
import shutil
import sys
import urllib.request
from pathlib import Path


def get_image_extension(source: str) -> str:
    """Extract image extension from path or URL, defaulting to .jpg."""
    ext = Path(source).suffix.lower()
    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    return ext if ext in valid_exts else ".jpg"


def sanitize_filename(filename: str) -> str:
    """Convert filename to lowercase with only alphanumeric and hyphens."""
    result = re.sub(r"[^a-z0-9-]", "-", filename.lower())
    result = re.sub(r"-+", "-", result)
    return result.strip("-")


def is_url(source: str) -> bool:
    """Check if source is a URL."""
    return source.startswith(("http://", "https://"))


def add_image_to_post(post_name: str, image_name: str, source: str):
    if not post_name or not image_name or not source:
        print('Usage: python scripts/add_image.py "<post-name>" "<image-name>" "<url-or-path>"')
        print("Examples:")
        print('  python scripts/add_image.py "my-post" "hero" "https://example.com/image.jpg"')
        print('  python scripts/add_image.py "my-post" "hero" "/path/to/local/image.png"')
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

    # Get file extension and destination path
    ext = get_image_extension(source)
    sanitized_name = sanitize_filename(image_name)
    image_path = image_dir / f"{sanitized_name}{ext}"

    # Copy or download the image
    if is_url(source):
        print(f"Downloading image from: {source}")
        try:
            urllib.request.urlretrieve(source, image_path)
        except Exception as e:
            print(f"Failed to download image: {e}")
            sys.exit(1)
    else:
        source_path = Path(source).expanduser()
        if not source_path.exists():
            print(f"File not found: {source_path}")
            sys.exit(1)
        print(f"Copying image from: {source_path}")
        shutil.copy2(source_path, image_path)

    # Read the draft content
    content = draft_path.read_text()

    # Create markdown link
    relative_image_path = f"{post_name}/{sanitized_name}{ext}"
    markdown_link = f"![{image_name}]({relative_image_path})"

    # Add the image link to the end of the content
    updated_content = content.strip() + "\n\n" + markdown_link + "\n"
    draft_path.write_text(updated_content)

    print("Image added to draft:")
    print(f"   Saved to: {image_path}")
    print(f"   Added to: {draft_path}")
    print(f"   Markdown: {markdown_link}")


if __name__ == "__main__":
    args = sys.argv[1:]
    post_name = args[0] if len(args) > 0 else ""
    image_name = args[1] if len(args) > 1 else ""
    source = args[2] if len(args) > 2 else ""
    add_image_to_post(post_name, image_name, source)
