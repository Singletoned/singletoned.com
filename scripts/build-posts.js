const fs = require("fs").promises;
const path = require("path");
const matter = require("gray-matter");
const pug = require("pug");
const { marked } = require("marked");
const yaml = require("js-yaml");

async function copyStaticFiles() {
  const staticFiles = [
    {
      src: path.join(__dirname, "../public/styles.css"),
      dest: path.join(__dirname, "../dist/styles.css"),
    },
    // Add other static files here as needed
  ];

  for (const file of staticFiles) {
    try {
      await fs.copyFile(file.src, file.dest);
      console.log(`Copied ${path.basename(file.src)}`);
    } catch (err) {
      if (err.code === "ENOENT") {
        console.log(`${path.basename(file.src)} not found - skipping`);
      } else {
        throw err;
      }
    }
  }
}

async function buildPosts() {
  try {
    // Create output directories if they don't exist
    const distDir = path.join(__dirname, "../dist");
    const articlesDir = path.join(__dirname, "../dist/articles");
    await fs.mkdir(distDir, { recursive: true });
    await fs.mkdir(articlesDir, { recursive: true });

    // Copy static files first
    await copyStaticFiles();

    // Compile the Pug template
    const templatePath = path.join(__dirname, "../templates/article.pug");
    const renderTemplate = pug.compileFile(templatePath);

    // Get all markdown files from posts directory
    const postsDir = path.join(__dirname, "../posts");
    let files;
    try {
      files = await fs.readdir(postsDir);
    } catch (err) {
      if (err.code === "ENOENT") {
        console.log("Posts directory not found, creating it...");
        await fs.mkdir(postsDir, { recursive: true });
        files = [];
      } else {
        throw err;
      }
    }
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

      // Merge author data from config with fallback values
      const authorId = frontmatter.author || "default";
      const authorData = siteConfig.authors?.[authorId] || {
        name: "Unknown Author",
        avatar: "/images/default-avatar.png",
        bio: "",
      };

      // Create new frontmatter with author data and site config
      const mergedFrontmatter = {
        ...frontmatter,
        author: authorData,
        site: siteConfig.site || {}, // Make site config available to templates
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
      const outputPath = path.join(articlesDir, outputFile);

      // Write the rendered HTML to file
      await fs.writeFile(outputPath, html);

      console.log(`Built ${outputFile}`);
    }

    // Build index page
    const indexTemplatePath = path.join(__dirname, "../templates/index.pug");
    const renderIndex = pug.compileFile(indexTemplatePath);
    const indexPath = path.join(__dirname, "../dist/index.html");

    // Prepare posts data for index page
    const postsForIndex = [];
    for (const file of markdownFiles) {
      const filePath = path.join(postsDir, file);
      const fileContent = await fs.readFile(filePath, "utf8");
      const { data: frontmatter } = matter(fileContent);

      const authorId = frontmatter.author || "default";
      const authorData = siteConfig.authors?.[authorId] || {
        name: "Unknown Author",
        avatar: "/images/default-avatar.png",
        bio: "",
      };

      postsForIndex.push({
        ...frontmatter,
        author: authorData,
        slug: file.replace(".md", ".html"),
        date: frontmatter.date ? new Date(frontmatter.date) : new Date(),
      });
    }
    postsForIndex.sort((a, b) => b.date - a.date); // Sort by date, newest first

    await fs.writeFile(
      indexPath,
      renderIndex({
        posts: postsForIndex,
        site: siteConfig.site || {},
      }),
    );

    console.log("Built index.html");
    console.log("All posts built successfully!");
  } catch (error) {
    console.error("Error building posts:", error);
    process.exit(1);
  }
}

buildPosts();
