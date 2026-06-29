# singletoned-com

Static site for singletoned.com.

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
