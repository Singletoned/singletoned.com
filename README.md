# singletoned-com

Static site for singletoned.com.

Deployment is via Netlify.

## Install

```bash
mate install
```

## Development

```bash
mate build
mate dev
mate test
mate check
```

## Deployment

Local verification:

```bash
mate check
```

Use the repository deploy command:

```bash
mate deploy
```

That command runs local checks, pushes `main` to GitHub, and waits for Netlify's GitHub-connected production deploy to finish. The generated site output lives in `public/`.

## Content workflow

Capture an idea:

```bash
mate idea "Post title or rough thought"
```

List captured ideas:

```bash
mate ideas
```

Promote an idea into a draft:

```bash
mate draft-from-idea idea-file-name
```

Process AI authoring instructions in a draft:

```bash
mate process draft-name
```

Create a draft directly:

```bash
mate draft "Post title"
```

Add an optional TL;DR to the draft's YAML front matter. It supports Markdown and appears in a labelled box before the article:

```yaml
tldr: |
  A short summary with **emphasis** or a [link](https://example.com).
```

Mark any AI-generated summary using the site's AI-generated content pattern.

Publish a draft:

```bash
mate publish draft-name
```

Add an image to a draft:

```bash
mate add-image draft-name image-name path-or-url
```

Drafts may include authoring-time placeholders such as:

```md
{{link: Slashdot}}
{{insert: an example block of AI generated content}}
```

`mate process` resolves those placeholders in place via Pi. `mate publish` now runs the same processing step automatically before publishing. If a post does not already have an `excerpt`, publishing fills one in automatically from the first sentence of the first body paragraph so the homepage has a snippet. If a post does not already have `tags`, publishing also uses Pi to add a small set of category tags for the post.
