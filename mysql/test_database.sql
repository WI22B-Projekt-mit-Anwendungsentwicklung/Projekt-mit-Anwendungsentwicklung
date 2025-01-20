CREATE DATABASE IF NOT EXISTS db;
use db;

CREATE TABLE Station (
    id VARCHAR(50) PRIMARY KEY,      -- Eindeutige ID der Station, max. Länge 50 Zeichen
    latitude FLOAT NOT NULL,         -- Geografische Breite, erforderlich
    longitude FLOAT NOT NULL         -- Geografische Länge, erforderlich
);
