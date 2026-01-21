import puppeteer from 'puppeteer';
import fs from 'fs';
import https from 'https';
import http from 'http';

async function downloadFile(url, filename) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    protocol.get(url, (response) => {
      // Handle redirects
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        downloadFile(response.headers.location, filename).then(resolve).catch(reject);
        return;
      }
      const fileStream = fs.createWriteStream(filename);
      response.pipe(fileStream);
      fileStream.on('finish', () => {
        fileStream.close();
        resolve(filename);
      });
    }).on('error', reject);
  });
}

async function main() {
  const browser = await puppeteer.launch({ headless: true });
  
  // DataForSEO
  console.log('=== DataForSEO ===');
  try {
    const page1 = await browser.newPage();
    await page1.goto('https://dataforseo.com', { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Find logo image
    const logoSrc = await page1.evaluate(() => {
      // Look for common logo patterns
      const selectors = [
        'header img[src*="logo"]',
        'img.logo',
        'img[alt*="logo" i]',
        'img[alt*="DataForSEO" i]',
        '.logo img',
        'header a img',
        'nav img',
        'img[src*="dataforseo"]'
      ];
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el && el.src) return el.src;
      }
      // Fallback - first img in header
      const headerImg = document.querySelector('header img');
      return headerImg ? headerImg.src : null;
    });
    
    if (logoSrc) {
      console.log('Found DataForSEO logo:', logoSrc);
      const ext = logoSrc.includes('.png') ? '.png' : logoSrc.includes('.svg') ? '.svg' : '.png';
      await downloadFile(logoSrc, 'dataforseo-logo' + ext);
      console.log('Downloaded!');
    } else {
      console.log('No logo found on DataForSEO homepage');
    }
    await page1.close();
  } catch (e) {
    console.log('Error with DataForSEO:', e.message);
  }
  
  // Clay
  console.log('\n=== Clay ===');
  try {
    const page2 = await browser.newPage();
    await page2.goto('https://www.clay.com', { waitUntil: 'networkidle2', timeout: 30000 });
    
    const logoSrc = await page2.evaluate(() => {
      const selectors = [
        'header img[src*="logo"]',
        'img.logo',
        'img[alt*="logo" i]',
        'img[alt*="Clay" i]',
        '.logo img',
        'header a img',
        'nav img',
        'img[src*="clay"]',
        'header svg',
        '.logo svg'
      ];
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el) {
          if (el.tagName === 'SVG') {
            return 'SVG:' + el.outerHTML;
          }
          if (el.src) return el.src;
        }
      }
      // Try to find any image in header/nav
      const headerImg = document.querySelector('header img, nav img');
      return headerImg ? headerImg.src : null;
    });
    
    if (logoSrc) {
      if (logoSrc.startsWith('SVG:')) {
        const svgContent = logoSrc.substring(4);
        fs.writeFileSync('clay-logo.svg', svgContent);
        console.log('Saved inline SVG for Clay');
      } else {
        console.log('Found Clay logo:', logoSrc);
        const ext = logoSrc.includes('.png') ? '.png' : logoSrc.includes('.svg') ? '.svg' : '.png';
        await downloadFile(logoSrc, 'clay-logo' + ext);
        console.log('Downloaded!');
      }
    } else {
      console.log('No logo found on Clay homepage');
    }
    await page2.close();
  } catch (e) {
    console.log('Error with Clay:', e.message);
  }
  
  await browser.close();
  console.log('\nDone!');
}

main().catch(console.error);
