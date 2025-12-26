# Facebook Pixel Installation Guide
## Step-by-Step Setup for Practical Data Work

---

## ✅ What Was Installed

### Files Updated:
1. **index.html** - Added Facebook Pixel with event tracking
2. **pixel-test.html** - NEW test page to verify pixel is working

### Events Configured:
- ✅ **PageView** - Tracks all page visits
- ✅ **ViewContent** - Tracks homepage visits
- ✅ **Lead** - Tracks contact form submissions
- ⏳ **Schedule** - Ready for consultation bookings
- ⏳ **Purchase** - Ready for client conversions

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your Facebook Pixel ID

1. Go to **Facebook Events Manager**:
   https://business.facebook.com/events_manager2

2. Click **"Connect Data Sources"** → **"Web"**

3. Click **"Get Started"** → **"Meta Pixel"**

4. Name it: **"Practical Data Work Pixel"**

5. Click **"Create Pixel"**

6. Copy your **Pixel ID** (looks like: `123456789012345`)

### Step 2: Update Your Website Code

Replace `YOUR_PIXEL_ID` with your actual Pixel ID in these files:

#### File 1: index.html (Line ~44)
```javascript
var pixelId = 'YOUR_PIXEL_ID';  // ← Replace this
```

#### File 2: pixel-test.html (Line ~108)
```javascript
var pixelId = 'YOUR_PIXEL_ID';  // ← Replace this
```

**Also update the noscript tag in both files:**
```html
<img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=YOUR_PIXEL_ID&ev=PageView&noscript=1"/>
```
Change `YOUR_PIXEL_ID` to your actual ID.

### Step 3: Deploy Changes

```bash
git add index.html pixel-test.html
git commit -m "Add Facebook Pixel tracking"
git push
```

Wait 2-3 minutes for Cloudflare Pages to deploy.

### Step 4: Test Your Pixel

1. **Install Facebook Pixel Helper** (Chrome Extension):
   https://chrome.google.com/webstore/detail/facebook-pixel-helper/fdgfkebogiimcoedlicjlajpkdmockpc

2. **Visit your test page**:
   https://practicaldatawork.com/pixel-test.html

3. **Look for the Pixel Helper icon** in your browser toolbar:
   - 🟢 Green checkmark = Pixel is working!
   - 🔴 Red = Pixel has errors (check Pixel ID)

4. **Click the test buttons** on the test page:
   - Test PageView
   - Test ViewContent  
   - Test Lead
   - Test Schedule
   - Test Purchase

5. **Verify in Facebook Events Manager**:
   - Go to: https://business.facebook.com/events_manager2
   - Click your pixel
   - Click "Test Events" tab
   - You should see events appearing within 5-10 minutes

---

## 📊 What Each Event Tracks

### PageView
**Fires on:** Every page load  
**Purpose:** Track website traffic, build retargeting audiences  
**Data sent:** Page URL, referrer

```javascript
fbq('track', 'PageView');
```

### ViewContent (Homepage)
**Fires on:** Homepage visits  
**Purpose:** Track engagement with main page  
**Data sent:**
```javascript
{
  content_name: 'Homepage',
  content_category: 'Main'
}
```

### Lead (Contact Form)
**Fires on:** Successful form submission  
**Purpose:** Track lead generation  
**Data sent:**
```javascript
{
  content_name: 'Contact Form Submission',
  content_category: 'Contact',
  value: 10.00,
  currency: 'USD'
}
```

**Triggers when:** Contact form successfully submits
**Location:** index.html line ~722

### Schedule (Consultation Booking)
**Ready for:** When you set up Calendly or booking system  
**Purpose:** Track consultation bookings  
**Data sent:**
```javascript
{
  content_name: 'Free Consultation Booked',
  value: 50.00,
  currency: 'USD'
}
```

**How to implement:** Add this code to your booking confirmation page.

### Purchase (Client Conversion)
**Ready for:** When client signs contract  
**Purpose:** Track revenue and ROI  
**Data sent:**
```javascript
{
  value: 5000.00,  // Actual contract value
  currency: 'USD',
  content_name: 'Professional Plan'  // Service tier
}
```

**How to implement:** Fire this event when contract is signed.

---

## 🧪 Testing Checklist

### Basic Verification
- [ ] Pixel Helper shows green checkmark
- [ ] PageView event fires on every page
- [ ] No console errors
- [ ] Events appear in Events Manager within 10 minutes

### Event Testing
- [ ] Homepage visit triggers ViewContent
- [ ] Contact form submission triggers Lead
- [ ] Test page buttons all fire correct events
- [ ] Event parameters are correct in Events Manager

### Cross-Browser Testing
- [ ] Chrome ✅
- [ ] Firefox ✅
- [ ] Safari ✅
- [ ] Mobile browsers ✅

---

## 🎯 Next Steps: Setting Up Custom Conversions

Once your pixel is firing correctly, create custom conversions in Ads Manager.

### Step 1: Create Custom Conversions

1. Go to **Events Manager** → **Custom Conversions**
2. Click **"Create Custom Conversion"**

### Conversion 1: Lead Magnet Download
```
Name: Lead Magnet Download
Event: Lead
Rules: content_name contains "Checklist"
Value: $10
Category: Lead
```

### Conversion 2: Consultation Booked
```
Name: Consultation Booked
Event: Schedule
Value: $50
Category: Lead
```

### Conversion 3: Client Conversion
```
Name: Client - Professional Plan
Event: Purchase
Rules: value equals 5000
Value: $5,000
Category: Purchase
```

### Step 2: Use in Ad Campaigns

When creating ads:
1. Set optimization goal to your custom conversion
2. Facebook will optimize to show ads to people likely to complete that action
3. Track ROI based on actual revenue

---

## 📈 Building Retargeting Audiences

With the pixel active, you can create powerful retargeting audiences:

### Audience 1: Website Visitors (Last 30 Days)
**Who:** Anyone who visited your site  
**Use for:** MOF carousel ads  
**Setup:**
- Events Manager → Audiences → Create Audience
- Custom Audience → Website
- Event: PageView
- Retention: 30 days

### Audience 2: Homepage Viewers (Last 14 Days)
**Who:** People who viewed homepage but didn't convert  
**Use for:** TOF retargeting, MOF lead magnet  
**Setup:**
- Event: ViewContent
- Filter: content_name = Homepage
- Retention: 14 days

### Audience 3: Lead Magnet Downloaders
**Who:** People who downloaded checklist  
**Use for:** BOF consultation ads  
**Setup:**
- Event: Lead
- Filter: content_name contains Checklist
- Retention: 60 days

### Audience 4: Consultation Page Visitors (Non-Bookers)
**Who:** Visited booking page but didn't book  
**Use for:** Urgency ads ("5 spots left")  
**Setup:**
- Event: PageView
- URL contains: /consultation
- Exclude: People who triggered Schedule event
- Retention: 7 days

---

## 🔧 Troubleshooting

### Pixel Not Firing

**Symptom:** Pixel Helper shows no pixel found

**Solutions:**
1. Check if Pixel ID is updated from 'YOUR_PIXEL_ID'
2. View page source, search for `fbq('init'`
3. Check console for JavaScript errors
4. Disable ad blockers
5. Test in incognito mode

### Events Not in Events Manager

**Symptom:** Pixel fires but no events in dashboard

**Solutions:**
1. Wait 15-20 minutes (data delay is normal)
2. Check "Test Events" tab (shows real-time data)
3. Verify Pixel ID matches in code and Events Manager
4. Check if events are blocked by Facebook (some parameters might be invalid)

### Contact Form Not Triggering Lead Event

**Symptom:** Form submits but no Lead event

**Current Status:** 
- Contact form has MailChannels email issue
- Pixel code is ready but form needs to work first
- See MAILCHANNELS_SETUP.md for email fix

**Solutions:**
1. Fix MailChannels DNS setup (required for form to work)
2. Test form submission works
3. Check console for JavaScript errors
4. Verify Lead event code is after successful submission

### Multiple PageView Events

**Symptom:** Pixel Helper shows PageView fired twice

**This is normal:**
- Base pixel fires PageView automatically
- Homepage also fires ViewContent
- Both events are useful for different purposes

---

## 🎓 Advanced: Server-Side Tracking (Optional)

For better tracking accuracy (bypasses ad blockers), consider server-side events.

### Benefits:
- More accurate (not blocked by ad blockers)
- Better attribution
- iOS 14.5+ compatibility

### Implementation:
Use Cloudflare Pages Functions to send events server-side:

```javascript
// In your contact form function
const response = await fetch('https://graph.facebook.com/v18.0/{PIXEL_ID}/events', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data: [{
      event_name: 'Lead',
      event_time: Math.floor(Date.now() / 1000),
      user_data: {
        em: hashedEmail,  // SHA256 hashed
        ph: hashedPhone,
      },
      custom_data: {
        value: 10.00,
        currency: 'USD',
      }
    }],
    access_token: 'YOUR_CONVERSION_API_TOKEN'
  })
});
```

**When to implement:** After basic pixel is working and you have consistent lead flow.

---

## 📊 Expected Results Timeline

### Week 1: Learning Phase
- Pixel collecting data
- Building retargeting audiences
- Don't optimize yet, let Facebook learn

### Week 2: Initial Optimization
- Review which events fire most
- Create custom conversions
- Set up retargeting audiences
- Start using pixel data in ad optimization

### Week 3: Attribution Data
- View attribution reports
- See which campaigns drive conversions
- Adjust budget based on pixel data

### Month 2+: Full Optimization
- Optimize for pixel events (not just clicks)
- Use lookalike audiences based on converters
- Track full funnel from ad to client
- Calculate true ROI with purchase events

---

## 🔗 Quick Reference Links

- **Events Manager:** https://business.facebook.com/events_manager2
- **Pixel Helper:** https://chrome.google.com/webstore/detail/facebook-pixel-helper/fdgfkebogiimcoedlicjlajpkdmockpc
- **Test Page:** https://practicaldatawork.com/pixel-test.html
- **Ads Manager:** https://business.facebook.com/adsmanager
- **Custom Conversions:** https://business.facebook.com/events_manager2/list/pixel/custom_conversions

---

## ✅ Installation Complete!

Your Facebook Pixel is now installed and ready to track. Next steps:

1. ✅ **Replace YOUR_PIXEL_ID** with actual Pixel ID
2. ✅ **Deploy changes** to production
3. ✅ **Test on pixel-test.html** page
4. ✅ **Verify in Events Manager**
5. ⏭️ **Fix contact form** (MailChannels DNS)
6. ⏭️ **Create custom conversions**
7. ⏭️ **Build retargeting audiences**
8. ⏭️ **Launch campaigns!**

---

**Last Updated:** December 26, 2024  
**Status:** Pixel code installed, waiting for Pixel ID configuration  
**Next:** Get Pixel ID from Events Manager and update code

