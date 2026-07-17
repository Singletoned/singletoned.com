# singletoned-com

Static site for singletoned.com.

Deployment is via Netlify.

## Install

```bash
just install
```

## Development

```bash
just build
just dev
just test
just check
```

## Deployment

Local verification:

```bash
just check
```

Use the repository deploy command:

```bash
just deploy
```

That command runs local checks, pushes `main` to GitHub, and waits for Netlify's GitHub-connected production deploy to finish. The generated site output lives in `public/`.

## Content workflow

Capture an idea:

```bash
just idea "Post title or rough thought"
```

List captured ideas:

```bash
just ideas
```

Promote an idea into a draft:

```bash
just draft-from-idea idea-file-name
```

Process AI authoring instructions in a draft:

```bash
just process draft-name
```

Create a draft directly:

```bash
just new "Post title"
```

Publish a draft:

```bash
just publish draft-name
```

Add an image to a draft:

```bash
just add-image draft-name image-name path-or-url
```

Drafts may include authoring-time placeholders such as:

```md
{{link: Slashdot}}
{{insert: an example block of AI generated content}}
```

`just process` resolves those placeholders in place via Pi. `just publish` now runs the same processing step automatically before publishing. If a post does not already have an `excerpt`, publishing fills one in automatically from the first sentence of the first body paragraph so the homepage has a snippet. If a post does not already have `tags`, publishing also uses Pi to add a small set of category tags for the post.
