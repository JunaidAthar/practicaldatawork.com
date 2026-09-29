-- D1 schema for free MFP refund audit requests (database: contacts).
-- Business contact info only. Never store patient information here.
-- Apply: npx wrangler d1 execute contacts --remote --file=setup-database.sql

CREATE TABLE IF NOT EXISTS audit_requests (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  name              TEXT NOT NULL,
  email             TEXT NOT NULL,
  phone             TEXT,
  role              TEXT,     -- Owner | Pharmacist in charge | Manager / billing | Co-op or group | Other
  pharmacy          TEXT NOT NULL,
  location          TEXT,     -- "City, ST"
  stores            TEXT,     -- 1 | 2–5 | 6–20 | 20+
  has_340b          TEXT,     -- No | Yes | Not sure
  monthly_mfp_fills INTEGER,
  notes             TEXT,
  status            TEXT NOT NULL DEFAULT 'new',  -- new | contacted | converted | closed
  admin_notes       TEXT,
  ip_address        TEXT,
  user_agent        TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_requests_created ON audit_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_requests_status ON audit_requests(status);
CREATE INDEX IF NOT EXISTS idx_audit_requests_email ON audit_requests(email);
