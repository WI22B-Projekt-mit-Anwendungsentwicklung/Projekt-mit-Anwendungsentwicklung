CREATE DATABASE IF NOT EXISTS db;
use db;

CREATE TABLE IF NOT EXISTS Station (
    SID INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(50),
    latitude FLOAT NOT NULL,         -- Geografische Breite, erforderlich
    longitude FLOAT NOT NULL,        -- Geografische Länge, erforderlich
    first_tmax INT NOT NULL,
    latest_tmax INT NOT NULL,
    first_tmin INT NOT NULL,
    latest_tmin INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Datapoint (
    DID INT AUTO_INCREMENT PRIMARY KEY,    -- Eindeutige ID für jeden Datensatz
    SID INT NOT NULL,               -- Fremdschlüssel zur Station-Tabelle
    year INT NOT NULL,
    month INT NOT NULL,
    tmax FLOAT NOT NULL,                  -- Durchschnittlicher Tmax-Wert des Monats
    tmin FLOAT NOT NULL,                  -- Durchschnittlicher Tmin-Wert des Monats
    FOREIGN KEY (SID) REFERENCES Station(SID) ON DELETE CASCADE
);

