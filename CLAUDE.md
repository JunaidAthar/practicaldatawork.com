# CLAUDE.md

Guidance for Claude Code in this repository.

## What this is
**Practical Data Work**: Medicare negotiated-price (MFP) refund reconciliation and recovery for independent
pharmacies. Two parts:
1. **Website** (repo root): static HTML deployed as a **Cloudflare Worker with static assets** (`wrangler.toml`). `worker/index.js` routes `/api/*` to the handlers in `functions/api/` and serves everything else from assets. D1 database `contacts` stores audit requests.
2. **Engine** (`pipeline/`): `mfp-recon`, a Python package that matches dispensed MFP claims to manufacturer refunds and classifies them.

The old consulting site (2,400 SEO pages, blog, generator) is archived at tag `archive/consulting-site-2026-09-28`. Don't restore it here.

## Hard rules
- **No PHI anywhere in this repo, in commits, logs, tests, fixtures or prompts.** Use `mfp-recon synth` data. Real pharmacy files live only in HIPAA-covered storage (`docs/hipaa.md`).
- The website form collects business contact info only. Keep the "no patient information" warnings.
- The Worker serves the repo root as static assets. `.assetsignore` excludes internal files (`pipeline`, `docs`, `worker`, `functions`, `*.md`, `*.toml`, `*.sql`, `*.py`, dotfiles); `functions/_middleware.js` does the same if ever deployed on Pages. If you add internal folders, add them to both.
- Infrastructure for client data is **Google Cloud** (+ Google Workspace), each under its own BAA. See `docs/infrastructure.md` and `docs/hipaa.md`. Don't introduce AWS/Azure.
- Don't claim affiliation with CMS, NCPA, Beacon or manufacturers. Sourced statistics only (see `docs/data-sources.md`).

## Commands
```bash
# Website: dry-run the Worker bundle (wrangler dev reload-loops because assets dir is the repo root)
npx wrangler deploy --dry-run --outdir /tmp/pdw-out

# Deploy: pushing main triggers the Cloudflare build
git push origin main

# Audit requests (production D1)
npx wrangler d1 execute contacts --remote --command="SELECT created_at,name,email,company,budget,message FROM contacts WHERE service='MFP refund audit' ORDER BY created_at DESC LIMIT 20"

# Engine
cd pipeline && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]" && pytest -q
mfp-recon synth --out data/synthetic
mfp-recon reconcile --dispenses data/synthetic/dispenses.csv --refunds data/synthetic/refunds.csv --prices data/synthetic/prices.csv --as-of 2026-09-28
mfp-recon opais-check --export <OPAIS export.xlsx> --name "<pharmacy>" --zip <zip>

# Sales PDFs -> assets/
python docs/sales/build_sales_pdfs.py   # requires: pip install playwright && playwright install chromium
```

## Secrets
`ADMIN_PASSWORD` (Pages secret; `.dev.vars` locally, gitignored). Optional `NOTIFY_EMAIL` for form notifications.

## Engine conventions
- Canonical tables: `dispenses`, `refunds`, `prices` (see `pipeline/README.md`). Source adapters (MTF 835, Beacon reports, pharmacy-system exports) convert raw files into these; build and test them against synthetic fixtures shaped like real files.
- Status logic lives in `pipeline/src/mfp_recon/reconcile.py`; add a test for every rule change.
