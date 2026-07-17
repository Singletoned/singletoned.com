# Implementation Plan

## Project Context

This repository is a simple static site for a personal domain. Its near-term purpose is to:

- publish writing
- highlight projects and things built
- act as a credible public-facing presence
- support occasional static app-related pages when needed

TredMarx is currently low priority. The site should stay simple, static, accessible, semantic, and should not rely on JavaScript.

A secondary goal is to use the site as a test bed for a design style/system built around clear signifiers and obvious affordances: things should look like what they are, and interactive elements should read as interactive without learned conventions.

## Current State

- Static site generator in Python (`build.py`, `cli.py`)
- Templates in `templates/`
- Content in `posts/` and `pages/`
- CSS in `static/style.css`
- Output in `public/`
- Netlify config exists (`netlify.toml`)
- Current templates and styling are minimal but visually unpolished
- Some content is inaccurate, notably `pages/about.md`
- `posts/cloudflare-is-surprisingly-bad.md` should not remain in the live site
- Draft workflow exists but does not yet reduce the friction of getting to a draft enough

## Target Outcome

### Near-term milestone

A visibly improved, tidier, more intentional site that:

- looks better than the current version
- has stronger spacing and hierarchy
- uses semantic HTML
- makes interactive elements obviously interactive
- redesigns homepage, article pages, and standalone pages
- cleans up scattered files/directories
- de-emphasises TredMarx in navigation
- stays easy to deploy safely and often

### First useful slice

A deployable visual refresh of the existing site structure without trying to solve workflow tooling and richer information architecture at the same time.

## Planning Assumptions and Decisions

Confirmed decisions:

- Keep the site static
- Prefer semantic HTML and accessibility over cleverness
- Do not rely on JavaScript
- No analytics, no cookies/banner nonsense unless legally required, no client-side search, no visual gimmicks/animations by default
- Web fonts are optional, not required
- Preserve the essence of traditional HTML element looks
- State changes should be clear and obvious
- Recent writing and projects are the core identity; “hire me” is a side effect
- Selected projects are later, not phase 1
- TredMarx stays available but should be removed or de-emphasised from top-level navigation
- AI-written content is allowed only if it is clearly marked as AI-generated and not made to look human-authored
- AI-content marking should be a reusable site-wide pattern, not a one-off exception
- Stay on Netlify unless there is a concrete reason to change
- Deploy in small safe increments where practical

## Phase 1: Visual Refresh and Structural Cleanup

### Goal

Make the site feel intentional, readable, and obviously interactive without expanding scope into workflow tooling.

### In Scope

- Redesign homepage
- Redesign blog post/article pages
- Redesign standalone pages such as `about`
- Clean up files/directories where it directly supports the redesign
- Remove `cloudflare-is-surprisingly-bad` from the live site
- Create durable planning/design documentation

### Out of Scope

- Major writing workflow changes
- Better image handling
- New projects section/page
- New app support/privacy pages unless already required
- Hosting migration
- Automated browser/mobile testing

### Deliverables

1. `IMPLEMENTATION_PLAN.md` saved in repo
2. `PROJECT.md` created early in implementation and kept up to date
3. `DESIGN.md` describing:
   - semantic-first design
   - strong signifiers / affordances
   - obvious states
   - how much to preserve native control behaviour and appearance
   - how AI-written content must be marked
4. Refreshed `layout.html`, `index.html`, `article.html`, and `page.html`
5. Reworked stylesheet focused on spacing, typography, hierarchy, states, and readability
6. Navigation that de-emphasises TredMarx while keeping it accessible
7. Accurate `about.md`, with any AI-written content clearly marked in HTML and visually
8. `cloudflare-is-surprisingly-bad` removed from the working tree/live site, with recovery via `git stash`

### Concrete Tasks

1. Create `PROJECT.md`
2. Create `DESIGN.md`
3. Audit current templates and page structure
4. Define visual primitives:
   - page width
   - spacing scale
   - typography scale
   - link/button/focus/active states
   - content rhythm
5. Refactor base layout and navigation
6. Redesign homepage around recent writing
7. Redesign article template
8. Redesign standalone page template
9. Rewrite `pages/about.md` accurately
10. Implement reusable AI-content marking pattern
11. Remove/depublish Cloudflare post and generated artifacts from working tree
12. Clean file/directory layout where obviously messy
13. Run build/tests/manual review
14. Deploy in small safe increments

### Dependencies

- `PROJECT.md` should exist before or during the first implementation pass
- `DESIGN.md` should be written before significant CSS/template churn so it guides implementation
- About-page rewrite depends on deciding the HTML/CSS pattern for AI-marked content
- Navigation changes depend on confirming TredMarx de-emphasis approach
- Cloudflare removal depends on preserving recoverability via `git stash`

## Phase 2: Writing Friction Reduction

### Goal

Make it easier to get from idea to draft.

### Primary Focus

A lightweight inbox/capture workflow for ideas before a post exists.

### In Scope

- Define what “idea capture” looks like in-repo
- Add a simple, editor-friendly structure for rough ideas
- Keep it Markdown and filesystem-based
- Improve draft creation enough that writing can start quickly

### Recommended Direction

Start with a simple model such as:

- an `ideas/` or `inbox/` directory with timestamped Markdown notes
- or a single `ideas.md` inbox if that proves simpler

Add only minimal tooling if needed:

- create idea note
- optionally promote idea into a draft later

Keep the system Emacs-friendly and avoid hiding content behind custom tooling.

### Explicitly Later

- append-to-draft helpers
- image workflow improvements
- publish checklist improvements
- richer editor integration

### Concrete Tasks

1. Choose inbox model (`ideas/` directory vs single inbox file)
2. Create the structure and naming conventions
3. Add the smallest useful CLI support if needed
4. Document the writing workflow
5. Validate that creating a new idea/draft is materially easier

## Later Phases

### Phase 3: Information Architecture and Project Surfacing

- Add selected projects section/page
- Decide whether project content belongs only on the homepage or also on a dedicated page
- Revisit TredMarx placement in that context

### Phase 4: Publishing Workflow Improvements

- Improve draft lifecycle
- Improve image handling
- Improve preview/publish flow

### Phase 5: Quality Automation

- Add automated browser/mobile testing
- Possibly add visual regression or responsive smoke tests

## Architecture / Design Decisions

### Design Principles

- Semantic HTML first
- Elements should visually represent what they are
- Interactive elements need strong signifiers
- Preserve traditional expectations where possible
- Avoid flat ambiguity
- Avoid fake-material skeuomorphism
- Prefer restrained depth and clear state changes
- Body links should remain obviously link-like
- Buttons/interactive controls should read as pressable/clickable at a glance

### Styling Strategy

- Start with custom CSS rather than a large framework
- Keep the CSS understandable and maintainable
- If a pipeline is introduced later, it must be automated
- Borrow from lightweight semantic CSS frameworks only if needed

### AI-Generated Content Policy

- AI-written content must not masquerade as human-authored content
- It should be explicitly marked in HTML and visually distinguished
- The pattern should be reusable and documented in `DESIGN.md`

### Hosting

- Stay on current static-hosting path unless a concrete blocker appears

## Testing and Validation

### Phase 1

Run:

- `just build`
- `just test`

Manual checks:

- homepage
- article page
- about page
- navigation
- responsive layout on mobile and desktop widths
- link clarity and hover/focus/active states
- keyboard navigation
- AI-content visual marker and semantics

### Phase 1 Acceptance Checks

- Site is not worse than the current version
- Visual spacing feels intentional
- Pages are readable on mobile and desktop
- Interactive elements are obviously interactive
- About page is accurate
- Cloudflare post is no longer published
- TredMarx is not prominent in top-level navigation
- `PROJECT.md` and `DESIGN.md` exist and are useful

### Later Validation

- Add automated browser/mobile testing in a later phase

## Risks and Mitigations

### Risk: Over-designing too early

Mitigation:

- Keep phase 1 limited to refresh plus cleanup
- Avoid building a grand design system before proving it on a few templates

### Risk: Framework choice becomes a distraction

Mitigation:

- Start with custom CSS unless a real limitation appears

### Risk: Unclear homepage identity

Mitigation:

- Prioritise recent writing first
- Keep project surfacing for a later focused pass

### Risk: Workflow tooling before real workflow exists

Mitigation:

- In phase 2, start with the smallest possible capture model
- Let actual usage shape the tooling

### Risk: AI-content marking becomes inconsistent

Mitigation:

- Define the pattern in `DESIGN.md`
- Treat it as a reusable rule, not a page-specific exception

## Open Questions

- Should selected projects eventually live only on the homepage or on a dedicated page too?
- What exact HTML/CSS pattern should represent AI-written content?
- How much of native form/control appearance should be preserved directly vs lightly reinterpreted?
- Should web fonts be introduced, and under what constraints?
- What exact shape should the writing inbox take in phase 2?
- Is Netlify definitely the deployment target, or merely the current default?

## Definition of Done

### Phase 1

Phase 1 is done when:

- homepage, article page, and standalone page templates have been visually refreshed
- the site looks more intentional and coherent than before
- spacing, hierarchy, and states are clearer
- interactivity is easier to recognise
- about content is accurate and any AI-written content is clearly marked
- the Cloudflare post is no longer part of the live site
- TredMarx remains available but is no longer prominent in top-level navigation
- `PROJECT.md` and `DESIGN.md` exist and are useful
- the site builds/tests successfully and is safe to deploy

### Phase 2

Phase 2 is done when:

- there is a simple, documented, low-friction idea-capture path
- getting from idea to draft is meaningfully easier than today
