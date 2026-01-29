#!/usr/bin/env python3
"""Development server with auto-rebuild and browser refresh."""

import sys
from pathlib import Path

from livereload import Server

sys.path.insert(0, str(Path(__file__).parent.parent))
from build import BlogBuilder


def rebuild():
    builder = BlogBuilder()
    builder.build()


def main():
    # Initial build
    rebuild()

    server = Server()

    # Watch source files and rebuild on changes
    server.watch("posts/*.md", rebuild)
    server.watch("pages/*.md", rebuild)
    server.watch("templates/*.html", rebuild)
    server.watch("static/**/*", rebuild)

    print("Development server starting...")
    server.serve(root="public", port=3000, open_url_delay=None)


if __name__ == "__main__":
    main()
