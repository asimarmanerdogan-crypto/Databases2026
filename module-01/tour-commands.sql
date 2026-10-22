.bail on
.mode column
.headers on
CREATE TABLE IF NOT EXISTS reading(machine TEXT, vib REAL);
DELETE FROM reading;
INSERT INTO reading VALUES ('cnc-01', 1.2), ('cnc-02', 2.4), ('cnc-01', 0.9);
.tables
.schema reading
.timer on
SELECT machine, max(vib) AS peak FROM reading GROUP BY machine;
.timer off
.echo off
.output module-01/tour.sql
.dump
.output stdout
.quit

