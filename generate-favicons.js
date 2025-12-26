#!/usr/bin/env node

/**
 * Generate Favicon Files from SVG
 * 
 * This script converts the SVG logo to various favicon formats.
 * 
 * Usage:
 *   node generate-favicons.js
 * 
 * Or install sharp and run:
 *   npm install sharp
 *   node generate-favicons.js
 */

const fs = require('fs');
const path = require('path');

// Check if sharp is available
let sharp;
try {
  sharp = require('sharp');
  console.log('✓ Sharp library found');
} catch (e) {
  console.log('⚠️  Sharp library not found. Install with: npm install sharp');
  console.log('');
  console.log('Alternative: Use an online favicon generator:');
  console.log('  1. Go to https://realfavicongenerator.net/');
  console.log('  2. Upload images/logo.svg');
  console.log('  3. Download and extract the favicons');
  console.log('  4. Replace the files in the root directory');
  console.log('');
  process.exit(1);
}

const svgPath = path.join(__dirname, 'images', 'logo.svg');
const sizes = [
  { size: 16, name: 'favicon-16x16.png' },
  { size: 32, name: 'favicon-32x32.png' },
  { size: 180, name: 'apple-touch-icon.png' },
  { size: 192, name: 'android-chrome-192x192.png' },
  { size: 512, name: 'android-chrome-512x512.png' },
];

console.log('Generating favicons from SVG...\n');

async function generateFavicons() {
  for (const { size, name } of sizes) {
    try {
      await sharp(svgPath)
        .resize(size, size)
        .png()
        .toFile(path.join(__dirname, name));
      console.log(`✓ Generated ${name} (${size}x${size})`);
    } catch (error) {
      console.error(`✗ Error generating ${name}:`, error.message);
    }
  }
  
  console.log('\n✅ Favicon generation complete!');
  console.log('\nFiles created:');
  sizes.forEach(({ name }) => console.log(`  - ${name}`));
  console.log('\nNote: For favicon.ico, use an online converter or image editor.');
}

generateFavicons().catch(console.error);

