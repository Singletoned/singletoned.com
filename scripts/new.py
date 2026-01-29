#!/usr/bin/env python3
"""Create a new draft article."""

import re
import sys
from pathlib import Path


def create_new_draft(title: str):
    if not title:
        print('Usage: python scripts/new.py "<title>"')
        print('Example: python scripts/new.py "My Amazing Article"')
        sys.exit(1)

    # Create filename from title
    filename = re.sub(r"[^a-z0-9\s]", "", title.lower())
    filename = re.sub(r"\s+", "-", filename) + ".md"

    drafts_dir = Path("drafts")
    draft_path = drafts_dir / filename

    if draft_path.exists():
        print(f"Draft already exists: {filename}")
        sys.exit(1)

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
    print(f"When ready, publish with: just publish {draft_path.stem}")


if __name__ == "__main__":
    title = " ".join(sys.argv[1:])
    create_new_draft(title)
