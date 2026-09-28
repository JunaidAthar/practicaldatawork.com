# CLAUDE.md

Guidance for Claude Code in this repository.

## What this is
**Practical Data Work**: Medicare negotiated-price (MFP) refund reconciliation and recovery for independent
pharmacies. Two parts:
1. **Website** (repo root): static HTML on Cloudflare Pages with Pages Functions and a D1 database for audit requests.
2. **Engine** (`pipeline/`): `mfp-recon`, a Python package that matches dispensed MFP claims to manufacturer refunds and classifies them.

The old consulting site (2,400 SEO pages, blog, generator) is archived at tag `archive/consulting-site-2026-09-28`. Don't restore it here.

## Hard rules
- **No PHI anywhere in this repo, in commits, logs, tests, fixtures or prompts.** Use `mfp-recon synth` data. Real pharmacy files live only in HIPAA-covered storage (`docs/hipaa.md`).
- The website form collects business contact info only. Keep the "no patient information" warnings.
- Pages serves the entire repo root. `functions/_middleware.js` (Pages) and `.assetsignore` (Workers assets) block `/pipeline`, `/docs`, `*.md`, `*.toml`, `*.sql`, `*.py`, dotfiles. If you add internal folders, add them to both.
- Don't claim affiliation with CMS, NCPA, Beacon or manufacturers. Sourced statistics only (see `docs/data-sources.md`).

## Commands
```bash
# Website: local dev with Functions + D1
npx wrangler pages dev . --d1=DB:contacts

# Deploy: Cloudflare auto-deploys main; other branches get preview URLs
git push origin <branch>

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
