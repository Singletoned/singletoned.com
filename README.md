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

Netlify can build this repo using `netlify.toml`, or you can deploy manually with the Netlify CLI:

```bash
netlify deploy --prod
```

The generated site output lives in `public/`.

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

`just process` resolves those placeholders in place via Pi. `just publish` now runs the same processing step automatically before publishing.
