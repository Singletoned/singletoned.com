import fs from "node:fs";
import path from "node:path";

async function downloadImage(url, filepath) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = new Uint8Array(arrayBuffer);

    fs.writeFileSync(filepath, buffer);
    return true;
  } catch (error) {
    console.error(`Failed to download image: ${error.message}`);
    return false;
  }
}

function getImageExtension(url) {
  const urlPath = new URL(url).pathname;
  const ext = path.extname(urlPath).toLowerCase();

  // Common image extensions
  const validExts = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"];
  if (validExts.includes(ext)) {
    return ext;
  }

  // Default to .jpg if no extension found
  return ".jpg";
}

function sanitizeFilename(filename) {
  return filename
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

async function addImageToPost(postName, imageName, imageUrl) {
  if (!postName || !imageName || !imageUrl) {
    console.error(
      'Usage: deno task add-image "<post-name>" "<image-name>" "<image-url>"',
    );
    console.error(
      'Example: deno task add-image "my-post" "hero-image" "https://example.com/image.jpg"',
    );
    process.exit(1);
  }

  // Validate URL
  try {
    new URL(imageUrl);
  } catch {
    console.error("Invalid URL provided");
    process.exit(1);
  }

  // Find the draft file
  const draftPath = path.join("./drafts", `${postName}.md`);
  if (!fs.existsSync(draftPath)) {
    console.error(`Draft not found: ${draftPath}`);
    console.error("Available drafts:");
    if (fs.existsSync("./drafts")) {
      const drafts = fs
        .readdirSync("./drafts")
        .filter((f) => f.endsWith(".md"));
      drafts.forEach((draft) =>
        console.error(`  - ${path.basename(draft, ".md")}`),
      );
    }
    process.exit(1);
  }

  // Create image directory for this post
  const imageDir = path.join("./static", postName);
  if (!fs.existsSync(imageDir)) {
    fs.mkdirSync(imageDir, { recursive: true });
  }

  // Get file extension from URL
  const ext = getImageExtension(imageUrl);
  const sanitizedImageName = sanitizeFilename(imageName);
  const imagePath = path.join(imageDir, `${sanitizedImageName}${ext}`);

  // Download the image
  console.log(`Downloading image from: ${imageUrl}`);
  const success = await downloadImage(imageUrl, imagePath);

  if (!success) {
    process.exit(1);
  }

  // Read the draft content
  const content = fs.readFileSync(draftPath, "utf8");

  // Create markdown link
  const relativeImagePath = `${postName}/${sanitizedImageName}${ext}`;
  const markdownLink = `![${imageName}](${relativeImagePath})`;

  // Add the image link to the end of the content
  const updatedContent = content.trim() + "\n\n" + markdownLink + "\n";

  // Write updated content back
  fs.writeFileSync(draftPath, updatedContent);

  console.log(`✅ Image downloaded and added to draft:`);
  console.log(`   📁 Saved to: ${imagePath}`);
  console.log(`   📝 Added to: ${draftPath}`);
  console.log(`   🔗 Markdown: ${markdownLink}`);
}

// Get arguments from command line
const [postName, imageName, imageUrl] = Deno.args;
await addImageToPost(postName, imageName, imageUrl);
