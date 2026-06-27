#!/usr/bin/env python3
"""Build the static blog site."""

import re
import shutil
from datetime import date
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader

SITE_TITLE = "Ed Singleton"
SITE_URL = "https://singletoned.com"


class BlogBuilder:
    def __init__(self):
        self.posts_dir = Path("posts")
        self.pages_dir = Path("pages")
        self.templates_dir = Path("templates")
        self.output_dir = Path("public")
        self.static_dir = Path("static")

        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self.md = markdown.Markdown(extensions=["extra", "meta", "toc"])

    def build(self):
        print("Building site...")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.copy_static()
        posts = self.build_posts()
        self.build_pages()
        self.build_index(posts)

        print("Site built successfully!")

    def copy_static(self):
        if not self.static_dir.exists():
            return
        for item in self.static_dir.iterdir():
            dest = self.output_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    def render_markdown(self, text):
        """Render markdown with external links opening in new tabs."""
        self.md.reset()
        html = self.md.convert(text)
        # Add target="_blank" and rel="noopener noreferrer" to external links
        html = re.sub(
            r'<a href="(https?://[^"]+)"',
            r'<a href="\1" target="_blank" rel="noopener noreferrer"',
            html,
        )
        return html

    def calculate_reading_time(self, text):
        """Calculate reading time based on ~200 words per minute."""
        words = len(text.split())
        minutes = max(1, round(words / 200))
        return f"{minutes} min read"

    def build_posts(self):
        posts = []
        if not self.posts_dir.exists():
            return posts

        for post_file in sorted(self.posts_dir.glob("*.md")):
            post = frontmatter.load(post_file)
            post_data = {
                **post.metadata,
                "content": self.render_markdown(post.content),
                "slug": post_file.stem,
                "reading_time": self.calculate_reading_time(post.content),
            }

            template = self.env.get_template("article.html")
            html = template.render(
                post=post_data,
                title=post_data.get("title"),
                current_year=date.today().year,
                site_title=SITE_TITLE,
                site_url=SITE_URL,
            )
            output_path = self.output_dir / f"{post_data['slug']}.html"
            output_path.write_text(html)

            posts.append(post_data)

        # Sort by date, newest first (convert to string to handle mixed types)
        posts.sort(key=lambda p: str(p.get("date", "")), reverse=True)
        return posts

    def build_pages(self):
        if not self.pages_dir.exists():
            return

        for page_file in self.pages_dir.glob("*.md"):
            page = frontmatter.load(page_file)
            page_data = {
                **page.metadata,
                "content": self.render_markdown(page.content),
                "slug": page_file.stem,
            }

            template = self.env.get_template("page.html")
            html = template.render(
                page=page_data,
                title=page_data.get("title"),
                current_year=date.today().year,
                site_title=SITE_TITLE,
                site_url=SITE_URL,
            )
            output_path = self.output_dir / f"{page_data['slug']}.html"
            output_path.write_text(html)

    def build_index(self, posts):
        template = self.env.get_template("index.html")
        html = template.render(
            posts=posts,
            current_year=date.today().year,
            site_title=SITE_TITLE,
            site_url=SITE_URL,
        )
        output_path = self.output_dir / "index.html"
        output_path.write_text(html)


if __name__ == "__main__":
    builder = BlogBuilder()
    builder.build()
