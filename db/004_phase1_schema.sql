-- OFFICINA
-- 004_phase1_schema.sql — migraciones Phase 1 / S30
-- Movido de src/db/schemas/ → db/ en S32
-- Aplica sobre schema base (001): elimina embedding/facts de nodes,
-- agrega contextual_type/external_id, crea node_chunks vector(1536),
-- crea schema session.*

-- BLOQUE 1 — limpiar índices sobre columnas a eliminar
DROP INDEX IF EXISTS idx_nodes_embedding;
DROP INDEX IF EXISTS idx_nodes_tsv;

-- BLOQUE 2 — eliminar columnas obsoletas
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding;
ALTER TABLE nodes DROP COLUMN IF EXISTS facts;

-- BLOQUE 3 — agregar columnas nuevas
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS contextual_type TEXT;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS external_id    TEXT;
ALTER TABLE nodes ALTER COLUMN node_type SET DEFAULT 'contextual';

-- BLOQUE 4 — CHECK constraints
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS check_persistent_no_contextual_type;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS check_contextual_has_contextual_type;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS check_contextual_type_values;

ALTER TABLE nodes ADD CONSTRAINT check_persistent_no_contextual_type
  CHECK (NOT (node_type = 'persistent' AND contextual_type IS NOT NULL));
ALTER TABLE nodes ADD CONSTRAINT check_contextual_has_contextual_type
  CHECK (NOT (node_type = 'contextual' AND contextual_type IS NULL));
ALTER TABLE nodes ADD CONSTRAINT check_contextual_type_values
  CHECK (contextual_type IN ('situational','episodic','documental','system') OR contextual_type IS NULL);

-- BLOQUE 5 — índices nuevos nodes
CREATE INDEX IF NOT EXISTS idx_nodes_contextual_type ON nodes(contextual_type) WHERE contextual_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_external_id ON nodes(external_id) WHERE external_id IS NOT NULL;

-- BLOQUE 6 — edges: agregar status
ALTER TABLE edges ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
CREATE INDEX IF NOT EXISTS idx_edges_status ON edges(status);

-- BLOQUE 7 — node_chunks
CREATE TABLE IF NOT EXISTS node_chunks (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id       UUID        NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  chunk_text    TEXT        NOT NULL,
  embedding     vector(1536),
  search_vector tsvector    GENERATED ALWAYS AS (to_tsvector('simple', chunk_text)) STORED,
  status        TEXT        NOT NULL DEFAULT 'active',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chunks_node_id ON node_chunks(node_id);
CREATE INDEX IF NOT EXISTS idx_chunks_search_vector ON node_chunks USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON node_chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);

-- BLOQUE 8 — usage (spend logging, reemplaza litellm.spend_logs)
CREATE TABLE IF NOT EXISTS usage (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID,
  model_used      TEXT,
  provider        TEXT,
  tokens_input    INTEGER,
  tokens_output   INTEGER,
  latency_ms      INTEGER,
  tool_calls      JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- BLOQUE 9 — schema session
CREATE SCHEMA IF NOT EXISTS session;

CREATE TABLE IF NOT EXISTS session.workspaces (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT        NOT NULL,
  description TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session.folders (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID        NOT NULL REFERENCES session.workspaces(id) ON DELETE CASCADE,
  name         TEXT        NOT NULL,
  description  TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session.conversations (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID        REFERENCES session.workspaces(id) ON DELETE SET NULL,
  folder_id    UUID        REFERENCES session.folders(id)    ON DELETE SET NULL,
  title        TEXT,
  model_group  TEXT        NOT NULL DEFAULT 'officina-primary',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session.messages (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID        NOT NULL REFERENCES session.conversations(id) ON DELETE CASCADE,
  role            TEXT        NOT NULL CHECK (role IN ('user','assistant')),
  content         TEXT        NOT NULL,
  model_used      TEXT,
  tokens_used     INTEGER,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session.documents (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id       UUID        REFERENCES session.folders(id)       ON DELETE SET NULL,
  conversation_id UUID        REFERENCES session.conversations(id) ON DELETE SET NULL,
  filename        TEXT        NOT NULL,
  content_type    TEXT,
  storage_path    TEXT        NOT NULL,
  status          TEXT        NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','processed','failed')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_session_conversations_workspace ON session.conversations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_session_conversations_folder    ON session.conversations(folder_id);
CREATE INDEX IF NOT EXISTS idx_session_messages_conversation   ON session.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_session_messages_created        ON session.messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_session_documents_folder        ON session.documents(folder_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_status        ON session.documents(status) WHERE status = 'pending';

-- BLOQUE 10 — verificación
SELECT 'nodes' AS objeto, COUNT(*) FROM nodes
UNION ALL SELECT 'edges', COUNT(*) FROM edges
UNION ALL SELECT 'node_chunks', COUNT(*) FROM node_chunks
UNION ALL SELECT 'usage', COUNT(*) FROM usage
UNION ALL SELECT 'session.workspaces', COUNT(*) FROM session.workspaces
UNION ALL SELECT 'session.conversations', COUNT(*) FROM session.conversations
UNION ALL SELECT 'session.messages', COUNT(*) FROM session.messages
UNION ALL SELECT 'session.documents', COUNT(*) FROM session.documents;
