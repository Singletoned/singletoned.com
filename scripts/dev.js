import express from "express";
import chokidar from "chokidar";
import path from "node:path";
import BlogBuilder from "../build.js";

const app = express();
const PORT = 3000;

// Serve static files from public directory
app.use(express.static("public"));

let isBuilding = false;

async function rebuild() {
  if (isBuilding) return;

  isBuilding = true;
  console.log("Changes detected, rebuilding...");

  try {
    const builder = new BlogBuilder();
    await builder.build();
    console.log("Rebuild complete!");
  } catch (error) {
    console.error("Build error:", error);
  } finally {
    isBuilding = false;
  }
}

// Initial build
console.log("Starting development server...");
rebuild().then(() => {
  // Start the server
  app.listen(PORT, () => {
    console.log(`Development server running at http://localhost:${PORT}`);
    console.log("Watching for changes...");
  });

  // Watch for changes
  const watcher = chokidar.watch(
    [
      "drafts/**/*.md",
      "posts/**/*.md",
      "pages/**/*.md",
      "templates/**/*.pug",
      "static/**/*",
    ],
    {
      ignored: /node_modules/,
      persistent: true,
    },
  );

  watcher.on("change", rebuild);
  watcher.on("add", rebuild);
  watcher.on("unlink", rebuild);
});
