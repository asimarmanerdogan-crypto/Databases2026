-- Task A: run against the EXISTING Module02/legacy.db only.

-- Predictions before indexing: Q1 SCAN; Q2 SCAN; Q3 SCAN.

SELECT sqlite_version();

SELECT name, sql FROM sqlite_schema WHERE type='table' AND name IN ('maint_job','machine');

SELECT name, tbl_name, sql FROM sqlite_schema WHERE type='index';

-- No existing ix_job_tech was present; no index was dropped.

-- Baseline

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
SELECT * FROM maint_job WHERE technician = 'Beier';

EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
SELECT * FROM machine WHERE machine_name = 'cnc-02';

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
SELECT * FROM maint_job WHERE technician LIKE '%ei%';

CREATE INDEX ix_job_tech ON maint_job(technician);

-- After indexing

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
SELECT * FROM maint_job WHERE technician = 'Beier';

EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
SELECT * FROM machine WHERE machine_name = 'cnc-02';

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
SELECT * FROM maint_job WHERE technician LIKE '%ei%';

-- Negative experiments

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE LOWER(technician) = 'beier';
SELECT * FROM maint_job WHERE LOWER(technician) = 'beier';

EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
SELECT * FROM maint_job WHERE technician LIKE '%ei%';
