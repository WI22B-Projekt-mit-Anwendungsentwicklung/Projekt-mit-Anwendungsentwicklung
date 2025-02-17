CREATE DATABASE IF NOT EXISTS db;
use db;

CREATE TABLE IF NOT EXISTS Station (
    SID INT AUTO_INCREMENT PRIMARY KEY,
    station_id VARCHAR(50),
    station_name VARCHAR(50),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    first_tmax INT NOT NULL,
    latest_tmax INT NOT NULL,
    first_tmin INT NOT NULL,
    latest_tmin INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Datapoint (
    DID INT AUTO_INCREMENT PRIMARY KEY,
    SID INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    tmax FLOAT NOT NULL,
    tmin FLOAT NOT NULL,
    FOREIGN KEY (SID) REFERENCES Station(SID) ON DELETE CASCADE
);

