# Simple Tech Blog - Justfile

# Build the static site
build:
    python build.py

# Start development server with live reload
dev:
    python scripts/dev.py

# Create a new draft article
new title:
    python scripts/new.py "{{ title }}"

# Publish a draft article (moves from drafts/ to posts/ with metadata)
publish filename:
    python scripts/publish.py {{ filename }}

# Add an image to a draft post
add-image post-name image-name url:
    python scripts/add_image.py "{{ post-name }}" "{{ image-name }}" "{{ url }}"

# Clean generated files
clean:
    rm -rf public/*

# Show available commands
help:
    @just --list

# Test internal links after building
test: build
    python tests/link_checker.py

# Build and test - useful before deployment
check: build test

# Format code using ruff
format:
    ruff format .
    ruff check --fix .

# Lint code using ruff
lint:
    ruff check .

# Install dependencies
install:
    uv pip install -r requirements.txt

# Default recipe
default: help
