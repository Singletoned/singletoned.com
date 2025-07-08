const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

class LinkChecker {
  constructor() {
    this.publicDir = './public';
    this.errors = [];
    this.warnings = [];
    this.checkedPages = new Set();
  }

  async checkLinks() {
    console.log('🔍 Checking internal links...');
    
    if (!fs.existsSync(this.publicDir)) {
      console.error('❌ Public directory not found. Run "npm run build" first.');
      process.exit(1);
    }

    // Get all HTML files
    const htmlFiles = this.getHtmlFiles(this.publicDir);
    
    if (htmlFiles.length === 0) {
      console.error('❌ No HTML files found in public directory.');
      process.exit(1);
    }

    console.log(`Found ${htmlFiles.length} HTML files to check`);

    // Check each HTML file
    for (const file of htmlFiles) {
      this.checkFile(file);
    }

    // Report results
    this.reportResults();
  }

  getHtmlFiles(dir) {
    const files = [];
    const items = fs.readdirSync(dir);

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        files.push(...this.getHtmlFiles(fullPath));
      } else if (item.endsWith('.html')) {
        files.push(fullPath);
      }
    }

    return files;
  }

  checkFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const $ = cheerio.load(content);
      const relativePath = path.relative(this.publicDir, filePath);

      console.log(`Checking: ${relativePath}`);
      this.checkedPages.add(relativePath);

      // Check all links
      $('a[href]').each((i, element) => {
        const href = $(element).attr('href');
        this.checkLink(href, relativePath, $(element).text().trim());
      });

      // Check CSS links
      $('link[rel="stylesheet"][href]').each((i, element) => {
        const href = $(element).attr('href');
        this.checkAsset(href, relativePath, 'CSS');
      });

      // Check script sources
      $('script[src]').each((i, element) => {
        const src = $(element).attr('src');
        this.checkAsset(src, relativePath, 'JavaScript');
      });

      // Check images
      $('img[src]').each((i, element) => {
        const src = $(element).attr('src');
        this.checkAsset(src, relativePath, 'Image');
      });

    } catch (error) {
      this.errors.push(`Error reading ${filePath}: ${error.message}`);
    }
  }

  checkLink(href, fromPage, linkText) {
    // Skip external links, mailto, tel, etc.
    if (this.isExternalLink(href)) {
      return;
    }

    // Skip anchors without path
    if (href.startsWith('#')) {
      return;
    }

    // Handle root-relative links
    let targetPath = href;
    if (href.startsWith('/')) {
      targetPath = href.substring(1);
    }

    // Remove anchor fragments
    targetPath = targetPath.split('#')[0];

    // If empty, it's linking to the current page or root
    if (!targetPath) {
      targetPath = 'index.html';
    }

    // Add .html if no extension
    if (!path.extname(targetPath)) {
      targetPath += '.html';
    }

    const fullTargetPath = path.join(this.publicDir, targetPath);

    if (!fs.existsSync(fullTargetPath)) {
      this.errors.push(`❌ Broken link in ${fromPage}: "${href}" -> ${targetPath} (text: "${linkText}")`);
    }
  }

  checkAsset(src, fromPage, type) {
    // Skip external assets
    if (this.isExternalLink(src)) {
      return;
    }

    // Handle root-relative paths
    let targetPath = src;
    if (src.startsWith('/')) {
      targetPath = src.substring(1);
    }

    const fullTargetPath = path.join(this.publicDir, targetPath);

    if (!fs.existsSync(fullTargetPath)) {
      this.errors.push(`❌ Missing ${type} asset in ${fromPage}: "${src}" -> ${targetPath}`);
    }
  }

  isExternalLink(url) {
    return url.startsWith('http://') || 
           url.startsWith('https://') || 
           url.startsWith('mailto:') || 
           url.startsWith('tel:') ||
           url.startsWith('//');
  }

  reportResults() {
    console.log('\n📊 Link Check Results:');
    console.log(`Pages checked: ${this.checkedPages.size}`);
    
    if (this.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      this.warnings.forEach(warning => console.log(`  ${warning}`));
    }

    if (this.errors.length > 0) {
      console.log('\n❌ Errors:');
      this.errors.forEach(error => console.log(`  ${error}`));
      console.log(`\nTotal errors: ${this.errors.length}`);
      process.exit(1);
    } else {
      console.log('\n✅ All internal links are working correctly!');
    }
  }
}

// Run the link checker
if (require.main === module) {
  const checker = new LinkChecker();
  checker.checkLinks().catch(console.error);
}

module.exports = LinkChecker;