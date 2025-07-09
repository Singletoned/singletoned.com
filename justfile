# Simple Tech Blog - Justfile

# Build the static site
build:
    deno task build

# Start development server with live reload
dev:
    deno task dev

# Create a new draft article
new title:
    deno task new "{{ title }}"

# Publish a draft article (moves from drafts/ to posts/ with metadata)
publish filename:
    deno task publish {{ filename }}

# Clean generated files
clean:
    rm -rf public/*

# Show available commands
help:
    @just --list

# Test internal links after building
test: build
    deno task test

# Build and serve locally (useful for testing)
serve: build
    cd public && python3 -m http.server 8000

# Build and test - useful before deployment
check: build test

# Format code using Deno
format:
    deno fmt

# Lint code using Deno
lint:
    deno lint

# Default recipe
default: help
