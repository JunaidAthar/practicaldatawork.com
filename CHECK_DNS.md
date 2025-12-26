# DNS Verification & Contact Form Debug Guide

## Step 1: Verify DNS Records Are Correct

Run these commands in your terminal to verify the DNS records:

```bash
# Check SPF record
dig TXT practicaldatawork.com +short

# Check Domain Lock record
dig TXT _mailchannels.practicaldatawork.com +short
```

**Expected results:**

SPF should show:
```
"v=spf1 include:relay.mailchannels.net ~all"
```

Domain Lock should show:
```
"v=mc1 cfid=YOUR_CLOUDFLARE_ACCOUNT_ID"
```

If you don't see these, DNS hasn't propagated yet (wait 5-10 more minutes).

---

## Step 2: Check Cloudflare Pages Logs

Your contact form submissions are currently being logged in Cloudflare. Here's how to see them:

### Option A: Real-Time Logs (Best for Debugging)

1. Go to: https://dash.cloudflare.com/
2. Click on your account → **Workers & Pages**
3. Click on **practicaldatawork.com** project
4. Click on the **latest deployment** (at the top)
5. Click **"View details"**
6. Click **"Real-time Logs"** or **"Begin log stream"**
7. Submit a test form
8. Watch the logs appear in real-time

**What to look for:**
- `Contact form submission:` - Shows the form was received
- `MailChannels error:` - Shows why email isn't sending
- Any error messages about DNS or authentication

### Option B: Function Logs (Historical)

1. Go to: https://dash.cloudflare.com/
2. Workers & Pages → practicaldatawork.com
3. Click **"Logs"** tab
4. Filter by date/time
5. Look for `/api/contact` requests

---

## Step 3: Test Email Sending Directly

Let me create a test page that will show you the exact error from MailChannels:

