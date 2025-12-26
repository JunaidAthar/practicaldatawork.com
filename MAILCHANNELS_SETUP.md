# MailChannels Setup for Cloudflare Pages

## How MailChannels Works on Cloudflare

MailChannels is **automatically available** on Cloudflare Pages/Workers - no API key needed. However, domain verification improves deliverability and prevents your emails from being marked as spam.

## Check Current Status

### 1. Test if MailChannels is working
```bash
curl -X POST https://practicaldatawork.com/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Test message"
  }'
```

### 2. Check Cloudflare Pages Function Logs
1. Go to: https://dash.cloudflare.com/
2. Select your account
3. Go to **Pages** → **practicaldatawork** (your project)
4. Click **Functions** tab
5. View the logs to see the actual error from MailChannels

**Common Error Messages:**
- `"Sender domain not allowed"` = Domain verification required
- `"Relay access denied"` = SPF record needed
- `"Invalid sender"` = FROM email domain must match your domain

## Domain Verification Setup

### Step 1: Add SPF Record (Required)

Go to Cloudflare Dashboard → DNS → Records → Add record

```
Type: TXT
Name: @ (or practicaldatawork.com)
Content: v=spf1 include:relay.mailchannels.net ~all
TTL: Auto
```

**Check if SPF exists:**
```bash
dig TXT practicaldatawork.com +short | grep spf
```

### Step 2: Add Domain Lock Record (Recommended)

This prevents others from sending emails using your domain through MailChannels.

```
Type: TXT
Name: _mailchannels
Content: v=mc1 cfid=practicaldatawork.com
TTL: Auto
```

**Verify:**
```bash
dig TXT _mailchannels.practicaldatawork.com +short
```

### Step 3: Add DKIM (Optional, Better Deliverability)

DKIM helps prevent emails from going to spam.

1. **Generate DKIM keys** using MailChannels:
   - Contact MailChannels support or use their API
   - Or use a DKIM generator: https://www.mailhardener.com/tools/dkim-generator

2. **Add DKIM DNS Record:**
```
Type: TXT
Name: mailchannels._domainkey
Content: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE
TTL: Auto
```

### Step 4: Update Contact Function

The contact function needs to specify DKIM domain and selector:

```javascript
personalizations: [
  {
    to: [{ email: 'junaid.athar@gmail.com', name: 'Junaid Athar' }],
    dkim_domain: 'practicaldatawork.com',  // Add this
    dkim_selector: 'mailchannels',         // Add this
  },
],
```

## Verify DNS Records

```bash
# Check SPF
dig TXT practicaldatawork.com +short

# Check domain lock
dig TXT _mailchannels.practicaldatawork.com +short

# Check DKIM (if configured)
dig TXT mailchannels._domainkey.practicaldatawork.com +short
```

## Alternative: Use FormSpree (Easier Setup)

If MailChannels continues to have issues, FormSpree is a popular alternative:

### FormSpree Setup (5 minutes)

1. **Sign up**: https://formspree.io/ (free tier: 50 submissions/month)

2. **Create a form** and get your form ID

3. **Update contact form** in `index.html`:
```html
<form class="form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  <!-- Keep existing fields -->
</form>
```

4. **Update JavaScript** (remove fetch, let form submit naturally):
```javascript
// Remove the fetch logic, form will submit to FormSpree
```

## Alternative: Use Web3Forms (No Account Required)

1. Get access key: https://web3forms.com/ (free, 250/month)

2. **Add hidden field to form**:
```html
<input type="hidden" name="access_key" value="YOUR_ACCESS_KEY">
```

3. **Update form action**:
```html
<form action="https://api.web3forms.com/submit" method="POST">
```

## Troubleshooting

### Check Function Logs
1. Cloudflare Dashboard → Pages → Your Project
2. Functions tab → View logs
3. Look for MailChannels API response

### Test with curl
```bash
# Test the API directly
curl -X POST https://api.mailchannels.net/tx/v1/send \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{
      "to": [{"email": "junaid.athar@gmail.com"}]
    }],
    "from": {
      "email": "noreply@practicaldatawork.com",
      "name": "Test"
    },
    "subject": "Test",
    "content": [{
      "type": "text/plain",
      "value": "Test message"
    }]
  }'
```

### Common Issues

**Issue**: "Sender domain not allowed"
**Solution**: Add SPF record (Step 1)

**Issue**: "Invalid sender"  
**Solution**: Use `noreply@practicaldatawork.com` not a different domain

**Issue**: Emails go to spam
**Solution**: Add SPF + DKIM records

**Issue**: Still not working after DNS changes
**Solution**: Wait 15-30 minutes for DNS propagation

## Current Status Check

Run this to see what DNS records you currently have:

```bash
echo "=== SPF Record ==="
dig TXT practicaldatawork.com +short | grep spf

echo -e "\n=== Domain Lock ==="
dig TXT _mailchannels.practicaldatawork.com +short

echo -e "\n=== DKIM ==="
dig TXT mailchannels._domainkey.practicaldatawork.com +short
```

## Recommended Quick Fix

**Option 1: Add SPF Record** (2 minutes)
1. Go to Cloudflare DNS
2. Add SPF TXT record
3. Wait 5-10 minutes
4. Test form again

**Option 2: Use FormSpree** (5 minutes)
1. Sign up at formspree.io
2. Update form action URL
3. Deploy
4. Works immediately

## Need Help?

Check Cloudflare Pages Function logs for the exact error message, then:
1. If it's DNS related → Add SPF/DKIM records
2. If it's a MailChannels API error → Consider FormSpree
3. If logs show success but no email → Check spam folder

---
Last updated: December 26, 2024

