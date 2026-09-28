# Cloudflare Pages Functions

- `_middleware.js`: blocks internal paths (`/pipeline`, `/docs`, `*.md`, `*.toml`, `*.sql`, `*.py`, dotfiles) from being served. **Keep this**: Pages serves the whole repo root.
- `api/audit-request.js`: `POST` from the landing-page form. Business contact info only (no PHI). Saves to D1 `contacts` (pharmacy → `company`, store count → `budget`, details → `message`, `service = 'MFP refund audit'`), then tries a MailChannels notification.
- `api/contacts-list.js`: authenticated `GET` for `admin/contacts.html` (Bearer `ADMIN_PASSWORD`).
