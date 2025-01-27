CREATE DATABASE IF NOT EXISTS db;
use db;

CREATE TABLE IF NOT EXISTS Station (
    id VARCHAR(50) PRIMARY KEY,      -- Eindeutige ID der Station, max. Länge 50 Zeichen
    latitude FLOAT NOT NULL,         -- Geografische Breite, erforderlich
    longitude FLOAT NOT NULL,        -- Geografische Länge, erforderlich
    first_tmax INT NOT NULL,
    latest_tmax INT NOT NULL,
    first_tmin INT NOT NULL,
    latest_tmin INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Datapoint (
    id INT AUTO_INCREMENT PRIMARY KEY,    -- Eindeutige ID für jeden Datensatz
    station_id VARCHAR(50),               -- Fremdschlüssel zur Station-Tabelle
    year INT NOT NULL,
    month INT NOT NULL,
    tmax FLOAT NOT NULL,                  -- Durchschnittlicher Tmax-Wert des Monats
    tmin FLOAT NOT NULL,                  -- Durchschnittlicher Tmin-Wert des Monats
    FOREIGN KEY (station_id) REFERENCES Station(id) ON DELETE CASCADE
);

