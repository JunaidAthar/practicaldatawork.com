-- Cloudflare D1 Database Setup for Contact Form
-- Run this to create the contacts table

CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT,
  service TEXT,
  budget TEXT,
  message TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT DEFAULT 'new',
  notes TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_created_at ON contacts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_status ON contacts(status);

-- Create a view for easy querying
CREATE VIEW IF NOT EXISTS recent_contacts AS
SELECT 
  id,
  name,
  email,
  company,
  service,
  budget,
  substr(message, 1, 100) || '...' as message_preview,
  created_at,
  status
FROM contacts
ORDER BY created_at DESC
LIMIT 50;

