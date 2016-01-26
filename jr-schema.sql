CREATE TABLE sensors
(
    name TEXT NOT NULL,
    id TEXT NOT NULL,
    notes TEXT,
    volts REAL,
    active INTEGER
);
CREATE TABLE temps
(
    timestamp TEXT,
    temp REAL,
    ID TEXT
);
