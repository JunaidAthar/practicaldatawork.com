# Deployment Guide - Practical Data Work

## Contact Form Setup

The contact form has been updated to send emails to **junaid.athar@gmail.com** and includes phone number **847-224-8510**.

### What Was Changed

1. **Contact Information Updated**:
   - Email: junaid.athar@gmail.com
   - Phone: 847-224-8510
   - Updated in contact section and footer

2. **Contact Form**:
   - Now sends real emails via Cloudflare Pages Functions
   - Uses MailChannels (free email service built into Cloudflare)
   - Sends formatted HTML emails with all form details

3. **Files Created**:
   - `functions/api/contact.js` - Serverless function to handle form submissions
   - `functions/README.md` - Documentation
   - `functions/test-contact-form.html` - Test page

## Deployment Steps

### 1. Test Locally (Optional but Recommended)

```bash
# Install Wrangler CLI (if not already installed)
npm install -g wrangler

# Run local development server
npx wrangler pages dev .

# Open browser to http://localhost:8788
# Test the contact form at http://localhost:8788/functions/test-contact-form.html
```

### 2. Deploy to Cloudflare Pages

Since your site is already on Cloudflare Pages, deployment is automatic:

```bash
# Commit the changes
git add .
git commit -m "Update contact info and add email functionality"
git push
```

Cloudflare Pages will automatically:
- Build and deploy your site
- Deploy the serverless function at `/api/contact`
- Enable MailChannels email delivery

### 3. Verify Email Delivery

After deployment:

1. Visit your site: https://practicaldatawork.com
2. Scroll to the contact form
3. Fill out and submit a test message
4. Check junaid.athar@gmail.com for the email

**Note**: First email might take 1-2 minutes. Subsequent emails are instant.

## Email Configuration (Optional - Better Deliverability)

To improve email deliverability and prevent emails from going to spam, add these DNS records in Cloudflare:

### SPF Record
```
Type: TXT
Name: practicaldatawork.com
Value: v=spf1 include:relay.mailchannels.net ~all
TTL: Auto
```

### Domain Verification for MailChannels
```
Type: TXT
Name: _mailchannels
Value: v=mc1 cfid=practicaldatawork.com
TTL: Auto
```

To add these:
1. Go to Cloudflare Dashboard
2. Select your domain: practicaldatawork.com
3. Go to DNS → Records
4. Click "Add record"
5. Add the records above

## Testing the Contact Form

### Online Test (After Deployment)
Visit: https://practicaldatawork.com/functions/test-contact-form.html

### Manual Test
1. Go to https://practicaldatawork.com
2. Scroll to contact section
3. Fill out the form
4. Submit
5. You should see "Thank you for your message!"
6. Check junaid.athar@gmail.com for the email

## Email Format

You'll receive emails with:
- **Subject**: "New Lead: [Name] - [Service]"
- **From**: noreply@practicaldatawork.com
- **Reply-To**: The submitter's email (so you can reply directly)
- **Content**: 
  - Name
  - Email
  - Company
  - Service Interest
  - Budget Range
  - Message
  - Timestamp
  - IP Address

## Troubleshooting

### Emails Not Arriving

**Check 1**: Verify deployment
```bash
# Check if function is deployed
curl https://practicaldatawork.com/api/contact
# Should return: Method Not Allowed (it only accepts POST)
```

**Check 2**: Test with curl
```bash
curl -X POST https://practicaldatawork.com/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Test message"
  }'
```

**Check 3**: View function logs
1. Go to Cloudflare Dashboard
2. Pages → Your project
3. View Functions logs

**Check 4**: Check spam folder
- MailChannels emails might initially go to spam
- Mark as "Not Spam" to train Gmail
- Add SPF records (see above) for better deliverability

### Form Shows Error

1. Check browser console for JavaScript errors
2. Verify the form action is `/api/contact`
3. Check network tab to see the API response
4. Ensure Cloudflare Pages function is deployed

### High Volume / Rate Limiting

MailChannels free tier includes:
- 10,000 emails per day (more than enough for contact forms)
- No credit card required
- Built into Cloudflare Pages

If you need more, consider:
- SendGrid (12,000/month free)
- Mailgun (5,000/month free)
- AWS SES (62,000/month free)

## Security Notes

- Form includes basic validation
- Cloudflare provides DDoS protection automatically
- Consider adding reCAPTCHA if you get spam
- Rate limiting can be added to the function if needed

## Support

If you encounter issues:
1. Check Cloudflare Pages build logs
2. Review function logs in Cloudflare Dashboard
3. Test with the test page: /functions/test-contact-form.html
4. Check this guide: https://developers.cloudflare.com/pages/functions/

---

Last updated: December 26, 2024

