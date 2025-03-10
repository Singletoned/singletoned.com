#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Function to convert a string to kebab-case
function toKebabCase(str) {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2') // Convert camelCase to kebab-case
    .replace(/[\s_]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/[^\w-]/g, '') // Remove special characters
    .toLowerCase(); // Convert to lowercase
}

// Get the post name from command line arguments
const postName = process.argv.slice(2).join(' ');

if (!postName) {
  console.error('Please provide a name for the post.');
  console.error('Usage: node scripts/create-draft.js "Your Post Title"');
  process.exit(1);
}

// Convert the post name to kebab-case for the filename
const kebabName = toKebabCase(postName);
const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
const fileName = `${date}-${kebabName}.md`;

// Path to the example post and the drafts directory
const rootDir = path.join(__dirname, '..');
const examplePostPath = path.join(rootDir, 'content', 'posts', 'example-post.md');
const draftsDir = path.join(rootDir, 'content', 'drafts');

// Create drafts directory if it doesn't exist
if (!fs.existsSync(draftsDir)) {
  fs.mkdirSync(draftsDir, { recursive: true });
  console.log(`Created drafts directory at ${draftsDir}`);
}

// Path for the new draft
const newDraftPath = path.join(draftsDir, fileName);

try {
  // Read the example post
  let exampleContent = fs.readFileSync(examplePostPath, 'utf8');
  
  // Update the title in the content
  exampleContent = exampleContent.replace(/title: .*/, `title: ${postName}`);
  
  // Write the new draft
  fs.writeFileSync(newDraftPath, exampleContent);
  
  console.log(`Created new draft: ${newDraftPath}`);
  
  // Try to open the file in the default editor
  try {
    if (process.platform === 'darwin') {
      execSync(`open "${newDraftPath}"`);
    } else if (process.platform === 'win32') {
      execSync(`start "" "${newDraftPath}"`);
    } else {
      execSync(`xdg-open "${newDraftPath}"`);
    }
    console.log('Opened the new draft in your default editor.');
  } catch (error) {
    console.log('Could not open the file automatically.');
  }
  
} catch (error) {
  if (error.code === 'ENOENT' && !fs.existsSync(examplePostPath)) {
    console.error(`Example post not found at ${examplePostPath}`);
    console.error('Please make sure the example-post.md exists in the content/posts directory.');
  } else {
    console.error('An error occurred:', error.message);
  }
  process.exit(1);
} 