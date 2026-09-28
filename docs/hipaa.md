# HIPAA setup checklist

We are a **business associate** of each pharmacy once we receive claim data. Nothing real moves until these are done.

## Before the first real file
- [ ] Business email on our domain (Google Workspace or Microsoft 365) with the provider's **BAA accepted**. Consumer Gmail has no BAA; don't use it for anything clinical.
- [ ] **Pharmacy BAA template** reviewed by a healthcare attorney.
- [ ] Written **security risk assessment** (required by the HIPAA Security Rule) and short policies: access control, incident response, breach notification, retention and destruction, workforce training.
- [ ] MFA on every account; full-disk encryption on laptops; password manager.
- [ ] Secure file intake with a BAA-covered vendor: Workspace Drive (to start), Box/ShareFile business, or AWS (BAA via AWS Artifact; S3 + Transfer Family, KMS encryption, CloudTrail).
- [ ] Minimum necessary: only negotiated-drug claims, payment files and supporting invoices.

## Rules
- The website form collects **business contact info only**. The form and site say never to send patient data.
- No PHI in email bodies or attachments. Prefer direct access (pharmacy names us MFP vendor on MTF, adds us to Beacon).
- No PHI in this git repo, in chat tools, or in AI tools without a BAA covering that tool. Develop on synthetic data.
- Every vendor that stores or processes PHI signs a BAA with us (subcontractor BAA).
- Log access; purge client data on the schedule in each BAA.

## Later
- Cyber insurance once we have clients.
- Compliance tooling (Vanta / Drata / Accountable) and a SOC 2 Type I, which co-ops will likely ask for.
