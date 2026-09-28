# API handlers

The site runs as a Cloudflare Worker (`worker/index.js`), which imports these handlers. They keep the Pages Functions signature so they also work on Pages.


- `_middleware.js`: Pages-only path blocker (the Worker relies on `.assetsignore`).
- `api/audit-request.js`: `POST` from the landing-page form. Business contact info only (no PHI). Saves to D1 `contacts` (pharmacy → `company`, store count → `budget`, details → `message`, `service = 'MFP refund audit'`), then tries a MailChannels notification.
- `api/contacts-list.js`: authenticated `GET` for `admin/contacts.html` (Bearer `ADMIN_PASSWORD`).
