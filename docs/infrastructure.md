# Infrastructure (Google Cloud)

## Layout
| Project | Purpose | PHI? |
|---|---|---|
| `tallyrx-prod` | Client data + reconciliation runs | Yes (BAA-covered products only) |
| `tallyrx-dev` | Development on synthetic data | **No, never** |

Region: `us-central1` (keep all PHI resources in the US).

## Data flow
1. **Intake**: early clients upload through the restricted Workspace Shared Drive; later, signed upload URLs into
   `gs://tallyrx-prod-intake` (per-client prefixes), or direct pulls from MTF/Beacon exports.
2. **Raw zone**: `gs://tallyrx-prod-raw/<client>/<source>/<date>/` (CMEK via Cloud KMS, uniform bucket-level access,
   public access prevention enforced, object versioning, lifecycle delete after the BAA retention period).
3. **Adapters** (Cloud Run jobs): parse 835 / Beacon / pharmacy-system exports into canonical tables.
4. **Warehouse**: BigQuery datasets `raw`, `canonical`, `recon` (per-client row-level security or one dataset per client).
   `mfp-recon` logic runs as Cloud Run jobs (or BigQuery SQL) on a Cloud Scheduler trigger.
5. **Outputs**: audit reports and dispute packets written to `gs://tallyrx-prod-reports/<client>/`, shared with the
   client via the Workspace Shared Drive.

## Controls
- IAM: groups, not individuals; least privilege; no service-account keys (use workload identity / attached SAs).
- Org policies: `storage.publicAccessPrevention`, `iam.disableServiceAccountKeyCreation`, `gcp.resourceLocations` (US only).
- Cloud Audit Logs: enable Data Access logs for Cloud Storage and BigQuery in `tallyrx-prod`; export to a locked log bucket.
- Secrets in Secret Manager; encryption keys in Cloud KMS with rotation.
- Budget alerts on the billing account.

## Setup commands (sketch)
```bash
gcloud projects create tallyrx-prod --organization=<ORG_ID>
gcloud config set project tallyrx-prod
gcloud services enable storage.googleapis.com bigquery.googleapis.com run.googleapis.com \
  cloudscheduler.googleapis.com cloudkms.googleapis.com secretmanager.googleapis.com
gcloud kms keyrings create tallyrx --location=us-central1
gcloud kms keys create phi --keyring=tallyrx --location=us-central1 --purpose=encryption --rotation-period=90d \
  --next-rotation-time=$(date -u -d '+90 days' +%Y-%m-%dT%H:%M:%SZ)
gcloud storage buckets create gs://tallyrx-prod-raw --location=us-central1 --uniform-bucket-level-access \
  --public-access-prevention --default-encryption-key=projects/tallyrx-prod/locations/us-central1/keyRings/tallyrx/cryptoKeys/phi
bq --location=US mk --dataset tallyrx-prod:canonical
```
(Grant the Cloud Storage service agent `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key before creating CMEK buckets.)

## Credits
Apply to the Google for Startups Cloud Program once the LLC, domain email and website are live.
