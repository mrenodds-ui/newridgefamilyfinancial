-- HAL-10593 / HON-003 — recon_variance_history (PHI-safe aggregates only)
-- Applied via softdent_visual_ledger_recon.ensure_recon_variance_history_schema
-- No patient/account/PHI columns. triggers_gold_ingest always 0.

CREATE TABLE IF NOT EXISTS recon_variance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start TEXT,
    period_end TEXT,
    visual_total REAL,
    ledger_total REAL,
    clamped_ledger_total REAL,
    variance_dollars REAL,
    top_carrier_code TEXT,
    scope_mismatch INTEGER NOT NULL DEFAULT 0,
    result_code TEXT,
    created_at TEXT NOT NULL,
    package_build_id TEXT,
    triggers_gold_ingest INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_recon_variance_history_created
    ON recon_variance_history(created_at DESC);
