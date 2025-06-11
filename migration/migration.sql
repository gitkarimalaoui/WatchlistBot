-- migration.sql

-- 1) Création de la table news_score si elle n'existe pas
CREATE TABLE IF NOT EXISTS news_score (
    symbol TEXT PRIMARY KEY,
    summary TEXT,
    score INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment TEXT,
    last_analyzed DATETIME
);

-- (Les ALTER TABLE seront gérés dynamiquement en Python)
