CREATE TABLE IF NOT EXISTS identities (
    id TEXT PRIMARY KEY,
    alias TEXT
);

CREATE TABLE IF NOT EXISTS vouches (
    source TEXT,
    target TEXT,
    value REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, target)
);
