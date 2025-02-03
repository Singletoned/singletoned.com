const fs = require('fs').promises;
const path = require('path');
const matter = require('gray-matter');
const pug = require('pug');
const { marked } = require('marked');

async function buildPosts() {
  try {
    // Create output directory if it doesn't exist
    const outputDir = path.join(__dirname, '../dist/articles');
    await fs.mkdir(outputDir, { recursive: true });

    // Compile the Pug template
    const templatePath = path.join(__dirname, '../article.pug');
    const renderTemplate = pug.compileFile(templatePath);

    // Get all markdown files from posts directory
    const postsDir = path.join(__dirname, '../posts');
    const files = await fs.readdir(postsDir);
    const markdownFiles = files.filter(file => file.endsWith('.md'));

    // Process each markdown file
    for (const file of markdownFiles) {
      // Read and parse the markdown file
      const filePath = path.join(postsDir, file);
      const fileContent = await fs.readFile(filePath, 'utf8');
      const { data: frontmatter, content } = matter(fileContent);

      // Convert markdown content to HTML
      const htmlContent = marked(content);

      // Render the template with our data
      const html = renderTemplate({
        ...frontmatter,
        content: htmlContent
      });

      // Create output filename (convert .md to .html)
      const outputFile = file.replace('.md', '.html');
      const outputPath = path.join(outputDir, outputFile);

      // Write the rendered HTML to file
      await fs.writeFile(outputPath, html);

      console.log(`Built ${outputFile}`);
    }

    console.log('All posts built successfully!');
  } catch (error) {
    console.error('Error building posts:', error);
    process.exit(1);
  }
}

buildPosts(); 