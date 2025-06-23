const fs = require('fs');
const path = require('path');

function createNewDraft(title) {
  if (!title) {
    console.error('Usage: npm run new "<title>"');
    console.error('Example: npm run new "My Amazing Article"');
    process.exit(1);
  }

  // Create a filename from the title
  const filename = title
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-') + '.md';

  const draftPath = path.join('./drafts', filename);

  // Check if draft already exists
  if (fs.existsSync(draftPath)) {
    console.error(`Draft already exists: ${filename}`);
    process.exit(1);
  }

  // Create the draft content
  const content = `---
title: ${title}
excerpt: ""
---

# ${title}

Write your article here...`;

  // Ensure drafts directory exists
  if (!fs.existsSync('./drafts')) {
    fs.mkdirSync('./drafts', { recursive: true });
  }

  // Write the draft
  fs.writeFileSync(draftPath, content);

  console.log(`Created new draft: ${filename}`);
  console.log(`Edit it in: drafts/${filename}`);
  console.log(`When ready, publish with: npm run publish ${path.basename(filename, '.md')}`);
}

// Get title from command line arguments
const title = process.argv.slice(2).join(' ');
createNewDraft(title);