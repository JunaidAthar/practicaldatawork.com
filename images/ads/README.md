# Ad Images Directory

This directory contains the images for Facebook Ads campaigns.

## Required Images

Upload the following 4 images to this directory:

1. **`tof_world_class_balance.jpg`** - TOF Campaign (Single Image)
   - Used for: Top of Funnel Awareness campaign
   - Format: JPG
   - Recommended size: 1200x628px (1.91:1 ratio)

2. **`mof_before_after.jpg`** - MOF Campaign (Carousel Card 1)
   - Used for: Middle of Funnel Carousel - Card 1
   - Format: JPG
   - Recommended size: 1080x1080px (1:1 ratio)

3. **`mof_dashboard.jpg`** - MOF Campaign (Carousel Card 2)
   - Used for: Middle of Funnel Carousel - Card 2
   - Format: JPG
   - Recommended size: 1080x1080px (1:1 ratio)

4. **`bof_free_assessment.jpg`** - BOF Campaign (Single Image)
   - Used for: Bottom of Funnel Conversion campaign
   - Format: JPG
   - Recommended size: 1200x628px (1.91:1 ratio)

## Image URLs

Once uploaded, images will be accessible at:
- `https://practicaldatawork.com/images/ads/tof_world_class_balance.jpg`
- `https://practicaldatawork.com/images/ads/mof_before_after.jpg`
- `https://practicaldatawork.com/images/ads/mof_dashboard.jpg`
- `https://practicaldatawork.com/images/ads/bof_free_assessment.jpg`

## Facebook Ads Image Requirements

### Single Image Ads (TOF, BOF)
- **Recommended:** 1200 x 628 pixels
- **Minimum:** 600 x 315 pixels
- **Aspect Ratio:** 1.91:1
- **Format:** JPG or PNG
- **File Size:** Max 30MB

### Carousel Ads (MOF)
- **Recommended:** 1080 x 1080 pixels (square)
- **Minimum:** 600 x 600 pixels
- **Aspect Ratio:** 1:1
- **Format:** JPG or PNG
- **File Size:** Max 30MB per image

## Upload Instructions

1. Place your 4 image files in this directory
2. Ensure filenames match exactly (case-sensitive)
3. After uploading, verify URLs work:
   ```bash
   curl -I https://practicaldatawork.com/images/ads/tof_world_class_balance.jpg
   ```
   Should return `content-type: image/jpeg` (not `text/html`)

4. Commit and push to deploy:
   ```bash
   git add images/ads/*.jpg
   git commit -m "Add Facebook ad images"
   git push
   ```

## Notes

- Images will be served via Cloudflare Pages
- After deployment, allow 2-3 minutes for CDN propagation
- Test image URLs before using in Facebook Ads Manager
- Ensure images are optimized for web (compressed but high quality)

