# Build the blog
build:
    bun run build

# Serve the built website
serve:
    @echo "Serving website at http://localhost:8080"
    python3 -m http.server 8080 --directory dist

# Test all links in the built site
test-links:
    bunx node scripts/test-links.js

# Format code using Prettier
format:
    bunx prettier --write 'scripts/**/*.js' 'templates/**/*.pug'
