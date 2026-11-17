#!/usr/bin/env python3
"""Check for broken internal links in the generated site."""

import sys
from pathlib import Path

from bs4 import BeautifulSoup


class LinkChecker:
    def __init__(self):
        self.public_dir = Path("public")
        self.errors = []
        self.checked_pages = set()

    def check_links(self):
        print("Checking internal links...")

        if not self.public_dir.exists():
            print('Public directory not found. Run "mate build" first.')
            sys.exit(1)

        html_files = list(self.public_dir.glob("**/*.html"))
        if not html_files:
            print("No HTML files found in public directory.")
            sys.exit(1)

        print(f"Found {len(html_files)} HTML files to check")

        for html_file in html_files:
            self.check_file(html_file)

        self.report_results()

    def check_file(self, file_path: Path):
        content = file_path.read_text()
        soup = BeautifulSoup(content, "html.parser")
        relative_path = file_path.relative_to(self.public_dir)

        print(f"Checking: {relative_path}")
        self.checked_pages.add(str(relative_path))

        # Check all links
        for link in soup.find_all("a", href=True):
            self.check_link(link["href"], str(relative_path), link.get_text(strip=True))

        # Check CSS links
        for link in soup.find_all("link", rel="stylesheet", href=True):
            self.check_asset(link["href"], str(relative_path), "CSS")

        # Check script sources
        for script in soup.find_all("script", src=True):
            self.check_asset(script["src"], str(relative_path), "JavaScript")

        # Check images
        for img in soup.find_all("img", src=True):
            self.check_asset(img["src"], str(relative_path), "Image")

    def is_external(self, url: str) -> bool:
        return bool(url.startswith(("http://", "https://", "mailto:", "tel:", "//")))

    def resolve_path(self, url: str, from_page: str) -> str:
        """Resolve a URL relative to the page it's on."""
        url = url.split("#")[0]  # Remove fragment
        if not url or url == "/":
            return "index.html"
        if url.endswith("/"):
            url += "index.html"
        if url.startswith("/"):
            return url.lstrip("/")
        # Relative path - resolve from the page's directory
        return str((Path(from_page).parent / url).as_posix())

    def check_link(self, href: str, from_page: str, link_text: str):
        if self.is_external(href):
            return
        if href.startswith("#"):
            return

        target_path = self.resolve_path(href, from_page)

        if not Path(target_path).suffix:
            target_path += ".html"

        full_path = self.public_dir / target_path
        if not full_path.exists():
            self.errors.append(
                f'Broken link in {from_page}: "{href}" -> {target_path} (text: "{link_text}")'
            )

    def check_asset(self, src: str, from_page: str, asset_type: str):
        if self.is_external(src):
            return

        target_path = self.resolve_path(src, from_page)
        full_path = self.public_dir / target_path
        if not full_path.exists():
            self.errors.append(f'Missing {asset_type} in {from_page}: "{src}" -> {target_path}')

    def report_results(self):
        print("\nLink Check Results:")
        print(f"Pages checked: {len(self.checked_pages)}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
            print(f"\nTotal errors: {len(self.errors)}")
            sys.exit(1)
        else:
            print("\nAll internal links are working correctly!")


if __name__ == "__main__":
    checker = LinkChecker()
    checker.check_links()
