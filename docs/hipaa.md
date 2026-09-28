# HIPAA setup checklist (Google stack)

We are a **business associate** of each pharmacy once we receive claim data. Nothing real moves until these are done.
Our stack: **Google Workspace** (email, early file intake) + **Google Cloud** (reconciliation engine). Each has its **own BAA**.

## 1. Google Workspace (email + Drive)
- [ ] Workspace on practicaldatawork.com, Business Starter or higher (Business Plus adds Vault for mail retention/eDiscovery).
- [ ] Super admin accepts the **Workspace HIPAA BAA**: Admin console → Account → Account settings → Legal and compliance.
- [ ] Enforce 2-Step Verification (passkeys / security keys) for all users.
- [ ] Turn OFF services not covered by the BAA (e.g. Photos, Blogger, YouTube, Contacts sharing) and restrict Marketplace / third-party app access.
- [ ] Drive: external sharing off by default; one restricted Shared Drive `Client Data (PHI)` with a folder per client; no "anyone with the link".
- [ ] Gmail: never send PHI in email; confidential mode is not a substitute for portals.
- [ ] DNS: MX `smtp.google.com`, SPF `v=spf1 include:_spf.google.com include:relay.mailchannels.net ~all`, DKIM from Admin console, DMARC `p=none` → `quarantine` after 2–4 weeks.
- [ ] Addresses: `junaid@`, `audits@` (group for form leads), `privacy@`, `security@`.

## 2. Google Cloud (engine)
- [ ] Cloud organization tied to the Workspace domain; billing account in the company (LLC) name.
- [ ] Accept the **Google Cloud BAA** (self-serve per "Privacy compliance and records for Google Cloud", or via sales). Separate from the Workspace BAA.
- [ ] Use only BAA-covered, GA products: Cloud Storage, BigQuery, Cloud Run (+ jobs), Cloud Run functions, Cloud Scheduler, Pub/Sub, Workflows, Secret Manager, Cloud KMS, Cloud Logging, IAP. No Pre-GA/preview products with PHI.
- [ ] See `docs/infrastructure.md` for projects, buckets, IAM, logging and retention.

## 3. Company & paperwork
- [ ] LLC formed; contracts, BAAs and cloud billing in the LLC's name.
- [ ] **Pharmacy BAA template** reviewed by a healthcare attorney.
- [ ] Written **security risk assessment** (HIPAA Security Rule) and short policies: access control, incident response, breach notification, retention & destruction, workforce training (log it yearly).
- [ ] Vendor/subcontractor BAA register (Google Workspace, Google Cloud, any other tool touching PHI).
- [ ] Cyber liability + professional (E&O) insurance before the first client file.

## 4. Devices
- [ ] FileVault on, auto-lock ≤ 5 min, automatic updates, separate work macOS user.
- [ ] Password manager; passkeys / security keys on Workspace, Google Cloud, GitHub, Cloudflare, bank.
- [ ] No PHI stored locally. Work in the cloud project or restricted Shared Drive.

## Rules
- The website form collects **business contact info only**; the site says never to send patient data.
- No PHI in email bodies/attachments, this git repo, chat tools, or AI tools without a BAA covering that tool. Develop on synthetic data.
- Least privilege; access logged; client data purged on the schedule in each BAA.

## Later
- Compliance tooling (Vanta / Drata / Accountable) and SOC 2 Type I, which co-ops will likely ask for.
