# API handlers

The site runs as a Cloudflare Worker (`worker/index.js`), which imports these handlers. They keep the Pages Functions signature so they also work on Pages.


- `_middleware.js`: Pages-only path blocker (the Worker relies on `.assetsignore`).
- `api/audit-request.js`: `POST` from the landing-page form. Business contact info only (no PHI). Saves to D1 table `audit_requests` (one column per form field, see `setup-database.sql`), then tries a MailChannels notification.
- `api/contacts-list.js`: authenticated `GET` for `admin/contacts.html` (Bearer `ADMIN_PASSWORD`).
