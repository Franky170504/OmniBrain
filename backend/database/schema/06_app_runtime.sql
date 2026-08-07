BEGIN;

-- ---------------------------------------------------------------------------
-- Fix ordering-sensitive trigger dependency from the existing schema set.
-- For a fresh database, run 04_common_functions.sql before 03_knowledge.sql.
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- knowledge.chunks currently makes content_checksum globally unique. That
-- prevents identical text (headers, disclaimers, repeated paragraphs) from
-- existing in more than one place. Keep the checksum searchable, but not
-- globally unique.
-- ---------------------------------------------------------------------------
ALTER TABLE knowledge.chunks
    DROP CONSTRAINT IF EXISTS uq_chunks_checksum;

CREATE INDEX IF NOT EXISTS idx_chunks_content_checksum
ON knowledge.chunks(content_checksum);

-- ---------------------------------------------------------------------------
-- Document access mapping.
-- knowledge.documents is globally deduplicated by checksum, so permissions
-- belong in a mapping table instead of putting one owner directly on the row.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge.document_user_access (
    access_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    user_id UUID NOT NULL,
    access_level VARCHAR(20) NOT NULL DEFAULT 'OWNER',
    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_user_access_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge.documents(document_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_document_user_access_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_document_user_access
        UNIQUE (document_id, user_id),

    CONSTRAINT chk_document_user_access_level
        CHECK (access_level IN ('OWNER', 'EDITOR', 'VIEWER'))
);

CREATE INDEX IF NOT EXISTS idx_document_user_access_user
ON knowledge.document_user_access(user_id);

CREATE INDEX IF NOT EXISTS idx_document_user_access_document
ON knowledge.document_user_access(document_id);

-- ---------------------------------------------------------------------------
-- Chat session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_engine.chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    selected_document_id UUID,
    title VARCHAR(255),
    session_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMPTZ,

    CONSTRAINT fk_chat_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_chat_sessions_document
        FOREIGN KEY (selected_document_id)
        REFERENCES knowledge.documents(document_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_chat_sessions_status
        CHECK (session_status IN ('ACTIVE', 'ARCHIVED', 'DELETED'))
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_updated
ON query_engine.chat_sessions(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_document
ON query_engine.chat_sessions(selected_document_id);

DROP TRIGGER IF EXISTS trg_chat_sessions_set_updated_at
ON query_engine.chat_sessions;

CREATE TRIGGER trg_chat_sessions_set_updated_at
BEFORE UPDATE ON query_engine.chat_sessions
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

-- ---------------------------------------------------------------------------
-- Chat messages
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_engine.chat_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_id UUID NOT NULL,
    document_id UUID,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chat_messages_session
        FOREIGN KEY (session_id)
        REFERENCES query_engine.chat_sessions(session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_chat_messages_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_chat_messages_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge.documents(document_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT uq_chat_messages_sequence
        UNIQUE (session_id, sequence_number),

    CONSTRAINT chk_chat_messages_role
        CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM', 'TOOL')),

    CONSTRAINT chk_chat_messages_content
        CHECK (length(trim(content)) > 0),

    CONSTRAINT chk_chat_messages_sequence
        CHECK (sequence_number >= 1)
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
ON query_engine.chat_messages(session_id, created_at);

-- ---------------------------------------------------------------------------
-- Agent execution records
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_engine.agent_runs (
    agent_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_message_id UUID NOT NULL,
    assistant_message_id UUID,
    route VARCHAR(30),
    route_reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    model_provider VARCHAR(50),
    model_name VARCHAR(150),
    langsmith_trace_id VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    latency_ms INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost_usd NUMERIC(14,8),
    error_type VARCHAR(150),
    error_message TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_agent_runs_session
        FOREIGN KEY (session_id)
        REFERENCES query_engine.chat_sessions(session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_agent_runs_user_message
        FOREIGN KEY (user_message_id)
        REFERENCES query_engine.chat_messages(message_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_agent_runs_assistant_message
        FOREIGN KEY (assistant_message_id)
        REFERENCES query_engine.chat_messages(message_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_agent_runs_route
        CHECK (route IS NULL OR route IN ('document_agent', 'general_agent', 'clarify_agent')),

    CONSTRAINT chk_agent_runs_status
        CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),

    CONSTRAINT chk_agent_runs_latency
        CHECK (latency_ms IS NULL OR latency_ms >= 0),

    CONSTRAINT chk_agent_runs_tokens
        CHECK (
            (prompt_tokens IS NULL OR prompt_tokens >= 0)
            AND (completion_tokens IS NULL OR completion_tokens >= 0)
            AND (total_tokens IS NULL OR total_tokens >= 0)
        )
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_session_started
ON query_engine.agent_runs(session_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_runs_route
ON query_engine.agent_runs(route);

DROP TRIGGER IF EXISTS trg_agent_runs_set_updated_at
ON query_engine.agent_runs;

CREATE TRIGGER trg_agent_runs_set_updated_at
BEFORE UPDATE ON query_engine.agent_runs
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

-- ---------------------------------------------------------------------------
-- One Qdrant retrieval operation
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_engine.retrieval_runs (
    retrieval_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_run_id UUID NOT NULL,
    user_id UUID NOT NULL,
    document_id UUID,
    query_text TEXT NOT NULL,
    collection_name VARCHAR(255) NOT NULL,
    embedding_model VARCHAR(255),
    search_limit INTEGER NOT NULL,
    score_threshold DOUBLE PRECISION,
    result_count INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT fk_retrieval_runs_agent
        FOREIGN KEY (agent_run_id)
        REFERENCES query_engine.agent_runs(agent_run_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_retrieval_runs_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_retrieval_runs_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge.documents(document_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_retrieval_runs_query
        CHECK (length(trim(query_text)) > 0),

    CONSTRAINT chk_retrieval_runs_search_limit
        CHECK (search_limit > 0),

    CONSTRAINT chk_retrieval_runs_result_count
        CHECK (result_count >= 0),

    CONSTRAINT chk_retrieval_runs_latency
        CHECK (latency_ms IS NULL OR latency_ms >= 0)
);

CREATE INDEX IF NOT EXISTS idx_retrieval_runs_agent
ON query_engine.retrieval_runs(agent_run_id);

CREATE INDEX IF NOT EXISTS idx_retrieval_runs_document
ON query_engine.retrieval_runs(document_id);

-- ---------------------------------------------------------------------------
-- Individual retrieved context items
-- text_snapshot is nullable so production can store references only.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_engine.context_items (
    context_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retrieval_run_id UUID NOT NULL,
    rank INTEGER NOT NULL,
    qdrant_point_id UUID,
    chunk_id UUID,
    document_id UUID,
    filename VARCHAR(255),
    page_start INTEGER,
    page_end INTEGER,
    score DOUBLE PRECISION,
    text_snapshot TEXT,
    text_checksum CHAR(64),
    token_count INTEGER,
    was_used_in_prompt BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_context_items_retrieval
        FOREIGN KEY (retrieval_run_id)
        REFERENCES query_engine.retrieval_runs(retrieval_run_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_context_items_chunk
        FOREIGN KEY (chunk_id)
        REFERENCES knowledge.chunks(chunk_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_context_items_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge.documents(document_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT uq_context_items_rank
        UNIQUE (retrieval_run_id, rank),

    CONSTRAINT chk_context_items_rank
        CHECK (rank >= 1),

    CONSTRAINT chk_context_items_page_start
        CHECK (page_start IS NULL OR page_start >= 1),

    CONSTRAINT chk_context_items_page_end
        CHECK (
            page_end IS NULL
            OR page_start IS NULL
            OR page_end >= page_start
        ),

    CONSTRAINT chk_context_items_token_count
        CHECK (token_count IS NULL OR token_count >= 0),

    CONSTRAINT chk_context_items_checksum
        CHECK (
            text_checksum IS NULL
            OR text_checksum ~ '^[A-Fa-f0-9]{64}$'
        )
);

CREATE INDEX IF NOT EXISTS idx_context_items_retrieval_rank
ON query_engine.context_items(retrieval_run_id, rank);

CREATE INDEX IF NOT EXISTS idx_context_items_chunk
ON query_engine.context_items(chunk_id);

CREATE INDEX IF NOT EXISTS idx_context_items_document
ON query_engine.context_items(document_id);

COMMIT;
