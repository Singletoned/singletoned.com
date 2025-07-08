# Simple Tech Blog - Justfile

# Install dependencies
install:
    npm install

# Build the static site
build:
    npm run build

# Start development server with live reload
dev:
    npm run dev

# Create a new draft article
new title:
    npm run new "{{title}}"

# Publish a draft article (moves from drafts/ to posts/ with metadata)
publish filename:
    npm run publish {{filename}}

# Clean generated files
clean:
    rm -rf public/*

# Show available commands
help:
    @just --list

# Test internal links after building
test: build
    npm test

# Build and serve locally (useful for testing)
serve: build
    cd public && python3 -m http.server 8000

# Build and test - useful before deployment
check: build test

# Default recipe
default: help