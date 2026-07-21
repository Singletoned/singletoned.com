# Repository Guidelines

## Project Structure & Module Organization

This repository builds a simple static blog. Core Python code lives in `build.py` and `cli.py`; the `blog` console command is defined in `pyproject.toml`. Content is split between `posts/` for published articles, `pages/` for standalone pages, and optional `drafts/` files created by the CLI. Jinja templates live in `templates/`, source assets live in `static/`, and generated site output is written to `public/`. Link validation lives in `tests/link_checker.py`.

## Build, Test, and Development Commands

Use `mate` targets:

- `mate install` installs the package in editable mode with `uv pip install -e .`.
- `mate build` renders Markdown, templates, and static assets into `public/`.
- `mate dev` starts the live-reload development server.
- `mate test` builds the site and runs the internal link checker.
- `mate check` runs the build-and-test path used before deployment.
- `mate format` formats Python with Ruff.
- `mate lint` runs Ruff checks.

For content workflows, use `mate new "Post Title"`, `mate publish post-slug`, and `mate add-image post-slug image-name path-or-url`.

Drafts may also contain authoring-time AI instructions using a placeholder syntax such as `{{command: instruction}}`, for example `{{link: Slashdot}}`. This mini-spec is intentionally in flux and subject to change. When publishing or otherwise processing an article, treat these placeholders as instructions for the AI agent to resolve before the final content is published.

## Coding Style & Naming Conventions

Python targets 3.10+ and uses Ruff with 100-character lines, double quotes, space indentation, and import sorting. Keep functions focused and prefer explicit failures over hidden defaults. Use lowercase, hyphenated slugs for Markdown filenames, image folders, and generated post URLs, for example `posts/my-article.md` and `static/my-article/diagram.png`.

## Testing Guidelines

Run `mate test` after changes that affect templates, links, content paths, static assets, or build logic. The current test suite is an executable Python link checker rather than a unit-test package. It expects `public/` to exist, so use the `mate test` target instead of invoking `tests/link_checker.py` directly.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Fix date sorting to handle mixed string and datetime.date types`. Keep commits small and focused. Pull requests should describe the user-visible change, list verification commands such as `mate check`, link related issues when applicable, and include screenshots for layout or visual content changes.

- Clearly mark any AI-generated text in site content, both visually and in the HTML. Never present AI-generated text as if it were human-authored.

## Learned Rules (managed by /learn)

<!-- pi:learn:start -->

- Commit draft and idea content files by default. If a draft or idea should stay out of history, the user can remove it later; do not leave such content uncommitted unless asked.
- Run `taidy .` before every commit.
<!-- pi:learn:end -->
