# Design

## Purpose

This site should feel simple, tidy, and intentional.

It is also a test bed for a design style built around clear signifiers and obvious affordances. Elements should look like what they are. Interactive elements should look interactive without relying on learned web conventions alone.

## Core Principles

1. **Semantic HTML first**
   - Prefer native HTML structure and meaning.
   - Do not flatten everything into generic containers.

2. **Strong signifiers**
   - Links should look like links.
   - Buttons should look like buttons.
   - Controls should look pressable/clickable only when they actually perform an action.
   - State changes should be obvious.

3. **Preserve traditional expectations**
   - Keep the essence of familiar HTML element behaviour and appearance.
   - Avoid reinvention for its own sake.

4. **Restrained depth, not fake materials**
   - Use borders, contrast, highlights, and shadows where they improve clarity.
   - Do not imitate leather, wood, paper, or other fake materials.
   - Avoid low-contrast neumorphism.

5. **Readable rhythm**
   - Spacing should make hierarchy obvious.
   - Typography should support long-form reading.
   - Mobile and desktop layouts should both feel calm and usable.

6. **Minimal moving parts**
   - No JavaScript dependency for core navigation or reading.
   - Avoid visual gimmicks and unnecessary animation.

## Interaction Rules

- Links go somewhere and should read as links.
- Buttons do something and should read as buttons.
- Do not style ordinary navigation links as faux buttons unless they genuinely behave like controls.
- Body links remain underlined by default.
- Hover, focus, and active states must all be visible.
- Keyboard focus must remain obvious.
- Interactive styling should increase clarity, not novelty.

## AI-Generated Content

AI-written content is allowed only when it is clearly marked and does not masquerade as human-authored writing.

Rules:

- Mark AI-written content both visually and in HTML.
- Use a reusable wrapper with explicit class/attribute markers.
- The marker should be prominent enough to notice before reading the content.

Current pattern:

- wrapper class: `.ai-generated`
- visible label: `.ai-generated__label`
- semantic marker: `data-authorship="ai"`

## Phase 1 Focus

Phase 1 applies these principles to:

- homepage
- article pages
- standalone pages such as `about`
- basic navigation and footer treatment

Projects surfacing, richer workflow tooling, and automated browser/mobile testing are later phases.
