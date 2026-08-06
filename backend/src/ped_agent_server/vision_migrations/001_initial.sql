PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vision_tasks (
    id TEXT PRIMARY KEY,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL,
    resume_status TEXT,
    error TEXT,
    spec_json TEXT NOT NULL,
    source_video_path TEXT NOT NULL,
    source_video_sha256 TEXT NOT NULL,
    model_id TEXT NOT NULL,
    scene_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vision_artifacts (
    artifact_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES vision_tasks(id) ON DELETE CASCADE,
    stage TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    parent_artifact_id TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vision_artifacts_task
ON vision_artifacts(task_id, stage, active, created_at);

CREATE TABLE IF NOT EXISTS vision_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES vision_tasks(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    event TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vision_events_task
ON vision_events(task_id, id);

CREATE TABLE IF NOT EXISTS vision_review_patches (
    patch_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES vision_tasks(id) ON DELETE CASCADE,
    parent_artifact_id TEXT NOT NULL,
    patch_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
