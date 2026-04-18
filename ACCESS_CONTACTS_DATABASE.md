# 📊 How to Access Your Contacts Database

## Method 1: Admin Panel (Easiest) ✅

**URL:** https://practicaldatawork.com/admin/contacts.html

**Password:** `***REDACTED***`

This is a web-based admin panel where you can:
- View all contact submissions
- Filter by status (new, contacted, converted, etc.)
- Search contacts
- Export data
- Mark contacts as contacted/converted

**Features:**
- Clean, user-friendly interface
- Real-time data from D1 database
- No technical knowledge required

---

## Method 2: Cloudflare Dashboard

1. Go to: https://dash.cloudflare.com/
2. Select your account
3. Go to **Workers & Pages** → **D1**
4. Find database: **contacts**
5. Click on it to view and query data

**You can:**
- View all records
- Run SQL queries
- Export data
- View database schema

---

## Method 3: Wrangler CLI (Command Line)

### View All Contacts

```bash
cd /Users/junaidathar/repo/practicaldatawork.com
npx wrangler d1 execute contacts --command "SELECT * FROM contacts ORDER BY created_at DESC"
```

### View Recent Contacts

```bash
npx wrangler d1 execute contacts --command "SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10"
```

### Count Contacts

```bash
npx wrangler d1 execute contacts --command "SELECT COUNT(*) as total FROM contacts"
```

### View by Status

```bash
npx wrangler d1 execute contacts --command "SELECT * FROM contacts WHERE status = 'new'"
```

### Export to CSV

```bash
npx wrangler d1 execute contacts --command "SELECT * FROM contacts" --output=contacts.csv
```

---

## Method 4: API Endpoint (Programmatic)

**Endpoint:** `https://practicaldatawork.com/api/contacts-list`

**Authentication:** Password required (same as admin panel)

**Example Request:**

```bash
curl "https://practicaldatawork.com/api/contacts-list?password=***REDACTED***"
```

**Response:** JSON array of all contacts

---

## Database Details

- **Database Name:** `contacts`
- **Database ID:** `9ef2d0a0-ca96-43de-940d-e3bb667f6c27`
- **Table:** `contacts`

### Table Schema

```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    service TEXT,
    budget TEXT,
    message TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'new'
);
```

### Status Values

- `new` - New contact (default)
- `contacted` - You've reached out
- `converted` - Became a client
- `archived` - No longer relevant

---

## Quick Access Links

- **Admin Panel:** https://practicaldatawork.com/admin/contacts.html
- **Cloudflare D1:** https://dash.cloudflare.com/ → Workers & Pages → D1
- **API Endpoint:** https://practicaldatawork.com/api/contacts-list

---

## Recommended Method

**Use the Admin Panel** - It's the easiest and most user-friendly way to view and manage your contacts!

Just go to: **https://practicaldatawork.com/admin/contacts.html**

Password: `***REDACTED***`


