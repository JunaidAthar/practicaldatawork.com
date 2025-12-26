# Cloudflare Pages Functions

This directory contains serverless functions that run on Cloudflare Pages.

## Contact Form Handler

The `/api/contact` endpoint handles contact form submissions and sends email notifications.

### How It Works

1. **Form Submission**: When users submit the contact form, it posts to `/api/contact`
2. **Email Delivery**: Uses MailChannels (free on Cloudflare) to send emails
3. **Recipient**: All emails are sent to `junaid.athar@gmail.com`
4. **Reply-To**: Emails are configured with the submitter's email as reply-to

### Setup Required

For the email functionality to work on Cloudflare Pages, you need to:

1. **Enable MailChannels** (it's free and built into Cloudflare Pages)
   - MailChannels is automatically available on Cloudflare Pages
   - No additional configuration needed

2. **Verify Domain** (optional, for better deliverability)
   - Go to your Cloudflare DNS settings
   - Add these DNS records:
   
   ```
   TXT record:
   Name: _mailchannels.practicaldatawork.com
   Value: v=mc1 cfid=practicaldatawork.com
   ```

3. **SPF Record** (optional, recommended)
   ```
   TXT record:
   Name: practicaldatawork.com
   Value: v=spf1 include:_spf.mx.cloudflare.net include:relay.mailchannels.net ~all
   ```

### Testing Locally

To test the contact form locally:

```bash
# Install Wrangler (Cloudflare CLI)
npm install -g wrangler

# Run development server
npx wrangler pages dev .

# The site will be available at http://localhost:8788
```

### Deployment

The function automatically deploys with your Cloudflare Pages site:

```bash
# Deploy via git push
git add .
git commit -m "Add contact form functionality"
git push

# Or deploy directly with Wrangler
npx wrangler pages deploy .
```

### Email Format

Emails sent to you will include:
- Sender's name and email (with reply-to configured)
- Company name (if provided)
- Service interest (if selected)
- Budget range (if selected)
- Message content
- Timestamp and IP address

### Troubleshooting

**Form not sending emails:**
1. Check browser console for errors
2. Verify the form posts to `/api/contact`
3. Check Cloudflare Pages function logs
4. Ensure MailChannels is not blocked

**Emails going to spam:**
1. Add SPF record to DNS
2. Verify domain ownership
3. Consider setting up DKIM

**Rate limiting:**
- MailChannels has generous free limits
- Consider adding rate limiting if needed
- Cloudflare provides DDoS protection automatically

### Alternative Email Services

If you prefer a different email service, you can modify the function to use:

- **SendGrid**: Requires API key
- **Mailgun**: Requires API key and domain verification
- **AWS SES**: Requires AWS credentials
- **Resend**: Modern alternative with good free tier

To switch services, update the `fetch()` call in `functions/api/contact.js` with your chosen provider's API.

