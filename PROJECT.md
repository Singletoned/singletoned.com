# Project

## Summary

This repository powers a simple static personal site on the same domain as Ed Singleton's email address. It is intended to be a credible public-facing home for:

- writing and blog posts
- projects and things built
- occasional static app-support pages when required

The site should be simple, semantic, accessible, responsive, and should not rely on JavaScript.

## Current Priorities

The immediate priority is to improve the look and feel of the site so it feels tidy, intentional, and well spaced.

Phase 1 focuses on:

- redesigning the homepage
- redesigning article pages
- redesigning standalone pages such as `about`
- cleaning up obvious file/directory clutter
- reducing the prominence of TredMarx in top-level navigation
- removing `posts/cloudflare-is-surprisingly-bad.md` from the live site
- documenting the project and design principles clearly

Selected projects, richer image handling, and browser/mobile automation are later phases.

## Product Intent

The main identity of the site is:

1. recent writing
2. projects / things built

A professional "hire me" impression is a welcome side effect, but not the primary organising goal.

TredMarx is currently low priority. It should remain available, but it should not dominate the site's main navigation or identity.

## Design Direction

This site is also a test bed for a design style/system built around clear signifiers and obvious affordances.

Principles:

- semantic HTML first
- elements should look like what they are
- interactive elements should obviously look interactive
- preserve the essence of traditional HTML controls and expectations
- avoid flat ambiguity
- avoid fake-material skeuomorphism
- prefer restrained depth, clear hierarchy, and obvious state changes

The goal is not novelty. The goal is clarity.

## Content Policy

- Do not create AI-generated content that looks like human-authored content.
- If AI-written content is used, it must be clearly marked both visually and in the HTML.
- No random extra pages should be added just because they seem useful.
- The project should make it easier for Ed to create real content himself.

## Technical Direction

- Keep the static-site architecture unless a real problem requires change.
- Prefer mostly native HTML plus a small, understandable custom stylesheet.
- Additional pipelines are acceptable if they are automated and justified.
- Use Netlify as the current hosting path unless there is a concrete reason to move.
- Avoid unnecessary complexity, client-side features, analytics, cookies, and visual gimmicks.

## Workflow Direction

Writing workflow should reduce the friction of getting from an idea to a draft.

The current direction is:

- capture rough ideas as Markdown notes in `ideas/`
- promote good ideas into `drafts/` with a CLI command
- keep the workflow filesystem-based and Emacs-friendly
- add tooling only where it reduces real friction

## Success Criteria

Near-term success means:

- the site looks more intentional than it does now
- spacing and hierarchy feel coherent
- interactive elements are easier to recognise
- homepage, article pages, and standalone pages feel consistent
- the site remains accessible and works well on mobile and desktop
- the project has clear documentation in `PROJECT.md`, `DESIGN.md`, and `IMPLEMENTATION_PLAN.md`
