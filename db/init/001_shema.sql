-- customers
CREATE TABLE IF NOT EXISTS customers (
  id UUID PRIMARY KEY,
  display_name TEXT,
  phone_e164 TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- calls
CREATE TABLE IF NOT EXISTS calls (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  livekit_room_id TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  status TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- help_requests
CREATE TABLE IF NOT EXISTS help_requests (
  id UUID PRIMARY KEY,
  call_id UUID REFERENCES calls(id),
  customer_id UUID NOT NULL REFERENCES customers(id),
  question_text TEXT NOT NULL,
  normalized_key TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  resolved_at TIMESTAMPTZ,
  cancel_reason TEXT
);

-- supervisor_responses
CREATE TABLE IF NOT EXISTS supervisor_responses (
  id UUID PRIMARY KEY,
  help_request_id UUID NOT NULL UNIQUE REFERENCES help_requests(id) ON DELETE CASCADE,
  responder_id TEXT,
  answer_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- knowledge_base
CREATE TABLE IF NOT EXISTS knowledge_base (
  id UUID PRIMARY KEY,
  normalized_key TEXT,
  question_text_example TEXT NOT NULL,
  answer_text TEXT NOT NULL,
  source_help_request_id UUID REFERENCES help_requests(id),
  valid_to TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB,
  embedding vector(1536)
);

-- followups
CREATE TABLE IF NOT EXISTS followups (
  id UUID PRIMARY KEY,
  help_request_id UUID NOT NULL UNIQUE REFERENCES help_requests(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL REFERENCES customers(id),
  channel TEXT NOT NULL,
  payload JSONB,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at TIMESTAMPTZ
);

-- indices for performance
CREATE INDEX IF NOT EXISTS hr_status_created_idx ON help_requests (status, created_at DESC);

-- Indexes for use later:
-- CREATE INDEX IF NOT EXISTS hr_expires_idx ON help_requests (expires_at);                -- timeout sweeper
-- CREATE INDEX IF NOT EXISTS followups_status_idx ON followups (status, created_at);      -- sender worker

-- ANN index for semantic KB search
CREATE INDEX IF NOT EXISTS knowledge_base_vec_idx
  ON knowledge_base
  USING ivfflat (embedding vector_cosine)
  WITH (lists = 100)