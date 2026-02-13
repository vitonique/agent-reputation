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

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    owner_id TEXT,
    type TEXT, -- 'Product', 'Infra', 'Content', 'Philosophy'
    weight REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_id) REFERENCES identities(id)
);
