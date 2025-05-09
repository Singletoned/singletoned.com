const fs = require('fs').promises;
const path = require('path');
const { JSDOM } = require('jsdom');
const axios = require('axios');

async function findHtmlFiles(dir) {
  const files = await fs.readdir(dir);
  const htmlFiles = [];
  
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = await fs.stat(fullPath);
    
    if (stat.isDirectory()) {
      htmlFiles.push(...await findHtmlFiles(fullPath));
    } else if (file.endsWith('.html')) {
      htmlFiles.push(fullPath);
    }
  }
  
  return htmlFiles;
}

async function checkLinks() {
  try {
    const distDir = path.join(__dirname, '../dist');
    const htmlFiles = await findHtmlFiles(distDir);
    const brokenLinks = [];
    
    for (const file of htmlFiles) {
      const content = await fs.readFile(file, 'utf8');
      const dom = new JSDOM(content);
      const links = dom.window.document.querySelectorAll('a[href]');
      
      for (const link of links) {
        const href = link.href;
        
        // Skip external links, mailto: and non-existent pages
        if (href.startsWith('http') || href.startsWith('mailto:') || 
            ['/about', '/contact', '/previous-post', '/next-post'].includes(href)) {
          continue;
        }
        
        // Check local links - handle both absolute and relative paths
        let localPath;
        if (href.startsWith('/')) {
          localPath = path.join(distDir, href.substring(1));
        } else {
          localPath = path.join(path.dirname(file), href);
        }
        try {
          await fs.access(localPath);
        } catch (err) {
          brokenLinks.push({
            file: path.relative(distDir, file),
            link: href,
            text: link.textContent.trim()
          });
        }
      }
    }
    
    if (brokenLinks.length > 0) {
      console.error('\nBroken links found:');
      brokenLinks.forEach(({file, link, text}) => {
        console.error(`- In ${file}: "${text}" -> ${link}`);
      });
      process.exit(1);
    } else {
      console.log('All links are valid!');
    }
  } catch (err) {
    console.error('Error checking links:', err);
    process.exit(1);
  }
}

checkLinks();
