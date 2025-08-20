ALTER TABLE help_requests
ALTER COLUMN expires_at
SET DEFAULT (now() + interval '1 hour');