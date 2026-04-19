# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this site is

Marketing and lead-generation website for **Practical Data Work**, a data consulting business. The site is deployed on **Cloudflare Pages** with serverless functions for backend logic.

## Key commands

```bash
# Deploy (Cloudflare Pages auto-deploys on push to main)
git push origin main

# Regenerate all ~2,400 programmatic SEO pages
node generate-pages.js

# Query the contacts database (production)
npx wrangler d1 execute contacts --command="SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10" --remote

# Local dev with Cloudflare Workers support
npx wrangler pages dev . --d1=DB:contacts
```

## Architecture

**Static HTML site** — no build step, no framework. Every page is a plain `.html` file served directly by Cloudflare Pages.

### Programmatic SEO pages (~2,400 files)
`generate-pages.js` generates all pages under `consulting/`, `consulting/industries/`, `compare/`, `guides/`, and `directory/`. **Do not manually edit files in those directories** — changes will be overwritten the next time the generator runs. Edit the templates and data inside `generate-pages.js` instead.

### Cloudflare Pages Functions (`functions/api/`)
- `contact.js` — handles contact form `POST`, saves to D1 database first, then sends email via MailChannels
- `contacts-list.js` — authenticated `GET` endpoint for the admin panel; reads `ADMIN_PASSWORD` from `env` (Cloudflare secret)

### Admin panel
`admin/contacts.html` — browser-only UI that calls `/api/contacts-list` with a Bearer token. Password is set as a Cloudflare Pages secret named `ADMIN_PASSWORD` (not in code).

### D1 database
Binding name `DB`, database name `contacts`. Schema is in `setup-database.sql`. The `wrangler.toml` has the database ID.

## Secrets and environment

- **`ADMIN_PASSWORD`** — set as a Cloudflare Pages secret (Dashboard → Settings → Environment Variables). For local dev, put it in `.dev.vars` (gitignored).
- Never hardcode credentials in source files or documentation.

## Deploying secrets to Cloudflare

```bash
npx wrangler pages secret put ADMIN_PASSWORD
```

## Content Security Policy

The `_headers` file sets CSP and security headers for all routes. If adding new external scripts or fonts, update `_headers` — inline scripts require `'unsafe-inline'` which is already allowed.
