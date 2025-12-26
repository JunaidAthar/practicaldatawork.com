#!/usr/bin/env node

/**
 * Generate favicon.ico from PNG
 * Uses the to-ico package to create a multi-resolution .ico file
 */

const fs = require('fs');
const path = require('path');

// Try to load to-ico
let toIco;
try {
  toIco = require('to-ico');
} catch (e) {
  console.log('Installing to-ico package...');
  require('child_process').execSync('npm install to-ico --no-save', { stdio: 'inherit' });
  toIco = require('to-ico');
}

const sharp = require('sharp');

async function generateFaviconIco() {
  console.log('Generating favicon.ico...');
  
  // Read the 16x16 and 32x32 PNGs
  const png16 = fs.readFileSync(path.join(__dirname, 'favicon-16x16.png'));
  const png32 = fs.readFileSync(path.join(__dirname, 'favicon-32x32.png'));
  
  // Create ICO with multiple sizes
  const ico = await toIco([png16, png32]);
  
  // Write the ICO file
  fs.writeFileSync(path.join(__dirname, 'favicon.ico'), ico);
  
  console.log('✓ Generated favicon.ico');
  console.log('\n✅ All favicons generated successfully!');
}

generateFaviconIco().catch(console.error);

