const fs = require("fs");
const path = require("path");
const fm = require("front-matter");

function publishDraft(filename) {
  if (!filename) {
    console.error("Usage: npm run publish <filename>");
    console.error("Example: npm run publish my-article");
    process.exit(1);
  }

  // Add .md extension if not provided
  if (!filename.endsWith(".md")) {
    filename += ".md";
  }

  const draftPath = path.join("./drafts", filename);
  const postPath = path.join("./posts", filename);

  // Check if draft exists
  if (!fs.existsSync(draftPath)) {
    console.error(`Draft not found: ${draftPath}`);
    process.exit(1);
  }

  // Read and parse the draft
  const content = fs.readFileSync(draftPath, "utf8");
  const parsed = fm(content);

  // Add metadata if not present
  const metadata = {
    date: new Date().toISOString().split("T")[0], // YYYY-MM-DD format
    ...parsed.attributes,
  };

  // Create the updated content
  const updatedContent = `---
title: ${metadata.title || path.basename(filename, ".md").replace(/-/g, " ")}
date: ${metadata.date}
excerpt: ${metadata.excerpt || ""}
---

${parsed.body}`;

  // Move to posts directory
  fs.writeFileSync(postPath, updatedContent);
  fs.unlinkSync(draftPath);

  console.log(`Published: ${filename}`);
  console.log(`Moved from drafts/ to posts/`);
  console.log(`Added publication date: ${metadata.date}`);
}

// Get filename from command line arguments
const filename = process.argv[2];
publishDraft(filename);
