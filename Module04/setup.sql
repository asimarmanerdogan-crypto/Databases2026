PRAGMA foreign_keys = ON;
-- Run only against a new Module04 database; no DROP statements.
CREATE TABLE sensor(
 sensor_id INTEGER PRIMARY KEY,
 machine_id TEXT NOT NULL,
 metric TEXT NOT NULL CHECK(metric IN ('temp_c','vib_rms','spindle_load')),
 unit TEXT NOT NULL,
 UNIQUE(machine_id,metric)
) STRICT;
CREATE TABLE reading(
 reading_id INTEGER PRIMARY KEY,
 sensor_id INTEGER NOT NULL REFERENCES sensor(sensor_id),
 ts TEXT NOT NULL,
 value REAL NOT NULL,
 interval_s INTEGER NOT NULL CHECK(interval_s>0),
 energy_j REAL GENERATED ALWAYS AS(value*interval_s) VIRTUAL,
 CHECK(value BETWEEN -273.15 AND 5000)
) STRICT;
CREATE UNIQUE INDEX ux_reading_sensor_ts ON reading(sensor_id,ts);
