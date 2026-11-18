-- GARDA Basic local database, media stays on dedicated local filesystem.
CREATE TABLE IF NOT EXISTS cameras (
 id uuid PRIMARY KEY,
 name text NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
 media_path text NOT NULL UNIQUE,
 source_ciphertext text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS cameras_created_idx ON cameras (created_at);
CREATE TABLE IF NOT EXISTS audit_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 action text NOT NULL,
 resource_id uuid,
 details jsonb NOT NULL DEFAULT '{}'::jsonb,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS audit_created_idx ON audit_events (created_at DESC);
CREATE INDEX IF NOT EXISTS audit_resource_idx ON audit_events (resource_id, created_at DESC);
CREATE TABLE IF NOT EXISTS incidents (
 id uuid PRIMARY KEY,
 camera_id uuid REFERENCES cameras(id) ON DELETE RESTRICT,
 title text NOT NULL,
 status text NOT NULL DEFAULT 'open'
 CHECK (status IN ('open', 'acknowledged', 'resolved')),
 created_at timestamptz NOT NULL DEFAULT now(),
 resolved_at timestamptz
);
CREATE INDEX IF NOT EXISTS incidents_camera_created_idx ON incidents (camera_id, created_at DESC);
