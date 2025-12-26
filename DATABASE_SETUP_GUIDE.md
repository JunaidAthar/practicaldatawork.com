# Cloudflare D1 Database Setup Guide

## Step-by-Step Instructions (15 minutes)

---

## Step 1: Create the D1 Database

### Option A: Using Cloudflare Dashboard (Easiest)

1. Go to: https://dash.cloudflare.com/
2. Click **Workers & Pages** in the left sidebar
3. Click **D1 SQL Database** tab at the top
4. Click **"Create database"** button
5. Enter database name: `contacts`
6. Click **"Create"**

### Option B: Using Wrangler CLI

```bash
cd /Users/junaidathar/repo/practicaldatawork.com

# Login to Cloudflare (if not already)
npx wrangler login

# Create the database
npx wrangler d1 create contacts
```

**Save the output!** It will show something like:
```
✅ Successfully created DB 'contacts'!

[[d1_databases]]
binding = "DB"
database_name = "contacts"
database_id = "xxxx-xxxx-xxxx-xxxx"
```

---

## Step 2: Update wrangler.toml

Open `wrangler.toml` and add this at the end:

```toml
[[d1_databases]]
binding = "DB"
database_name = "contacts"
database_id = "YOUR_DATABASE_ID_FROM_STEP_1"
```

**Replace `YOUR_DATABASE_ID_FROM_STEP_1` with the actual database_id from the previous step.**

---

## Step 3: Create the Database Table

### Option A: Using Cloudflare Dashboard

1. In Cloudflare Dashboard → D1 SQL Database
2. Click on your **contacts** database
3. Click **"Console"** tab
4. Copy and paste the contents of `setup-database.sql`
5. Click **"Execute"**

### Option B: Using Wrangler CLI

```bash
cd /Users/junaidathar/repo/practicaldatawork.com

# Run the setup script
npx wrangler d1 execute contacts --file=setup-database.sql
```

You should see:
```
✅ Executed setup-database.sql
```

---

## Step 4: Bind Database to Pages Project

### Option A: Using Cloudflare Dashboard

1. Go to: https://dash.cloudflare.com/
2. Workers & Pages → **practicaldatawork.com**
3. Click **"Settings"** tab
4. Scroll to **"Bindings"**
5. Click **"Add"** → **"D1 database"**
6. Variable name: `DB`
7. D1 database: Select **contacts**
8. Click **"Save"**

### Option B: Update wrangler.toml (Already Done in Step 2)

The binding is already set in `wrangler.toml`, so when you deploy, it will be bound automatically.

---

## Step 5: Deploy Updated Code

```bash
cd /Users/junaidathar/repo/practicaldatawork.com

# Commit changes
git add .
git commit -m "Add D1 database storage for contacts"
git push

# Wait 2-3 minutes for Cloudflare Pages to deploy
```

---

## Step 6: Test the Contact Form

1. Go to: https://practicaldatawork.com/#contact
2. Fill out and submit the form
3. You should see: "Message sent successfully!"

---

## Step 7: View Your Contacts

### Option A: Admin Panel (Best)

Visit: **https://practicaldatawork.com/admin/contacts.html**

Username: `admin`  
Password: (I'll set this up for you - check the next section)

### Option B: D1 Console (Cloudflare Dashboard)

1. Go to: https://dash.cloudflare.com/
2. D1 SQL Database → **contacts**
3. Click **"Console"** tab
4. Run queries:

```sql
-- View all contacts
SELECT * FROM contacts ORDER BY created_at DESC;

-- View only new contacts
SELECT * FROM contacts WHERE status = 'new' ORDER BY created_at DESC;

-- Count total contacts
SELECT COUNT(*) as total FROM contacts;

-- Search by email
SELECT * FROM contacts WHERE email LIKE '%@gmail.com%';
```

### Option C: Using Wrangler CLI

```bash
# View all contacts
npx wrangler d1 execute contacts --command="SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10"

# Count contacts
npx wrangler d1 execute contacts --command="SELECT COUNT(*) as total FROM contacts"
```

---

## Database Schema

Your `contacts` table has these fields:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-incrementing ID |
| name | TEXT | Contact's name |
| email | TEXT | Contact's email |
| company | TEXT | Company name (optional) |
| service | TEXT | Service interest (optional) |
| budget | TEXT | Budget range (optional) |
| message | TEXT | Contact message |
| ip_address | TEXT | Visitor's IP |
| user_agent | TEXT | Browser info |
| created_at | TEXT | Timestamp (ISO 8601) |
| status | TEXT | 'new', 'contacted', 'converted', 'closed' |
| notes | TEXT | Your notes about the contact |

---

## Admin Panel Features

The admin panel I'm creating will have:

- ✅ View all contacts in a table
- ✅ Search and filter
- ✅ Mark status (new, contacted, converted, closed)
- ✅ Add notes to each contact
- ✅ Export to CSV
- ✅ View full conversation history
- ✅ Click to email or call
- ✅ Mobile-responsive

---

## Security

The admin panel will be protected by:
- Password authentication (stored securely)
- Rate limiting
- Only accessible to you

---

## Free Tier Limits

Cloudflare D1 Free Tier includes:
- ✅ 5 GB storage (enough for ~50,000 contacts)
- ✅ 5 million read queries per day
- ✅ 100,000 write queries per day
- ✅ Unlimited databases

You'll never hit these limits for a contact form! 🎉

---

## Next Steps

1. Create the D1 database (Step 1)
2. Get the database_id
3. Tell me the database_id and I'll update wrangler.toml
4. I'll deploy the updated code
5. You'll have a working database with admin panel!

---

## Troubleshooting

### Error: "DB is not defined"

**Solution:** The D1 binding isn't set up. Make sure you:
1. Added the binding in wrangler.toml
2. Bound it to the Pages project in dashboard
3. Redeployed the project

### Error: "no such table: contacts"

**Solution:** The table wasn't created. Run the setup SQL:
```bash
npx wrangler d1 execute contacts --file=setup-database.sql
```

### Error: "Cannot read properties of undefined (reading 'prepare')"

**Solution:** The D1 database isn't available to the function. Check the binding in Settings → Bindings.

---

**Ready?** Let's start with Step 1 - create the database!

