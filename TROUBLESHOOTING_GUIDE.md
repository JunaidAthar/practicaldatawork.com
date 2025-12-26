# Troubleshooting Guide
## Fixing Common Issues on Practical Data Work

---

## 🔧 Current Issues & Solutions

### Issue 1: Blog Links Not Working (308 Redirects)

**Symptom:** Clicking blog links results in errors or redirects

**Root Cause:** Cloudflare Pages may not be processing `_redirects` file correctly

**Solutions:**

#### Option A: Use .html Extensions (Immediate Fix)
Update all blog links to include `.html`:

```html
<!-- Change from: -->
<a href="/blog/modern-data-stack">Modern Data Stack</a>

<!-- To: -->
<a href="/blog/modern-data-stack.html">Modern Data Stack</a>
```

#### Option B: Use _routes.json (Cloudflare Preferred)
The `_routes.json` file is already in place and should handle routing.

Check the file contains:
```json
{
  "version": 1,
  "include": ["/*"],
  "exclude": []
}
```

#### Option C: Remove _redirects File
If `_routes.json` is present, `_redirects` might conflict. Try:
```bash
git rm _redirects
git commit -m "Remove conflicting _redirects file"
git push
```

#### Option D: Use Cloudflare Page Rules
In Cloudflare Dashboard:
1. Go to Pages → practicaldatawork.com → Settings
2. Add custom headers or redirects
3. Or use Cloudflare Workers for routing

**Test Command:**
```bash
curl -I https://practicaldatawork.com/blog/modern-data-stack
```

Expected: `200 OK`  
If you see: `308 Permanent Redirect` → Issue confirmed

---

### Issue 2: Contact Form Not Working

**Symptom:** Form submission shows error or doesn't send email

**Root Causes & Solutions:**

#### Cause A: MailChannels Domain Not Verified

**Check if this is the issue:**
- Form submits but shows "Email delivery is being configured"
- Logs show MailChannels error

**Solution:**
Add DNS records in Cloudflare:

1. **SPF Record:**
```
Type: TXT
Name: @
Content: v=spf1 include:relay.mailchannels.net ~all
TTL: Auto
```

2. **Domain Lock Record:**
```
Type: TXT
Name: _mailchannels
Content: v=mc1 cfid=YOUR_CLOUDFLARE_ACCOUNT_ID
TTL: Auto
```

To get your Cloudflare Account ID:
- Go to Cloudflare Dashboard
- Click on any domain
- Account ID is in the right sidebar

**Verify DNS:**
```bash
dig TXT practicaldatawork.com
dig TXT _mailchannels.practicaldatawork.com
```

#### Cause B: Function Not Deployed

**Check if function exists:**
```bash
curl -X POST https://practicaldatawork.com/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Test"}'
```

Expected: JSON response with success/error  
If you see: 404 → Function not deployed

**Solution:**
Verify `functions/` directory is committed:
```bash
git add functions/
git commit -m "Add contact form function"
git push
```

Wait 2-3 minutes for Cloudflare Pages to deploy.

#### Cause C: CORS Issues

**Check browser console for:**
```
Access to fetch at 'https://practicaldatawork.com/api/contact' from origin...
has been blocked by CORS policy
```

**Solution:**
The function already includes CORS headers. If still blocked, add to `_headers`:
```
/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: POST, OPTIONS
  Access-Control-Allow-Headers: Content-Type
```

#### Cause D: Form Data Not Sent Correctly

**Check JavaScript console for errors**

The form submission code should be:
```javascript
const formData = new FormData(form);
const data = Object.fromEntries(formData.entries());

const response = await fetch('/api/contact', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
});
```

---

### Issue 3: Logo/Favicon Not Showing in Browser Tab

**Symptom:** Browser tab shows generic icon or "P" instead of logo

**Root Causes & Solutions:**

#### Cause A: Browser Cache

**Solution:**
Hard refresh the page:
- **Chrome/Firefox:** Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- **Safari:** Cmd+Option+E (clear cache), then Cmd+R

#### Cause B: Favicon Files Not Deployed

**Check if files exist:**
```bash
curl -I https://practicaldatawork.com/favicon.ico
curl -I https://practicaldatawork.com/favicon-32x32.png
curl -I https://practicaldatawork.com/images/logo.svg
```

Expected: `200 OK` for all  
If `404` → Files not deployed

**Solution:**
```bash
git add favicon*.png favicon.ico apple-touch-icon.png images/logo.svg
git commit -m "Add favicon files"
git push
```

#### Cause C: Incorrect HTML Links

**Check index.html has:**
```html
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/svg+xml" href="/images/logo.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

#### Cause D: SVG Logo Doesn't Exist

**Check if logo was created:**
```bash
ls -lh images/logo.svg
```

If missing, create it or use PNG fallback:
```html
<link rel="icon" type="image/png" href="/favicon-32x32.png">
```

#### Cause E: Favicon Size Issues

Some browsers are picky about favicon sizes.

**Verify file sizes:**
- favicon.ico: ~5KB (contains 16x16, 32x32, 48x48)
- favicon-16x16.png: ~600B
- favicon-32x32.png: ~1.3KB
- apple-touch-icon.png: ~7KB (180x180)

If files are 0 bytes or corrupted, regenerate them.

---

## 🧪 Diagnostic Tools

### Test Page
Visit: https://practicaldatawork.com/test-site.html

This page will automatically test:
- ✅ Favicon file loading
- ✅ All blog links
- ✅ Contact form submission

### Manual Testing

#### Test Blog Links:
```bash
# Should return 200 OK
curl -I https://practicaldatawork.com/blog/modern-data-stack
curl -I https://practicaldatawork.com/blog/mlops-fundamentals
curl -I https://practicaldatawork.com/blog/data-quality
```

#### Test Contact Form:
```bash
curl -X POST https://practicaldatawork.com/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "This is a test message"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Message sent successfully"
}
```

#### Test Favicon:
```bash
curl -I https://practicaldatawork.com/favicon.ico
```

Expected: `200 OK` with `Content-Type: image/x-icon`

---

## 🔍 Cloudflare Deployment Checklist

After pushing changes, verify deployment:

1. **Check Cloudflare Pages Dashboard:**
   - Go to: https://dash.cloudflare.com/
   - Pages → practicaldatawork.com
   - Look for latest deployment
   - Status should be "Success"

2. **Check Deployment Logs:**
   - Click on latest deployment
   - Review build logs for errors
   - Check if functions were deployed

3. **Wait for Propagation:**
   - DNS changes: 5-10 minutes
   - Code changes: 2-3 minutes
   - Cache purge: 1-2 minutes

4. **Purge Cache:**
   - Cloudflare Dashboard → Caching
   - Click "Purge Everything"
   - Wait 1 minute
   - Test again

---

## 🚨 Quick Fixes

### If Everything is Broken:

1. **Check Git Status:**
```bash
cd /Users/junaidathar/repo/practicaldatawork.com
git status
git log --oneline -5
```

2. **Verify Files Exist:**
```bash
ls -lh index.html
ls -lh blog/*.html
ls -lh functions/api/contact.js
ls -lh favicon*.png
```

3. **Check Cloudflare Deployment:**
- Visit: https://dash.cloudflare.com/
- Pages → practicaldatawork.com
- Latest deployment should be "Success"

4. **Test Locally:**
```bash
# Install Wrangler (Cloudflare CLI)
npm install -g wrangler

# Login
wrangler login

# Test locally
wrangler pages dev .
```

Then visit: http://localhost:8788

---

## 📞 Still Not Working?

### Check These Common Issues:

1. **DNS Not Pointing to Cloudflare:**
   - Go to domain registrar
   - Verify nameservers point to Cloudflare

2. **Cloudflare SSL/TLS Mode:**
   - Dashboard → SSL/TLS
   - Should be "Full" or "Full (strict)"

3. **Cloudflare Page Rules Conflicting:**
   - Dashboard → Rules → Page Rules
   - Remove any conflicting rules

4. **Browser Extensions Blocking:**
   - Disable ad blockers
   - Disable privacy extensions
   - Test in incognito mode

5. **Network Issues:**
   - Try different network
   - Try mobile data
   - Try VPN

---

## 📊 Expected Behavior

### Blog Links:
- ✅ `/blog/modern-data-stack` → Shows article (200 OK)
- ✅ `/blog/modern-data-stack.html` → Shows article (200 OK)
- ❌ Should NOT redirect (308)

### Contact Form:
- ✅ Submit form → "Message sent successfully"
- ✅ Email arrives at junaid.athar@gmail.com
- ❌ Should NOT show "Failed to send message"

### Favicon:
- ✅ Browser tab shows blue "P" logo
- ✅ Bookmark shows logo
- ✅ Mobile home screen shows logo
- ❌ Should NOT show generic icon

---

## 🔧 Nuclear Option (Last Resort)

If nothing works, redeploy from scratch:

```bash
# 1. Verify all files are committed
git status
git add .
git commit -m "Fix all issues"
git push

# 2. In Cloudflare Dashboard:
# - Pages → practicaldatawork.com → Settings
# - Click "Retry Deployment" on latest build
# OR
# - Delete deployment and reconnect GitHub repo

# 3. Wait 5 minutes

# 4. Purge all cache
# - Cloudflare Dashboard → Caching → Purge Everything

# 5. Hard refresh browser
# - Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

---

**Last Updated:** December 26, 2024  
**Status:** Diagnostic tools created, awaiting test results

