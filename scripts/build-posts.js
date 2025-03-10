const fs = require("fs").promises;
const path = require("path");
const matter = require("gray-matter");
const pug = require("pug");
const { marked } = require("marked");
const yaml = require("js-yaml");

async function buildPosts() {
  try {
    // Create output directory if it doesn't exist
    const outputDir = path.join(__dirname, "../dist/articles");
    await fs.mkdir(outputDir, { recursive: true });

    // Compile the Pug template
    const templatePath = path.join(__dirname, "../templates/article.pug");
    const renderTemplate = pug.compileFile(templatePath);

    // Get all markdown files from posts directory
    const postsDir = path.join(__dirname, "../posts");
    const files = await fs.readdir(postsDir);
    const markdownFiles = files.filter((file) => file.endsWith(".md"));

    // Load site configuration
    const configPath = path.join(__dirname, "../config/site.yaml");
    const siteConfig = yaml.load(await fs.readFile(configPath, "utf8"));

    // Process each markdown file
    for (const file of markdownFiles) {
      // Read and parse the markdown file
      const filePath = path.join(postsDir, file);
      const fileContent = await fs.readFile(filePath, "utf8");
      const { data: frontmatter, content } = matter(fileContent);






      // Merge author data from config
      const authorId = frontmatter.author || "default";
      const authorData = siteConfig.authors[authorId];

      // Create new frontmatter with author data and site config
      const mergedFrontmatter = {
        ...frontmatter,
        author: authorData,
        site: siteConfig.site, // Make site config available to templates
      };


      
      // Convert markdown content to HTML
      const htmlContent = marked(content);

      // Calculate reading time
      const wordCount = content.split(/\s+/).length;
      const readingTime = Math.ceil(wordCount / 200);

      // Render the template with our data
      const html = renderTemplate({
        ...mergedFrontmatter,
        content: htmlContent,
        readingTime,
      });

      // Create output filename (convert .md to .html)
      const outputFile = file.replace(".md", ".html");
      const outputPath = path.join(outputDir, outputFile);

      // Write the rendered HTML to file
      await fs.writeFile(outputPath, html);

      console.log(`Built ${outputFile}`);
    }

    console.log("All posts built successfully!");
  } catch (error) {
    console.error("Error building posts:", error);
    process.exit(1);
  }
}

buildPosts();
