# Practical Data Work: MFP refund recovery for independent pharmacies

practicaldatawork.com now markets and runs a Medicare negotiated-price (MFP) refund reconciliation and
recovery service for independent pharmacies. The previous data-consulting site is archived at tag
`archive/consulting-site-2026-09-28` and branch `archive/consulting-site`.

| Path | What |
|---|---|
| `index.html`, `privacy.html`, `404.html`, `styles.css`, `assets/`, `images/` | Public website (static, Cloudflare Pages) |
| `functions/` | Pages Functions: audit-request form API, admin API, path-blocking middleware |
| `admin/contacts.html` | Password-protected view of form submissions (D1) |
| `pipeline/` | `mfp-recon` Python reconciliation engine (synthetic data only in repo) |
| `docs/` | HIPAA checklist, data sources, sales playbook, unit-economics model |

See `CLAUDE.md` for commands and conventions.
