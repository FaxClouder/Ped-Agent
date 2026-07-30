CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    answer_document TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at, id);

CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    status TEXT NOT NULL,
    error TEXT,
    cancel_requested INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX idx_runs_conversation ON runs(conversation_id, created_at DESC);
CREATE UNIQUE INDEX idx_one_active_run_per_conversation
ON runs(conversation_id)
WHERE status IN ('queued', 'running');

CREATE TABLE run_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    event TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_run_events_replay ON run_events(run_id, id);

CREATE TABLE evidence_items (
    evidence_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES runs(id) ON DELETE SET NULL,
    origin TEXT NOT NULL,
    title TEXT NOT NULL,
    quote TEXT NOT NULL,
    locator TEXT,
    url TEXT,
    doi TEXT,
    resource_id TEXT,
    version_id TEXT,
    chunk_id TEXT,
    publisher TEXT,
    authority TEXT,
    retrieved_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    score REAL NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX idx_evidence_run ON evidence_items(run_id);

CREATE TABLE message_citations (
    message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    evidence_id TEXT NOT NULL REFERENCES evidence_items(evidence_id),
    claim_ids TEXT NOT NULL,
    PRIMARY KEY (message_id, label)
);

