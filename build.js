import fs from "node:fs";
import path from "node:path";
import pug from "pug";
import MarkdownIt from "markdown-it";
import linkAttributes from "markdown-it-link-attributes";
import fm from "front-matter";
import readingTime from "reading-time";

const md = new MarkdownIt();
md.use(linkAttributes, {
  pattern: /^https?:\/\//,
  attrs: {
    target: "_blank",
    rel: "noopener noreferrer",
  },
});

class BlogBuilder {
  constructor() {
    this.postsDir = "./posts";
    this.pagesDir = "./pages";
    this.templatesDir = "./templates";
    this.outputDir = "./public";
    this.staticDir = "./static";
  }

  async build() {
    console.log("Building site...");

    // Ensure output directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    // Copy static files
    this.copyStatic();

    // Build posts
    const posts = await this.buildPosts();

    // Build pages
    await this.buildPages();

    // Build index page with post list
    await this.buildIndex(posts);

    console.log("Site built successfully!");
  }

  copyStatic() {
    if (fs.existsSync(this.staticDir)) {
      this.copyRecursive(this.staticDir, this.outputDir);
    }
  }

  copyRecursive(src, dest) {
    const files = fs.readdirSync(src);
    files.forEach((file) => {
      const srcPath = path.join(src, file);
      const destPath = path.join(dest, file);
      const stat = fs.statSync(srcPath);

      if (stat.isDirectory()) {
        if (!fs.existsSync(destPath)) {
          fs.mkdirSync(destPath, { recursive: true });
        }
        this.copyRecursive(srcPath, destPath);
      } else {
        // Ensure destination directory exists
        const destDir = path.dirname(destPath);
        if (!fs.existsSync(destDir)) {
          fs.mkdirSync(destDir, { recursive: true });
        }
        fs.copyFileSync(srcPath, destPath);
      }
    });
  }

  async buildPosts() {
    const posts = [];

    if (!fs.existsSync(this.postsDir)) {
      return posts;
    }

    const postFiles = fs
      .readdirSync(this.postsDir)
      .filter((file) => file.endsWith(".md"));

    for (const file of postFiles) {
      const filePath = path.join(this.postsDir, file);
      const content = fs.readFileSync(filePath, "utf8");
      const parsed = fm(content);

      const post = {
        ...parsed.attributes,
        content: md.render(parsed.body),
        slug: path.basename(file, ".md"),
        readingTime: readingTime(parsed.body).text,
      };

      // Generate post HTML
      const html = this.renderTemplate("article", { post });
      const outputPath = path.join(this.outputDir, `${post.slug}.html`);
      fs.writeFileSync(outputPath, html);

      posts.push(post);
    }

    // Sort posts by date (newest first)
    posts.sort((a, b) => new Date(b.date) - new Date(a.date));

    return posts;
  }

  async buildPages() {
    if (!fs.existsSync(this.pagesDir)) {
      return;
    }

    const pageFiles = fs
      .readdirSync(this.pagesDir)
      .filter((file) => file.endsWith(".md"));

    for (const file of pageFiles) {
      const filePath = path.join(this.pagesDir, file);
      const content = fs.readFileSync(filePath, "utf8");
      const parsed = fm(content);

      const page = {
        ...parsed.attributes,
        content: md.render(parsed.body),
        slug: path.basename(file, ".md"),
      };

      const html = this.renderTemplate("page", { page });
      const outputPath = path.join(this.outputDir, `${page.slug}.html`);
      fs.writeFileSync(outputPath, html);
    }
  }

  async buildIndex(posts) {
    const html = this.renderTemplate("index", { posts });
    const outputPath = path.join(this.outputDir, "index.html");
    fs.writeFileSync(outputPath, html);
  }

  renderTemplate(templateName, data) {
    const templatePath = path.join(this.templatesDir, `${templateName}.pug`);
    return pug.renderFile(templatePath, data);
  }
}

// Run build if called directly
if (import.meta.main) {
  const builder = new BlogBuilder();
  builder.build().catch(console.error);
}

export default BlogBuilder;
