# Simple Tech Blog - Justfile
# Thin wrapper around the blog CLI (for those who prefer just)

# Build the static site
build:
    blog build

# Start development server with live reload
dev:
    blog dev

# Capture a new idea in the inbox
idea title:
    blog idea "{{ title }}"

# List captured ideas
ideas:
    blog ideas

# Create a new draft article
new title:
    blog new "{{ title }}"

# Start a draft from an idea note
draft-from-idea idea-name:
    blog draft-from-idea {{ idea-name }}

# Resolve AI instruction placeholders in a draft
process filename:
    blog process {{ filename }}

# Publish a draft article (processes instructions, then moves from drafts/ to posts/)
publish filename:
    blog publish {{ filename }}

# Add an image to a draft post
add-image post-name image-name url:
    blog add-image "{{ post-name }}" "{{ image-name }}" "{{ url }}"

# Clean generated files
clean:
    blog clean

# Show available commands
help:
    @just --list

# Test internal links after building
test:
    blog test

# Build and test - useful before deployment
check:
    blog check

# Format code using ruff
format:
    blog format

# Lint code using ruff
lint:
    blog lint

# Install dependencies
install:
    uv pip install -e .

# Default recipe
default: help
