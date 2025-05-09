# Build the blog
build:
    bun run build

# Serve the built website
serve:
    @echo "Serving website at http://localhost:8080"
    python3 -m http.server 8080 --directory dist
